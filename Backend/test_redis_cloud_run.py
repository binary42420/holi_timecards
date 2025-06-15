#!/usr/bin/env python3
"""
Test Redis connection from Cloud Run environment
"""

import os
import sys
import asyncio
import json
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

def test_redis_connection():
    """Test Redis connection with detailed diagnostics"""
    print("🧪 Testing Redis Connection for Cloud Run")
    print("=" * 45)
    
    try:
        # Check environment variables
        print("📋 Redis Environment Variables:")
        redis_host = os.getenv('REDIS_HOST')
        redis_port = os.getenv('REDIS_PORT')
        redis_password = os.getenv('REDIS_PASSWORD')
        
        print(f"   REDIS_HOST: {redis_host}")
        print(f"   REDIS_PORT: {redis_port}")
        print(f"   REDIS_PASSWORD: {'set' if redis_password else 'not set'}")
        
        if not redis_host or not redis_port or not redis_password:
            print("❌ Missing Redis environment variables")
            return False
        
        # Test Redis connection
        print("\n🔌 Testing Redis Connection...")
        from config.redis_config import redis_config
        
        # Test sync connection
        print("   Testing sync connection...")
        redis_client = redis_config.get_sync_connection()
        result = redis_client.ping()
        
        if result:
            print("   ✅ Redis sync connection successful")
            
            # Test basic operations
            print("   Testing basic operations...")
            test_key = "test_connection_key"
            test_value = "test_value_123"
            
            # Set a value
            redis_client.set(test_key, test_value, ex=60)  # Expire in 60 seconds
            print(f"   ✅ Set key '{test_key}' = '{test_value}'")
            
            # Get the value
            retrieved_value = redis_client.get(test_key)
            if retrieved_value and retrieved_value.decode() == test_value:
                print(f"   ✅ Retrieved key '{test_key}' = '{retrieved_value.decode()}'")
            else:
                print(f"   ❌ Failed to retrieve key or value mismatch")
                return False
            
            # Delete the test key
            redis_client.delete(test_key)
            print(f"   ✅ Deleted test key '{test_key}'")
            
            return True
        else:
            print("   ❌ Redis ping failed")
            return False
            
    except Exception as e:
        print(f"❌ Redis connection test failed: {e}")
        traceback.print_exc()
        return False

def test_session_creation():
    """Test session creation with Redis"""
    print("\n🧪 Testing Session Creation")
    print("=" * 30)
    
    try:
        from security.secure_session import secure_session_manager
        
        # Test session creation
        print("   Creating test session...")
        session_data = {
            'user_id': 999,
            'username': 'test_user',
            'is_manager': True,
            'is_admin': False
        }
        
        session_id = secure_session_manager.create_session(
            user_data=session_data,
            client_ip='127.0.0.1'
        )
        
        if session_id:
            print(f"   ✅ Session created: {session_id[:20]}...")
            
            # Test session retrieval
            print("   Retrieving session...")
            retrieved_session = secure_session_manager.get_session(session_id)
            
            if retrieved_session:
                print(f"   ✅ Session retrieved: user_id={retrieved_session.get('user_id')}")
                
                # Test session deletion
                print("   Deleting session...")
                deleted = secure_session_manager.delete_session(session_id)
                
                if deleted:
                    print("   ✅ Session deleted successfully")
                    return True
                else:
                    print("   ❌ Failed to delete session")
                    return False
            else:
                print("   ❌ Failed to retrieve session")
                return False
        else:
            print("   ❌ Failed to create session")
            return False
            
    except Exception as e:
        print(f"❌ Session creation test failed: {e}")
        traceback.print_exc()
        return False

def test_login_handler():
    """Test the login handler that's failing"""
    print("\n🧪 Testing Login Handler")
    print("=" * 25)
    
    try:
        from handlers.login import handle_login
        
        # Test login
        print("   Testing login with admin credentials...")
        login_data = {
            'username': 'admin',
            'password': 'Hdfatboy1!'
        }
        
        response, session = handle_login(login_data, '127.0.0.1')
        
        print(f"   Response: {response}")
        
        if response.get('user_exists'):
            print("   ✅ Login handler working correctly")
            if session:
                print(f"   ✅ Session created: {session}")
            return True
        else:
            print(f"   ❌ Login failed: {response.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Login handler test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all Redis and session tests"""
    print("🚀 Cloud Run Redis Diagnostics")
    print("=" * 35)
    
    tests = [
        ("Redis Connection", test_redis_connection),
        ("Session Creation", test_session_creation),
        ("Login Handler", test_login_handler)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}")
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*35}")
    print("REDIS DIAGNOSTICS SUMMARY")
    print('='*35)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 ALL REDIS TESTS PASSED!")
        print("Redis and session creation are working correctly.")
    else:
        print("\n❌ SOME REDIS TESTS FAILED")
        print("This explains the 'Session service temporarily unavailable' error.")
        
        # Provide troubleshooting suggestions
        print("\n🔧 TROUBLESHOOTING SUGGESTIONS:")
        print("1. Check Redis Cloud connection string")
        print("2. Verify Redis Cloud firewall settings")
        print("3. Check Cloud Run environment variables")
        print("4. Verify Redis Cloud service is running")
    
    return all_passed

if __name__ == "__main__":
    main()
