#!/usr/bin/env python3
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
    print("\n🧪 Testing Fixed Redis Configuration")
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
    
    print("\n📊 Test Results:")
    print(f"   Original Config: {'✅ Working' if original_works else '❌ Failed'}")
    print(f"   Fixed Config: {'✅ Working' if fixed_works else '❌ Failed'}")
    
    if original_works:
        print("\n✅ Original Redis configuration is working!")
        print("   No changes needed to Redis setup.")
    elif fixed_works:
        print("\n🔧 Fixed Redis configuration works!")
        print("   Consider updating imports to use fixed config.")
    else:
        print("\n❌ Both configurations failed!")
        print("   Check Redis server status and credentials.")

if __name__ == "__main__":
    main()
