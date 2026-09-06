from typing import Optional, Tuple
import re
from app.extensions import db
from app.models.user import User

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

class AuthService:
    @staticmethod
    def register_user(email: str, password: str, full_name: str, phone: str = None, role: str = 'customer') -> Tuple[Optional[User], Optional[str]]:
        """
        Validates user input and creates a new user account.
        """
        email = (email or '').strip().lower()
        full_name = (full_name or '').strip()
        phone = (phone or '').strip()

        if not email or not re.match(EMAIL_REGEX, email):
            return None, "Please provide a valid email address."

        if not password or len(password) < 6:
            return None, "Password must be at least 6 characters long."

        if not full_name:
            return None, "Full name is required."

        if role not in ('customer', 'pharmacy', 'admin'):
            role = 'customer'

        if User.query.filter_by(email=email).first():
            return None, "An account with this email address already exists."

        user = User(
            email=email,
            full_name=full_name,
            phone=phone,
            role=role,
            is_active=True
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        return user, None

    @staticmethod
    def authenticate(email: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        """
        Authenticates a user by email and password.
        """
        email = (email or '').strip().lower()
        if not email or not password:
            return None, "Email and password are required."

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return None, "Invalid email or password."

        if not user.is_active:
            return None, "Your account has been deactivated. Please contact support."

        return user, None
