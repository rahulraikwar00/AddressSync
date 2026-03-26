# schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserBase(BaseModel):
    aadhaar_number: str = Field(..., min_length=12, max_length=12)
    name: str = Field(..., min_length=2)
    email: EmailStr
    current_address: str = Field(..., min_length=5)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)  # Simple: just 6 chars minimum


class UserLogin(BaseModel):
    aadhaar_number: str
    password: str


class UserResponse(UserBase):
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
