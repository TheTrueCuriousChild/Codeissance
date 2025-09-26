# app/agents/monitor_inventory.py
import time
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import crud
from app.routes.emergency import trigger_emergency_sos, EmergencyRequest

# Set the threshold for low inventory
LOW_INVENTORY_THRESHOLD = 5  # units

def monitor_inventory(interval: int = 60):
    """
    Continuously monitor hospital inventories and trigger emergency SOS if blood units are low.
    :param interval: Time in seconds between checks (default: 60s)
    """
    db: Session = SessionLocal()
    try:
        while True:
            all_hospitals = crud.get_all_users(db)  # get all users
            for user in all_hospitals:
                if not user.is_hospital or not user.hospital_profile:
                    continue
                hospital_id = user.hospital_profile.id
                inventories = crud.get_inventory_by_hospital(db, hospital_id)
                for inv in inventories:
                    if inv.units_available < LOW_INVENTORY_THRESHOLD:
                        # Trigger Emergency SOS
                        emergency_request = EmergencyRequest(
                            hospital_id=hospital_id,
                            blood_group=inv.blood_group,
                            units_needed=LOW_INVENTORY_THRESHOLD
                        )
                        # Directly call the function from emergency.py
                        response = trigger_emergency_sos(emergency_request, db=db)
                        print(f"[ALERT] Low inventory detected for Hospital {hospital_id}, Blood {inv.blood_group}")
                        print(response)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Inventory monitoring stopped.")
    finally:
        db.close()
