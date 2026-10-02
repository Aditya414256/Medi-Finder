import pytest
from app.services.order_service import OrderService
from app.services.prescription_service import PrescriptionService
from app.models.order import Order
from app.models.inventory import PharmacyInventory
from app.models.pharmacy import Pharmacy

def test_order_requires_prescription_enforcement(app, test_data):
    with app.app_context():
        customer_id = test_data['customer_id']
        pharmacy_id = test_data['pharmacy_id']
        med_rx_id = test_data['med_rx_id'] # Requires prescription

        # Try ordering Rx medicine without prescription -> should fail
        order, err = OrderService.create_order(
            customer_id=customer_id,
            pharmacy_id=pharmacy_id,
            order_type='PICKUP',
            contact_phone='+1-555-1234',
            items_data=[{'medicine_id': med_rx_id, 'quantity': 1}],
            prescription_id=None
        )
        assert order is None
        assert err is not None
        assert 'require a valid prescription' in err.lower()

        # Create prescription and retry -> should succeed
        rx = PrescriptionService.create_prescription(
            customer_id=customer_id,
            file_path='rx.pdf',
            original_filename='rx.pdf',
            mime_type='application/pdf',
            file_size=1000
        )
        order2, err2 = OrderService.create_order(
            customer_id=customer_id,
            pharmacy_id=pharmacy_id,
            order_type='PICKUP',
            contact_phone='+1-555-1234',
            items_data=[{'medicine_id': med_rx_id, 'quantity': 1}],
            prescription_id=rx.id
        )
        assert err2 is None
        assert order2 is not None
        assert order2.status == Order.STATUS_PENDING

def test_order_state_machine_valid_pipeline(app, test_data):
    with app.app_context():
        customer_id = test_data['customer_id']
        pharmacy_id = test_data['pharmacy_id']
        med_otc_id = test_data['med_otc_id']
        pharmacy_owner_id = test_data['pharmacy_owner_id']

        inv_before = PharmacyInventory.query.filter_by(pharmacy_id=pharmacy_id, medicine_id=med_otc_id).first()
        initial_qty = inv_before.quantity

        order, _ = OrderService.create_order(
            customer_id=customer_id,
            pharmacy_id=pharmacy_id,
            order_type='PICKUP',
            contact_phone='+1-555-1234',
            items_data=[{'medicine_id': med_otc_id, 'quantity': 2}]
        )
        assert order.status == Order.STATUS_PENDING

        # PENDING -> ACCEPTED
        ok, _ = OrderService.transition_order_status(order.id, Order.STATUS_ACCEPTED, actor_user_id=pharmacy_owner_id)
        assert ok is True

        # ACCEPTED -> CONFIRMED
        ok, _ = OrderService.transition_order_status(order.id, Order.STATUS_CONFIRMED, actor_user_id=pharmacy_owner_id)
        assert ok is True

        # CONFIRMED -> PREPARING
        ok, _ = OrderService.transition_order_status(order.id, Order.STATUS_PREPARING, actor_user_id=pharmacy_owner_id)
        assert ok is True

        # PREPARING -> READY_FOR_PICKUP
        ok, _ = OrderService.transition_order_status(order.id, Order.STATUS_READY_FOR_PICKUP, actor_user_id=pharmacy_owner_id)
        assert ok is True

        # READY_FOR_PICKUP -> COMPLETED
        ok, _ = OrderService.transition_order_status(order.id, Order.STATUS_COMPLETED, actor_user_id=pharmacy_owner_id)
        assert ok is True
        assert order.status == Order.STATUS_COMPLETED

        # Stock deduction checked
        inv_after = PharmacyInventory.query.filter_by(pharmacy_id=pharmacy_id, medicine_id=med_otc_id).first()
        assert inv_after.quantity == initial_qty - 2

def test_order_invalid_state_transition_rejected(app, test_data):
    with app.app_context():
        customer_id = test_data['customer_id']
        pharmacy_id = test_data['pharmacy_id']
        med_otc_id = test_data['med_otc_id']
        pharmacy_owner_id = test_data['pharmacy_owner_id']

        order, _ = OrderService.create_order(
            customer_id=customer_id,
            pharmacy_id=pharmacy_id,
            order_type='PICKUP',
            contact_phone='+1-555-1234',
            items_data=[{'medicine_id': med_otc_id, 'quantity': 1}]
        )
        # Attempt illegal jump directly from PENDING to COMPLETED
        ok, msg = OrderService.transition_order_status(order.id, Order.STATUS_COMPLETED, actor_user_id=pharmacy_owner_id)
        assert ok is False
        assert 'Invalid status transition' in msg
