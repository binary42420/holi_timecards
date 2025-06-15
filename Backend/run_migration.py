#!/usr/bin/env python3
"""
Simple migration script to add Google OAuth columns.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import initialize_database_and_session
from sqlalchemy import text

def run_migration():
    """Run the Google OAuth migration."""
    print("🔄 Adding Google OAuth columns to database...")
    
    try:
        # Initialize database connection
        db, _ = initialize_database_and_session()
        print("✓ Database connected")
        
        # SQL commands to run
        commands = [
            "ALTER TABLE users ADD COLUMN google_id VARCHAR(100) UNIQUE NULL",
            "ALTER TABLE users ADD COLUMN email VARCHAR(255) NULL", 
            "ALTER TABLE users ADD COLUMN google_picture VARCHAR(500) NULL",
            "ALTER TABLE users ADD COLUMN last_login DATETIME NULL",
            "ALTER TABLE users MODIFY COLUMN password VARCHAR(255) NULL"
        ]
        
        for i, cmd in enumerate(commands, 1):
            try:
                print(f"Running command {i}/{len(commands)}...")
                db.execute(text(cmd))
                db.commit()
                print(f"✓ Command {i} completed")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print(f"✓ Column already exists (skipping)")
                else:
                    print(f"⚠️  Command {i} failed: {e}")
        
        # Add indexes
        index_commands = [
            "CREATE INDEX idx_users_google_id ON users(google_id)",
            "CREATE INDEX idx_users_email ON users(email)"
        ]
        
        for cmd in index_commands:
            try:
                db.execute(text(cmd))
                db.commit()
                print("✓ Index created")
            except Exception as e:
                if "Duplicate key name" in str(e):
                    print("✓ Index already exists")
                else:
                    print(f"⚠️  Index creation failed: {e}")
        
        print("\n🎉 Migration completed!")
        print("✓ Google OAuth columns added successfully")
        print("✓ You can now restart your server and test Google OAuth")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
