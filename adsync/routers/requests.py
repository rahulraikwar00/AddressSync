# routers/active_requests.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import ActiveRequest, Agency, SessionLocal, User
from pydantic import BaseModel
from logging_config import logging

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
    logging.info(f"Fetching active requests for agency {agency_id} from the database.")
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
            "agency_id": agency_id,
            "requid": request.requid,
            "user_aadhaarnumber": request.user_aadhaarnumber,
            "new_address": request.new_address,
            "status": request.status
        }
        for request in active_requests
    ]




@router.post("/Create-requests/")
async def create_active_request(request_data: RequestCreate, db: Session = Depends(get_db)):
    logging.info("Received request to create a new active request.")

    # Check if the agency exists
    agency = db.query(Agency).filter(Agency.agency_id == request_data.agency_id).first()
    user = db.query(User).filter(request_data.user_aadhaarnumber==User.aadhaarnumber).first()


    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    existing_request = db.query(ActiveRequest).filter(ActiveRequest.user_aadhaarnumber == request_data.user_aadhaarnumber,
        ActiveRequest.agency_id == request_data.agency_id,
        ActiveRequest.status == 'pending'  
    ).first()

    if existing_request:
        raise HTTPException(
            status_code=422,
            detail="There is already an active request for this user and agency."
        )

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

class UpdateRequest(BaseModel):
    status:str
    agency_id:str
    requid:str

@router.post('/update-request-status')
async def update_request(update_data: UpdateRequest, db: Session = Depends(get_db)):
    # Check if the request with the provided requid exists
    request_to_update = db.query(ActiveRequest).filter(ActiveRequest.requid == update_data.requid).first()

    if request_to_update:
        # Update the status of the request
        request_to_update.status = update_data.status
        db.commit()
        db.refresh(request_to_update)
        return {"message": "Request status updated successfully","request_data":{
            request_to_update
        }}
    else:
        # Return an error response if the request does not exist
        raise HTTPException(status_code=404, detail="Request not found")