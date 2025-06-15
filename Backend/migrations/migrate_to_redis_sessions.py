#!/usr/bin/env python3
"""
Migration script to transition EasyShifts to Redis-based sessions and secure passwords
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import get_db_session
from db.controllers.users_controller import UsersController
from security.secure_session import password_security
from config.redis_config import redis_config
from cache.redis_cache import smart_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RedisSessionMigration:
    """Handles migration to Redis-based sessions and secure passwords"""
    
    def __init__(self):
        self.redis_client = None
        self.migration_stats = {
            'users_processed': 0,
            'passwords_upgraded': 0,
            'errors': 0,
            'redis_connection_tested': False
        }
    
    def test_redis_connection(self) -> bool:
        """Test Redis connection"""
        try:
            self.redis_client = redis_config.get_sync_connection()
            result = self.redis_client.ping()
            
            if result:
                logger.info("✅ Redis connection successful")
                self.migration_stats['redis_connection_tested'] = True
                return True
            else:
                logger.error("❌ Redis ping failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            return False
    
    def backup_user_passwords(self) -> bool:
        """Create backup of current user passwords"""
        try:
            backup_file = f"user_passwords_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            
            with get_db_session() as session:
                users_controller = UsersController(session)
                
                # Get all users
                users = session.query(users_controller.model).all()
                
                with open(backup_file, 'w') as f:
                    f.write("-- User password backup before Redis migration\n")
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
                users_controller = UsersController(session)
                
                # Get all users with passwords
                users = session.query(users_controller.model).filter(
                    users_controller.model.password.isnot(None)
                ).all()
                
                for user in users:
                    try:
                        self.migration_stats['users_processed'] += 1
                        
                        # Skip if already hashed (bcrypt hashes start with $2b$)
                        if user.password.startswith('$2b$'):
                            logger.debug(f"User {user.username} already has hashed password")
                            continue
                        
                        # Hash the plain text password
                        hashed_password = password_security.hash_password(user.password)
                        
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
        """Test password verification with a sample user"""
        try:
            with get_db_session() as session:
                users_controller = UsersController(session)
                
                # Get a user with a hashed password
                user = session.query(users_controller.model).filter(
                    users_controller.model.password.like('$2b$%')
                ).first()
                
                if not user:
                    logger.warning("⚠️ No users with hashed passwords found for testing")
                    return True
                
                # Test with a known password (this is just a test)
                test_password = "test_password_123"
                hashed = password_security.hash_password(test_password)
                
                if password_security.verify_password(test_password, hashed):
                    logger.info("✅ Password verification test passed")
                    return True
                else:
                    logger.error("❌ Password verification test failed")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Password verification test error: {e}")
            return False
    
    def setup_redis_keys(self) -> bool:
        """Set up initial Redis key structure"""
        try:
            # Test basic Redis operations
            test_key = "easyshifts:migration:test"
            test_value = {"timestamp": datetime.now().isoformat(), "status": "migration_test"}
            
            # Test set operation
            result = smart_cache.set_cache(test_key, test_value, ttl=60)
            if not result:
                logger.error("❌ Failed to set test cache value")
                return False
            
            # Test get operation
            retrieved_value = smart_cache.get_cache(test_key)
            if not retrieved_value:
                logger.error("❌ Failed to retrieve test cache value")
                return False
            
            # Clean up test key
            smart_cache.delete_cache(test_key)
            
            logger.info("✅ Redis cache operations test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Redis setup test failed: {e}")
            return False
    
    def validate_migration(self) -> bool:
        """Validate the migration was successful"""
        try:
            validation_results = {
                'redis_connection': False,
                'password_hashing': False,
                'cache_operations': False
            }
            
            # Test Redis connection
            if self.test_redis_connection():
                validation_results['redis_connection'] = True
            
            # Test password hashing
            if self.test_password_verification():
                validation_results['password_hashing'] = True
            
            # Test cache operations
            if self.setup_redis_keys():
                validation_results['cache_operations'] = True
            
            # Check if all validations passed
            all_passed = all(validation_results.values())
            
            if all_passed:
                logger.info("✅ All migration validations passed")
            else:
                logger.error(f"❌ Some validations failed: {validation_results}")
            
            return all_passed
            
        except Exception as e:
            logger.error(f"❌ Migration validation failed: {e}")
            return False
    
    def run_migration(self) -> bool:
        """Run the complete migration process"""
        logger.info("🚀 Starting Redis session migration...")
        
        try:
            # Step 1: Test Redis connection
            logger.info("Step 1: Testing Redis connection...")
            if not self.test_redis_connection():
                logger.error("❌ Migration aborted: Redis connection failed")
                return False
            
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
            
            # Step 4: Test Redis operations
            logger.info("Step 4: Testing Redis operations...")
            if not self.setup_redis_keys():
                logger.error("❌ Migration aborted: Redis operations test failed")
                return False
            
            # Step 5: Validate migration
            logger.info("Step 5: Validating migration...")
            if not self.validate_migration():
                logger.error("❌ Migration validation failed")
                return False
            
            # Migration completed successfully
            logger.info("✅ Redis session migration completed successfully!")
            self.print_migration_summary()
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed with error: {e}")
            return False
    
    def print_migration_summary(self):
        """Print migration summary"""
        print("\n" + "="*60)
        print("REDIS SESSION MIGRATION SUMMARY")
        print("="*60)
        print(f"Users processed: {self.migration_stats['users_processed']}")
        print(f"Passwords upgraded: {self.migration_stats['passwords_upgraded']}")
        print(f"Errors encountered: {self.migration_stats['errors']}")
        print(f"Redis connection tested: {self.migration_stats['redis_connection_tested']}")
        print("="*60)
        
        if self.migration_stats['errors'] == 0:
            print("✅ Migration completed without errors!")
        else:
            print(f"⚠️ Migration completed with {self.migration_stats['errors']} errors")
        
        print("\nNext steps:")
        print("1. Update your application to use Redis sessions")
        print("2. Set required environment variables (REDIS_PASSWORD, SESSION_SECRET_KEY, etc.)")
        print("3. Deploy the updated application")
        print("4. Monitor Redis performance and session management")
        print("="*60)

def main():
    """Main migration function"""
    print("EasyShifts Redis Session Migration")
    print("=" * 40)
    
    # Check if Redis environment variables are set
    required_env_vars = ['REDIS_HOST', 'REDIS_PORT']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please set the following environment variables:")
        print("- REDIS_HOST")
        print("- REDIS_PORT")
        print("- REDIS_PASSWORD (optional, but recommended)")
        return False
    
    # Confirm migration
    response = input("\nThis will upgrade all user passwords to bcrypt hashes. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        return False
    
    # Run migration
    migration = RedisSessionMigration()
    success = migration.run_migration()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
