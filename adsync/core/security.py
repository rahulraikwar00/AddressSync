# core/security.py
import hashlib
import secrets
from jose import jwt
from datetime import datetime, timedelta
from .config import settings


def get_password_hash(password: str) -> str:
    """Simple password hashing using SHA-256"""
    # Add a salt to make it slightly more secure
    salt = "address_sync_salt_2024"
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return get_password_hash(plain_password) == hashed_password


def create_token(data: dict):
    """Create JWT token"""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
