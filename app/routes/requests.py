# app/routes/requests.py
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas, models
from app.database import get_db, SessionLocal
from app.utils.notifications import format_whatsapp_message, send_whatsapp
from app.utils.distance import haversine_distance

router = APIRouter(
    prefix="/requests",
    tags=["requests"]
)

# ------------------------
# Notify nearest donor asynchronously
# ------------------------
def notify_nearest_donor(request_id: int):
    db = SessionLocal()
    try:
        # Fetch request and associated hospital
        request = db.query(models.Request).filter(models.Request.id == request_id).first()
        if not request:
            return

        hospital = request.hospital
        if not hospital or not hospital.latitude or not hospital.longitude:
            return

        # Fetch all donors with valid location
        donors = db.query(models.DonorProfile).filter(
            models.DonorProfile.latitude.isnot(None),
            models.DonorProfile.longitude.isnot(None),
            models.DonorProfile.availability == True
        ).all()
        if not donors:
            return

        # Find nearest donor
        nearest_donor = min(
            donors,
            key=lambda d: haversine_distance(
                hospital.latitude, hospital.longitude,
                d.latitude, d.longitude
            )
        )

        donor_user = nearest_donor.user
        if donor_user.phone:
            # Decide whether this is blood or organ
            resource_type = request.blood_group if request.blood_group else "Organ"

            # Prepare WhatsApp message
            message = format_whatsapp_message(
                hospital_name=hospital.user.name,
                blood_group=resource_type,
                units=request.units_needed,
                donor_lat=nearest_donor.latitude,
                donor_lon=nearest_donor.longitude,
                hospital_lat=hospital.latitude,
                hospital_lon=hospital.longitude
            )
            send_whatsapp(donor_user.phone, message)
    finally:
        db.close()


# ------------------------
# Create a new request (hospital)
# ------------------------
@router.post("/", response_model=schemas.RequestResponse)
def create_request(
    request: schemas.RequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    hospital = crud.get_hospital_by_id(db, request.hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    try:
        new_request = crud.create_request(db, request)

        # Schedule donor notification in background
        background_tasks.add_task(notify_nearest_donor, new_request.id)

        return new_request
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating request: {str(e)}")


# ------------------------
# Get all requests
# ------------------------
@router.get("/", response_model=List[schemas.RequestResponse])
def get_all_requests(db: Session = Depends(get_db)):
    return db.query(models.Request).all()


# ------------------------
# Get requests by hospital
# ------------------------
@router.get("/hospital/{hospital_id}", response_model=List[schemas.RequestResponse])
def get_requests_by_hospital(hospital_id: int, db: Session = Depends(get_db)):
    hospital = crud.get_hospital_by_id(db, hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return db.query(models.Request).filter(models.Request.hospital_id == hospital_id).all()


# ------------------------
# Get pending requests (not yet fulfilled)
# ------------------------
@router.get("/pending", response_model=List[schemas.RequestResponse])
def get_pending_requests(db: Session = Depends(get_db)):
    return crud.get_pending_requests(db)
