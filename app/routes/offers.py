# app/routes/offers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/offers",
    tags=["offers"]
)

# ------------------------
# Create an offer for a request
# ------------------------
@router.post("/", response_model=schemas.OfferResponse)
def create_offer(offer: schemas.OfferCreate, db: Session = Depends(get_db)):
    # Check if request exists
    req = crud.get_request_by_id(db, offer.request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Check if donor exists
    donor = crud.get_donor_by_id(db, offer.donor_id)
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")
    
    # Optional: ensure donor blood group matches request
    if donor.blood_group != req.blood_group:
        raise HTTPException(
            status_code=400,
            detail=f"Donor blood group ({donor.blood_group}) does not match request ({req.blood_group})"
        )

    return crud.create_offer(db, offer)


# ------------------------
# List offers for a specific request
# ------------------------
@router.get("/request/{request_id}", response_model=List[schemas.OfferResponse])
def get_offers_by_request(request_id: int, db: Session = Depends(get_db)):
    req = crud.get_request_by_id(db, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return crud.get_offers_by_request(db, request_id)


# ------------------------
# Accept an offer
# ------------------------
@router.put("/{offer_id}/accept", response_model=schemas.OfferResponse)
def accept_offer(offer_id: int, db: Session = Depends(get_db)):
    offer = db.query(crud.models.Offer).filter(crud.models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    # Mark offer as accepted
    offer.accepted = True
    db.commit()
    db.refresh(offer)

    # Optional: update hospital inventory to reduce units
    request = crud.get_request_by_id(db, offer.request_id)
    inventory = db.query(crud.models.Inventory).filter(
        crud.models.Inventory.hospital_id == request.hospital_id,
        crud.models.Inventory.blood_group == request.blood_group
    ).first()

    if inventory:
        inventory.units_available -= request.units_needed
        db.commit()
        db.refresh(inventory)

    # Mark request as fulfilled
    request.fulfilled = True
    db.commit()
    db.refresh(request)

    return offer
