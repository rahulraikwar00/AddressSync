import logging

from fastapi import APIRouter, Depends, HTTPException
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
    """Pull the citizen's current address. Requires an active consent."""
    consent = db.get(Consent, consent_id)
    if not consent or consent.agency_id != agency.id:
        raise HTTPException(status_code=404, detail="Consent not found")
    if consent.status != "granted":
        raise HTTPException(status_code=403, detail="Consent revoked or inactive")

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
            detail={"consent_id": consent_id, "version": record.version},
        )
    )
    db.commit()

    return {
        "consent_id": consent.id,
        "purpose": consent.purpose,
        "citizen_ref": consent.citizen.aadhaar_ref,
        "citizen_name": consent.citizen.name,
        "address": {**record.as_dict(), "version": record.version},
        "pulled_at": utcnow().isoformat() + "Z",
    }
