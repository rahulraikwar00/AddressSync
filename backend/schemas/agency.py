# schemas/agency.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class AgencyBase(BaseModel):
    id: str = Field(..., min_length=3)
    name: str = Field(..., min_length=2)
    email: EmailStr


class AgencyCreate(AgencyBase):
    password: str = Field(..., min_length=6)  # Simple: just 6 chars minimum


class AgencyLogin(BaseModel):
    id: str
    password: str


class AgencyResponse(AgencyBase):
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
