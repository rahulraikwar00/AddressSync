# models/request.py
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from core.database import Base
import uuid


class AddressRequest(Base):
    __tablename__ = "address_requests"

    id = Column(String, primary_key=True,
                default=lambda: str(uuid.uuid4())[:8])
    user_aadhaar = Column(String, ForeignKey("users.aadhaar_number"))
    agency_id = Column(String, ForeignKey("agencies.id"))
    new_address = Column(String)
    # pending, approved, rejected, cancelled
    status = Column(String, default="pending")
    reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
