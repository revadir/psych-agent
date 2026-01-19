"""
Scribe session model for storing clinical notes.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base
from datetime import datetime


class ScribeSession(Base):
    """Model for scribe sessions (clinical notes)."""
    
    __tablename__ = "scribe_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(String(50), nullable=False)
    patient_name = Column(String(255), nullable=False)
    note_template = Column(String(100), nullable=False)
    duration = Column(String(50), nullable=True)
    
    # Clinical content
    chief_complaint = Column(Text, nullable=True)
    history_present_illness = Column(Text, nullable=True)
    review_systems = Column(Text, nullable=True)
    assessment_plan = Column(Text, nullable=True)
    followup_disposition = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="scribe_sessions")
