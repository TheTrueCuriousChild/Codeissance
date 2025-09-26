# scripts/test_notification.py
import logging
from datetime import datetime
from app.database import SessionLocal
from app import models
from app.utils.distance import haversine_distance
from app.utils.notifications import format_whatsapp_message, send_whatsapp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_notification")


def test_send():
    db = SessionLocal()
    try:
        # Pick the first hospital with valid location
        hospital = db.query(models.HospitalProfile).filter(
            models.HospitalProfile.latitude.isnot(None),
            models.HospitalProfile.longitude.isnot(None)
        ).first()

        if not hospital:
            logger.warning("⚠️ No hospital with valid location found")
            return

        # Fetch all donors with valid location
        donors = db.query(models.DonorProfile).filter(
            models.DonorProfile.latitude.isnot(None),
            models.DonorProfile.longitude.isnot(None)
        ).all()

        if not donors:
            logger.warning("⚠️ No donors with valid location found")
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
        if not donor_user.phone:
            logger.warning(f"⚠️ Donor {donor_user.name} has no phone number")
            return

        # 🔑 Pick request details dynamically (first pending request from that hospital)
        request = (
            db.query(models.Request)
            .filter(
                models.Request.hospital_id == hospital.id,
                models.Request.fulfilled == False
            )
            .order_by(models.Request.created_at.desc())
            .first()
        )

        if not request:
            logger.warning(f"⚠️ No pending request found for hospital {hospital.user.name}")
            return

        # Prepare WhatsApp message dynamically
        message = format_whatsapp_message(
            hospital_name=hospital.user.name,
            blood_group=request.blood_group or "N/A",
            units=request.units_needed,
            donor_lat=nearest_donor.latitude,
            donor_lon=nearest_donor.longitude,
            hospital_lat=hospital.latitude,
            hospital_lon=hospital.longitude
        )

        # Send WhatsApp message
        success = send_whatsapp(donor_user.phone, message)
        if success:
            logger.info(f"✅ WhatsApp message sent to {donor_user.name} ({donor_user.phone})")
        else:
            logger.error(f"❌ Failed to send message to {donor_user.name} ({donor_user.phone})")

    except Exception as e:
        logger.error(f"🔥 Error in test_send: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    test_send()
