# app/schemas.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

# ------------------------
# User schemas
# ------------------------
class UserBase(BaseModel):
    name: str = Field(..., example="John Doe")
    phone: str = Field(..., example="9876543210")
    email: Optional[EmailStr] = Field(None, example="john@example.com")

class UserCreate(UserBase):
    is_donor: bool = False
    is_hospital: bool = False
    role: Optional[str] = "user"

class UserResponse(UserBase):
    id: int
    is_donor: bool
    is_hospital: bool
    role: str
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ------------------------
# Donor Profile schemas
# ------------------------
class DonorProfileBase(BaseModel):
    blood_group: str = Field(..., example="A+")
    last_donation: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    availability: bool = True
    consent_emergency: bool = True

class DonorProfileCreate(DonorProfileBase):
    user_id: int

class DonorProfileResponse(DonorProfileBase):
    id: int
    user_id: int
    last_notified_request: Optional[int] = None
    last_notified_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ------------------------
# Hospital Profile schemas
# ------------------------
class HospitalProfileBase(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    verified: bool = False

class HospitalProfileCreate(HospitalProfileBase):
    user_id: int

class HospitalProfileResponse(HospitalProfileBase):
    id: int
    user_id: int

    model_config = {"from_attributes": True}


# ------------------------
# Inventory schemas
# ------------------------
class InventoryBase(BaseModel):
    blood_group: str
    units_available: int
    threshold: int = 5

class InventoryCreate(InventoryBase):
    hospital_id: int

class InventoryResponse(InventoryBase):
    id: int
    hospital_id: int
    updated_at: datetime

    model_config = {"from_attributes": True}


# ------------------------
# Request schemas
# ------------------------
class RequestBase(BaseModel):
    blood_group: str
    units_needed: int
    urgency: Optional[str] = "medium"
    fulfilled: Optional[bool] = False

class RequestCreate(RequestBase):
    hospital_id: int

class RequestResponse(RequestBase):
    id: int
    hospital_id: int
    created_at: datetime
    fulfilled_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ------------------------
# Offer schemas
# ------------------------
class OfferBase(BaseModel):
    accepted: bool = False

class OfferCreate(OfferBase):
    request_id: int
    donor_id: int

class OfferResponse(OfferBase):
    id: int
    request_id: int
    donor_id: int
    notified_at: datetime

    model_config = {"from_attributes": True}
