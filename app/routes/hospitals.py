# app/routes/hospitals.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/hospitals",
    tags=["hospitals"]
)

# ------------------------
# Create hospital user
# ------------------------
@router.post("/", response_model=schemas.UserResponse)
def create_hospital(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if not user.is_hospital:
        user.is_hospital = True
    db_user = crud.get_user_by_phone(db, phone=user.phone)
    if db_user:
        raise HTTPException(status_code=400, detail="User with this phone already exists")
    return crud.create_user(db, user)


# ------------------------
# Create hospital profile
# ------------------------
@router.post("/profile/", response_model=schemas.HospitalProfileResponse)
def create_hospital_profile(profile: schemas.HospitalProfileCreate, db: Session = Depends(get_db)):
    user = crud.get_user(db, profile.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_hospital_profile(db, profile)


# ------------------------
# Get hospital by ID
# ------------------------
@router.get("/{hospital_id}", response_model=schemas.HospitalProfileResponse)
def get_hospital(hospital_id: int, db: Session = Depends(get_db)):
    hospital = crud.get_hospital_by_id(db, hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital


# ------------------------
# Get all hospitals
# ------------------------
@router.get("/", response_model=List[schemas.HospitalProfileResponse])
def list_hospitals(db: Session = Depends(get_db)):
    hospitals = db.query(crud.models.HospitalProfile).all()
    return hospitals
