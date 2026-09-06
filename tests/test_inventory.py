import time
from datetime import datetime, timezone
from app.services.inventory_service import InventoryService
from app.models.inventory import PharmacyInventory

def test_inventory_stock_status_and_mandatory_timestamp(app, test_data):
    with app.app_context():
        pharmacy_id = test_data['pharmacy_id']
        med_id = test_data['med_otc_id']

        inv = PharmacyInventory.query.filter_by(pharmacy_id=pharmacy_id, medicine_id=med_id).first()
        initial_timestamp = inv.last_updated_at

        # Sleep briefly to ensure datetime change
        time.sleep(0.01)

        # Update to quantity 0 -> OUT_OF_STOCK
        updated_item, err = InventoryService.add_or_update_inventory_item(
            pharmacy_id=pharmacy_id,
            medicine_id=med_id,
            quantity=0,
            price=4.50
        )
        assert err is None
        assert updated_item.stock_status == 'OUT_OF_STOCK'
        assert updated_item.last_updated_at > initial_timestamp

        # Update to quantity 5 -> LOW_STOCK
        updated_item2, _ = InventoryService.add_or_update_inventory_item(
            pharmacy_id=pharmacy_id,
            medicine_id=med_id,
            quantity=5,
            price=4.50
        )
        assert updated_item2.stock_status == 'LOW_STOCK'

        # Update to quantity 50 -> AVAILABLE
        updated_item3, _ = InventoryService.add_or_update_inventory_item(
            pharmacy_id=pharmacy_id,
            medicine_id=med_id,
            quantity=50,
            price=4.50
        )
        assert updated_item3.stock_status == 'AVAILABLE'

def test_inventory_negative_values_rejected(app, test_data):
    with app.app_context():
        pharmacy_id = test_data['pharmacy_id']
        med_id = test_data['med_otc_id']

        _, err_qty = InventoryService.add_or_update_inventory_item(pharmacy_id, med_id, quantity=-5, price=2.0)
        assert err_qty == "Quantity cannot be negative."

        _, err_price = InventoryService.add_or_update_inventory_item(pharmacy_id, med_id, quantity=10, price=-1.0)
        assert err_price == "Price cannot be negative."
