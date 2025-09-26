# app/crud.py
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app import models, schemas

# ------------------------
# Users
# ------------------------
def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(
        name=user.name,
        phone=user.phone,
        email=user.email,
        is_donor=user.is_donor,
        is_hospital=user.is_hospital
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_phone(db: Session, phone: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.phone == phone).first()

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


# ------------------------
# Donor Profiles
# ------------------------
def create_donor_profile(db: Session, donor: schemas.DonorProfileCreate) -> models.DonorProfile:
    db_donor = models.DonorProfile(**donor.dict())
    db.add(db_donor)
    db.commit()
    db.refresh(db_donor)
    return db_donor

def get_donor_by_id(db: Session, donor_id: int) -> Optional[models.DonorProfile]:
    return db.query(models.DonorProfile).filter(models.DonorProfile.id == donor_id).first()

def get_available_donors(db: Session, blood_group: str) -> List[models.DonorProfile]:
    return db.query(models.DonorProfile).filter(
        models.DonorProfile.blood_group == blood_group,
        models.DonorProfile.availability == True,
        models.DonorProfile.consent_emergency == True
    ).all()

# New: Mark donor notified for a request
def mark_donor_notified(db: Session, donor_id: int, request_id: int):
    donor = get_donor_by_id(db, donor_id)
    if donor:
        # Here you could log donor notification in a table or just update a timestamp
        donor.last_notified_request = request_id
        donor.last_notified_at = datetime.utcnow()
        db.commit()
        db.refresh(donor)
    return donor


# ------------------------
# Hospital Profiles
# ------------------------
def create_hospital_profile(db: Session, hospital: schemas.HospitalProfileCreate) -> models.HospitalProfile:
    db_hospital = models.HospitalProfile(**hospital.dict())
    db.add(db_hospital)
    db.commit()
    db.refresh(db_hospital)
    return db_hospital

def get_hospital_by_id(db: Session, hospital_id: int) -> Optional[models.HospitalProfile]:
    return db.query(models.HospitalProfile).filter(models.HospitalProfile.id == hospital_id).first()


# ------------------------
# Inventory
# ------------------------
def create_inventory(db: Session, inventory: schemas.InventoryCreate) -> models.Inventory:
    db_inventory = models.Inventory(**inventory.dict())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

def update_inventory_units(db: Session, inventory_id: int, units: int) -> models.Inventory:
    db_inventory = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if db_inventory:
        db_inventory.units_available = units
        db_inventory.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_inventory)
    return db_inventory

def get_inventory_by_hospital(db: Session, hospital_id: int) -> List[models.Inventory]:
    return db.query(models.Inventory).filter(models.Inventory.hospital_id == hospital_id).all()

def get_inventory_by_hospital_blood(db: Session, hospital_id: int, blood_group: str):
    return db.query(models.Inventory).filter(
        models.Inventory.hospital_id == hospital_id,
        models.Inventory.blood_group == blood_group
    ).first()

def get_all_inventories(db: Session) -> List[models.Inventory]:
    return db.query(models.Inventory).all()


# ------------------------
# Requests
# ------------------------
def create_request(db: Session, request: schemas.RequestCreate) -> models.Request:
    db_request = models.Request(**request.dict())
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

def get_request_by_id(db: Session, request_id: int) -> Optional[models.Request]:
    return db.query(models.Request).filter(models.Request.id == request_id).first()

def get_pending_requests(db: Session) -> List[models.Request]:
    return db.query(models.Request).filter(models.Request.fulfilled == False).all()

# New: Mark request fulfilled
def mark_request_fulfilled(db: Session, request_id: int):
    req = get_request_by_id(db, request_id)
    if req:
        req.fulfilled = True
        req.fulfilled_at = datetime.utcnow()
        db.commit()
        db.refresh(req)
    return req


# ------------------------
# Offers
# ------------------------
def create_offer(db: Session, offer: schemas.OfferCreate) -> models.Offer:
    db_offer = models.Offer(**offer.dict())
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)
    return db_offer

def get_offers_by_request(db: Session, request_id: int) -> List[models.Offer]:
    return db.query(models.Offer).filter(models.Offer.request_id == request_id).all()
