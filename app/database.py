# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Load database URL from environment variable, fallback to SQLite for dev
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./donation.db")

# SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=True  # set to True to see SQL queries in terminal
)

# Session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    """
    FastAPI dependency to get a database session.
    Usage in endpoints:
        def endpoint(db: Session = Depends(get_db))
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
if __name__ == "__main__":
    from app import models  # import models so SQLAlchemy knows about them
    Base.metadata.create_all(bind=engine)