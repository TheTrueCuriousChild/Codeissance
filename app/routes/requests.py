# app/routes/requests.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/requests",
    tags=["requests"]
)

# ------------------------
# Create a new request (hospital)
# ------------------------
@router.post("/", response_model=schemas.RequestResponse)
def create_request(request: schemas.RequestCreate, db: Session = Depends(get_db)):
    hospital = crud.get_hospital_by_id(db, request.hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    try:
        return crud.create_request(db, request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating request: {str(e)}")

# ------------------------
# Get all requests
# ------------------------
@router.get("/", response_model=List[schemas.RequestResponse])
def get_all_requests(db: Session = Depends(get_db)):
    return db.query(crud.models.Request).all()

# ------------------------
# Get requests by hospital
# ------------------------
@router.get("/hospital/{hospital_id}", response_model=List[schemas.RequestResponse])
def get_requests_by_hospital(hospital_id: int, db: Session = Depends(get_db)):
    hospital = crud.get_hospital_by_id(db, hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return db.query(crud.models.Request).filter(crud.models.Request.hospital_id == hospital_id).all()

# ------------------------
# Get pending requests (not yet fulfilled)
# ------------------------
@router.get("/pending", response_model=List[schemas.RequestResponse])
def get_pending_requests(db: Session = Depends(get_db)):
    return crud.get_pending_requests(db)
