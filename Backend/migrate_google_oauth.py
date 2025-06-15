#!/usr/bin/env python3
"""
Database migration script to add Google OAuth columns to existing EasyShifts database.
This script adds the necessary columns for Google OAuth functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import initialize_database_and_session
from sqlalchemy import text
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_column_exists(db, table_name, column_name):
    """Check if a column exists in a table."""
    try:
        result = db.execute(text(f"""
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = '{table_name}'
            AND COLUMN_NAME = '{column_name}'
        """))
        
        count = result.fetchone()[0]
        return count > 0
    except Exception as e:
        logger.error(f"Error checking column {column_name}: {e}")
        return False

def add_google_oauth_columns():
    """Add Google OAuth columns to the users table."""
    logger.info("Starting Google OAuth database migration...")
    
    try:
        # Initialize database connection
        db, _ = initialize_database_and_session()
        logger.info("✓ Database connection established")
        
        # Define the columns to add
        columns_to_add = [
            {
                'name': 'google_id',
                'definition': 'VARCHAR(100) UNIQUE NULL',
                'description': 'Google OAuth unique identifier'
            },
            {
                'name': 'email',
                'definition': 'VARCHAR(255) NULL',
                'description': 'User email address'
            },
            {
                'name': 'google_picture',
                'definition': 'VARCHAR(500) NULL',
                'description': 'URL to Google profile picture'
            },
            {
                'name': 'last_login',
                'definition': 'DATETIME NULL',
                'description': 'Timestamp of last login'
            }
        ]
        
        # Check and add each column
        for column in columns_to_add:
            column_name = column['name']
            column_def = column['definition']
            description = column['description']
            
            logger.info(f"Checking column: {column_name}")
            
            if check_column_exists(db, 'users', column_name):
                logger.info(f"✓ Column '{column_name}' already exists")
            else:
                logger.info(f"Adding column '{column_name}': {description}")
                
                try:
                    # Add the column
                    sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_def}"
                    db.execute(text(sql))
                    db.commit()
                    logger.info(f"✓ Successfully added column '{column_name}'")
                    
                except Exception as e:
                    logger.error(f"✗ Failed to add column '{column_name}': {e}")
                    db.rollback()
                    return False
        
        # Also make password column nullable for Google OAuth users
        logger.info("Checking if password column is nullable...")
        try:
            result = db.execute(text("""
                SELECT IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'users'
                AND COLUMN_NAME = 'password'
            """))
            
            is_nullable = result.fetchone()[0]
            
            if is_nullable == 'NO':
                logger.info("Making password column nullable for Google OAuth users...")
                db.execute(text("ALTER TABLE users MODIFY COLUMN password VARCHAR(255) NULL"))
                db.commit()
                logger.info("✓ Password column is now nullable")
            else:
                logger.info("✓ Password column is already nullable")
                
        except Exception as e:
            logger.error(f"Error modifying password column: {e}")
            db.rollback()
        
        # Add index on google_id for better performance
        logger.info("Adding index on google_id column...")
        try:
            db.execute(text("CREATE INDEX idx_users_google_id ON users(google_id)"))
            db.commit()
            logger.info("✓ Index on google_id created")
        except Exception as e:
            if "Duplicate key name" in str(e):
                logger.info("✓ Index on google_id already exists")
            else:
                logger.warning(f"Could not create index on google_id: {e}")
        
        # Add index on email for better performance
        logger.info("Adding index on email column...")
        try:
            db.execute(text("CREATE INDEX idx_users_email ON users(email)"))
            db.commit()
            logger.info("✓ Index on email created")
        except Exception as e:
            if "Duplicate key name" in str(e):
                logger.info("✓ Index on email already exists")
            else:
                logger.warning(f"Could not create index on email: {e}")
        
        logger.info("\n" + "="*50)
        logger.info("🎉 Google OAuth migration completed successfully!")
        logger.info("="*50)
        logger.info("\nNext steps:")
        logger.info("1. Restart your backend server")
        logger.info("2. Test Google OAuth login/signup")
        logger.info("3. Check that regular login still works")
        
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()

def verify_migration():
    """Verify that the migration was successful."""
    logger.info("\nVerifying migration...")
    
    try:
        db, _ = initialize_database_and_session()
        
        # Check all required columns exist
        required_columns = ['google_id', 'email', 'google_picture', 'last_login']
        
        for column in required_columns:
            if check_column_exists(db, 'users', column):
                logger.info(f"✓ Column '{column}' exists")
            else:
                logger.error(f"✗ Column '{column}' missing")
                return False
        
        # Test a simple query to make sure everything works
        result = db.execute(text("SELECT COUNT(*) FROM users"))
        count = result.fetchone()[0]
        logger.info(f"✓ Users table accessible, {count} users found")
        
        logger.info("✅ Migration verification successful!")
        return True
        
    except Exception as e:
        logger.error(f"Migration verification failed: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    print("EasyShifts Google OAuth Database Migration")
    print("=" * 50)
    
    # Run migration
    success = add_google_oauth_columns()
    
    if success:
        # Verify migration
        verify_success = verify_migration()
        
        if verify_success:
            print("\n🚀 Migration completed successfully!")
            print("You can now use Google OAuth login and signup.")
            sys.exit(0)
        else:
            print("\n❌ Migration verification failed!")
            sys.exit(1)
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
