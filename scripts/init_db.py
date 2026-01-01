#!/usr/bin/env python3
"""
Database initialization script.
Creates all tables and sets up the database schema.
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.db.session import create_tables
from app.core.config import settings

def main():
    """Initialize the database."""
    print(f"Initializing database at: {settings.database_url}")
    
    try:
        create_tables()
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
