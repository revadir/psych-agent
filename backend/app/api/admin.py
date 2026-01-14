"""
Admin API endpoints for feedback analytics and management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db.session import get_db
from app.core.auth import get_current_user
from app.models.database import User, Feedback, Message, ChatSession

router = APIRouter()


class FeedbackStats(BaseModel):
    total_feedback: int
    positive_feedback: int
    negative_feedback: int
    text_feedback_count: int
    avg_rating: Optional[float]
    feedback_by_day: List[dict]


class FeedbackDetail(BaseModel):
    id: int
    session_id: int
    message_id: int
    user_email: str
    question: str
    response: str
    rating: Optional[str]
    text_feedback: Optional[str]
    model_used: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


@router.get("/admin/feedback/stats", response_model=FeedbackStats)
async def get_feedback_stats(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive feedback statistics."""
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Date range
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Basic stats
    total_feedback = db.query(Feedback).filter(Feedback.created_at >= start_date).count()
    positive_feedback = db.query(Feedback).filter(
        Feedback.created_at >= start_date,
        Feedback.rating == 'up'
    ).count()
    negative_feedback = db.query(Feedback).filter(
        Feedback.created_at >= start_date,
        Feedback.rating == 'down'
    ).count()
    text_feedback_count = db.query(Feedback).filter(
        Feedback.created_at >= start_date,
        Feedback.text_feedback.isnot(None),
        Feedback.text_feedback != ''
    ).count()
    
    # Average rating (1 for up, 0 for down)
    avg_rating = None
    if positive_feedback + negative_feedback > 0:
        avg_rating = positive_feedback / (positive_feedback + negative_feedback)
    
    # Feedback by day
    from sqlalchemy import case
    feedback_by_day = db.query(
        func.date(Feedback.created_at).label('date'),
        func.count(Feedback.id).label('count'),
        func.sum(case((Feedback.rating == 'up', 1), else_=0)).label('positive'),
        func.sum(case((Feedback.rating == 'down', 1), else_=0)).label('negative')
    ).filter(
        Feedback.created_at >= start_date
    ).group_by(
        func.date(Feedback.created_at)
    ).order_by(
        func.date(Feedback.created_at)
    ).all()
    
    feedback_by_day_list = [
        {
            'date': str(row.date),
            'total': row.count,
            'positive': row.positive,
            'negative': row.negative
        }
        for row in feedback_by_day
    ]
    
    return FeedbackStats(
        total_feedback=total_feedback,
        positive_feedback=positive_feedback,
        negative_feedback=negative_feedback,
        text_feedback_count=text_feedback_count,
        avg_rating=avg_rating,
        feedback_by_day=feedback_by_day_list
    )


@router.get("/admin/feedback/details", response_model=List[FeedbackDetail])
async def get_feedback_details(
    rating: Optional[str] = Query(None, description="Filter by rating: up, down"),
    has_text: Optional[bool] = Query(None, description="Filter by text feedback presence"),
    limit: int = Query(50, description="Number of records to return"),
    offset: int = Query(0, description="Number of records to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed feedback records with filtering."""
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    query = db.query(Feedback).join(User, Feedback.user_id == User.id)
    
    # Apply filters
    if rating:
        query = query.filter(Feedback.rating == rating)
    
    if has_text is not None:
        if has_text:
            query = query.filter(
                Feedback.text_feedback.isnot(None),
                Feedback.text_feedback != ''
            )
        else:
            query = query.filter(
                (Feedback.text_feedback.is_(None)) | (Feedback.text_feedback == '')
            )
    
    # Get results with user email
    results = query.order_by(desc(Feedback.created_at)).offset(offset).limit(limit).all()
    
    # Format response
    feedback_details = []
    for feedback in results:
        user = db.query(User).filter(User.id == feedback.user_id).first()
        feedback_details.append(FeedbackDetail(
            id=feedback.id,
            session_id=feedback.session_id,
            message_id=feedback.message_id,
            user_email=user.email if user else "Unknown",
            question=feedback.question,
            response=feedback.response[:500] + "..." if len(feedback.response) > 500 else feedback.response,
            rating=feedback.rating,
            text_feedback=feedback.text_feedback,
            model_used=feedback.model_used,
            created_at=feedback.created_at.isoformat()
        ))
    
    return feedback_details


@router.get("/admin/feedback/export")
async def export_feedback_csv(
    days: int = Query(30, description="Number of days to export"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export feedback data as CSV."""
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    from fastapi.responses import StreamingResponse
    import csv
    import io
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    feedback_data = db.query(Feedback).join(User, Feedback.user_id == User.id).filter(
        Feedback.created_at >= start_date
    ).order_by(desc(Feedback.created_at)).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        'ID', 'Date', 'User Email', 'Rating', 'Has Text Feedback', 
        'Question', 'Response Preview', 'Model Used'
    ])
    
    # Data
    for feedback in feedback_data:
        user = db.query(User).filter(User.id == feedback.user_id).first()
        writer.writerow([
            feedback.id,
            feedback.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            user.email if user else "Unknown",
            feedback.rating or "None",
            "Yes" if feedback.text_feedback else "No",
            feedback.question[:100] + "..." if len(feedback.question) > 100 else feedback.question,
            feedback.response[:100] + "..." if len(feedback.response) > 100 else feedback.response,
            feedback.model_used or "Unknown"
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=feedback_export_{datetime.now().strftime('%Y%m%d')}.csv"}
    )