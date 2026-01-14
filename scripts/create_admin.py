"""
One-time script to create admin user in production.
Run this once after deployment.
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.db.session import SessionLocal
from app.services.auth_service import AuthService

def create_admin():
    db = SessionLocal()
    try:
        email = "revadigar@gmail.com"
        
        # Check if user already exists
        existing = AuthService.get_user_by_email(db, email)
        if existing:
            print(f"User {email} already exists")
            return
        
        # Add to allowlist as admin
        user = AuthService.add_user_to_allowlist(db, email, is_admin=True)
        print(f"✅ Admin user created: {email}")
        print(f"   Default password: admin123")
        print(f"   Please change password after first login")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
