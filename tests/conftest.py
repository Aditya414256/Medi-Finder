import os
import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.pharmacy import Pharmacy
from app.models.medicine import Medicine, MedicineCategory
from app.models.inventory import PharmacyInventory

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_data(app):
    with app.app_context():
        admin = User(email='admin_test@example.com', full_name='Admin User', role='admin')
        admin.set_password('AdminPass123!')
        
        pharmacy_owner = User(email='pharmacy_test@example.com', full_name='Pharmacy Owner', role='pharmacy')
        pharmacy_owner.set_password('PharmPass123!')
        
        customer = User(email='customer_test@example.com', full_name='Customer User', role='customer')
        customer.set_password('CustPass123!')

        db.session.add_all([admin, pharmacy_owner, customer])
        db.session.commit()

        # Create test pharmacy for pharmacy owner
        pharmacy = Pharmacy(
            owner_id=pharmacy_owner.id,
            name='Test Apex Pharmacy',
            license_number='DL-TEST-999',
            phone='+1-555-9999',
            email='test@apexpharm.example.com',
            address='100 Test St',
            city='Test City',
            state='Test State',
            pincode='100001',
            latitude=28.6139,
            longitude=77.2090,
            verification_status='APPROVED',
            supports_pickup=True,
            supports_delivery=True,
            delivery_fee=2.00
        )
        db.session.add(pharmacy)

        # Create category & test medicine
        cat = MedicineCategory(name='General Pain', slug='general-pain')
        db.session.add(cat)
        db.session.flush()

        med_otc = Medicine(
            category_id=cat.id,
            name='Paracetamol 500mg Test',
            generic_name='Acetaminophen',
            brand_name='Crocin Test',
            strength='500mg',
            dosage_form='Tablet',
            requires_prescription=False,
            description='Test fever medicine'
        )

        med_rx = Medicine(
            category_id=cat.id,
            name='Amoxicillin 500mg Test',
            generic_name='Amoxicillin',
            brand_name='Novamox Test',
            strength='500mg',
            dosage_form='Capsule',
            requires_prescription=True,
            description='Test antibiotic'
        )

        db.session.add_all([med_otc, med_rx])
        db.session.commit()

        # Add inventory
        inv1 = PharmacyInventory(
            pharmacy_id=pharmacy.id,
            medicine_id=med_otc.id,
            quantity=50,
            price=3.00,
            stock_status='AVAILABLE'
        )
        inv2 = PharmacyInventory(
            pharmacy_id=pharmacy.id,
            medicine_id=med_rx.id,
            quantity=5,
            price=8.50,
            stock_status='LOW_STOCK'
        )
        db.session.add_all([inv1, inv2])
        db.session.commit()

        return {
            'admin_id': admin.id,
            'pharmacy_owner_id': pharmacy_owner.id,
            'customer_id': customer.id,
            'pharmacy_id': pharmacy.id,
            'med_otc_id': med_otc.id,
            'med_rx_id': med_rx.id,
            'category_id': cat.id
        }

@pytest.fixture
def auth_client_customer(client, test_data):
    client.post('/auth/login', data={'email': 'customer_test@example.com', 'password': 'CustPass123!'})
    return client

@pytest.fixture
def auth_client_pharmacy(client, test_data):
    client.post('/auth/login', data={'email': 'pharmacy_test@example.com', 'password': 'PharmPass123!'})
    return client

@pytest.fixture
def auth_client_admin(client, test_data):
    client.post('/auth/login', data={'email': 'admin_test@example.com', 'password': 'AdminPass123!'})
    return client
