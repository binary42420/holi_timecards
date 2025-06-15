#!/usr/bin/env python3
"""
Quick Redis connection test for EasyShifts
Tests the Redis connection with the provided credentials
"""

import os
import sys
import json
import time
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.production')

try:
    import redis
    import bcrypt
    print("✅ Required packages (redis, bcrypt) are available")
except ImportError as e:
    print(f"❌ Missing required packages: {e}")
    print("Please install: pip install redis bcrypt python-dotenv")
    sys.exit(1)

def test_redis_connection():
    """Test Redis connection with the provided credentials"""
    print("🔍 Testing Redis connection...")
    
    # Get Redis configuration from environment
    redis_host = os.getenv('REDIS_HOST', 'redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com')
    redis_port = int(os.getenv('REDIS_PORT', '12649'))
    redis_password = os.getenv('REDIS_PASSWORD', 'AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa')
    redis_db = int(os.getenv('REDIS_DB', '0'))
    
    print(f"Host: {redis_host}")
    print(f"Port: {redis_port}")
    print(f"Database: {redis_db}")
    print(f"Password: {'*' * len(redis_password) if redis_password else 'None'}")
    
    try:
        # Create Redis client
        redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            db=redis_db,
            decode_responses=True,
            socket_timeout=10,
            socket_connect_timeout=10
        )
        
        # Test basic connectivity
        print("\n🔄 Testing basic connectivity...")
        start_time = time.time()
        ping_result = redis_client.ping()
        ping_time = (time.time() - start_time) * 1000
        
        if ping_result:
            print(f"✅ PING successful ({ping_time:.2f}ms)")
        else:
            print("❌ PING failed")
            return False
        
        # Test basic operations
        print("\n🔄 Testing basic operations...")
        
        # SET operation
        test_key = "easyshifts:test:connection"
        test_value = {
            "timestamp": datetime.now().isoformat(),
            "test": "Redis connection test",
            "status": "success"
        }
        
        redis_client.setex(test_key, 60, json.dumps(test_value))
        print("✅ SET operation successful")
        
        # GET operation
        retrieved_value = redis_client.get(test_key)
        if retrieved_value:
            parsed_value = json.loads(retrieved_value)
            print("✅ GET operation successful")
            print(f"   Retrieved: {parsed_value['test']}")
        else:
            print("❌ GET operation failed")
            return False
        
        # DELETE operation
        redis_client.delete(test_key)
        print("✅ DELETE operation successful")
        
        # Test session-like operations
        print("\n🔄 Testing session operations...")
        
        session_key = "easyshifts:session:test_session_123"
        session_data = {
            "user_id": 1,
            "username": "test_user",
            "is_manager": True,
            "created_at": datetime.now().isoformat(),
            "csrf_token": "test_csrf_token_123"
        }
        
        # Store session with 1 hour expiration
        redis_client.setex(session_key, 3600, json.dumps(session_data))
        print("✅ Session storage successful")
        
        # Retrieve session
        stored_session = redis_client.get(session_key)
        if stored_session:
            session_obj = json.loads(stored_session)
            print(f"✅ Session retrieval successful for user: {session_obj['username']}")
        else:
            print("❌ Session retrieval failed")
            return False
        
        # Clean up test session
        redis_client.delete(session_key)
        print("✅ Session cleanup successful")
        
        # Test cache operations
        print("\n🔄 Testing cache operations...")
        
        cache_key = "easyshifts:cache:user_profile:1"
        cache_data = {
            "id": 1,
            "username": "test_user",
            "name": "Test User",
            "email": "test@example.com",
            "cached_at": datetime.now().isoformat()
        }
        
        # Store cache with 30 minutes expiration
        redis_client.setex(cache_key, 1800, json.dumps(cache_data))
        print("✅ Cache storage successful")
        
        # Retrieve cache
        cached_data = redis_client.get(cache_key)
        if cached_data:
            cache_obj = json.loads(cached_data)
            print(f"✅ Cache retrieval successful for: {cache_obj['name']}")
        else:
            print("❌ Cache retrieval failed")
            return False
        
        # Clean up test cache
        redis_client.delete(cache_key)
        print("✅ Cache cleanup successful")
        
        # Test Redis info
        print("\n📊 Redis server information...")
        info = redis_client.info()
        print(f"Redis version: {info.get('redis_version', 'Unknown')}")
        print(f"Used memory: {info.get('used_memory_human', 'Unknown')}")
        print(f"Connected clients: {info.get('connected_clients', 'Unknown')}")
        print(f"Total commands processed: {info.get('total_commands_processed', 'Unknown')}")
        
        return True
        
    except redis.ConnectionError as e:
        print(f"❌ Redis connection error: {e}")
        return False
    except redis.TimeoutError as e:
        print(f"❌ Redis timeout error: {e}")
        return False
    except redis.AuthenticationError as e:
        print(f"❌ Redis authentication error: {e}")
        print("Please check your Redis password")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_password_hashing():
    """Test bcrypt password hashing functionality"""
    print("\n🔐 Testing password hashing...")
    
    try:
        # Test password
        test_password = "REDACTED_FOR_SECURITY"
        
        # Hash the password
        salt = bcrypt.gensalt(rounds=12)
        hashed_password = bcrypt.hashpw(test_password.encode('utf-8'), salt)
        print("✅ Password hashing successful")
        
        # Verify the password
        is_valid = bcrypt.checkpw(test_password.encode('utf-8'), hashed_password)
        if is_valid:
            print("✅ Password verification successful")
        else:
            print("❌ Password verification failed")
            return False
        
        # Test with wrong password
        wrong_password = "REDACTED_FOR_SECURITY"
        is_invalid = bcrypt.checkpw(wrong_password.encode('utf-8'), hashed_password)
        if not is_invalid:
            print("✅ Wrong password correctly rejected")
        else:
            print("❌ Wrong password incorrectly accepted")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Password hashing error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 EasyShifts Redis Connection Test")
    print("=" * 40)
    
    # Test Redis connection
    redis_success = test_redis_connection()
    
    # Test password hashing
    password_success = test_password_hashing()
    
    # Summary
    print("\n" + "=" * 40)
    print("TEST SUMMARY")
    print("=" * 40)
    
    if redis_success:
        print("✅ Redis connection: PASSED")
    else:
        print("❌ Redis connection: FAILED")
    
    if password_success:
        print("✅ Password hashing: PASSED")
    else:
        print("❌ Password hashing: FAILED")
    
    overall_success = redis_success and password_success
    
    if overall_success:
        print("\n🎉 All tests PASSED! Redis integration is ready.")
        print("\nNext steps:")
        print("1. Run the migration script: python migrations/migrate_to_redis_sessions.py")
        print("2. Update your application to use Redis sessions")
        print("3. Deploy to production")
    else:
        print("\n❌ Some tests FAILED. Please fix the issues before proceeding.")
    
    print("=" * 40)
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
