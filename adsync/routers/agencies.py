# routers/agencies.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Agency, SessionLocal
from pydantic import BaseModel
from logging_config import logging

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AgencyCreate(BaseModel):
    agency_id: str
    password_hash: str

@router.post("/register/")
async def create_agency(agency_data: AgencyCreate, db: Session=Depends(get_db)):
    logging.info("Received request to create a new agency.")
    # Check if the agency_id already exists
    existing_agency = db.query(Agency).filter(Agency.agency_id == agency_data.agency_id).first()
    if existing_agency:
        raise HTTPException(status_code=400, detail="Agency with this agency_id already exists")

    # Create a new agency
    new_agency = Agency(agency_id=agency_data.agency_id, password_hash=agency_data.password_hash)
    db.add(new_agency)
    db.commit()
    db.refresh(new_agency)

    return new_agency
