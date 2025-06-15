"""
Database Migration: Create User Sessions Table
Run this script to create the persistent session storage table
"""

import logging
import os
import sys
from sqlalchemy import create_engine, text

# Add the Backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_session_table():
    """Create the user_sessions table"""
    try:
        # Get database session
        from main import get_db_session
        db_session = get_db_session()
        engine = db_session.bind
        
        # Create the table
        logger.info("Creating user_sessions table...")
        
        # SQL to create the table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(255) UNIQUE NOT NULL,
            user_id INT NOT NULL,
            csrf_token VARCHAR(255) NOT NULL,
            username VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            is_manager BOOLEAN DEFAULT FALSE NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE NOT NULL,
            login_method VARCHAR(50) DEFAULT 'password' NOT NULL,
            google_id VARCHAR(255),
            session_data TEXT,
            client_ip VARCHAR(45),
            user_agent VARCHAR(500),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            expires_at DATETIME NOT NULL,
            is_active BOOLEAN DEFAULT TRUE NOT NULL,
            
            INDEX idx_session_id (session_id),
            INDEX idx_user_id (user_id),
            INDEX idx_username (username),
            INDEX idx_expires_at (expires_at),
            INDEX idx_is_active (is_active)
        );
        """
        
        # Execute the SQL
        with engine.connect() as connection:
            connection.execute(text(create_table_sql))
            connection.commit()
        
        logger.info("✅ user_sessions table created successfully!")
        
        # Verify table exists
        with engine.connect() as connection:
            result = connection.execute(text("SHOW TABLES LIKE 'user_sessions'"))
            if result.fetchone():
                logger.info("✅ Table verification successful")
            else:
                logger.error("❌ Table verification failed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create user_sessions table: {e}")
        return False

def check_table_exists():
    """Check if the user_sessions table exists"""
    try:
        from main import get_db_session
        db_session = get_db_session()
        engine = db_session.bind
        
        with engine.connect() as connection:
            result = connection.execute(text("SHOW TABLES LIKE 'user_sessions'"))
            exists = result.fetchone() is not None
            
        if exists:
            logger.info("✅ user_sessions table already exists")
        else:
            logger.info("❌ user_sessions table does not exist")
            
        return exists
        
    except Exception as e:
        logger.error(f"Error checking table existence: {e}")
        return False

def get_table_info():
    """Get information about the user_sessions table"""
    try:
        from main import get_db_session
        db_session = get_db_session()
        engine = db_session.bind
        
        with engine.connect() as connection:
            # Get table structure
            result = connection.execute(text("DESCRIBE user_sessions"))
            columns = result.fetchall()
            
            logger.info("user_sessions table structure:")
            for column in columns:
                logger.info(f"  {column[0]} - {column[1]} - {column[2]} - {column[3]}")
            
            # Get row count
            result = connection.execute(text("SELECT COUNT(*) FROM user_sessions"))
            count = result.fetchone()[0]
            logger.info(f"Total sessions in table: {count}")
            
            # Get active sessions count
            result = connection.execute(text("SELECT COUNT(*) FROM user_sessions WHERE is_active = TRUE AND expires_at > NOW()"))
            active_count = result.fetchone()[0]
            logger.info(f"Active sessions: {active_count}")
            
        return True
        
    except Exception as e:
        logger.error(f"Error getting table info: {e}")
        return False

if __name__ == "__main__":
    logger.info("🔄 Database Migration: Create User Sessions Table")
    logger.info("=" * 50)
    
    # Check if table exists
    if check_table_exists():
        logger.info("Table already exists, getting info...")
        get_table_info()
    else:
        logger.info("Creating user_sessions table...")
        if create_session_table():
            logger.info("✅ Migration completed successfully!")
            get_table_info()
        else:
            logger.error("❌ Migration failed!")
    
    logger.info("=" * 50)
    logger.info("Migration script completed")
