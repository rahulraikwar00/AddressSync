import hashlib
import secrets
from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .models import Agency, Citizen, OtpChallenge

bearer = HTTPBearer(auto_error=False)

OTP_TTL_SECONDS = 300
OTP_MAX_ATTEMPTS = 5


def hash_value(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def mask_aadhaar(aadhaar: str) -> str:
    return f"XXXX XXXX {aadhaar[-4:]}"


# --- OTP (mock UIDAI eKYC) ---
def create_otp_challenge(db: Session, aadhaar_number: str) -> str:
    otp = f"{secrets.randbelow(1_000_000):06d}"
    aadhaar_hash = hash_value(aadhaar_number)
    db.query(OtpChallenge).filter(
        OtpChallenge.aadhaar_hash == aadhaar_hash,
        OtpChallenge.consumed.is_(False),
    ).update({"consumed": True})
    db.add(
        OtpChallenge(
            aadhaar_hash=aadhaar_hash,
            otp_hash=hash_value(otp),
            expires_at=datetime.utcnow() + timedelta(seconds=OTP_TTL_SECONDS),
        )
    )
    db.commit()
    return otp


def verify_otp(db: Session, aadhaar_number: str, otp: str) -> None:
    challenge = (
        db.query(OtpChallenge)
        .filter(
            OtpChallenge.aadhaar_hash == hash_value(aadhaar_number),
            OtpChallenge.consumed.is_(False),
        )
        .order_by(OtpChallenge.created_at.desc())
        .first()
    )
    if not challenge or challenge.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="No active OTP. Request a new one.")
    challenge.attempts += 1
    if challenge.attempts > OTP_MAX_ATTEMPTS:
        challenge.consumed = True
        db.commit()
        raise HTTPException(status_code=429, detail="Too many attempts. Request a new OTP.")
    if not secrets.compare_digest(challenge.otp_hash, hash_value(otp)):
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid OTP")
    challenge.consumed = True
    db.commit()


# --- JWT ---
def create_token(subject: str, token_type: str) -> str:
    payload = {
        "sub": subject,
        "type": token_type,
        "exp": datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def _decode(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_current_citizen(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> Citizen:
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated")
    claims = _decode(creds.credentials)
    if claims.get("type") != "citizen":
        raise HTTPException(status_code=403, detail="Citizen token required")
    citizen = db.get(Citizen, claims["sub"])
    if not citizen:
        raise HTTPException(status_code=401, detail="Unknown citizen")
    return citizen


def get_current_agency(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> Agency:
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated")
    claims = _decode(creds.credentials)
    if claims.get("type") != "agency":
        raise HTTPException(status_code=403, detail="Agency token required")
    agency = db.get(Agency, claims["sub"])
    if not agency:
        raise HTTPException(status_code=401, detail="Unknown agency")
    return agency


# --- Agency API keys / webhook secrets ---
def generate_api_key() -> tuple[str, str]:
    raw = "agk_" + secrets.token_hex(16)
    return raw, hash_value(raw)


def generate_webhook_secret() -> str:
    return "whsec_" + secrets.token_hex(16)
