# scripts/test_notification.py
import logging
from app.database import SessionLocal
from app import models
from app.utils.distance import haversine_distance
from app.utils.notifications import format_whatsapp_message, send_whatsapp
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_notification")

def test_send():
    db = SessionLocal()

    try:
        # Pick a hospital (City Hospital)
        hospital = db.query(models.HospitalProfile).join(models.User).filter(
            models.User.name == "City Hospital"
        ).first()

        if not hospital:
            logger.warning("Hospital not found")
            return

        # Get all donors
        donors = db.query(models.DonorProfile).all()

        # Find nearest donor
        nearest_donor = None
        nearest_distance = float("inf")

        for donor in donors:
            if donor.latitude is None or donor.longitude is None:
                continue

            dist = haversine_distance(
                hospital.latitude, hospital.longitude,
                donor.latitude, donor.longitude
            )
            if dist < nearest_distance:
                nearest_distance = dist
                nearest_donor = donor

        if not nearest_donor:
            logger.warning("No donors with valid location found")
            return

        # Prepare message with clickable map link
        message = format_whatsapp_message(
            hospital_name=hospital.user.name,
            blood_group="O+",  # or dynamically set based on hospital request
            units=2,           # example units
            latitude=hospital.latitude,
            longitude=hospital.longitude
        )

        # Send WhatsApp message to nearest donor
        donor_user = nearest_donor.user
        if not donor_user.phone:
            logger.warning(f"Donor {donor_user.name} has no phone number")
            return

        success = send_whatsapp(donor_user.phone, message)
        if success:
            logger.info(f"✅ WhatsApp message sent to {donor_user.name} ({donor_user.phone})")
        else:
            logger.error(f"❌ Failed to send message to {donor_user.name} ({donor_user.phone})")

    except Exception as e:
        logger.error(f"Error in test_send: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_send()
