#!/usr/bin/env python3
"""
Fix legacy fields in shifts table to be nullable.
"""

import sys
from sqlalchemy import text
from main import initialize_database_and_session

def fix_legacy_fields():
    """Make legacy shift fields nullable."""
    print("🔄 Making legacy shift fields nullable...")
    
    try:
        # Initialize database connection
        db, _ = initialize_database_and_session()
        print("✓ Database connected")
        
        # SQL commands to make legacy fields nullable
        commands = [
            "ALTER TABLE shifts MODIFY COLUMN shiftDate DATE NULL",
            "ALTER TABLE shifts MODIFY COLUMN shiftPart ENUM('morning','noon','evening') NULL"
        ]
        
        for i, cmd in enumerate(commands, 1):
            try:
                print(f"Running command {i}/{len(commands)}...")
                db.execute(text(cmd))
                db.commit()
                print(f"✓ Command {i} completed")
            except Exception as e:
                print(f"⚠️  Command {i} failed: {e}")
        
        print("\n🎉 Legacy fields fix completed!")
        return True
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    success = fix_legacy_fields()
    sys.exit(0 if success else 1)
