from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from app.extensions import db
from app.models.inventory import PharmacyInventory
from app.models.medicine import Medicine

class InventoryService:
    @staticmethod
    def get_pharmacy_inventory(pharmacy_id: int, query_str: str = None, status_filter: str = None) -> List[PharmacyInventory]:
        query = PharmacyInventory.query.filter_by(pharmacy_id=pharmacy_id).join(Medicine)

        if query_str:
            term = f"%{query_str.strip()}%"
            query = query.filter(
                (Medicine.name.ilike(term)) |
                (Medicine.generic_name.ilike(term)) |
                (Medicine.brand_name.ilike(term))
            )

        if status_filter:
            query = query.filter(PharmacyInventory.stock_status == status_filter.upper())

        return query.order_by(PharmacyInventory.last_updated_at.desc()).all()

    @staticmethod
    def add_or_update_inventory_item(
        pharmacy_id: int,
        medicine_id: int,
        quantity: int,
        price: float,
        notes: str = None,
        batch_number: str = None,
        expiry_date = None
    ) -> Tuple[Optional[PharmacyInventory], Optional[str]]:
        """
        Adds or updates inventory for a given pharmacy & medicine.
        CRITICAL: Explicitly touches and updates last_updated_at timestamp.
        """
        medicine = db.session.get(Medicine, medicine_id)
        if not medicine:
            return None, "Selected medicine does not exist."

        if quantity < 0:
            return None, "Quantity cannot be negative."
        if price < 0:
            return None, "Price cannot be negative."

        item = PharmacyInventory.query.filter_by(
            pharmacy_id=pharmacy_id,
            medicine_id=medicine_id
        ).first()

        if not item:
            item = PharmacyInventory(
                pharmacy_id=pharmacy_id,
                medicine_id=medicine_id
            )

        item.update_stock(
            quantity=quantity,
            price=price,
            notes=notes,
            batch_number=batch_number,
            expiry_date=expiry_date
        )

        db.session.add(item)
        db.session.commit()
        return item, None

    @staticmethod
    def delete_inventory_item(pharmacy_id: int, inventory_id: int) -> bool:
        item = PharmacyInventory.query.filter_by(id=inventory_id, pharmacy_id=pharmacy_id).first()
        if not item:
            return False
        db.session.delete(item)
        db.session.commit()
        return True

    @staticmethod
    def get_inventory_stats(pharmacy_id: int) -> Dict[str, int]:
        items = PharmacyInventory.query.filter_by(pharmacy_id=pharmacy_id).all()
        return {
            'total_items': len(items),
            'available': sum(1 for i in items if i.stock_status == 'AVAILABLE'),
            'low_stock': sum(1 for i in items if i.stock_status == 'LOW_STOCK'),
            'out_of_stock': sum(1 for i in items if i.stock_status == 'OUT_OF_STOCK')
        }
