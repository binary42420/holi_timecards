#!/usr/bin/env python3
"""
Add soft delete columns to the users table.
This script adds is_deleted and deleted_at columns to support soft delete functionality.
"""

import sys
import os
from sqlalchemy import text

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import initialize_database_and_session

def add_soft_delete_columns():
    """Add soft delete columns to the users table"""
    print("🔧 Adding soft delete columns to users table...")
    
    try:
        # Initialize database connection
        db, _ = initialize_database_and_session()
        print("✓ Database connected")
        
        # Check if columns already exist
        def check_column_exists(column_name):
            try:
                result = db.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = 'users'
                    AND COLUMN_NAME = '{column_name}'
                """))
                return result.fetchone()[0] > 0
            except Exception as e:
                print(f"Error checking column {column_name}: {e}")
                return False
        
        # Add is_deleted column
        if check_column_exists('is_deleted'):
            print("✓ is_deleted column already exists")
        else:
            print("Adding is_deleted column...")
            db.execute(text("ALTER TABLE users ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT FALSE"))
            db.commit()
            print("✓ is_deleted column added")
        
        # Add deleted_at column
        if check_column_exists('deleted_at'):
            print("✓ deleted_at column already exists")
        else:
            print("Adding deleted_at column...")
            db.execute(text("ALTER TABLE users ADD COLUMN deleted_at DATETIME NULL"))
            db.commit()
            print("✓ deleted_at column added")
        
        # Verify the changes
        print("\n🔍 Verifying table structure...")
        result = db.execute(text("DESCRIBE users"))
        columns = result.fetchall()
        
        has_is_deleted = any('is_deleted' in str(col) for col in columns)
        has_deleted_at = any('deleted_at' in str(col) for col in columns)
        
        if has_is_deleted and has_deleted_at:
            print("✅ Soft delete columns successfully added!")
            print("   - is_deleted: BOOLEAN NOT NULL DEFAULT FALSE")
            print("   - deleted_at: DATETIME NULL")
        else:
            print("❌ Verification failed - columns may not have been added correctly")
            return False
        
        print("\n🎉 Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    print("🚀 Starting soft delete columns migration...")
    success = add_soft_delete_columns()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("The users table now supports soft delete functionality.")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above and try again.")
        sys.exit(1)
