from typing import Optional

from pydantic import BaseModel, Field


# --- Citizen ---
class OtpRequest(BaseModel):
    aadhaar_number: str = Field(pattern=r"^\d{12}$")


class OtpVerify(BaseModel):
    aadhaar_number: str = Field(pattern=r"^\d{12}$")
    otp: str = Field(pattern=r"^\d{6}$")


class AddressUpdate(BaseModel):
    line1: str = Field(min_length=3, max_length=200)
    line2: Optional[str] = Field(default=None, max_length=200)
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=100)
    pincode: str = Field(pattern=r"^\d{6}$")


class ConsentGrant(BaseModel):
    agency_id: str
    purpose: str = Field(default="address verification", max_length=200)


# --- Agency ---
class AgencyRegister(BaseModel):
    slug: str = Field(min_length=3, max_length=40)
    name: str = Field(min_length=2, max_length=120)
    webhook_url: Optional[str] = None


class AgencyLogin(BaseModel):
    api_key: str


class WebhookConfig(BaseModel):
    webhook_url: str
