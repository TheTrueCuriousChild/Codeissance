# app/routes/donors.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/donors",
    tags=["donors"]
)

# ------------------------
# Create a donor user
# ------------------------
@router.post("/", response_model=schemas.UserResponse)
def create_donor(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if not user.is_donor:
        user.is_donor = True  # Ensure user is marked as donor
    db_user = crud.get_user_by_phone(db, phone=user.phone)
    if db_user:
        raise HTTPException(status_code=400, detail="User with this phone already exists")
    return crud.create_user(db, user)


# ------------------------
# Create donor profile
# ------------------------
@router.post("/profile/", response_model=schemas.DonorProfileResponse)
def create_donor_profile(profile: schemas.DonorProfileCreate, db: Session = Depends(get_db)):
    user = crud.get_user(db, profile.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_donor_profile(db, profile)


# ------------------------
# Get all donors
# ------------------------
@router.get("/", response_model=List[schemas.DonorProfileResponse])
def list_available_donors(blood_group: str, db: Session = Depends(get_db)):
    donors = crud.get_available_donors(db, blood_group)
    return donors
