import logging
import uuid

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import (
    generate_api_key,
    generate_webhook_secret,
    get_current_agency,
    hash_value,
)
from ..db import get_db
from ..models import AddressRecord, Agency, AuditLog, Consent, utcnow
from ..schemas import AgencyLogin, AgencyRegister, WebhookConfig

router = APIRouter(tags=["agency"])
logger = logging.getLogger("addresssync.agency")


@router.post("/agencies/register", status_code=201)
def register_agency(data: AgencyRegister, db: Session = Depends(get_db)):
    if db.get(Agency, data.slug):
        raise HTTPException(status_code=409, detail="Agency slug already exists")

    api_key, api_key_hash = generate_api_key()
    agency = Agency(
        id=data.slug,
        name=data.name,
        api_key_hash=api_key_hash,
        webhook_secret=generate_webhook_secret(),
        webhook_url=data.webhook_url,
    )
    db.add(agency)
    db.add(
        AuditLog(
            actor_type="system",
            actor_id=agency.id,
            action="agency.registered",
            detail={"name": agency.name},
        )
    )
    db.commit()
    # credentials are shown exactly once
    return {
        "agency_id": agency.id,
        "name": agency.name,
        "api_key": api_key,
        "webhook_url": agency.webhook_url,
        "note": "store the api_key now; it cannot be retrieved again",
    }


@router.post("/agencies/login")
def login_agency(data: AgencyLogin, db: Session = Depends(get_db)):
    from ..auth import create_token

    agency = (
        db.query(Agency).filter(Agency.api_key_hash == hash_value(data.api_key)).first()
    )
    if not agency:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {
        "access_token": create_token(agency.id, "agency"),
        "token_type": "bearer",
        "agency": {"id": agency.id, "name": agency.name},
    }


@router.get("/agency/me")
def agency_me(agency: Agency = Depends(get_current_agency)):
    return {
        "id": agency.id,
        "name": agency.name,
        "webhook_url": agency.webhook_url,
    }


@router.put("/agency/webhook")
def set_webhook(
    data: WebhookConfig,
    agency: Agency = Depends(get_current_agency),
    db: Session = Depends(get_db),
):
    agency.webhook_url = data.webhook_url
    db.add(
        AuditLog(
            actor_type="agency",
            actor_id=agency.id,
            action="webhook.configured",
            detail={"webhook_url": data.webhook_url},
        )
    )
    db.commit()
    return {"agency_id": agency.id, "webhook_url": agency.webhook_url}


@router.get("/agency/addresses/{consent_id}")
def pull_address(
    consent_id: str,
    agency: Agency = Depends(get_current_agency),
    db: Session = Depends(get_db),
):
    """Pull the citizen's current address. Allowed for pending consents too —
    reviewing before confirm/reject is required."""
    consent = db.get(Consent, consent_id)
    if not consent or consent.agency_id != agency.id:
        raise HTTPException(status_code=404, detail="Consent not found")
    if consent.status == "rejected":
        raise HTTPException(
            status_code=403, detail="Consent was rejected or cancelled")

    first_review = consent.reviewed_at is None and consent.status == "pending"
    if first_review:
        consent.reviewed_at = utcnow()

    record = (
        db.query(AddressRecord)
        .filter(
            AddressRecord.citizen_id == consent.citizen_id,
            AddressRecord.superseded_at.is_(None),
        )
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Citizen has no address on file")

    db.add(
        AuditLog(
            actor_type="agency",
            actor_id=agency.id,
            action="address.pulled",
            detail={
                "consent_id": consent_id,
                "version": record.version,
                **({"review": True} if first_review else {}),
            },
        )
    )
    db.commit()

    return {
        "consent_id": consent.id,
        "consent_status": consent.status,
        "purpose": consent.purpose,
        "citizen_ref": consent.citizen.aadhaar_ref,
        "citizen_name": consent.citizen.name,
        "address": {**record.as_dict(), "version": record.version},
        "pulled_at": utcnow().isoformat() + "Z",
    }


@router.get("/agency/consents/handled")
def handled_consents(
    agency: Agency = Depends(get_current_agency),
    db: Session = Depends(get_db),
):
    """Record of every consent this agency has acted on, with the handle id
    issued at action time."""
    rows = (
        db.query(Consent)
        .filter(Consent.agency_id == agency.id, Consent.handle_id.isnot(None))
        .order_by(Consent.handled_at.desc())
        .all()
    )
    return [
        {
            "consent_id": c.id,
            "handle_id": c.handle_id,
            "citizen_name": c.citizen.name,
            "citizen_ref": c.citizen.aadhaar_ref,
            "purpose": c.purpose,
            "status": c.status,
            "remark": c.remark,
            "handled_at": c.handled_at.isoformat() if c.handled_at else None,
        }
        for c in rows
    ]


@router.post("/agency/consents/{consent_id}/confirm")
def confirm_consent(
    consent_id: str,
    body: dict = Body(default={}),
    agency: Agency = Depends(get_current_agency),
    db: Session = Depends(get_db),
):
    consent = db.get(Consent, consent_id)
    if not consent or consent.agency_id != agency.id:
        raise HTTPException(status_code=404, detail="Consent not found")
    if consent.status != "pending":
        raise HTTPException(status_code=400, detail="Consent is not pending")
    if consent.reviewed_at is None:
        raise HTTPException(
            status_code=400,
            detail="Pull the address first — review is required before confirming",
        )

    consent.status = "confirmed"
    consent.confirmed_at = utcnow()
    consent.handled_at = utcnow()
    consent.handle_id = str(uuid.uuid4())
    consent.remark = body.get("remark")

    db.add(
        AuditLog(
            actor_type="agency",
            actor_id=agency.id,
            action="consent.confirmed",
            detail={"consent_id": consent_id, "handle_id": consent.handle_id},
        )
    )
    db.commit()
    return {
        "consent_id": consent.id,
        "status": "confirmed",
        "handle_id": consent.handle_id,
    }


@router.post("/agency/consents/{consent_id}/reject")
def reject_consent(
    consent_id: str,
    body: dict = Body(default={}),
    agency: Agency = Depends(get_current_agency),
    db: Session = Depends(get_db),
):
    consent = db.get(Consent, consent_id)
    if not consent or consent.agency_id != agency.id:
        raise HTTPException(status_code=404, detail="Consent not found")
    if consent.status != "pending":
        raise HTTPException(status_code=400, detail="Consent is not pending")
    if consent.reviewed_at is None:
        raise HTTPException(
            status_code=400,
            detail="Pull the address first — review is required before rejecting",
        )

    consent.status = "rejected"
    consent.handled_at = utcnow()
    consent.handle_id = str(uuid.uuid4())
    consent.remark = body.get("remark", "Rejected by agency")

    db.add(
        AuditLog(
            actor_type="agency",
            actor_id=agency.id,
            action="consent.rejected",
            detail={
                "consent_id": consent_id,
                "remark": consent.remark,
                "handle_id": consent.handle_id,
            },
        )
    )
    db.commit()
    return {
        "consent_id": consent.id,
        "status": "rejected",
        "handle_id": consent.handle_id,
    }
