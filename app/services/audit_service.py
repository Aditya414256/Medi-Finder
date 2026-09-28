from typing import List
from app.extensions import db
from app.models.audit import AuditLog

class AuditService:
    @staticmethod
    def log(actor_user_id: int, action: str, target_type: str, target_id: int = None, details: str = None, ip_address: str = None) -> AuditLog:
        entry = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
            ip_address=ip_address
        )
        db.session.add(entry)
        db.session.commit()
        return entry

    @staticmethod
    def get_recent_logs(limit: int = 100) -> List[AuditLog]:
        return AuditLog.query.order_by(AuditLog.created_at.desc()).limit(limit).all()
