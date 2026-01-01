"""
Authentication service for JWT token management and user verification.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models import User, Allowlist

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for handling authentication operations."""

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """Verify JWT token and return email."""
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            email: str = payload.get("sub")
            if email is None:
                return None
            return email
        except JWTError:
            return None

    @staticmethod
    def is_user_allowed(db: Session, email: str) -> bool:
        """Check if user is in allowlist."""
        return db.query(Allowlist).filter(Allowlist.email == email).first() is not None

    @staticmethod
    def get_or_create_user(db: Session, email: str) -> Optional[User]:
        """Get existing user or create new one if in allowlist."""
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        if user:
            return user
        
        # Check if user is allowed
        allowlist_entry = db.query(Allowlist).filter(Allowlist.email == email).first()
        if not allowlist_entry:
            return None
        
        # Create new user
        user = User(email=email, is_admin=allowlist_entry.is_admin)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
