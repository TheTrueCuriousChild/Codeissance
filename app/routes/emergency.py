# app/routes/emergency.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db
from app.agents import router_ai
from app.utils.notifications import send_whatsapp

router = APIRouter(prefix="/emergency", tags=["emergency"])

class EmergencyRequest(schemas.BaseModel):
    hospital_id: int
    blood_group: str
    units_needed: int

@router.post("/", response_model=dict)
def trigger_emergency_sos(emergency: EmergencyRequest, db: Session = Depends(get_db)):
    hospital = crud.get_hospital_by_id(db, emergency.hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    inventory_list = crud.get_inventory_by_hospital(db, emergency.hospital_id)
    current_units = 0
    for inv in inventory_list:
        if inv.blood_group == emergency.blood_group:
            current_units = inv.units_available
            break

    if current_units >= emergency.units_needed:
        return {"message": "Sufficient inventory available. No SOS required."}

    donors = router_ai.router_agent.get_nearest_donors(
        blood_group=emergency.blood_group,
        hospital_lat=hospital.latitude,
        hospital_lon=hospital.longitude,
        db=db
    )

    if not donors:
        return {"message": "No donors found nearby. Please escalate manually."}

    notified_donors = []
    for donor in donors:
        phone_number = getattr(donor.user, "phone", None)
        if phone_number:
            message = (
                f"Emergency! Hospital {hospital.name} needs {emergency.units_needed} units of {emergency.blood_group}.\n"
                f"Distance: {getattr(donor, 'distance_km', '?')} km\n"
                f"Estimated travel time: {getattr(donor, 'eta_min', '?')} min\n"
                f"Navigate: {getattr(donor, 'maps_link', '')}\n"
                "Please contact immediately."
            )
            send_whatsapp(phone_number, message)

    return {
        "message": f"Emergency SOS triggered! {len(notified_donors)} donors notified.",
        "notified_donors": notified_donors
    }
