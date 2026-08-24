import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .db import Base


def uid() -> str:
    return uuid.uuid4().hex


def utcnow() -> datetime:
    return datetime.utcnow()


class Citizen(Base):
    __tablename__ = "citizens"

    id = Column(String, primary_key=True, default=uid)
    # raw Aadhaar is never stored: masked display ref + hash for login lookup only
    aadhaar_ref = Column(String, nullable=False, unique=True, index=True)
    aadhaar_hash = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    dob = Column(String)
    phone = Column(String)
    created_at = Column(DateTime, default=utcnow)

    addresses = relationship(
        "AddressRecord", back_populates="citizen", order_by="AddressRecord.version"
    )
    consents = relationship("Consent", back_populates="citizen")


class OtpChallenge(Base):
    __tablename__ = "otp_challenges"

    id = Column(String, primary_key=True, default=uid)
    aadhaar_hash = Column(String, index=True, nullable=False)
    otp_hash = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    consumed = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)


class AddressRecord(Base):
    """Immutable address version. Current address = row where superseded_at IS NULL."""

    __tablename__ = "addresses"

    id = Column(String, primary_key=True, default=uid)
    citizen_id = Column(String, ForeignKey("citizens.id"),
                        index=True, nullable=False)
    version = Column(Integer, nullable=False)
    line1 = Column(String, nullable=False)
    line2 = Column(String)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    pincode = Column(String, nullable=False)
    created_at = Column(DateTime, default=utcnow)
    superseded_at = Column(DateTime)

    citizen = relationship("Citizen", back_populates="addresses")

    def as_dict(self) -> dict:
        return {
            "line1": self.line1,
            "line2": self.line2,
            "city": self.city,
            "state": self.state,
            "pincode": self.pincode,
        }


class Agency(Base):
    __tablename__ = "agencies"

    id = Column(String, primary_key=True)  # slug, e.g. "bangalore-mc"
    name = Column(String, nullable=False)
    api_key_hash = Column(String, nullable=False, unique=True, index=True)
    # prototype: plain; encrypt in prod
    webhook_secret = Column(String, nullable=False)
    webhook_url = Column(String)
    created_at = Column(DateTime, default=utcnow)

    consents = relationship("Consent", back_populates="agency")


class Consent(Base):
    __tablename__ = "consents"
    __table_args__ = (UniqueConstraint(
        "citizen_id", "agency_id", name="uq_citizen_agency"),)
    # pending|confirmed|rejected
    status = Column(String, nullable=False, default="pending")
    remark = Column(String)
    id = Column(String, primary_key=True, default=uid)
    citizen_id = Column(String, ForeignKey("citizens.id"),
                        index=True, nullable=False)
    agency_id = Column(String, ForeignKey("agencies.id"),
                       index=True, nullable=False)
    purpose = Column(String, nullable=False, default="address verification")
    created_at = Column(DateTime, default=utcnow)
    confirmed_at = Column(DateTime)
    # stamped on the agency's first pull; acting requires a prior review
    reviewed_at = Column(DateTime)
    # stamped when the agency acts; citizen cancellations never get one
    handled_at = Column(DateTime)
    # reference UUID issued at the moment the agency takes its action
    handle_id = Column(String, index=True)

    citizen = relationship("Citizen", back_populates="consents")
    agency = relationship("Agency", back_populates="consents")


class Event(Base):
    """Transactional outbox: one row per notification an agency must receive."""

    __tablename__ = "events"

    id = Column(String, primary_key=True, default=uid)
    # address.updated (only type enqueued today; confirm/reject/cancel are audit-only)
    type = Column(String, nullable=False)
    citizen_id = Column(String, index=True)
    agency_id = Column(String, index=True, nullable=False)
    payload = Column(JSON, nullable=False)
    # pending | delivered | failed
    status = Column(String, nullable=False, default="pending")
    attempts = Column(Integer, default=0)
    next_attempt_at = Column(DateTime, default=utcnow)
    last_error = Column(Text)
    created_at = Column(DateTime, default=utcnow)
    delivered_at = Column(DateTime)


class WebhookReceipt(Base):
    """What the built-in fake agency receiver got (demo visibility)."""

    __tablename__ = "webhook_receipts"

    id = Column(String, primary_key=True, default=uid)
    agency_id = Column(String, index=True)
    event_id = Column(String, index=True)
    signature_valid = Column(Boolean, default=False)
    body = Column(JSON)
    received_at = Column(DateTime, default=utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=uid)
    ts = Column(DateTime, default=utcnow, index=True)
    actor_type = Column(String)  # citizen | agency | system
    actor_id = Column(String)
    action = Column(String)
    detail = Column(JSON)
