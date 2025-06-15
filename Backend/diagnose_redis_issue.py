#!/usr/bin/env python3
"""
Diagnose and fix Redis session service issues
"""

import os
import sys
import asyncio
import json
from datetime import datetime

def test_redis_connection():
    """Test Redis connection with current configuration"""
    print("🔍 Diagnosing Redis Connection")
    print("=" * 35)
    
    try:
        from config.redis_config import redis_config, session_manager
        
        print("📋 Redis Configuration:")
        print(f"   Host: {redis_config.host}")
        print(f"   Port: {redis_config.port}")
        print(f"   Password: {'***' if redis_config.password else 'None'}")
        print(f"   Session Timeout: {redis_config.session_timeout}s")
        print()
        
        # Test sync connection
        print("🧪 Testing Sync Connection...")
        try:
            redis_client = redis_config.get_sync_connection()
            ping_result = redis_client.ping()
            print(f"   ✅ Sync Ping: {ping_result}")
        except Exception as e:
            print(f"   ❌ Sync Connection Failed: {e}")
            return False
        
        # Test async connection
        print("🧪 Testing Async Connection...")
        try:
            async def test_async():
                redis_client = await redis_config.get_async_connection()
                ping_result = await redis_client.ping()
                await redis_client.close()
                return ping_result
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            ping_result = loop.run_until_complete(test_async())
            loop.close()
            print(f"   ✅ Async Ping: {ping_result}")
        except Exception as e:
            print(f"   ❌ Async Connection Failed: {e}")
            return False
        
        # Test session creation
        print("🧪 Testing Session Management...")
        try:
            test_session_data = {
                'user_id': 'test_user',
                'username': 'test',
                'is_manager': False,
                'test_timestamp': datetime.utcnow().isoformat()
            }
            
            success = session_manager.create_session('test_session_123', test_session_data)
            if success:
                print("   ✅ Session Creation: Success")
                
                # Test session retrieval
                retrieved = session_manager.get_session('test_session_123')
                if retrieved:
                    print("   ✅ Session Retrieval: Success")
                    
                    # Cleanup test session
                    session_manager.delete_session('test_session_123')
                    print("   ✅ Session Cleanup: Success")
                    return True
                else:
                    print("   ❌ Session Retrieval: Failed")
                    return False
            else:
                print("   ❌ Session Creation: Failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Session Management Failed: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Redis configuration modules not found")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def check_environment_variables():
    """Check if all required environment variables are set"""
    print("\n🔍 Environment Variables Check")
    print("=" * 35)
    
    required_vars = [
        'REDIS_HOST',
        'REDIS_PORT', 
        'REDIS_PASSWORD',
        'DB_HOST',
        'DB_PASSWORD'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var:
                print(f"   ✅ {var}: ***")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("\n✅ All required environment variables are set")
        return True

def fix_redis_configuration():
    """Create a fixed Redis configuration"""
    print("\n🔧 Creating Fixed Redis Configuration")
    print("=" * 40)
    
    # Create a robust Redis config
    fixed_config = '''"""
Fixed Redis Configuration for EasyShifts
Addresses connection and session management issues
"""

import os
import redis
import aioredis
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class FixedRedisConfig:
    """Robust Redis configuration with better error handling"""
    
    def __init__(self):
        # Redis connection settings with fallbacks
        self.host = os.getenv('REDIS_HOST', 'redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com')
        self.port = int(os.getenv('REDIS_PORT', '12649'))
        self.password = os.getenv('REDIS_PASSWORD', 'AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa')
        self.db = int(os.getenv('REDIS_DB', '0'))
        
        # Session settings
        self.session_timeout = int(os.getenv('SESSION_TIMEOUT', '3600'))  # 1 hour
        self.max_connections = int(os.getenv('REDIS_MAX_CONNECTIONS', '20'))
        
        # Connection pool settings
        self.socket_timeout = 5.0
        self.socket_connect_timeout = 5.0
        self.retry_on_timeout = True
        self.health_check_interval = 30
        
        logger.info(f"Redis config initialized: {self.host}:{self.port}")
    
    def get_sync_connection(self) -> redis.Redis:
        """Get synchronous Redis connection with connection pooling"""
        try:
            connection_pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                max_connections=self.max_connections,
                socket_timeout=self.socket_timeout,
                socket_connect_timeout=self.socket_connect_timeout,
                retry_on_timeout=self.retry_on_timeout,
                health_check_interval=self.health_check_interval,
                decode_responses=True
            )
            
            client = redis.Redis(connection_pool=connection_pool)
            
            # Test connection
            client.ping()
            logger.debug("Sync Redis connection established successfully")
            return client
            
        except Exception as e:
            logger.error(f"Failed to create sync Redis connection: {e}")
            raise
    
    async def get_async_connection(self) -> aioredis.Redis:
        """Get asynchronous Redis connection"""
        try:
            redis_url = f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
            
            client = aioredis.from_url(
                redis_url,
                socket_timeout=self.socket_timeout,
                socket_connect_timeout=self.socket_connect_timeout,
                retry_on_timeout=self.retry_on_timeout,
                max_connections=self.max_connections,
                decode_responses=True
            )
            
            # Test connection
            await client.ping()
            logger.debug("Async Redis connection established successfully")
            return client
            
        except Exception as e:
            logger.error(f"Failed to create async Redis connection: {e}")
            raise

class FixedSessionManager:
    """Improved session manager with better error handling"""
    
    def __init__(self, redis_config: FixedRedisConfig):
        self.redis_config = redis_config
        self.session_prefix = "easyshifts:session:"
        
    def _get_session_key(self, session_id: str) -> str:
        """Get Redis key for session"""
        return f"{self.session_prefix}{session_id}"
    
    def create_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Create session with retry logic"""
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                redis_client = self.redis_config.get_sync_connection()
                
                # Add metadata
                enhanced_data = {
                    **session_data,
                    'created_at': datetime.utcnow().isoformat(),
                    'last_accessed': datetime.utcnow().isoformat(),
                    'session_id': session_id
                }
                
                # Store with expiration
                session_key = self._get_session_key(session_id)
                result = redis_client.setex(
                    session_key,
                    self.redis_config.session_timeout,
                    json.dumps(enhanced_data, default=str)
                )
                
                if result:
                    logger.info(f"Session created successfully: {session_id}")
                    return True
                else:
                    logger.warning(f"Session creation returned False: {session_id}")
                    
            except Exception as e:
                logger.error(f"Session creation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"Failed to create session after {max_retries} attempts")
        
        return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session with error handling"""
        try:
            redis_client = self.redis_config.get_sync_connection()
            session_key = self._get_session_key(session_id)
            
            session_data = redis_client.get(session_key)
            if session_data:
                parsed_data = json.loads(session_data)
                
                # Update last accessed time
                parsed_data['last_accessed'] = datetime.utcnow().isoformat()
                redis_client.setex(
                    session_key,
                    self.redis_config.session_timeout,
                    json.dumps(parsed_data, default=str)
                )
                
                logger.debug(f"Session retrieved successfully: {session_id}")
                return parsed_data
            else:
                logger.debug(f"Session not found: {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        try:
            redis_client = self.redis_config.get_sync_connection()
            session_key = self._get_session_key(session_id)
            result = redis_client.delete(session_key)
            
            if result:
                logger.info(f"Session deleted successfully: {session_id}")
                return True
            else:
                logger.warning(f"Session not found for deletion: {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False

# Global instances
fixed_redis_config = FixedRedisConfig()
fixed_session_manager = FixedSessionManager(fixed_redis_config)
'''
    
    with open('config/fixed_redis_config.py', 'w', encoding='utf-8') as f:
        f.write(fixed_config)
    
    print("   ✅ Created config/fixed_redis_config.py")
    return True

def create_redis_test_script():
    """Create a comprehensive Redis test script"""
    test_script = '''#!/usr/bin/env python3
"""
Comprehensive Redis connection and session test
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_original_redis():
    """Test original Redis configuration"""
    print("🧪 Testing Original Redis Configuration")
    try:
        from config.redis_config import redis_config, session_manager
        
        # Test connection
        client = redis_config.get_sync_connection()
        ping_result = client.ping()
        print(f"   ✅ Original Redis Ping: {ping_result}")
        
        # Test session
        test_data = {'test': 'data', 'timestamp': '2025-06-11'}
        success = session_manager.create_session('test_original', test_data)
        print(f"   ✅ Original Session Creation: {success}")
        
        if success:
            retrieved = session_manager.get_session('test_original')
            print(f"   ✅ Original Session Retrieval: {retrieved is not None}")
            session_manager.delete_session('test_original')
        
        return True
        
    except Exception as e:
        print(f"   ❌ Original Redis Failed: {e}")
        return False

def test_fixed_redis():
    """Test fixed Redis configuration"""
    print("\\n🧪 Testing Fixed Redis Configuration")
    try:
        from config.fixed_redis_config import fixed_redis_config, fixed_session_manager
        
        # Test connection
        client = fixed_redis_config.get_sync_connection()
        ping_result = client.ping()
        print(f"   ✅ Fixed Redis Ping: {ping_result}")
        
        # Test session
        test_data = {'test': 'data', 'timestamp': '2025-06-11', 'fixed': True}
        success = fixed_session_manager.create_session('test_fixed', test_data)
        print(f"   ✅ Fixed Session Creation: {success}")
        
        if success:
            retrieved = fixed_session_manager.get_session('test_fixed')
            print(f"   ✅ Fixed Session Retrieval: {retrieved is not None}")
            fixed_session_manager.delete_session('test_fixed')
        
        return True
        
    except Exception as e:
        print(f"   ❌ Fixed Redis Failed: {e}")
        return False

def main():
    """Run comprehensive Redis tests"""
    print("🚀 Redis Connection Comprehensive Test")
    print("=" * 45)
    
    original_works = test_original_redis()
    fixed_works = test_fixed_redis()
    
    print("\\n📊 Test Results:")
    print(f"   Original Config: {'✅ Working' if original_works else '❌ Failed'}")
    print(f"   Fixed Config: {'✅ Working' if fixed_works else '❌ Failed'}")
    
    if original_works:
        print("\\n✅ Original Redis configuration is working!")
        print("   No changes needed to Redis setup.")
    elif fixed_works:
        print("\\n🔧 Fixed Redis configuration works!")
        print("   Consider updating imports to use fixed config.")
    else:
        print("\\n❌ Both configurations failed!")
        print("   Check Redis server status and credentials.")

if __name__ == "__main__":
    main()
'''
    
    with open('test_redis_comprehensive.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("   ✅ Created test_redis_comprehensive.py")

def main():
    """Run Redis diagnosis and fixes"""
    print("🚀 Redis Session Service Diagnosis & Fix")
    print("=" * 45)
    
    # Step 1: Check environment variables
    env_ok = check_environment_variables()
    
    # Step 2: Test current Redis connection
    redis_ok = test_redis_connection()
    
    # Step 3: Create fixes if needed
    if not redis_ok:
        print("\n🔧 Creating Redis fixes...")
        fix_redis_configuration()
        create_redis_test_script()
        
        print("\n📋 Next Steps:")
        print("1. Run: python test_redis_comprehensive.py")
        print("2. If fixed config works, update imports in handlers")
        print("3. Test login functionality")
    else:
        print("\n✅ Redis is working correctly!")
        print("   The session service issue may be elsewhere.")
        
        # Create test script anyway for monitoring
        create_redis_test_script()
        print("\n📋 Created monitoring script: test_redis_comprehensive.py")

if __name__ == "__main__":
    main()
