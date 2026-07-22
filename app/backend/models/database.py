import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration string
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:secret@localhost:5432/predictive_maintenance")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency injection wrapper providing an isolated session lifetime per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()