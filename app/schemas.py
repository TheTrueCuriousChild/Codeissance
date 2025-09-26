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
    blood_group: Optional[str] = Field(None, example="A+")
    donor_type: str = Field("blood", example="blood")  # blood / organ / both
    organs_available: Optional[str] = Field(None, example="kidney,liver")
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
    blood_group: Optional[str] = None
    organ_type: Optional[str] = None
    type: str = "blood"  # blood / organ
    units_available: int
    threshold: int = 5
    expiry_date: Optional[datetime] = None

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
    request_type: str = "blood"  # blood / organ
    blood_group: Optional[str] = None
    organ_type: Optional[str] = None
    units_needed: int
    urgency: Optional[str] = "medium"
    details: Optional[str] = None
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


# ------------------------
# Donation Log schemas
# ------------------------
class DonationLogBase(BaseModel):
    donation_type: str = "blood"  # blood / organ
    blood_group: Optional[str] = None
    organ_type: Optional[str] = None
    units: int = 1

class DonationLogCreate(DonationLogBase):
    donor_id: int
    hospital_id: int
    request_id: Optional[int] = None

class DonationLogResponse(DonationLogBase):
    id: int
    donor_id: int
    hospital_id: int
    request_id: Optional[int]
    donation_date: datetime

    model_config = {"from_attributes": True}


# ------------------------
# Notification Log schemas
# ------------------------
class NotificationLogBase(BaseModel):
    method: str = "sms"  # sms / email / app
    status: str = "sent"  # sent / delivered / failed

class NotificationLogCreate(NotificationLogBase):
    donor_id: int
    request_id: int

class NotificationLogResponse(NotificationLogBase):
    id: int
    donor_id: int
    request_id: int
    sent_at: datetime

    model_config = {"from_attributes": True}
