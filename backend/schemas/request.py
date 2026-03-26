from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from models.request import RequestStatus


class RequestBase(BaseModel):
    user_aadhaar: str = Field(..., pattern="^[0-9]{12}$")
    agency_id: str = Field(..., min_length=3, max_length=50)
    new_address: str = Field(..., min_length=5, max_length=500)

    @field_validator('user_aadhaar')
    @classmethod
    def validate_aadhaar(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 12:
            raise ValueError('Aadhaar number must be 12 digits')
        return v


class RequestCreate(RequestBase):
    pass


class RequestUpdate(BaseModel):
    status: RequestStatus
    reason: Optional[str] = Field(None, max_length=500)


class RequestResponse(BaseModel):
    id: str
    user_aadhaar: str
    agency_id: str
    new_address: str
    status: RequestStatus
    reason: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
