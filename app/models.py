# app/models.py
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

# ------------------------
# User table (donors and hospitals)
# ------------------------
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    is_donor = Column(Boolean, default=False)
    is_hospital = Column(Boolean, default=False)
    role = Column(String, default="user")  # Optional: admin / staff / donor
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime, nullable=True)

    donor_profile = relationship("DonorProfile", back_populates="user", uselist=False)
    hospital_profile = relationship("HospitalProfile", back_populates="user", uselist=False)


# ------------------------
# Donor profile
# ------------------------
class DonorProfile(Base):
    __tablename__ = "donor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    blood_group = Column(String, nullable=False)
    last_donation = Column(DateTime, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    availability = Column(Boolean, default=True)
    consent_emergency = Column(Boolean, default=True)  # allow emergency contact

    # For emergency notifications
    last_notified_request = Column(Integer, nullable=True)
    last_notified_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="donor_profile")


# ------------------------
# Hospital profile
# ------------------------
class HospitalProfile(Base):
    __tablename__ = "hospital_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address = Column(String, nullable=True)
    verified = Column(Boolean, default=False)

    user = relationship("User", back_populates="hospital_profile")


# ------------------------
# Inventory (blood or organ units)
# ------------------------
class Inventory(Base):
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospital_profiles.id"), nullable=False)
    blood_group = Column(String, nullable=False)
    units_available = Column(Integer, default=0)
    threshold = Column(Integer, default=5)  # Critical units threshold
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    hospital = relationship("HospitalProfile")


# ------------------------
# Request (patient need)
# ------------------------
class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospital_profiles.id"), nullable=False)
    blood_group = Column(String, nullable=False)
    units_needed = Column(Integer, nullable=False)
    urgency = Column(String, default="medium")  # low / medium / high
    fulfilled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    fulfilled_at = Column(DateTime, nullable=True)

    hospital = relationship("HospitalProfile")


# ------------------------
# Offer (matching donor to request)
# ------------------------
class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    donor_id = Column(Integer, ForeignKey("donor_profiles.id"), nullable=False)
    accepted = Column(Boolean, default=False)
    notified_at = Column(DateTime(timezone=True), server_default=func.now())

    request = relationship("Request")
    donor = relationship("DonorProfile")
