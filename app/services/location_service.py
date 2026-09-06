from typing import List, Dict, Any, Optional
from app.models.pharmacy import Pharmacy
from app.models.inventory import PharmacyInventory
from app.utils.helpers import calculate_haversine_distance, humanize_time_ago

class LocationService:
    @staticmethod
    def get_nearby_pharmacies_for_medicine(
        medicine_id: int,
        customer_lat: Optional[float] = None,
        customer_lon: Optional[float] = None,
        max_radius_km: float = 50.0,
        only_verified: bool = True,
        only_available: bool = False,
        requires_pickup: bool = False,
        requires_delivery: bool = False,
        sort_by: str = 'nearest' # 'nearest', 'available', 'recent'
    ) -> List[Dict[str, Any]]:
        """
        Retrieves pharmacies stocking a given medicine, annotates distance & last_updated, and applies filters.
        """
        query = PharmacyInventory.query.filter_by(medicine_id=medicine_id).join(Pharmacy)
        
        # Only active pharmacies
        query = query.filter(Pharmacy.is_active == True)

        if only_verified:
            query = query.filter(Pharmacy.verification_status == 'APPROVED')

        if only_available:
            query = query.filter(PharmacyInventory.stock_status.in_(['AVAILABLE', 'LOW_STOCK']))

        if requires_pickup:
            query = query.filter(Pharmacy.supports_pickup == True)

        if requires_delivery:
            query = query.filter(Pharmacy.supports_delivery == True)

        inventory_records = query.all()
        results = []

        for record in inventory_records:
            pharmacy = record.pharmacy
            distance = 0.0
            if customer_lat is not None and customer_lon is not None and pharmacy.latitude and pharmacy.longitude:
                distance = calculate_haversine_distance(customer_lat, customer_lon, pharmacy.latitude, pharmacy.longitude)
                if max_radius_km and distance > max_radius_km:
                    continue

            item_data = {
                'inventory_id': record.id,
                'pharmacy_id': pharmacy.id,
                'pharmacy_name': pharmacy.name,
                'pharmacy_phone': pharmacy.phone,
                'pharmacy_email': pharmacy.email,
                'address': pharmacy.address,
                'city': pharmacy.city,
                'state': pharmacy.state,
                'pincode': pharmacy.pincode,
                'latitude': pharmacy.latitude,
                'longitude': pharmacy.longitude,
                'is_verified': pharmacy.is_verified,
                'verification_status': pharmacy.verification_status,
                'supports_pickup': pharmacy.supports_pickup,
                'supports_delivery': pharmacy.supports_delivery,
                'delivery_fee': pharmacy.delivery_fee,
                'opening_hours': pharmacy.opening_hours,
                'quantity': record.quantity,
                'price': record.price,
                'stock_status': record.stock_status,
                'status_badge_class': record.status_badge_class,
                'last_updated_at': record.last_updated_at,
                'last_updated_human': humanize_time_ago(record.last_updated_at),
                'distance_km': distance,
                'batch_number': record.batch_number,
                'expiry_date': record.expiry_date
            }
            results.append(item_data)

        # Sorting
        if sort_by == 'nearest' and customer_lat is not None and customer_lon is not None:
            results.sort(key=lambda x: x['distance_km'])
        elif sort_by == 'available':
            status_priority = {'AVAILABLE': 1, 'LOW_STOCK': 2, 'OUT_OF_STOCK': 3, 'UNKNOWN': 4}
            results.sort(key=lambda x: (status_priority.get(x['stock_status'], 5), x['distance_km']))
        elif sort_by == 'recent':
            results.sort(key=lambda x: x['last_updated_at'], reverse=True)

        return results

    @staticmethod
    def get_all_nearby_pharmacies(
        customer_lat: Optional[float] = None,
        customer_lon: Optional[float] = None,
        max_radius_km: float = 50.0,
        only_verified: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Retrieves all pharmacies for the interactive map.
        """
        query = Pharmacy.query.filter(Pharmacy.is_active == True)
        if only_verified:
            query = query.filter(Pharmacy.verification_status == 'APPROVED')

        pharmacies = query.all()
        results = []
        for p in pharmacies:
            distance = 0.0
            if customer_lat is not None and customer_lon is not None and p.latitude and p.longitude:
                distance = calculate_haversine_distance(customer_lat, customer_lon, p.latitude, p.longitude)
                if max_radius_km and distance > max_radius_km:
                    continue

            results.append({
                'id': p.id,
                'name': p.name,
                'phone': p.phone,
                'email': p.email,
                'address': p.address,
                'city': p.city,
                'state': p.state,
                'pincode': p.pincode,
                'latitude': p.latitude,
                'longitude': p.longitude,
                'is_verified': p.is_verified,
                'verification_status': p.verification_status,
                'supports_pickup': p.supports_pickup,
                'supports_delivery': p.supports_delivery,
                'delivery_fee': p.delivery_fee,
                'opening_hours': p.opening_hours,
                'distance_km': distance,
                'medicine_count': p.inventory_items.count()
            })

        if customer_lat is not None and customer_lon is not None:
            results.sort(key=lambda x: x['distance_km'])

        return results
