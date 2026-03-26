# models/agency.py
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from core.database import Base


class Agency(Base):
    __tablename__ = "agencies"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
