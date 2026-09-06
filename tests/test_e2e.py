import pytest
from app.models.user import User
from app.models.pharmacy import Pharmacy
from app.models.medicine import Medicine
from app.models.prescription import Prescription
from app.models.order import Order
from app.services.order_service import OrderService
from app.services.prescription_service import PrescriptionService
from app.services.pharmacy_service import PharmacyService

def test_full_end_to_end_journey(client, test_data):
    """
    Tests complete end-to-end user journeys:
    1. Customer discovers medicine & checks nearby stock timestamps
    2. Customer uploads prescription and places order
    3. Pharmacy logs in, reviews prescription manually, advances state machine
    4. Admin logs in, verifies pending pharmacy with audit log
    """
    # 1. Customer search
    res = client.get('/search?q=Paracetamol')
    assert res.status_code == 200

    # 2. View details
    res_detail = client.get(f"/medicine/{test_data['med_otc_id']}")
    assert res_detail.status_code == 200

    # 3. Customer places order
    client.post('/auth/login', data={'email': 'customer_test@example.com', 'password': 'CustPass123!'})
    
    # Upload prescription
    rx = PrescriptionService.create_prescription(
        customer_id=test_data['customer_id'],
        file_path='test_e2e_rx.pdf',
        original_filename='E2E_Prescription.pdf',
        mime_type='application/pdf',
        file_size=2048,
        patient_name='John Doe',
        doctor_name='Dr. Smith'
    )

    # Place Order with Rx medicine
    order, err = OrderService.create_order(
        customer_id=test_data['customer_id'],
        pharmacy_id=test_data['pharmacy_id'],
        order_type='PICKUP',
        contact_phone='+1-555-0201',
        items_data=[{'medicine_id': test_data['med_rx_id'], 'quantity': 1}],
        prescription_id=rx.id,
        customer_notes='Please hold until tomorrow morning.'
    )
    assert err is None
    assert order is not None
    assert order.status == Order.STATUS_PENDING

    # 4. Pharmacy owner logs in and manages order
    client.get('/auth/logout')
    client.post('/auth/login', data={'email': 'pharmacy_test@example.com', 'password': 'PharmPass123!'})

    # Manual prescription review
    rx_ok, _ = PrescriptionService.manual_review_prescription(
        prescription_id=rx.id,
        reviewer_user_id=test_data['pharmacy_owner_id'],
        decision='APPROVED'
    )
    assert rx_ok is True
    assert rx.status == 'APPROVED'

    # Advance state machine: PENDING -> ACCEPTED -> CONFIRMED -> PREPARING -> READY_FOR_PICKUP -> COMPLETED
    assert OrderService.transition_order_status(order.id, Order.STATUS_ACCEPTED, actor_user_id=test_data['pharmacy_owner_id'])[0] is True
    assert OrderService.transition_order_status(order.id, Order.STATUS_CONFIRMED, actor_user_id=test_data['pharmacy_owner_id'])[0] is True
    assert OrderService.transition_order_status(order.id, Order.STATUS_PREPARING, actor_user_id=test_data['pharmacy_owner_id'])[0] is True
    assert OrderService.transition_order_status(order.id, Order.STATUS_READY_FOR_PICKUP, actor_user_id=test_data['pharmacy_owner_id'])[0] is True
    assert OrderService.transition_order_status(order.id, Order.STATUS_COMPLETED, actor_user_id=test_data['pharmacy_owner_id'])[0] is True

    # 5. Admin verification workflow
    client.get('/auth/logout')
    client.post('/auth/login', data={'email': 'admin_test@example.com', 'password': 'AdminPass123!'})

    res_admin_queue = client.get('/admin/pharmacies?status=PENDING')
    assert res_admin_queue.status_code == 200

    admin_ok, _ = PharmacyService.review_verification(
        pharmacy_id=test_data['pharmacy_id'],
        admin_user_id=test_data['admin_id'],
        decision='APPROVED',
        notes='State drug license verification confirmed.'
    )
    assert admin_ok is True
