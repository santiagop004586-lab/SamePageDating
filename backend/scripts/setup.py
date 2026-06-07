#!/usr/bin/env python3
"""
Quick setup script for SamePageDating
Initializes database and seeds compatibility questions
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.init_dating_db import init_db, seed_compatibility_questions


def main():
    print("=" * 60)
    print("SamePageDating - Database Setup")
    print("=" * 60)
    print()
    
    try:
        # Initialize database
        print("Step 1: Creating database tables...")
        init_db()
        print("✓ Database tables created")
        print()
        
        # Seed compatibility questions
        print("Step 2: Seeding compatibility questions...")
        seed_compatibility_questions()
        print("✓ Compatibility questions seeded")
        print()
        
        print("=" * 60)
        print("✓ Setup complete! Database is ready.")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Start the backend: docker-compose up -d")
        print("2. Start the frontend: cd frontend && npm start")
        print("3. Navigate to http://localhost:3000")
        print()
        
    except Exception as e:
        print(f"✗ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
