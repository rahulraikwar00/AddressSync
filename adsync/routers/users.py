# routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User, SessionLocal
from pydantic import BaseModel

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    aadhaarnumber: int
    password_hash: str
    new_address: str

@router.post("/register/")
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