#!/usr/bin/env python3
"""
Migration script to add soft delete columns to all remaining tables.
This script adds is_deleted and deleted_at columns to client_companies and shifts tables.
"""

import os
import sys
from sqlalchemy import text
import logging

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import get_db_session

def migrate_all_soft_delete_columns():
    """Add soft delete columns to all remaining tables that need them"""
    logging.info("🔧 Starting comprehensive soft delete columns migration...")
    
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
            
            # Tables that need soft delete columns (based on models.py)
            tables_to_update = [
                'users',           # Already done, but check anyway
                'client_companies', # Needs migration
                'jobs',            # Already done, but check anyway
                'shifts'           # Needs migration
            ]
            
            migration_results = {}
            
            for table_name in tables_to_update:
                logging.info(f"🔧 Processing table: {table_name}")
                table_results = {'is_deleted': False, 'deleted_at': False}
                
                # Add is_deleted column
                if check_column_exists(table_name, 'is_deleted'):
                    logging.info(f"✓ {table_name}.is_deleted column already exists")
                    table_results['is_deleted'] = True
                else:
                    try:
                        logging.info(f"Adding is_deleted column to {table_name}...")
                        session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT FALSE"))
                        session.commit()
                        logging.info(f"✓ {table_name}.is_deleted column added")
                        table_results['is_deleted'] = True
                    except Exception as e:
                        logging.error(f"❌ Failed to add is_deleted to {table_name}: {e}")
                
                # Add deleted_at column
                if check_column_exists(table_name, 'deleted_at'):
                    logging.info(f"✓ {table_name}.deleted_at column already exists")
                    table_results['deleted_at'] = True
                else:
                    try:
                        logging.info(f"Adding deleted_at column to {table_name}...")
                        session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN deleted_at DATETIME NULL"))
                        session.commit()
                        logging.info(f"✓ {table_name}.deleted_at column added")
                        table_results['deleted_at'] = True
                    except Exception as e:
                        logging.error(f"❌ Failed to add deleted_at to {table_name}: {e}")
                
                migration_results[table_name] = table_results
            
            # Verify the changes
            logging.info("🔍 Verifying all table structures...")
            all_verified = True
            
            for table_name in tables_to_update:
                try:
                    result = session.execute(text(f"DESCRIBE {table_name}"))
                    columns = result.fetchall()
                    
                    has_is_deleted = any('is_deleted' in str(col) for col in columns)
                    has_deleted_at = any('deleted_at' in str(col) for col in columns)
                    
                    if has_is_deleted and has_deleted_at:
                        logging.info(f"✅ {table_name} soft delete columns verified!")
                    else:
                        logging.error(f"❌ {table_name} verification failed - missing columns")
                        all_verified = False
                except Exception as e:
                    logging.error(f"❌ Error verifying {table_name}: {e}")
                    all_verified = False
            
            # Summary
            if all_verified:
                logging.info("✅ All soft delete columns migration completed successfully!")
                logging.info("📋 Migration Summary:")
                for table_name, results in migration_results.items():
                    status = "✅" if results['is_deleted'] and results['deleted_at'] else "❌"
                    logging.info(f"   {status} {table_name}: is_deleted={results['is_deleted']}, deleted_at={results['deleted_at']}")
                logging.info("   - Column type: is_deleted BOOLEAN NOT NULL DEFAULT FALSE")
                logging.info("   - Column type: deleted_at DATETIME NULL")
                return True
            else:
                logging.error("❌ Some table verifications failed")
                return False
        
    except Exception as e:
        logging.error(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = migrate_all_soft_delete_columns()
    
    if success:
        print("✅ Comprehensive soft delete migration completed successfully!")
    else:
        print("❌ Comprehensive soft delete migration failed!")
        sys.exit(1)
