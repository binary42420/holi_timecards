#!/usr/bin/env python3
"""
Test server startup to identify any issues
"""

import os
import sys
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all imports that Server.py uses"""
    print("🧪 Testing Server.py Imports")
    print("=" * 30)
    
    try:
        print("   📦 Testing basic imports...")
        import asyncio
        import json
        import logging
        from datetime import datetime, timezone
        print("   ✅ Basic imports successful")
        
        print("   📦 Testing web framework imports...")
        from aiohttp import web
        import aiohttp_cors
        import websockets
        print("   ✅ Web framework imports successful")
        
        print("   📦 Testing database imports...")
        from main import get_db_session, database_initialized
        print("   ✅ Database imports successful")
        
        print("   📦 Testing handler imports...")
        from handlers import login
        from handlers import employee_signin
        from handlers import manager_signin
        print("   ✅ Handler imports successful")
        
        print("   📦 Testing Redis imports...")
        from config.redis_config import redis_config
        from security.secure_session import secure_session_manager
        print("   ✅ Redis imports successful")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_environment():
    """Test environment variables"""
    print("\n🧪 Testing Environment Variables")
    print("=" * 35)
    
    required_vars = [
        'DB_HOST', 'DB_PORT', 'DB_USER', 'DB_NAME', 'DB_PASSWORD',
        'REDIS_HOST', 'REDIS_PORT', 'REDIS_PASSWORD',
        'SESSION_SECRET_KEY', 'CSRF_SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            display_value = '*' * 10 if 'PASSWORD' in var or 'KEY' in var else value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n   ❌ Missing variables: {', '.join(missing_vars)}")
        return False
    else:
        print(f"\n   ✅ All environment variables present")
        return True

def test_database_connection():
    """Test database connection"""
    print("\n🧪 Testing Database Connection")
    print("=" * 35)
    
    try:
        from main import get_db_session, database_initialized
        
        print(f"   📊 Database initialized: {database_initialized}")
        
        if database_initialized:
            with get_db_session() as session:
                # Simple test query
                result = session.execute("SELECT 1 as test").fetchone()
                if result and result[0] == 1:
                    print("   ✅ Database connection successful")
                    return True
                else:
                    print("   ❌ Database query failed")
                    return False
        else:
            print("   ❌ Database not initialized")
            return False
            
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        traceback.print_exc()
        return False

def test_redis_connection():
    """Test Redis connection"""
    print("\n🧪 Testing Redis Connection")
    print("=" * 30)
    
    try:
        from config.redis_config import redis_config
        
        redis_client = redis_config.get_sync_connection()
        result = redis_client.ping()
        
        if result:
            print("   ✅ Redis connection successful")
            return True
        else:
            print("   ❌ Redis ping failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Redis connection failed: {e}")
        traceback.print_exc()
        return False

def test_login_handler():
    """Test login handler directly"""
    print("\n🧪 Testing Login Handler")
    print("=" * 30)
    
    try:
        from handlers.login import handle_login
        
        test_data = {
            "username": "admin",
            "password": "Hdfatboy1!"
        }
        
        print("   🔍 Testing login handler...")
        response, session = handle_login(test_data, "127.0.0.1")
        
        if response.get('user_exists'):
            print("   ✅ Login handler working")
            print(f"      User exists: {response.get('user_exists')}")
            print(f"      Is manager: {response.get('is_manager')}")
            print(f"      Session ID: {response.get('session_id', 'N/A')[:20]}...")
            return True
        else:
            print("   ❌ Login handler failed")
            print(f"      Error: {response.get('error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Login handler test failed: {e}")
        traceback.print_exc()
        return False

def test_server_startup():
    """Test server startup components"""
    print("\n🧪 Testing Server Startup Components")
    print("=" * 40)
    
    try:
        print("   📦 Importing Server module...")
        import Server
        print("   ✅ Server module imported successfully")
        
        print("   🔍 Testing handle_request function...")
        response = Server.handle_request(10, {"username": "admin", "password": "Hdfatboy1!"}, "test_client")
        
        if response.get('request_id') == 10:
            print("   ✅ handle_request function working")
            print(f"      Response: {response}")
            return True
        else:
            print("   ❌ handle_request function failed")
            print(f"      Response: {response}")
            return False
            
    except Exception as e:
        print(f"   ❌ Server startup test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all startup tests"""
    print("🚀 EasyShifts Server Startup Diagnostics")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Environment Variables", test_environment),
        ("Database Connection", test_database_connection),
        ("Redis Connection", test_redis_connection),
        ("Login Handler", test_login_handler),
        ("Server Startup", test_server_startup)
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
    print(f"\n{'='*50}")
    print("STARTUP DIAGNOSTICS SUMMARY")
    print('='*50)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All startup tests passed!")
        print("The server should be able to start successfully.")
        print("\nTry starting the server with:")
        print("cd Backend && python Server.py")
    else:
        print("\n❌ Some startup tests failed.")
        print("Fix the issues above before starting the server.")
    
    return all_passed

if __name__ == "__main__":
    main()
