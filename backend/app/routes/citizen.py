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
    citizen = db.query(Citizen).filter(Citizen.aadhaar_hash == aadhaar_hash).first()
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

    db.add(AuditLog(actor_type="citizen", actor_id=citizen.id, action="login.otp_success"))
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
        "consents": [
            {
                "id": c.id,
                "agency_id": c.agency_id,
                "purpose": c.purpose,
                "status": c.status,
                "granted_at": c.granted_at.isoformat() if c.granted_at else None,
                "revoked_at": c.revoked_at.isoformat() if c.revoked_at else None,
            }
            for c in consents
        ],
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
        .filter(Consent.citizen_id == current.id, Consent.status == "granted")
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
            detail={"version": version, "notified_agencies": len(active_consents)},
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
    return [
        {
            "id": c.id,
            "agency_id": c.agency_id,
            "purpose": c.purpose,
            "status": c.status,
            "granted_at": c.granted_at.isoformat() if c.granted_at else None,
            "revoked_at": c.revoked_at.isoformat() if c.revoked_at else None,
        }
        for c in consents
    ]


@router.post("/consents", status_code=201)
def grant_consent(
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
    regrant = False
    if consent:
        if consent.status == "granted":
            raise HTTPException(status_code=409, detail="Consent already granted")
        consent.status = "granted"
        consent.purpose = data.purpose
        consent.granted_at = utcnow()
        consent.revoked_at = None
        regrant = True
    else:
        consent = Consent(
            citizen_id=current.id, agency_id=agency.id, purpose=data.purpose
        )
        db.add(consent)

    db.flush()

    # push the current address immediately so the agency is in sync from day one
    current_addr = _current_address(db, current.id)
    if current_addr:
        enqueue(
            db,
            type_="address.updated",
            agency_id=agency.id,
            citizen_id=current.id,
            payload={
                "consent_id": consent.id,
                "citizen_ref": current.aadhaar_ref,
                "address": {**current_addr.as_dict(), "version": current_addr.version},
                "reason": "consent_granted",
            },
        )

    db.add(
        AuditLog(
            actor_type="citizen",
            actor_id=current.id,
            action="consent.granted" if not regrant else "consent.re_granted",
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
def revoke_consent(
    agency_id: str,
    current: Citizen = Depends(get_current_citizen),
    db: Session = Depends(get_db),
):
    consent = (
        db.query(Consent)
        .filter(Consent.citizen_id == current.id, Consent.agency_id == agency_id)
        .first()
    )
    if not consent or consent.status != "granted":
        raise HTTPException(status_code=404, detail="No active consent for this agency")

    consent.status = "revoked"
    consent.revoked_at = utcnow()

    # NOTE: revocation event deliberately carries no address data
    enqueue(
        db,
        type_="consent.revoked",
        agency_id=agency_id,
        citizen_id=current.id,
        payload={"consent_id": consent.id, "citizen_ref": current.aadhaar_ref},
    )
    db.add(
        AuditLog(
            actor_type="citizen",
            actor_id=current.id,
            action="consent.revoked",
            detail={"agency_id": agency_id, "consent_id": consent.id},
        )
    )
    db.commit()
    return {"consent_id": consent.id, "agency_id": agency_id, "status": "revoked"}
