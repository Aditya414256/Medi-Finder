import pytest
from app.utils.helpers import calculate_haversine_distance
from app.services.location_service import LocationService

def test_haversine_distance_calculation():
    dist = calculate_haversine_distance(28.6139, 77.2090, 28.6289, 77.2180)
    assert 1.5 <= dist <= 2.2

    zero_dist = calculate_haversine_distance(28.6139, 77.2090, 28.6139, 77.2090)
    assert zero_dist == 0.0

def test_nearby_pharmacies_for_medicine(app, test_data):
    with app.app_context():
        med_id = test_data['med_otc_id']
        results = LocationService.get_nearby_pharmacies_for_medicine(
            medicine_id=med_id,
            customer_lat=28.6139,
            customer_lon=77.2090,
            max_radius_km=25.0,
            only_verified=True
        )
        assert len(results) >= 1
        first = results[0]
        assert first['pharmacy_name'] == 'Test Apex Pharmacy'
        assert first['stock_status'] == 'AVAILABLE'
        assert first['is_verified'] is True
        assert 'last_updated_human' in first
        assert first['distance_km'] == 0.0
