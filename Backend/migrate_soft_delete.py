#!/usr/bin/env python3
"""
Migration script to add soft delete columns to users table.
This script can be run in the production environment where database access is available.
"""

import os
import sys
from sqlalchemy import text
import logging

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import get_db_session

def migrate_soft_delete_columns():
    """Add soft delete columns to the users table"""
    logging.info("🔧 Starting soft delete columns migration...")
    
    try:
        with get_db_session() as session:
            logging.info("✓ Database session created")
            
            # Check if columns already exist
            def check_column_exists(column_name):
                try:
                    result = session.execute(text(f"""
                        SELECT COUNT(*) 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_SCHEMA = DATABASE()
                        AND TABLE_NAME = 'users'
                        AND COLUMN_NAME = '{column_name}'
                    """))
                    return result.fetchone()[0] > 0
                except Exception as e:
                    logging.error(f"Error checking column {column_name}: {e}")
                    return False
            
            # Add is_deleted column
            if check_column_exists('is_deleted'):
                logging.info("✓ is_deleted column already exists")
            else:
                logging.info("Adding is_deleted column...")
                session.execute(text("ALTER TABLE users ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT FALSE"))
                session.commit()
                logging.info("✓ is_deleted column added")
            
            # Add deleted_at column
            if check_column_exists('deleted_at'):
                logging.info("✓ deleted_at column already exists")
            else:
                logging.info("Adding deleted_at column...")
                session.execute(text("ALTER TABLE users ADD COLUMN deleted_at DATETIME NULL"))
                session.commit()
                logging.info("✓ deleted_at column added")
            
            # Verify the changes
            logging.info("🔍 Verifying table structure...")
            result = session.execute(text("DESCRIBE users"))
            columns = result.fetchall()
            
            has_is_deleted = any('is_deleted' in str(col) for col in columns)
            has_deleted_at = any('deleted_at' in str(col) for col in columns)
            
            if has_is_deleted and has_deleted_at:
                logging.info("✅ Soft delete columns successfully added!")
                logging.info("   - is_deleted: BOOLEAN NOT NULL DEFAULT FALSE")
                logging.info("   - deleted_at: DATETIME NULL")
                return True
            else:
                logging.error("❌ Verification failed - columns may not have been added correctly")
                return False
        
    except Exception as e:
        logging.error(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = migrate_soft_delete_columns()
    
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
        sys.exit(1)
