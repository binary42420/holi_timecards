#!/usr/bin/env python3
"""
Load environment variables and test Redis connection
"""

import os
import sys
from pathlib import Path

def load_environment():
    """Load environment variables from .env file"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    print("📋 Loading environment variables from .env")
    
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
                if 'PASSWORD' in key or 'SECRET' in key:
                    print(f"   ✅ {key}: ***")
                else:
                    print(f"   ✅ {key}: {value}")
    
    return True

def test_redis_with_env():
    """Test Redis connection with loaded environment"""
    print("\n🧪 Testing Redis with Environment Variables")
    print("=" * 45)
    
    try:
        # Import after environment is loaded
        from config.redis_config import redis_config, session_manager
        
        print("📋 Redis Configuration:")
        print(f"   Host: {redis_config.host}")
        print(f"   Port: {redis_config.port}")
        print(f"   Password: {'***' if redis_config.password else 'None'}")
        print(f"   Session Timeout: {redis_config.session_timeout}s")
        print()
        
        # Test connection
        print("🔌 Testing Connection...")
        redis_client = redis_config.get_sync_connection()
        ping_result = redis_client.ping()
        print(f"   ✅ Ping Result: {ping_result}")
        
        # Test session management
        print("🧪 Testing Session Management...")
        test_session_data = {
            'user_id': 1,
            'username': 'test_user',
            'is_manager': False,
            'test_mode': True
        }
        
        session_id = 'test_session_12345'
        
        # Create session
        create_success = session_manager.create_session(session_id, test_session_data)
        print(f"   ✅ Session Creation: {create_success}")
        
        if create_success:
            # Retrieve session
            retrieved_data = session_manager.get_session(session_id)
            print(f"   ✅ Session Retrieval: {retrieved_data is not None}")
            
            if retrieved_data:
                print(f"   📊 Retrieved Data: {retrieved_data.get('username')}")
            
            # Delete session
            delete_success = session_manager.delete_session(session_id)
            print(f"   ✅ Session Deletion: {delete_success}")
            
            return True
        else:
            print("   ❌ Session creation failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Redis Test Failed: {e}")
        return False

def test_login_functionality():
    """Test the actual login functionality"""
    print("\n🔐 Testing Login Functionality")
    print("=" * 35)
    
    try:
        from handlers.login import handle_login
        
        # Test login with admin credentials
        login_data = {
            'username': 'admin',
            'password': 'Hdfatboy1!'
        }
        
        print("🧪 Testing admin login...")
        response, user_session = handle_login(login_data, '127.0.0.1')
        
        print(f"   📊 Response: {response}")
        
        if response.get('data', {}).get('user_exists'):
            print("   ✅ Login successful!")
            return True
        else:
            print(f"   ❌ Login failed: {response.get('data', {}).get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Login test failed: {e}")
        return False

def create_startup_script():
    """Create a startup script that loads environment and starts server"""
    startup_script = '''#!/usr/bin/env python3
"""
EasyShifts Server Startup with Environment Loading
"""

import os
import sys
from pathlib import Path

def load_environment():
    """Load environment variables from .env file"""
    env_file = Path('.env')
    
    if env_file.exists():
        print("📋 Loading environment variables...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Environment variables loaded")
    else:
        print("⚠️  No .env file found, using system environment")

def main():
    """Start server with environment loaded"""
    print("🚀 Starting EasyShifts Server with Environment")
    print("=" * 50)
    
    # Load environment first
    load_environment()
    
    # Import and start server
    try:
        import Server
        import asyncio
        
        print("🔌 Starting combined HTTP/WebSocket server...")
        asyncio.run(Server.start_combined_server())
        
    except KeyboardInterrupt:
        print("\\n⏹️  Server stopped by user")
    except Exception as e:
        print(f"\\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
'''
    
    with open('start_server_with_env.py', 'w', encoding='utf-8') as f:
        f.write(startup_script)
    
    print("✅ Created start_server_with_env.py")

def main():
    """Run environment loading and Redis testing"""
    print("🚀 EasyShifts Environment & Redis Setup")
    print("=" * 45)
    
    # Load environment
    env_loaded = load_environment()
    
    if not env_loaded:
        print("❌ Failed to load environment")
        return
    
    # Test Redis
    redis_works = test_redis_with_env()
    
    # Test login
    login_works = test_login_functionality()
    
    # Create startup script
    create_startup_script()
    
    print("\n" + "=" * 45)
    print("📊 RESULTS SUMMARY")
    print("=" * 45)
    print(f"Environment Loading: {'✅ Success' if env_loaded else '❌ Failed'}")
    print(f"Redis Connection: {'✅ Working' if redis_works else '❌ Failed'}")
    print(f"Login Functionality: {'✅ Working' if login_works else '❌ Failed'}")
    
    if redis_works and login_works:
        print("\n🎉 All systems working!")
        print("📋 Next steps:")
        print("1. Use: python start_server_with_env.py")
        print("2. Test login in frontend")
        print("3. Deploy updated backend")
    elif redis_works:
        print("\n✅ Redis is working!")
        print("⚠️  Login may need additional debugging")
    else:
        print("\n❌ Redis connection issues remain")
        print("📋 Check Redis server status and credentials")

if __name__ == "__main__":
    main()
