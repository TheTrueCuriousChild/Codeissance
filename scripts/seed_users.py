# scripts/seed_users.py
import logging
from app.database import SessionLocal, engine, Base
from app import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_users")

# Recreate tables if not exist
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()

    try:
        # ------------------------
        # Hospitals
        # ------------------------
        hospital1_user = models.User(
            name="City Hospital",
            phone="+911111111111",
            email="cityhospital@example.com",
            is_hospital=True,
            role="hospital",
        )
        hospital1_profile = models.HospitalProfile(
            user=hospital1_user,
            latitude=28.6139,   # Delhi
            longitude=77.2090,
            address="Connaught Place, Delhi",
            verified=True,
        )

        hospital2_user = models.User(
            name="Metro Care",
            phone="+922222222222",
            email="metrocare@example.com",
            is_hospital=True,
            role="hospital",
        )
        hospital2_profile = models.HospitalProfile(
            user=hospital2_user,
            latitude=19.0760,   # Mumbai
            longitude=72.8777,
            address="Bandra, Mumbai",
            verified=True,
        )

        # ------------------------
        # Donors (all mapped to your WhatsApp number)
        # ------------------------
        donors = []
        donor_data = [
            ("Alice", "A+", 28.7041, 77.1025),   # Delhi
            ("Bob", "B+", 19.0760, 72.8777),     # Mumbai
            ("Charlie", "O-", 13.0827, 80.2707)  # Chennai
        ]

        for name, blood_group, lat, lon in donor_data:
            donor_user = models.User(
                name=name,
                phone="+919930709904",  # your sandbox number
                email=f"{name.lower()}@example.com",
                is_donor=True,
                role="donor",
            )
            donor_profile = models.DonorProfile(
                user=donor_user,
                blood_group=blood_group,
                latitude=lat,
                longitude=lon,
                availability=True,
                consent_emergency=True,
            )
            donors.append(donor_profile)

        # ------------------------
        # Commit all
        # ------------------------
        db.add_all([hospital1_user, hospital2_user] + [d.user for d in donors])
        db.commit()

        logger.info("✅ Seed data inserted successfully!")

    except Exception as e:
        logger.error(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
