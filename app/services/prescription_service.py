from typing import Optional, Tuple, List
from datetime import datetime
from app.extensions import db
from app.models.prescription import Prescription
from app.models.notification import Notification
from app.models.audit import AuditLog
from app.models.user import User

class PrescriptionService:
    @staticmethod
    def create_prescription(
        customer_id: int,
        file_path: str,
        original_filename: str,
        mime_type: str,
        file_size: int,
        patient_name: str = None,
        doctor_name: str = None,
        notes: str = None
    ) -> Prescription:
        prescription = Prescription(
            customer_id=customer_id,
            file_path=file_path,
            original_filename=original_filename,
            mime_type=mime_type,
            file_size=file_size,
            status='PENDING_REVIEW',
            patient_name=patient_name,
            doctor_name=doctor_name,
            notes=notes
        )
        db.session.add(prescription)
        db.session.commit()
        return prescription

    @staticmethod
    def get_prescriptions_for_customer(customer_id: int) -> List[Prescription]:
        return Prescription.query.filter_by(customer_id=customer_id).order_by(Prescription.created_at.desc()).all()

    @staticmethod
    def get_prescription_by_id(prescription_id: int) -> Optional[Prescription]:
        return db.session.get(Prescription, prescription_id)

    @staticmethod
    def can_access_prescription(prescription: Prescription, user: User) -> bool:
        """
        Ensures strict access control:
        1. Customer who uploaded it
        2. Admin
        3. Pharmacy owner if associated with an order/request belonging to that pharmacy
        """
        if not user or not user.is_authenticated:
            return False

        if user.is_admin:
            return True

        if prescription.customer_id == user.id:
            return True

        if user.is_pharmacy and user.pharmacy:
            # Check if any order or request for this pharmacy is linked to this prescription
            has_order = prescription.orders.filter_by(pharmacy_id=user.pharmacy.id).first() is not None
            has_req = prescription.medicine_requests.filter_by(pharmacy_id=user.pharmacy.id).first() is not None
            if has_order or has_req:
                return True

        return False

    @staticmethod
    def manual_review_prescription(
        prescription_id: int,
        reviewer_user_id: int,
        decision: str, # 'APPROVED' or 'REJECTED'
        rejection_reason: str = None,
        ip_address: str = None
    ) -> Tuple[bool, str]:
        """
        Strictly manual prescription verification by authorized pharmacy staff/admin.
        Automated AI approval is prohibited.
        """
        prescription = db.session.get(Prescription, prescription_id)
        if not prescription:
            return False, "Prescription not found."

        if decision not in ('APPROVED', 'REJECTED'):
            return False, "Invalid review status."

        prescription.status = decision
        prescription.reviewed_by_user_id = reviewer_user_id
        prescription.reviewed_at = datetime.utcnow()
        if decision == 'REJECTED':
            prescription.rejection_reason = rejection_reason or "Prescription does not meet safety/legibility guidelines."
        else:
            prescription.rejection_reason = None

        # Notification to customer
        reviewer = db.session.get(User, reviewer_user_id)
        reviewer_name = reviewer.full_name if reviewer else "Pharmacy Staff"
        
        if decision == 'APPROVED':
            notif_msg = f"Your prescription #{prescription.id} has been manually reviewed and approved by {reviewer_name}."
        else:
            notif_msg = f"Your prescription #{prescription.id} was rejected. Reason: {prescription.rejection_reason}"

        notif = Notification(
            user_id=prescription.customer_id,
            title=f"Prescription {decision.capitalize()}",
            message=notif_msg,
            type="PRESCRIPTION",
            link_url="/prescriptions"
        )
        db.session.add(notif)

        # Audit log
        audit = AuditLog(
            actor_user_id=reviewer_user_id,
            action=f"PRESCRIPTION_{decision}",
            target_type="Prescription",
            target_id=prescription.id,
            details=f"Manual review: {decision}. Reason/Notes: {rejection_reason or 'N/A'}",
            ip_address=ip_address
        )
        db.session.add(audit)

        db.session.commit()
        return True, f"Prescription marked as {decision}."
