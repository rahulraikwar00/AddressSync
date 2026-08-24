import json
from datetime import datetime

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..events import sign
from ..models import (
    AddressRecord,
    Agency,
    AuditLog,
    Citizen,
    Consent,
    Event,
    OtpChallenge,
    WebhookReceipt,
    utcnow,
)
from ..seed_data import DEMO_AADHAAR, DEMO_AGENCIES, seed_demo_data

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/receiver/{agency_id}")
async def fake_agency_receiver(
    agency_id: str, request: Request, db: Session = Depends(get_db)
):
    """Built-in fake agency inbox so webhooks have somewhere real to land."""
    body = await request.body()
    agency = db.get(Agency, agency_id)

    signature_valid = False
    if agency:
        signature_valid = (
            request.headers.get("x-signature", "") == sign(agency.webhook_secret, body)
        )

    parsed = None
    try:
        parsed = json.loads(body)
    except ValueError:
        pass

    receipt = WebhookReceipt(
        agency_id=agency_id,
        event_id=request.headers.get("x-event-id", ""),
        signature_valid=signature_valid,
        body=parsed,
    )
    db.add(receipt)
    db.commit()
    return {"status": "received", "signature_valid": signature_valid}


def _iso(dt):
    return dt.isoformat() if isinstance(dt, datetime) else dt


@router.get("/state")
def demo_state(db: Session = Depends(get_db)):
    """Everything the single-page demo needs; polled by the page for live updates."""
    citizen_names = {c.id: c.name for c in db.query(Citizen).all()}
    agency_names = {a.id: a.name for a in db.query(Agency).all()}
    return {
        "citizens": [
            {"id": c.id, "aadhaar_ref": c.aadhaar_ref, "name": c.name}
            for c in db.query(Citizen).all()
        ],
        "agencies": [
            {"id": a.id, "name": a.name, "webhook_url": a.webhook_url}
            for a in db.query(Agency).all()
        ],
        "consents": [
            {
                "id": c.id,
                "agency_id": c.agency_id,
                "citizen_id": c.citizen_id,
                "citizen_ref": c.citizen.aadhaar_ref,
                "citizen_name": c.citizen.name,
                "status": c.status,
                "purpose": c.purpose,
                "remark": c.remark,
                "created_at": _iso(c.created_at),
                "confirmed_at": _iso(c.confirmed_at),
                "reviewed_at": _iso(c.reviewed_at),
                "handled_at": _iso(c.handled_at),
                "handle_id": c.handle_id,
            }
            for c in db.query(Consent).all()
        ],
        "events": [
            {
                "id": e.id,
                "type": e.type,
                "agency_id": e.agency_id,
                "status": e.status,
                "attempts": e.attempts,
                "last_error": e.last_error,
                "created_at": _iso(e.created_at),
                "delivered_at": _iso(e.delivered_at),
            }
            for e in db.query(Event).order_by(Event.created_at.desc()).limit(25).all()
        ],
        "receipts": [
            {
                "id": r.id,
                "agency_id": r.agency_id,
                "event_id": r.event_id,
                "signature_valid": r.signature_valid,
                "type": (r.body or {}).get("type") if r.body else None,
                "received_at": _iso(r.received_at),
            }
            for r in db.query(WebhookReceipt)
            .order_by(WebhookReceipt.received_at.desc())
            .limit(15)
            .all()
        ],
        "audit": [
            {
                "id": a.id,
                "ts": _iso(a.ts),
                "actor_type": a.actor_type or "system",
                "actor": (
                    agency_names.get(a.actor_id)
                    if a.actor_type == "agency"
                    else citizen_names.get(a.actor_id)
                    if a.actor_type == "citizen"
                    else None
                ),
                "action": a.action,
                "detail": a.detail,
            }
            for a in db.query(AuditLog)
            .order_by(AuditLog.ts.desc())
            .limit(100)
            .all()
        ],
        "server_time": utcnow().isoformat() + "Z",
        **(
            {
                "demo_credentials": {
                    "aadhaar_number": DEMO_AADHAAR,
                    "agencies": {a["slug"]: a["api_key"] for a in DEMO_AGENCIES},
                }
            }
            if settings.dev_mode
            else {}
        ),
    }


@router.post("/reset")
def reset_demo(db: Session = Depends(get_db)):
    """Wipe all tables and reseed. Prototype convenience only."""
    # delete children before parents to respect FKs
    for model in (
        WebhookReceipt,
        Event,
        Consent,
        AddressRecord,
        OtpChallenge,
        AuditLog,
        Citizen,
        Agency,
    ):
        db.query(model).delete()
    db.commit()

    seed_demo_data(db)
    db.add(AuditLog(actor_type="system", actor_id=None, action="demo.reset"))
    db.commit()
    return {"status": "reseeded"}
