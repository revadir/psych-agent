"""
Database session management and initialization.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.models.database import Base
import os


def get_database_url():
    """Get absolute database URL."""
    import os
    
    # Use production database URL if available
    prod_url = os.getenv("DATABASE_URL")
    if prod_url:
        return prod_url
    
    # Fallback to local SQLite
    if settings.database_url.startswith("sqlite:///./"):
        # Convert relative path to absolute
        rel_path = settings.database_url.replace("sqlite:///./", "")
        abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", rel_path))
        return f"sqlite:///{abs_path}"
    return settings.database_url


# Create database engine
engine = create_engine(
    get_database_url(),
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all database tables."""
    # Ensure data directory exists for SQLite
    db_url = get_database_url()
    if "sqlite" in db_url:
        db_path = db_url.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
