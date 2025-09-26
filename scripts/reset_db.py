# scripts/reset_db.py
from app.database import Base, engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reset_db")

def reset_database():
    logger.info("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("All tables dropped.")

    logger.info("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("All tables created successfully!")

if __name__ == "__main__":
    reset_database()
