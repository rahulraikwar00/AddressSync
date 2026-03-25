# routers/agencies.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.agency import Agency
from core.security import get_password_hash, verify_password, create_token
from services.auth import get_current_agency
from core.logging import ActivityLogger
router = APIRouter(prefix="/agencies", tags=["Agencies"])


@router.post("/register")
def register_agency(agency_data: dict, db: Session = Depends(get_db)):
    # Check if exists
    existing = db.query(Agency).filter(Agency.id == agency_data["id"]).first()
    if existing:
        ActivityLogger.log_registration(
            "agency", agency_data["id"], agency_data["name"])
        raise HTTPException(status_code=400, detail="Agency already exists")

    # Create agency
    agency = Agency(
        id=agency_data["id"],
        name=agency_data["name"],
        email=agency_data["email"],
        password_hash=get_password_hash(agency_data["password"])
    )
    db.add(agency)
    db.commit()
    db.refresh(agency)
    ActivityLogger.log_registration("agency", agency.id, agency.name)
    return {"message": "Agency created", "agency": agency}


@router.post("/login")
def login_agency(login_data: dict, db: Session = Depends(get_db)):
    agency = db.query(Agency).filter(Agency.id == login_data["id"]).first()
    if not agency or not verify_password(login_data["password"], agency.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"sub": agency.id, "type": "agency"})
    ActivityLogger.log_login("agency", agency.id)
    return {"access_token": token, "token_type": "bearer", "agency": agency}


@router.get("/me")
def get_me(current_agency: Agency = Depends(get_current_agency)):
    ActivityLogger.log_agency_action(current_agency.id, "VIEW_PROFILE")
    return current_agency
