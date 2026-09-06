from typing import Optional, List, Tuple
from datetime import datetime
from app.extensions import db
from app.models.pharmacy import Pharmacy, VerificationDocument
from app.models.notification import Notification
from app.models.audit import AuditLog

class PharmacyService:
    @staticmethod
    def create_or_update_pharmacy(owner_id: int, data: dict, pharmacy_id: int = None) -> Tuple[Optional[Pharmacy], Optional[str]]:
        """
        Creates or updates a pharmacy profile.
        """
        if pharmacy_id:
            pharmacy = db.session.get(Pharmacy, pharmacy_id)
            if not pharmacy:
                return None, "Pharmacy not found."
        else:
            existing = Pharmacy.query.filter_by(owner_id=owner_id).first()
            if existing:
                pharmacy = existing
            else:
                pharmacy = Pharmacy(owner_id=owner_id)

        # Check unique license
        license_num = data.get('license_number', '').strip()
        if license_num:
            duplicate = Pharmacy.query.filter(Pharmacy.license_number == license_num, Pharmacy.id != (pharmacy.id or 0)).first()
            if duplicate:
                return None, f"License number '{license_num}' is already registered with another pharmacy."
            pharmacy.license_number = license_num

        pharmacy.name = data['name'].strip()
        pharmacy.phone = data['phone'].strip()
        pharmacy.email = data['email'].strip()
        pharmacy.address = data['address'].strip()
        pharmacy.city = data['city'].strip()
        pharmacy.state = data['state'].strip()
        pharmacy.pincode = data['pincode'].strip()
        pharmacy.latitude = float(data.get('latitude', 0.0) or 0.0)
        pharmacy.longitude = float(data.get('longitude', 0.0) or 0.0)
        pharmacy.supports_pickup = bool(data.get('supports_pickup', True))
        pharmacy.supports_delivery = bool(data.get('supports_delivery', False))
        pharmacy.delivery_fee = float(data.get('delivery_fee', 0.0) or 0.0)
        pharmacy.opening_hours = data.get('opening_hours', '9:00 AM - 9:00 PM')

        db.session.add(pharmacy)
        db.session.commit()
        return pharmacy, None

    @staticmethod
    def add_verification_document(pharmacy_id: int, doc_type: str, file_path: str, original_filename: str, mime_type: str, file_size: int) -> VerificationDocument:
        doc = VerificationDocument(
            pharmacy_id=pharmacy_id,
            document_type=doc_type,
            file_path=file_path,
            original_filename=original_filename,
            mime_type=mime_type,
            file_size=file_size
        )
        db.session.add(doc)
        
        # Set pharmacy status to PENDING if not already APPROVED
        pharmacy = db.session.get(Pharmacy, pharmacy_id)
        if pharmacy and pharmacy.verification_status != 'APPROVED':
            pharmacy.verification_status = 'PENDING'
            
        db.session.commit()
        return doc

    @staticmethod
    def review_verification(pharmacy_id: int, admin_user_id: int, decision: str, notes: str = None, ip_address: str = None) -> Tuple[bool, str]:
        """
        Admin action to approve or reject a pharmacy verification.
        Logs audit trail and notifies pharmacy owner.
        """
        pharmacy = db.session.get(Pharmacy, pharmacy_id)
        if not pharmacy:
            return False, "Pharmacy not found."

        if decision not in ('APPROVED', 'REJECTED'):
            return False, "Invalid verification decision."

        pharmacy.verification_status = decision
        pharmacy.verification_notes = notes
        pharmacy.verified_at = datetime.utcnow() if decision == 'APPROVED' else None

        # Audit log
        audit = AuditLog(
            actor_user_id=admin_user_id,
            action=f"PHARMACY_{decision}",
            target_type="Pharmacy",
            target_id=pharmacy.id,
            details=f"Admin {decision.lower()} pharmacy '{pharmacy.name}'. Notes: {notes or 'N/A'}",
            ip_address=ip_address
        )
        db.session.add(audit)

        # Notify Pharmacy Owner
        notif_msg = f"Your pharmacy verification for '{pharmacy.name}' has been {decision.lower()}."
        if notes:
            notif_msg += f" Note: {notes}"

        notif = Notification(
            user_id=pharmacy.owner_id,
            title=f"Verification {decision.capitalize()}",
            message=notif_msg,
            type="VERIFICATION",
            link_url="/pharmacy/verification"
        )
        db.session.add(notif)

        db.session.commit()
        return True, f"Pharmacy has been {decision.lower()} successfully."
