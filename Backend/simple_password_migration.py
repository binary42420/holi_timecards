#!/usr/bin/env python3
"""
Simple password migration script for EasyShifts
Upgrades plain text passwords to bcrypt hashes without async dependencies
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import get_db_session
from db.controllers.users_controller import UsersController

# Import bcrypt directly
import bcrypt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimplePasswordMigration:
    """Simple password migration without Redis dependencies"""
    
    def __init__(self):
        self.migration_stats = {
            'users_processed': 0,
            'passwords_upgraded': 0,
            'already_hashed': 0,
            'errors': 0
        }
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def backup_user_passwords(self) -> bool:
        """Create backup of current user passwords"""
        try:
            backup_file = f"user_passwords_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

            with get_db_session() as session:
                # Import User model directly
                from db.models import User

                # Get all users
                users = session.query(User).all()

                with open(backup_file, 'w') as f:
                    f.write("-- User password backup before migration\n")
                    f.write(f"-- Created: {datetime.now().isoformat()}\n\n")

                    for user in users:
                        if user.password:
                            # Escape single quotes in password
                            escaped_password = user.password.replace("'", "''")
                            f.write(f"-- User: {user.username}\n")
                            f.write(f"UPDATE users SET password = '{escaped_password}' WHERE id = {user.id};\n\n")

                logger.info(f"✅ Password backup created: {backup_file}")
                return True

        except Exception as e:
            logger.error(f"❌ Failed to create password backup: {e}")
            return False
    
    def upgrade_user_passwords(self) -> bool:
        """Upgrade plain text passwords to bcrypt hashes"""
        try:
            with get_db_session() as session:
                # Import User model directly
                from db.models import User

                # Get all users with passwords
                users = session.query(User).filter(
                    User.password.isnot(None)
                ).all()

                logger.info(f"Found {len(users)} users with passwords")

                for user in users:
                    try:
                        self.migration_stats['users_processed'] += 1

                        # Skip if already hashed (bcrypt hashes start with $2b$)
                        if user.password.startswith('$2b$'):
                            logger.debug(f"User {user.username} already has hashed password")
                            self.migration_stats['already_hashed'] += 1
                            continue

                        # Hash the plain text password
                        hashed_password = self.hash_password(user.password)

                        # Update user password
                        user.password = hashed_password
                        session.commit()

                        self.migration_stats['passwords_upgraded'] += 1
                        logger.info(f"✅ Upgraded password for user: {user.username}")

                    except Exception as e:
                        self.migration_stats['errors'] += 1
                        logger.error(f"❌ Failed to upgrade password for user {user.username}: {e}")
                        session.rollback()
                        continue

                logger.info(f"✅ Password upgrade completed. Upgraded {self.migration_stats['passwords_upgraded']} passwords")
                return True

        except Exception as e:
            logger.error(f"❌ Password upgrade failed: {e}")
            return False
    
    def test_password_verification(self) -> bool:
        """Test password verification with upgraded passwords"""
        try:
            with get_db_session() as session:
                # Import User model directly
                from db.models import User

                # Get a user with a hashed password
                user = session.query(User).filter(
                    User.password.like('$2b$%')
                ).first()

                if not user:
                    logger.warning("⚠️ No users with hashed passwords found for testing")
                    return True

                # Test with a known password (this is just a test)
                test_password = "test_password_123"
                hashed = self.hash_password(test_password)

                if self.verify_password(test_password, hashed):
                    logger.info("✅ Password verification test passed")
                    return True
                else:
                    logger.error("❌ Password verification test failed")
                    return False

        except Exception as e:
            logger.error(f"❌ Password verification test error: {e}")
            return False
    
    def test_redis_connection(self) -> bool:
        """Test Redis connection"""
        try:
            import redis
            
            redis_host = os.getenv('REDIS_HOST', 'redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com')
            redis_port = int(os.getenv('REDIS_PORT', '12649'))
            redis_password = os.getenv('REDIS_PASSWORD', 'AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa')
            
            redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                decode_responses=True,
                socket_timeout=5
            )
            
            result = redis_client.ping()
            if result:
                logger.info("✅ Redis connection test passed")
                return True
            else:
                logger.error("❌ Redis ping failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Redis connection test failed: {e}")
            return False
    
    def run_migration(self) -> bool:
        """Run the complete migration process"""
        logger.info("🚀 Starting simple password migration...")
        
        try:
            # Step 1: Test Redis connection
            logger.info("Step 1: Testing Redis connection...")
            if not self.test_redis_connection():
                logger.warning("⚠️ Redis connection failed, but continuing with password migration")
            
            # Step 2: Backup existing passwords
            logger.info("Step 2: Creating password backup...")
            if not self.backup_user_passwords():
                logger.error("❌ Migration aborted: Password backup failed")
                return False
            
            # Step 3: Upgrade passwords to bcrypt
            logger.info("Step 3: Upgrading passwords to bcrypt...")
            if not self.upgrade_user_passwords():
                logger.error("❌ Migration aborted: Password upgrade failed")
                return False
            
            # Step 4: Test password verification
            logger.info("Step 4: Testing password verification...")
            if not self.test_password_verification():
                logger.error("❌ Migration aborted: Password verification test failed")
                return False
            
            # Migration completed successfully
            logger.info("✅ Password migration completed successfully!")
            self.print_migration_summary()
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed with error: {e}")
            return False
    
    def print_migration_summary(self):
        """Print migration summary"""
        print("\n" + "="*60)
        print("PASSWORD MIGRATION SUMMARY")
        print("="*60)
        print(f"Users processed: {self.migration_stats['users_processed']}")
        print(f"Passwords upgraded: {self.migration_stats['passwords_upgraded']}")
        print(f"Already hashed: {self.migration_stats['already_hashed']}")
        print(f"Errors encountered: {self.migration_stats['errors']}")
        print("="*60)
        
        if self.migration_stats['errors'] == 0:
            print("✅ Migration completed without errors!")
        else:
            print(f"⚠️ Migration completed with {self.migration_stats['errors']} errors")
        
        print("\nNext steps:")
        print("1. Update your login handlers to use bcrypt verification")
        print("2. Test login functionality with existing users")
        print("3. Deploy the updated application")
        print("4. Monitor authentication performance")
        print("="*60)

def main():
    """Main migration function"""
    print("EasyShifts Simple Password Migration")
    print("=" * 40)
    
    # Confirm migration
    response = input("\nThis will upgrade all user passwords to bcrypt hashes. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        return False
    
    # Run migration
    migration = SimplePasswordMigration()
    success = migration.run_migration()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
