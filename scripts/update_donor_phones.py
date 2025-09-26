import os
from dotenv import load_dotenv
from sqlalchemy import text
from app.database import SessionLocal
import logging

# Load env vars
load_dotenv()
TEST_PERSONAL_NUMBER = os.getenv("TEST_PERSONAL_NUMBER")

if not TEST_PERSONAL_NUMBER:
    raise ValueError("TEST_PERSONAL_NUMBER is not set in .env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("update_donor_phones")


def update_user_phones():
    db = SessionLocal()
    try:
        # Use raw SQL instead of ORM (ignores schema mismatch)
        result = db.execute(text("SELECT id, phone FROM users")).fetchall()

        for row in result:
            user_id, old_phone = row
            db.execute(
                text("UPDATE users SET phone = :phone WHERE id = :id"),
                {"phone": TEST_PERSONAL_NUMBER, "id": user_id},
            )
            logger.info(f"Updated user {user_id} phone from {old_phone} to {TEST_PERSONAL_NUMBER}")

        db.commit()
        logger.info("✅ All user phone numbers updated successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    update_user_phones()
