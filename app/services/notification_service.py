from typing import List
from app.extensions import db
from app.models.notification import Notification

class NotificationService:
    @staticmethod
    def get_user_notifications(user_id: int, limit: int = 50) -> List[Notification]:
        return Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()

    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> bool:
        notif = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notif:
            notif.is_read = True
            db.session.commit()
            return True
        return False

    @staticmethod
    def mark_all_as_read(user_id: int) -> int:
        count = Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
        return count
