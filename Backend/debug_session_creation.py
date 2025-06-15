#!/usr/bin/env python3
"""
Debug session creation to identify why "Session creation failed" is occurring
"""

import os
import sys
import json
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_redis_connection():
    """Test basic Redis connection"""
    print("🔍 Testing Redis Connection")
    print("=" * 30)
    
    try:
        import redis
        
        redis_host = os.getenv('REDIS_HOST', 'redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com')
        redis_port = int(os.getenv('REDIS_PORT', '12649'))
        redis_password = os.getenv('REDIS_PASSWORD', 'AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa')
        
        print(f"Host: {redis_host}")
        print(f"Port: {redis_port}")
        print(f"Password: {'*' * len(redis_password) if redis_password else 'None'}")
        
        redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True,
            socket_timeout=10
        )
        
        result = redis_client.ping()
        if result:
            print("✅ Redis connection successful")
            
            # Test basic operations
            test_key = "easyshifts:test:connection"
            test_value = "test_value_123"
            
            redis_client.set(test_key, test_value, ex=60)
            retrieved = redis_client.get(test_key)
            
            if retrieved == test_value:
                print("✅ Redis read/write operations working")
                redis_client.delete(test_key)
                return True
            else:
                print(f"❌ Redis read/write failed: expected '{test_value}', got '{retrieved}'")
                return False
        else:
            print("❌ Redis ping failed")
            return False
            
    except Exception as e:
        print(f"❌ Redis connection error: {e}")
        traceback.print_exc()
        return False

def test_redis_config():
    """Test the Redis configuration module"""
    print("\n🔍 Testing Redis Config Module")
    print("=" * 35)
    
    try:
        from config.redis_config import redis_config, session_manager
        
        print("✅ Redis config module imported successfully")
        
        # Test connection through config
        redis_client = redis_config.get_sync_connection()
        result = redis_client.ping()
        
        if result:
            print("✅ Redis config connection working")
            
            # Test session manager
            test_session_id = "test_session_123"
            test_user_data = {
                "user_id": 999,
                "username": "test_user",
                "is_manager": False
            }
            
            print(f"🧪 Testing session creation with ID: {test_session_id}")
            
            success = session_manager.create_session(test_session_id, test_user_data)
            
            if success:
                print("✅ Session creation successful")
                
                # Test session retrieval
                retrieved_data = session_manager.get_session(test_session_id)
                if retrieved_data:
                    print("✅ Session retrieval successful")
                    print(f"   Retrieved data: {json.dumps(retrieved_data, indent=2)}")
                    
                    # Clean up
                    session_manager.delete_session(test_session_id)
                    print("✅ Session cleanup successful")
                    return True
                else:
                    print("❌ Session retrieval failed")
                    return False
            else:
                print("❌ Session creation failed")
                return False
                
        else:
            print("❌ Redis config connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Redis config test error: {e}")
        traceback.print_exc()
        return False

def test_secure_session_manager():
    """Test the secure session manager"""
    print("\n🔍 Testing Secure Session Manager")
    print("=" * 40)
    
    try:
        from security.secure_session import secure_session_manager
        
        print("✅ Secure session manager imported successfully")
        
        # Test user data
        test_user_data = {
            "user_id": 1,
            "username": "admin",
            "is_manager": True,
            "is_admin": True,
            "email": None,
            "login_method": "password"
        }
        
        test_client_ip = "127.0.0.1"
        
        print(f"🧪 Testing secure session creation")
        print(f"   User data: {json.dumps(test_user_data, indent=2)}")
        print(f"   Client IP: {test_client_ip}")
        
        try:
            session_id, csrf_token = secure_session_manager.create_secure_session(test_user_data, test_client_ip)
            
            print("✅ Secure session creation successful")
            print(f"   Session ID: {session_id[:20]}...")
            print(f"   CSRF Token: {csrf_token[:20]}...")
            
            # Test session validation
            validated_data = secure_session_manager.validate_session(session_id, csrf_token, test_client_ip)
            
            if validated_data:
                print("✅ Session validation successful")
                print(f"   Validated user: {validated_data.get('username')}")
                
                # Clean up
                secure_session_manager.invalidate_session(session_id)
                print("✅ Session cleanup successful")
                return True
            else:
                print("❌ Session validation failed")
                return False
                
        except Exception as e:
            print(f"❌ Secure session creation failed: {e}")
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Secure session manager test error: {e}")
        traceback.print_exc()
        return False

def test_environment_variables():
    """Test required environment variables"""
    print("\n🔍 Testing Environment Variables")
    print("=" * 35)
    
    required_vars = [
        'REDIS_HOST',
        'REDIS_PORT', 
        'REDIS_PASSWORD',
        'SESSION_SECRET_KEY',
        'CSRF_SECRET_KEY'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 10) if 'PASSWORD' in var or 'KEY' in var else value}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("\n✅ All required environment variables are set")
        return True

def test_login_flow():
    """Test the complete login flow"""
    print("\n🔍 Testing Complete Login Flow")
    print("=" * 35)
    
    try:
        from handlers.login import handle_login
        
        test_data = {
            "username": "admin",
            "password": "Hdfatboy1!"
        }
        
        test_client_ip = "127.0.0.1"
        
        print(f"🧪 Testing login with: {test_data['username']}")
        
        response, session = handle_login(test_data, test_client_ip)
        
        print(f"📤 Login response: {json.dumps(response, indent=2)}")
        
        if response.get('user_exists'):
            print("✅ Login successful")
            return True
        else:
            print("❌ Login failed")
            print(f"   Error: {response.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Login flow test error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests"""
    print("🚀 EasyShifts Session Creation Diagnostics")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Redis Connection", test_redis_connection),
        ("Redis Config Module", test_redis_config),
        ("Secure Session Manager", test_secure_session_manager),
        ("Complete Login Flow", test_login_flow)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*50}")
    print("DIAGNOSTIC SUMMARY")
    print('='*50)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! Session creation should be working.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        print("\nCommon fixes:")
        print("1. Check Redis connection credentials")
        print("2. Verify environment variables are loaded")
        print("3. Ensure Redis server is accessible")
        print("4. Check for import errors in modules")
    
    return all_passed

if __name__ == "__main__":
    main()
