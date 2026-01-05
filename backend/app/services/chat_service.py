"""
Chat service for managing sessions and messages.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import ChatSession, Message, User
from datetime import datetime


class ChatService:
    """Service for handling chat session operations."""

    @staticmethod
    def create_session(db: Session, user_id: int, title: Optional[str] = None) -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(
            user_id=user_id,
            title=title or f"Chat Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_user_sessions(db: Session, user_id: int) -> List[ChatSession]:
        """Get all sessions for a user, ordered by most recent."""
        return db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(desc(ChatSession.updated_at)).all()

    @staticmethod
    def get_session(db: Session, session_id: int, user_id: int) -> Optional[ChatSession]:
        """Get a specific session if it belongs to the user."""
        return db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()

    @staticmethod
    def delete_session(db: Session, session_id: int, user_id: int) -> bool:
        """Delete a session if it belongs to the user."""
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()
        
        if not session:
            return False
        
        db.delete(session)
        db.commit()
        return True

    @staticmethod
    def add_message(db: Session, session_id: int, role: str, content: str, citations: list = None) -> Message:
        """Add a message to a session."""
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
            citations=citations
        )
        db.add(message)
        
        # Update session timestamp
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            session.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_session_messages(db: Session, session_id: int) -> List[Message]:
        """Get all messages for a session, ordered chronologically."""
        return db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.created_at).all()
