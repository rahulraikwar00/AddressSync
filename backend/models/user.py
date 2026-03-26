# models/user.py
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from core.database import Base


class User(Base):
    __tablename__ = "users"

    aadhaar_number = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    phone_number = Column(String, nullable=True)
    password_hash = Column(String)
    current_address = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
