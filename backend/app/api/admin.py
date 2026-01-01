"""
Admin API endpoints for allowlist management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.core.auth import get_admin_user
from app.models import User, Allowlist
from app.models.schemas import AllowlistRequest, AllowlistResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/allowlist", response_model=AllowlistResponse)
async def add_to_allowlist(
    request: AllowlistRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Add user to allowlist."""
    # Check if already exists
    existing = db.query(Allowlist).filter(Allowlist.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already in allowlist"
        )
    
    # Add to allowlist
    allowlist_entry = Allowlist(email=request.email, is_admin=request.is_admin)
    db.add(allowlist_entry)
    db.commit()
    db.refresh(allowlist_entry)
    
    return allowlist_entry


@router.delete("/allowlist/{email}")
async def remove_from_allowlist(
    email: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Remove user from allowlist."""
    allowlist_entry = db.query(Allowlist).filter(Allowlist.email == email).first()
    if not allowlist_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found in allowlist"
        )
    
    db.delete(allowlist_entry)
    db.commit()
    
    return {"message": f"Removed {email} from allowlist"}


@router.get("/allowlist", response_model=List[AllowlistResponse])
async def get_allowlist(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Get all allowlist entries."""
    return db.query(Allowlist).all()
