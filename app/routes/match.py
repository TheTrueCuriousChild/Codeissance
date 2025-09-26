# app/routes/match.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/match",
    tags=["match"]
)

# ------------------------
# Get compatible donors for a request
# ------------------------
@router.get("/donors-for-request/{request_id}", response_model=List[schemas.DonorProfileResponse])
def get_donors_for_request(request_id: int, db: Session = Depends(get_db)):
    """
    Returns a list of donors that match the blood group of a given request.
    """
    request_obj = crud.get_request_by_id(db, request_id)
    if not request_obj:
        raise HTTPException(status_code=404, detail="Request not found")
    
    donors = crud.get_available_donors(db, request_obj.blood_group)
    return donors

# ------------------------
# Get all matches (offers) for a hospital's requests
# ------------------------
@router.get("/hospital/{hospital_id}", response_model=List[schemas.OfferResponse])
def get_matches_for_hospital(hospital_id: int, db: Session = Depends(get_db)):
    """
    Returns all donor offers for requests from a specific hospital.
    """
    hospital = crud.get_hospital_by_id(db, hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    # Get all requests from this hospital
    requests = db.query(crud.models.Request).filter(crud.models.Request.hospital_id == hospital_id).all()
    offers = []
    for req in requests:
        req_offers = crud.get_offers_by_request(db, req.id)
        offers.extend(req_offers)
    return offers

# ------------------------
# Create a donor offer for a request
# ------------------------
@router.post("/create-offer", response_model=schemas.OfferResponse)
def create_donor_offer(offer: schemas.OfferCreate, db: Session = Depends(get_db)):
    """
    Create an offer linking a donor to a request.
    """
    request_obj = crud.get_request_by_id(db, offer.request_id)
    donor_obj = crud.get_donor_by_id(db, offer.donor_id)
    
    if not request_obj:
        raise HTTPException(status_code=404, detail="Request not found")
    if not donor_obj:
        raise HTTPException(status_code=404, detail="Donor not found")
    
    return crud.create_offer(db, offer)

# ------------------------
# AI-assisted automatic donor matching
# ------------------------
@router.post("/auto-match/{request_id}", response_model=List[schemas.OfferResponse])
def auto_match_donors(request_id: int, db: Session = Depends(get_db)):
    """
    Automatically finds compatible donors for a request and creates offers.
    Simulates agentic AI behavior.
    """
    # Step 1: Fetch the patient request
    request_obj = crud.get_request_by_id(db, request_id)
    if not request_obj:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Step 2: Fetch eligible donors
    compatible_donors = crud.get_available_donors(db, blood_group=request_obj.blood_group)
    if not compatible_donors:
        raise HTTPException(status_code=404, detail="No available donors found")
    
    # Step 3: Create offers automatically
    offers_created = []
    for donor in compatible_donors:
        offer_data = schemas.OfferCreate(
            request_id=request_obj.id,
            donor_id=donor.id,
            accepted=False  # initially not accepted
        )
        offer = crud.create_offer(db, offer_data)
        offers_created.append(offer)
    
    return offers_created
