"""
Feedback API endpoints for collecting user feedback on AI responses.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.db.session import get_db
from app.core.auth import get_current_user
from app.models.database import User, Feedback, Message, ChatSession

router = APIRouter()


class FeedbackCreate(BaseModel):
    message_id: int
    rating: Optional[str] = None  # 'up' or 'down'
    text_feedback: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    session_id: int
    message_id: int
    question: str
    response: str
    rating: Optional[str]
    text_feedback: Optional[str]
    model_used: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit feedback for an AI response."""
    
    # Get the message and validate it belongs to user
    message = db.query(Message).filter(Message.id == feedback_data.message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Verify user owns the session
    session = db.query(ChatSession).filter(
        ChatSession.id == message.session_id,
        ChatSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to provide feedback for this message"
        )
    
    # Get the user question (previous message)
    user_message = db.query(Message).filter(
        Message.session_id == message.session_id,
        Message.role == "user",
        Message.id < message.id
    ).order_by(Message.id.desc()).first()
    
    question = user_message.content if user_message else "Unknown question"
    
    # Check if feedback already exists
    existing_feedback = db.query(Feedback).filter(
        Feedback.message_id == feedback_data.message_id,
        Feedback.user_id == current_user.id
    ).first()
    
    if existing_feedback:
        # Update existing feedback
        existing_feedback.rating = feedback_data.rating
        existing_feedback.text_feedback = feedback_data.text_feedback
        db.commit()
        db.refresh(existing_feedback)
        return existing_feedback
    
    # Create new feedback
    feedback = Feedback(
        session_id=message.session_id,
        message_id=feedback_data.message_id,
        user_id=current_user.id,
        question=question,
        response=message.content,
        rating=feedback_data.rating,
        text_feedback=feedback_data.text_feedback,
        model_used="llama3.2:1b"  # Could be extracted from message metadata
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    return feedback


@router.get("/feedback", response_model=List[FeedbackResponse])
async def get_user_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all feedback submitted by the current user."""
    
    feedback_list = db.query(Feedback).filter(
        Feedback.user_id == current_user.id
    ).order_by(Feedback.created_at.desc()).all()
    
    return feedback_list


@router.get("/admin/feedback", response_model=List[FeedbackResponse])
async def get_all_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all feedback (admin only)."""
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    feedback_list = db.query(Feedback).order_by(Feedback.created_at.desc()).all()
    
    return feedback_list