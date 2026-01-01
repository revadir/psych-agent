#!/usr/bin/env python3
"""
Test database functionality.
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.db.session import SessionLocal
from app.models import User, Allowlist

def test_database():
    """Test basic database operations."""
    db = SessionLocal()
    
    try:
        # Test creating a user
        test_user = User(email="test@example.com", is_admin=False)
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"✅ Created user: {test_user.email} (ID: {test_user.id})")
        
        # Test creating allowlist entry
        allowlist_entry = Allowlist(email="admin@example.com", is_admin=True)
        db.add(allowlist_entry)
        db.commit()
        db.refresh(allowlist_entry)
        
        print(f"✅ Created allowlist entry: {allowlist_entry.email} (ID: {allowlist_entry.id})")
        
        # Test querying
        users = db.query(User).all()
        allowlist = db.query(Allowlist).all()
        
        print(f"✅ Found {len(users)} users and {len(allowlist)} allowlist entries")
        
        # Cleanup
        db.delete(test_user)
        db.delete(allowlist_entry)
        db.commit()
        
        print("✅ Database test completed successfully!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_database()
