import asyncio
import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta

import httpx
from sqlalchemy.orm import Session

from .config import settings
from .db import SessionLocal
from .models import Agency, Event, utcnow

logger = logging.getLogger("addresssync.events")

BACKOFF_SECONDS = [5, 15, 45]


def enqueue(
    db: Session,
    type_: str,
    agency_id: str,
    payload: dict,
    citizen_id: str | None = None,
) -> Event:
    """Write to the outbox in the same transaction as the state change."""
    event = Event(type=type_, agency_id=agency_id, citizen_id=citizen_id, payload=payload)
    db.add(event)
    return event


def build_envelope(event: Event) -> bytes:
    body = {
        "event_id": event.id,
        "type": event.type,
        "occurred_at": event.created_at.isoformat() + "Z",
        "payload": event.payload,
    }
    return json.dumps(body, separators=(",", ":")).encode()


def sign(secret: str, body: bytes) -> str:
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


async def deliver(event_id: str) -> None:
    with SessionLocal() as db:
        event = db.get(Event, event_id)
        if not event or event.status != "pending":
            return
        agency = db.get(Agency, event.agency_id)
        if not agency or not agency.webhook_url:
            # leave pending; agencies without a webhook can still pull.
            # give up only after many idle cycles so late webhook config still works
            event.attempts += 1
            event.last_error = "agency has no webhook configured"
            if event.attempts >= settings.webhook_max_attempts * 10:
                event.status = "failed"
            db.commit()
            return

        body = build_envelope(event)
        headers = {
            "content-type": "application/json",
            "x-event-id": event.id,
            "x-event-type": event.type,
            "x-signature": sign(agency.webhook_secret, body),
        }
        try:
            async with httpx.AsyncClient(timeout=settings.webhook_timeout_seconds) as client:
                resp = await client.post(agency.webhook_url, content=body, headers=headers)
            if not (200 <= resp.status_code < 300):
                raise RuntimeError(f"receiver returned HTTP {resp.status_code}")
            event.status = "delivered"
            event.delivered_at = utcnow()
            event.last_error = None
            logger.info("delivered %s -> %s", event.type, agency.id)
        except Exception as exc:
            event.attempts += 1
            event.last_error = str(exc)[:500]
            if event.attempts >= settings.webhook_max_attempts:
                event.status = "failed"
            else:
                delay = BACKOFF_SECONDS[min(event.attempts - 1, len(BACKOFF_SECONDS) - 1)]
                event.next_attempt_at = utcnow() + timedelta(seconds=delay)
                logger.warning(
                    "delivery %s attempt %d failed (%s), retry in %ds",
                    event.id,
                    event.attempts,
                    event.last_error,
                    delay,
                )
        db.commit()


async def worker_loop() -> None:
    logger.info("webhook worker started")
    while True:
        try:
            with SessionLocal() as db:
                due_ids = [
                    row[0]
                    for row in db.query(Event.id)
                    .filter(Event.status == "pending", Event.next_attempt_at <= utcnow())
                    .all()
                ]
            for event_id in due_ids:
                await deliver(event_id)
        except Exception:
            logger.exception("worker cycle failed")
        await asyncio.sleep(settings.worker_poll_seconds)
