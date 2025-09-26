# app/routes/inventories.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/inventories",
    tags=["inventories"]
)

# ------------------------
# Add or update blood inventory
# ------------------------
@router.post("/", response_model=schemas.InventoryResponse)
def add_inventory(inventory: schemas.InventoryCreate, db: Session = Depends(get_db)):
    # Ensure the hospital exists
    hospital = crud.get_hospital_by_id(db, inventory.hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    try:
        # Check if the blood group already exists for this hospital
        existing = crud.get_inventory_by_hospital_blood(db, inventory.hospital_id, inventory.blood_group)
        if existing:
            # Update units and timestamp
            existing.units_available = inventory.units_available
            db.commit()
            db.refresh(existing)
            return existing

        # Create new inventory record
        return crud.create_inventory(db, inventory)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding/updating inventory: {str(e)}")


# ------------------------
# Get inventory of a specific hospital
# ------------------------
@router.get("/hospital/{hospital_id}", response_model=List[schemas.InventoryResponse])
def get_hospital_inventory(hospital_id: int, db: Session = Depends(get_db)):
    hospital = crud.get_hospital_by_id(db, hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return crud.get_inventory_by_hospital(db, hospital_id)


# ------------------------
# Get all inventories
# ------------------------
@router.get("/", response_model=List[schemas.InventoryResponse])
def get_all_inventories(db: Session = Depends(get_db)):
    try:
        return db.query(crud.models.Inventory).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching inventories: {str(e)}")
