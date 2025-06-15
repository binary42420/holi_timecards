#!/usr/bin/env python3
"""
Redis Authentication Fix Script
Fixes Redis authentication issues causing session creation failures.
"""

import os
import sys
from pathlib import Path

def check_environment_variables():
    """Check critical environment variables"""
    print("🔍 Checking Environment Variables")
    print("=" * 40)
    
    required_vars = {
        'DB_PASSWORD': 'Database password',
        'REDIS_PASSWORD': 'Redis password',
        'PORT': 'Server port (defaults to 8080)',
        'HOST': 'Server host (defaults to 0.0.0.0)'
    }
    
    missing_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var:
                print(f"✅ {var}: ****** (set)")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET ({description})")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing {len(missing_vars)} critical environment variables!")
        return False, missing_vars
    else:
        print("\n✅ All critical environment variables are set")
        return True, []

def fix_environment_variables():
    """Fix missing environment variables"""
    print("\n🔧 Fixing Environment Variables")
    print("=" * 35)
    
    fixes_applied = []
    
    # Fix 1: Ensure PORT environment variable is set
    if not os.getenv('PORT'):
        os.environ['PORT'] = '8080'
        fixes_applied.append("Set default PORT=8080")
        print("✅ Set default PORT=8080")
    
    # Fix 2: Ensure HOST environment variable is set
    if not os.getenv('HOST'):
        os.environ['HOST'] = '0.0.0.0'
        fixes_applied.append("Set default HOST=0.0.0.0")
        print("✅ Set default HOST=0.0.0.0")
    
    # Fix 3: Set database passwords from known values if missing
    if not os.getenv('DB_PASSWORD'):
        os.environ['DB_PASSWORD'] = 'a61d15d9b4f2671739338d1082cc7b75c0084e21'
        fixes_applied.append("Set DB_PASSWORD from known value")
        print("✅ Set DB_PASSWORD from known value")
    
    if not os.getenv('REDIS_PASSWORD'):
        os.environ['REDIS_PASSWORD'] = 'AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa'
        fixes_applied.append("Set REDIS_PASSWORD from known value")
        print("✅ Set REDIS_PASSWORD from known value")
    
    if fixes_applied:
        print(f"\n✅ Applied {len(fixes_applied)} fixes:")
        for fix in fixes_applied:
            print(f"   • {fix}")
    else:
        print("ℹ️  No fixes needed")
    
    return fixes_applied

def test_redis_connection():
    """Test Redis connection with authentication"""
    print("\n🔍 Testing Redis Connection")
    print("=" * 30)

    try:
        from security.secure_session import secure_session_manager
        
        # Test creating a session to verify Redis works
        test_user_data = {
            "user_id": 1,
            "username": "test_user",
            "is_manager": True,
            "login_method": "test"
        }
        
        print("🔍 Testing Redis session creation...")
        session_id, csrf_token = secure_session_manager.create_secure_session(test_user_data, "127.0.0.1")
        
        if session_id and csrf_token:
            print("✅ Redis connection and session creation successful")
            print(f"   Session ID: {session_id[:20]}...")
            print(f"   CSRF Token: {csrf_token[:20]}...")
            
            # Clean up test session
            secure_session_manager.invalidate_session(session_id)
            print("✅ Test session cleaned up")
            return True
        else:
            print("❌ Session creation returned None values")
            return False

    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def main():
    """Main fix function"""
    print("🔧 Redis Authentication Fix Tool")
    print("=" * 40)
    
    # Step 1: Check environment variables
    env_ok, missing_vars = check_environment_variables()
    
    # Step 2: Apply fixes if needed
    if not env_ok:
        fixes = fix_environment_variables()
        print(f"\n✅ Applied {len(fixes)} environment fixes")
    
    # Step 3: Test Redis connection
    redis_ok = test_redis_connection()
    
    # Summary
    print("\n📋 Fix Summary")
    print("=" * 15)
    print(f"Environment Variables: {'✅' if env_ok or not missing_vars else '❌'}")
    print(f"Redis Connection: {'✅' if redis_ok else '❌'}")
    
    if redis_ok:
        print("\n🎉 Redis authentication is working!")
        print("\n📝 Next steps:")
        print("   1. Start the backend server")
        print("   2. Test Google authentication")
        print("   3. Verify session creation works")
        return True
    else:
        print("\n⚠️  Redis authentication issues remain.")
        print("\nPossible solutions:")
        print("   1. Check Redis Cloud credentials")
        print("   2. Verify network connectivity")
        print("   3. Check Redis server status")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
