#!/usr/bin/env python3
"""
Test chat service functionality.
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.db.session import SessionLocal
from app.models import User
from app.services.chat_service import ChatService

def test_chat_service():
    """Test chat service operations."""
    db = SessionLocal()
    
    try:
        # Create test user
        test_user = User(email="test@example.com", is_admin=False)
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"✅ Created test user: {test_user.email} (ID: {test_user.id})")
        
        # Test session creation
        session = ChatService.create_session(db, test_user.id, "Test Session")
        print(f"✅ Created session: {session.title} (ID: {session.id})")
        
        # Test adding messages
        user_msg = ChatService.add_message(db, session.id, "user", "Hello, I need help with diagnosis")
        print(f"✅ Added user message (ID: {user_msg.id})")
        
        assistant_msg = ChatService.add_message(db, session.id, "assistant", "I can help you with psychiatric diagnosis support.")
        print(f"✅ Added assistant message (ID: {assistant_msg.id})")
        
        # Test retrieving messages
        messages = ChatService.get_session_messages(db, session.id)
        print(f"✅ Retrieved {len(messages)} messages")
        
        # Test retrieving user sessions
        user_sessions = ChatService.get_user_sessions(db, test_user.id)
        print(f"✅ Retrieved {len(user_sessions)} sessions for user")
        
        # Test session deletion
        deleted = ChatService.delete_session(db, session.id, test_user.id)
        print(f"✅ Session deletion: {deleted}")
        
        # Cleanup
        db.delete(test_user)
        db.commit()
        
        print("✅ Chat service test completed successfully!")
        
    except Exception as e:
        print(f"❌ Chat service test failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_chat_service()
