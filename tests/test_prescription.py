import io
import pytest
from app.utils.security import validate_file_upload
from app.services.prescription_service import PrescriptionService
from app.models.prescription import Prescription
from werkzeug.datastructures import FileStorage

def test_file_upload_security_validation(app):
    with app.app_context():
        # Valid PDF
        pdf_stream = io.BytesIO(b'%PDF-1.4 valid dummy pdf header content')
        pdf_file = FileStorage(stream=pdf_stream, filename='my_rx.pdf', content_type='application/pdf')
        is_valid, err, ext = validate_file_upload(pdf_file)
        assert is_valid is True
        assert ext == 'pdf'

        # Invalid executable extension
        exe_stream = io.BytesIO(b'malicious script binary')
        exe_file = FileStorage(stream=exe_stream, filename='hack.exe', content_type='application/octet-stream')
        is_valid, err, ext = validate_file_upload(exe_file)
        assert is_valid is False
        assert 'unsupported file type' in err.lower()

        # Fake PDF header spoofing
        fake_pdf = io.BytesIO(b'NOT A REAL PDF HEADER')
        fake_file = FileStorage(stream=fake_pdf, filename='fake.pdf', content_type='application/pdf')
        is_valid, err, ext = validate_file_upload(fake_file)
        assert is_valid is False
        assert 'not a valid pdf' in err.lower()

def test_prescription_manual_review_lifecycle(app, test_data):
    with app.app_context():
        customer_id = test_data['customer_id']
        pharmacy_owner_id = test_data['pharmacy_owner_id']

        rx = PrescriptionService.create_prescription(
            customer_id=customer_id,
            file_path='test_rx_file.pdf',
            original_filename='Prescription_Test.pdf',
            mime_type='application/pdf',
            file_size=1024,
            patient_name='John Doe',
            doctor_name='Dr. Smith'
        )
        assert rx.status == 'PENDING_REVIEW'

        # Manual Approval by Pharmacist
        success, msg = PrescriptionService.manual_review_prescription(
            prescription_id=rx.id,
            reviewer_user_id=pharmacy_owner_id,
            decision='APPROVED'
        )
        assert success is True
        assert rx.status == 'APPROVED'
        assert rx.reviewed_by_user_id == pharmacy_owner_id
        assert rx.reviewed_at is not None

        # Rejection with reason
        success2, msg2 = PrescriptionService.manual_review_prescription(
            prescription_id=rx.id,
            reviewer_user_id=pharmacy_owner_id,
            decision='REJECTED',
            rejection_reason='Prescription date expired'
        )
        assert success2 is True
        assert rx.status == 'REJECTED'
        assert rx.rejection_reason == 'Prescription date expired'
