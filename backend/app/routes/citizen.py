import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import (
    create_otp_challenge,
    create_token,
    get_current_citizen,
    hash_value,
    mask_aadhaar,
    verify_otp,
)
from ..config import settings
from ..db import get_db
from ..events import enqueue
from ..models import AddressRecord, Agency, AuditLog, Citizen, Consent, utcnow
from ..schemas import AddressUpdate, ConsentGrant, OtpRequest, OtpVerify

router = APIRouter(prefix="/citizen", tags=["citizen"])
logger = logging.getLogger("addresssync.citizen")


def _current_address(db: Session, citizen_id: str) -> AddressRecord | None:
    return (
        db.query(AddressRecord)
        .filter(
            AddressRecord.citizen_id == citizen_id,
            AddressRecord.superseded_at.is_(None),
        )
        .first()
    )


def _consent_dict(c: Consent) -> dict:
    return {
        "id": c.id,
        "agency_id": c.agency_id,
        "purpose": c.purpose,
        "status": c.status,
        "remark": c.remark,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "confirmed_at": c.confirmed_at.isoformat() if c.confirmed_at else None,
        "handled_at": c.handled_at.isoformat() if c.handled_at else None,
        "handle_id": c.handle_id,
    }


@router.post("/otp/request")
def request_otp(data: OtpRequest, db: Session = Depends(get_db)):
    """Mock UIDAI: issues an OTP for the Aadhaar number."""
    otp = create_otp_challenge(db, data.aadhaar_number)
    db.add(
        AuditLog(
            actor_type="system",
            actor_id=mask_aadhaar(data.aadhaar_number),
            action="otp.requested",
        )
    )
    db.commit()
    resp = {"expires_in_seconds": 300}
    if settings.dev_mode:
        # in production this arrives by SMS from UIDAI; dev mode returns it directly
        resp["otp"] = otp
        resp["note"] = "dev_mode: OTP returned in response instead of SMS"
    return resp


@router.post("/otp/verify")
def verify_otp_and_login(data: OtpVerify, db: Session = Depends(get_db)):
    verify_otp(db, data.aadhaar_number, data.otp)

    aadhaar_hash = hash_value(data.aadhaar_number)
    citizen = db.query(Citizen).filter(
        Citizen.aadhaar_hash == aadhaar_hash).first()
    if not citizen:
        # first login: auto-provision from the (mock) eKYC response
        citizen = Citizen(
            aadhaar_ref=mask_aadhaar(data.aadhaar_number),
            aadhaar_hash=aadhaar_hash,
            name=f"Citizen {data.aadhaar_number[-4:]}",
            dob="1990-01-01",
            phone="+91-90000-00000",
        )
        db.add(citizen)
        db.commit()
        db.refresh(citizen)
        logger.info("provisioned new citizen %s", citizen.aadhaar_ref)

    db.add(AuditLog(actor_type="citizen",
           actor_id=citizen.id, action="login.otp_success"))
    db.commit()
    return {
        "access_token": create_token(citizen.id, "citizen"),
        "token_type": "bearer",
        "citizen": {
            "id": citizen.id,
            "aadhaar_ref": citizen.aadhaar_ref,
            "name": citizen.name,
            "dob": citizen.dob,
            "phone": citizen.phone,
        },
    }


@router.get("/me")
def me(current: Citizen = Depends(get_current_citizen), db: Session = Depends(get_db)):
    current_addr = _current_address(db, current.id)
    consents = (
        db.query(Consent).filter(Consent.citizen_id == current.id).all()
    )
    return {
        "id": current.id,
        "aadhaar_ref": current.aadhaar_ref,
        "name": current.name,
        "dob": current.dob,
        "phone": current.phone,
        "address": ({**current_addr.as_dict(), "version": current_addr.version} if current_addr else None),
        "consents": [_consent_dict(c) for c in consents],
    }


@router.put("/address")
def update_address(
    data: AddressUpdate,
    current: Citizen = Depends(get_current_citizen),
    db: Session = Depends(get_db),
):
    """Citizen updates their address once; consented agencies are notified via outbox."""
    old = _current_address(db, current.id)
    now = utcnow()
    version = (old.version + 1) if old else 1

    record = AddressRecord(
        citizen_id=current.id,
        version=version,
        line1=data.line1,
        line2=data.line2,
        city=data.city,
        state=data.state,
        pincode=data.pincode,
    )
    if old:
        old.superseded_at = now
    db.add(record)
    db.flush()

    address_payload = {**record.as_dict(), "version": version}

    active_consents = (
        db.query(Consent)
        .filter(Consent.citizen_id == current.id, Consent.status == "confirmed")
        .all()
    )
    for consent in active_consents:
        enqueue(
            db,
            type_="address.updated",
            agency_id=consent.agency_id,
            citizen_id=current.id,
            payload={
                "consent_id": consent.id,
                "citizen_ref": current.aadhaar_ref,
                "address": address_payload,
                "reason": "citizen_update",
            },
        )

    db.add(
        AuditLog(
            actor_type="citizen",
            actor_id=current.id,
            action="address.updated",
            detail={"version": version,
                    "notified_agencies": len(active_consents)},
        )
    )
    db.commit()
    return {
        "address": address_payload,
        "agencies_notified": [c.agency_id for c in active_consents],
    }


@router.get("/consents")
def list_consents(
    current: Citizen = Depends(get_current_citizen), db: Session = Depends(get_db)
):
    consents = db.query(Consent).filter(Consent.citizen_id == current.id).all()
    return [_consent_dict(c) for c in consents]


@router.post("/consents", status_code=201)
def request_consent(
    data: ConsentGrant,
    current: Citizen = Depends(get_current_citizen),
    db: Session = Depends(get_db),
):
    agency = db.get(Agency, data.agency_id)
    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")

    consent = (
        db.query(Consent)
        .filter(Consent.citizen_id == current.id, Consent.agency_id == agency.id)
        .first()
    )
    rerequest = False
    if consent:
        if consent.status == "pending":
            raise HTTPException(
                status_code=409, detail="Consent request already pending")
        if consent.status == "confirmed":
            raise HTTPException(
                status_code=409, detail="Consent already confirmed")
        consent.status = "pending"
        consent.purpose = data.purpose
        consent.remark = None
        consent.confirmed_at = None
        consent.handled_at = None
        consent.handle_id = None
        rerequest = True
    else:
        consent = Consent(
            citizen_id=current.id, agency_id=agency.id, purpose=data.purpose
        )
        db.add(consent)
        rerequest = False

    db.flush()

    db.add(
        AuditLog(
            actor_type="citizen",
            actor_id=current.id,
            action="consent.requested" if not rerequest else "consent.re_requested",
            detail={"agency_id": agency.id, "consent_id": consent.id},
        )
    )
    db.commit()
    return {
        "consent_id": consent.id,
        "agency_id": agency.id,
        "status": consent.status,
        "purpose": consent.purpose,
    }


@router.delete("/consents/{agency_id}")
def cancel_consent(
    agency_id: str,
    current: Citizen = Depends(get_current_citizen),
    db: Session = Depends(get_db),
):
    """Cancel a consent request. Only possible while it is still pending:
    once the agency has acted (confirmed/rejected) the record is final."""
    consent = (
        db.query(Consent)
        .filter(Consent.citizen_id == current.id, Consent.agency_id == agency_id)
        .first()
    )
    if not consent or consent.status == "rejected":
        raise HTTPException(
            status_code=404, detail="No active consent for this agency")
    if consent.status == "confirmed":
        raise HTTPException(
            status_code=409,
            detail="Consent already confirmed by agency; it can no longer be cancelled",
        )

    consent.status = "rejected"
    consent.remark = "Cancelled by citizen"
    consent.handled_at = utcnow()

    db.add(
        AuditLog(
            actor_type="citizen",
            actor_id=current.id,
            action="consent.cancelled",
            detail={"agency_id": agency_id, "consent_id": consent.id},
        )
    )
    db.commit()
    return {"consent_id": consent.id, "agency_id": agency_id, "status": "rejected"}
