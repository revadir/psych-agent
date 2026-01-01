#!/usr/bin/env python3
"""
Initialize allowlist with admin user.
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.db.session import SessionLocal
from app.models import Allowlist
from app.core.config import settings

def main():
    """Add admin user to allowlist."""
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(Allowlist).filter(Allowlist.email == settings.admin_email).first()
        if existing_admin:
            print(f"✅ Admin user {settings.admin_email} already exists in allowlist")
            return
        
        # Create admin user
        admin_user = Allowlist(email=settings.admin_email, is_admin=True)
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"✅ Added admin user {settings.admin_email} to allowlist")
        
    except Exception as e:
        print(f"❌ Error adding admin user: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
