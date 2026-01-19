"""
Scribe session service for managing clinical notes.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import ScribeSession, User
from datetime import datetime


class ScribeSessionService:
    """Service for handling scribe session operations."""

    @staticmethod
    def create_session(
        db: Session, 
        user_id: int, 
        patient_name: str,
        patient_id: str,
        note_template: str,
        duration: str,
        content: Dict[str, str]
    ) -> ScribeSession:
        """Create a new scribe session."""
        session = ScribeSession(
            user_id=user_id,
            patient_id=patient_id,
            patient_name=patient_name,
            note_template=note_template,
            duration=duration,
            chief_complaint=content.get('chief_complaint', ''),
            history_present_illness=content.get('history_present_illness', ''),
            review_systems=content.get('review_systems', ''),
            assessment_plan=content.get('assessment_plan', ''),
            followup_disposition=content.get('followup_disposition', '')
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_user_sessions(db: Session, user_id: int) -> List[ScribeSession]:
        """Get all scribe sessions for a user, ordered by most recent."""
        return db.query(ScribeSession).filter(
            ScribeSession.user_id == user_id
        ).order_by(desc(ScribeSession.created_at)).all()

    @staticmethod
    def get_session(db: Session, session_id: int, user_id: int) -> Optional[ScribeSession]:
        """Get a specific scribe session by ID and user."""
        return db.query(ScribeSession).filter(
            ScribeSession.id == session_id,
            ScribeSession.user_id == user_id
        ).first()

    @staticmethod
    def delete_session(db: Session, session_id: int, user_id: int) -> bool:
        """Delete a scribe session."""
        session = db.query(ScribeSession).filter(
            ScribeSession.id == session_id,
            ScribeSession.user_id == user_id
        ).first()
        
        if session:
            db.delete(session)
            db.commit()
            return True
        return False

    @staticmethod
    def update_session(
        db: Session, 
        session_id: int, 
        user_id: int, 
        content: Dict[str, str]
    ) -> Optional[ScribeSession]:
        """Update a scribe session's content."""
        session = db.query(ScribeSession).filter(
            ScribeSession.id == session_id,
            ScribeSession.user_id == user_id
        ).first()
        
        if session:
            session.chief_complaint = content.get('chief_complaint', session.chief_complaint)
            session.history_present_illness = content.get('history_present_illness', session.history_present_illness)
            session.review_systems = content.get('review_systems', session.review_systems)
            session.assessment_plan = content.get('assessment_plan', session.assessment_plan)
            session.followup_disposition = content.get('followup_disposition', session.followup_disposition)
            session.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(session)
            return session
        return None
