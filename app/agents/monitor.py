# app/agents/monitor.py

import logging
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import SessionLocal
from time import sleep
from threading import Thread
from app.agents import router_ai
from app.utils.notifications import send_whatsapp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("monitor_agent")

CRITICAL_THRESHOLD = 5       # Units below which auto-request is triggered
CHECK_INTERVAL = 60          # Seconds between checks
AUTO_REQUEST_MULTIPLIER = 2  # Request 2x threshold

def monitor_inventory():
    db: Session = SessionLocal()
    try:
        logger.info("Inventory monitoring agent running...")
        while True:
            try:
                inventories = crud.get_all_inventories(db)
                for inv in inventories:
                    if inv.units_available < CRITICAL_THRESHOLD:
                        logger.warning(
                            f"Low inventory: Hospital {inv.hospital_id}, Blood {inv.blood_group}, Units {inv.units_available}"
                        )

                        # Skip if pending request exists
                        existing_requests = db.query(crud.models.Request).filter(
                            crud.models.Request.hospital_id == inv.hospital_id,
                            crud.models.Request.blood_group == inv.blood_group,
                            crud.models.Request.fulfilled == False
                        ).all()

                        if existing_requests:
                            continue

                        # Create high-priority request
                        request_data = schemas.RequestCreate(
                            hospital_id=inv.hospital_id,
                            blood_group=inv.blood_group,
                            units_needed=CRITICAL_THRESHOLD * AUTO_REQUEST_MULTIPLIER,
                            urgency="high"
                        )
                        new_request = crud.create_request(db, request_data)
                        logger.info(
                            f"Auto-created request {new_request.id}: Hospital {inv.hospital_id}, Blood {inv.blood_group}, Units needed: {request_data.units_needed}"
                        )

                        # Fetch hospital info
                        hospital = crud.get_hospital_by_id(db, inv.hospital_id)
                        if not hospital:
                            continue

                        # Notify nearest donors
                        donors = router_ai.router_agent.get_nearest_donors(
                            blood_group=inv.blood_group,
                            hospital_lat=hospital.latitude,
                            hospital_lon=hospital.longitude,
                            db=db
                        )

                        notified_count = 0
                        for donor in donors:
                            phone_number = getattr(donor.user, "phone", None)
                            if phone_number:
                                msg = f"Urgent! Hospital {hospital.user.name} needs {request_data.units_needed} units of {inv.blood_group} blood. Please respond immediately."
                                send_whatsapp(phone_number, msg)
                                # Mark donor as notified
                                crud.mark_donor_notified(db, donor.id, new_request.id)
                                notified_count += 1
                            if notified_count >= request_data.units_needed:
                                break

            except Exception as e:
                logger.error(f"Error during inventory monitoring loop: {e}")
            sleep(CHECK_INTERVAL)
    finally:
        db.close()
        logger.info("Inventory monitoring agent stopped.")

def start_monitoring():
    thread = Thread(target=monitor_inventory, daemon=True)
    thread.start()
    logger.info("Inventory monitoring agent started.")
