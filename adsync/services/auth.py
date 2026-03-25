# services/auth.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from sqlalchemy.orm import Session
from core.database import get_db
from core.config import settings
from models.user import User
from models.agency import Agency

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        aadhaar = payload.get("sub")
        user = db.query(User).filter(User.aadhaar_number == aadhaar).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_agency(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        agency_id = payload.get("sub")
        agency = db.query(Agency).filter(Agency.id == agency_id).first()
        if not agency:
            raise HTTPException(status_code=401, detail="Agency not found")
        return agency
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


# Add this to services/auth.py

def get_current_user_or_agency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """Get current user or agency from token"""
    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        user_type = payload.get("type")

        if user_type == "user":
            user = db.query(User).filter(
                User.aadhaar_number == user_id).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            return {"type": "user", "id": user.aadhaar_number, "data": user}

        elif user_type == "agency":
            agency = db.query(Agency).filter(Agency.id == user_id).first()
            if not agency:
                raise HTTPException(status_code=401, detail="Agency not found")
            return {"type": "agency", "id": agency.id, "data": agency}

        else:
            raise HTTPException(status_code=401, detail="Invalid token type")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
