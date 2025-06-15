#!/usr/bin/env python3
"""
Migration script to add soft delete columns to jobs table.
This script can be run in the production environment where database access is available.
"""

import os
import sys
from sqlalchemy import text
import logging

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import get_db_session

def migrate_jobs_soft_delete_columns():
    """Add soft delete columns to the jobs table"""
    logging.info("🔧 Starting jobs soft delete columns migration...")
    
    try:
        with get_db_session() as session:
            logging.info("✓ Database session created")
            
            # Check if columns already exist for a given table
            def check_column_exists(table_name, column_name):
                try:
                    result = session.execute(text(f"""
                        SELECT COUNT(*) 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_SCHEMA = DATABASE()
                        AND TABLE_NAME = '{table_name}'
                        AND COLUMN_NAME = '{column_name}'
                    """))
                    return result.fetchone()[0] > 0
                except Exception as e:
                    logging.error(f"Error checking column {column_name} in {table_name}: {e}")
                    return False
            
            # Tables to update
            tables_to_update = ['jobs']
            
            for table_name in tables_to_update:
                logging.info(f"🔧 Processing table: {table_name}")
                
                # Add is_deleted column
                if check_column_exists(table_name, 'is_deleted'):
                    logging.info(f"✓ {table_name}.is_deleted column already exists")
                else:
                    logging.info(f"Adding is_deleted column to {table_name}...")
                    session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT FALSE"))
                    session.commit()
                    logging.info(f"✓ {table_name}.is_deleted column added")
                
                # Add deleted_at column
                if check_column_exists(table_name, 'deleted_at'):
                    logging.info(f"✓ {table_name}.deleted_at column already exists")
                else:
                    logging.info(f"Adding deleted_at column to {table_name}...")
                    session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN deleted_at DATETIME NULL"))
                    session.commit()
                    logging.info(f"✓ {table_name}.deleted_at column added")
            
            # Verify the changes
            logging.info("🔍 Verifying table structures...")
            all_verified = True
            
            for table_name in tables_to_update:
                result = session.execute(text(f"DESCRIBE {table_name}"))
                columns = result.fetchall()
                
                has_is_deleted = any('is_deleted' in str(col) for col in columns)
                has_deleted_at = any('deleted_at' in str(col) for col in columns)
                
                if has_is_deleted and has_deleted_at:
                    logging.info(f"✅ {table_name} soft delete columns verified!")
                else:
                    logging.error(f"❌ {table_name} verification failed")
                    all_verified = False
            
            if all_verified:
                logging.info("✅ All jobs soft delete columns successfully added!")
                logging.info("   - is_deleted: BOOLEAN NOT NULL DEFAULT FALSE")
                logging.info("   - deleted_at: DATETIME NULL")
                return True
            else:
                logging.error("❌ Some verifications failed")
                return False
        
    except Exception as e:
        logging.error(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = migrate_jobs_soft_delete_columns()
    
    if success:
        print("✅ Jobs migration completed successfully!")
    else:
        print("❌ Jobs migration failed!")
        sys.exit(1)
