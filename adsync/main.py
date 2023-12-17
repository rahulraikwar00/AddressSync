# main.py
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import User, Agency, ActiveRequest, SessionLocal

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#data validation
class UserCreate(BaseModel):
    aadhaarnumber: int
    password_hash: str
    new_address: str

class AgencyCreate(BaseModel):
    agency_id: str
    password_hash: str


# home functions
@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}


@app.post("/users/")
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if the aadhaarnumber already exists
    existing_user = db.query(User).filter(User.aadhaarnumber == user_data.aadhaarnumber).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this aadhaarnumber already exists")

    # Create a new user
    new_user = User(aadhaarnumber=user_data.aadhaarnumber, password_hash=user_data.password_hash, new_address=user_data.new_address)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post("/agencies/")
async def create_agency(agency_data: AgencyCreate, db: Session=Depends(get_db)):
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



@app.get("/active-request-for-agency/{agency_id}")
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



class RequestCreate(BaseModel):
    user_aadhaarnumber: int
    agency_id: str
    new_address: str


@app.post("/active-requests/")
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
