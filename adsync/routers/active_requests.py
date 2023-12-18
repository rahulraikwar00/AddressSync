# routers/active_requests.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import ActiveRequest, Agency, SessionLocal
from pydantic import BaseModel

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RequestCreate(BaseModel):
    user_aadhaarnumber: int
    agency_id: str
    new_address: str


@router.get("/active-requests/{agency_id}")
async def get_active_request_for_agency(agency_id: str, db: Session = Depends(get_db)):
    # Check if the agency exists
    agency = db.query(Agency).filter(Agency.agency_id == agency_id).first()

    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")

    # Check if there are active requests for the agency, limit to 10
    active_requests = db.query(ActiveRequest).filter(ActiveRequest.agency_id == agency_id).limit(10).all()

    if not active_requests:
        raise HTTPException(status_code=404, detail="No active requests for the agency")

    # Return the list of active requests
    return [
        {
            "requid": request.requid,
            "user_aadhaarnumber": request.user_aadhaarnumber,
            "new_address": request.new_address,
            "status": request.status
        }
        for request in active_requests
    ]




@router.post("/Create-requests/")
async def create_active_request(request_data: RequestCreate, db: Session = Depends(get_db)):
    # Check if the agency exists
    agency = db.query(Agency).filter(Agency.agency_id == request_data.agency_id).first()

    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")

    # Create the active request
    active_request = ActiveRequest(
        user_aadhaarnumber=request_data.user_aadhaarnumber,
        agency_id=request_data.agency_id,
        new_address=request_data.new_address,
    )
    db.add(active_request)
    db.commit()
    db.refresh(active_request)

    return active_request