# routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.user import User
from core.security import get_password_hash, verify_password, create_token
from services.auth import get_current_user
from core.logging import ActivityLogger

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register")
def register_user(user_data: dict, db: Session = Depends(get_db)):
    # Check if user exists
    existing = db.query(User).filter(User.aadhaar_number ==
                                     user_data["aadhaar_number"]).first()
    if existing:
        ActivityLogger.log_registration(
            "user", user_data["aadhaar_number"], user_data["name"])
        raise HTTPException(status_code=400, detail="User already exists")

    # Create user
    user = User(
        aadhaar_number=user_data["aadhaar_number"],
        name=user_data["name"],
        email=user_data["email"],
        password_hash=get_password_hash(user_data["password"]),
        current_address=user_data["current_address"]
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    ActivityLogger.log_registration("user", user.aadhaar_number, user.name)
    return {"message": "User created", "user": user}


@router.post("/login")
def login_user(login_data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.aadhaar_number ==
                                 login_data["aadhaar_number"]).first()
    if not user or not verify_password(login_data["password"], user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"sub": user.aadhaar_number, "type": "user"})
    ActivityLogger.log_login("user", user.aadhaar_number)
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    ActivityLogger.log_user_action(current_user.aadhaar_number, "VIEW_PROFILE")
    return current_user
