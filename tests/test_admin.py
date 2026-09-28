import pytest
from app.services.pharmacy_service import PharmacyService
from app.services.medicine_service import MedicineService
from app.models.pharmacy import Pharmacy
from app.models.audit import AuditLog

def test_pharmacy_admin_verification_workflow(app, test_data):
    with app.app_context():
        admin_id = test_data['admin_id']
        pharmacy_id = test_data['pharmacy_id']

        pharmacy = Pharmacy.query.get(pharmacy_id)
        # Set to pending
        pharmacy.verification_status = 'PENDING'
        assert pharmacy.is_verified is False

        # Admin reviews and approves
        success, msg = PharmacyService.review_verification(
            pharmacy_id=pharmacy_id,
            admin_user_id=admin_id,
            decision='APPROVED',
            notes='All licenses verified with Pharmacy Board'
        )
        assert success is True
        assert pharmacy.verification_status == 'APPROVED'
        assert pharmacy.is_verified is True
        assert pharmacy.verified_at is not None

        # Verify Audit Log entry
        audit = AuditLog.query.filter_by(target_id=pharmacy.id, action='PHARMACY_APPROVED').first()
        assert audit is not None
        assert audit.actor_user_id == admin_id

def test_medicine_catalog_crud(app, test_data):
    with app.app_context():
        med_data = {
            'name': 'Cetirizine 10mg Test',
            'generic_name': 'Cetirizine Dihydrochloride',
            'brand_name': 'Zyrtec Test',
            'strength': '10mg',
            'dosage_form': 'Tablet',
            'requires_prescription': False,
            'description': 'Allergy medicine'
        }
        med = MedicineService.create_or_update_medicine(med_data)
        assert med.id is not None
        assert med.name == 'Cetirizine 10mg Test'

        # Update
        med_data['strength'] = '20mg'
        updated_med = MedicineService.create_or_update_medicine(med_data, medicine_id=med.id)
        assert updated_med.strength == '20mg'
