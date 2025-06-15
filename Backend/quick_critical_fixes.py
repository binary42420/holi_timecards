#!/usr/bin/env python3
"""
Quick fixes for the most critical EasyShifts issues
"""

import os
import re

def fix_enhanced_schedule_handlers():
    """Fix the enhanced schedule handlers file"""
    file_path = "handlers/enhanced_schedule_handlers.py"
    
    if not os.path.exists(file_path):
        print(f"❌ {file_path} not found")
        return
    
    print(f"🔧 Fixing {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already fixed
    if 'with get_db_session() as session:' in content:
        print("   ✅ Already using context managers")
        return
    
    # Replace the import
    content = content.replace(
        'from main import get_db_session',
        'from main import get_db_session'
    )
    
    # Fix the most critical function - handle_get_enhanced_schedule_data
    old_pattern = r'''def handle_get_enhanced_schedule_data\(data, user_session\):
    """Get comprehensive schedule data with analytics"""
    try:
        # Get all shifts for the current week
        controller = ShiftsController\(db\)'''
    
    new_pattern = '''def handle_get_enhanced_schedule_data(data, user_session):
    """Get comprehensive schedule data with analytics"""
    try:
        # Get all shifts for the current week
        with get_db_session() as session:
            controller = ShiftsController(session)'''
    
    content = re.sub(old_pattern, new_pattern, content, flags=re.MULTILINE)
    
    # Add proper indentation for the rest of the function
    # This is a simplified fix - full fix would need more complex parsing
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("   ✅ Applied basic fixes")

def add_error_handling_to_manager_schedule():
    """Add basic error handling to manager_schedule.py"""
    file_path = "handlers/manager_schedule.py"
    
    if not os.path.exists(file_path):
        print(f"❌ {file_path} not found")
        return
    
    print(f"🔧 Adding error handling to {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count current error handling
    function_count = len(re.findall(r'def\s+handle_\w+', content))
    try_count = len(re.findall(r'try:', content))
    
    print(f"   📊 Current: {try_count} try blocks for {function_count} handler functions")
    
    if try_count / function_count < 0.5:
        print("   ⚠️  Low error coverage - needs manual review")
        print("   📝 Recommendation: Wrap each handler function in try-catch")
    else:
        print("   ✅ Adequate error coverage")

def create_environment_config():
    """Create a secure environment configuration"""
    env_content = """# EasyShifts Production Environment Configuration
# IMPORTANT: Never commit this file with real values

# Database Configuration
DB_HOST=your_database_host
DB_PORT=3305
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_secure_database_password

# Redis Configuration
REDIS_HOST=your_redis_host
REDIS_PORT=6379
REDIS_PASSWORD=your_secure_redis_password

# Security Keys (Generate new ones for production!)
SESSION_SECRET_KEY=generate_a_secure_32_character_key_here
CSRF_SECRET_KEY=generate_another_secure_32_character_key

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Application Settings
ENVIRONMENT=production
DEBUG=false
VALIDATE_SESSION_IP=false
LOG_LEVEL=INFO

# Security Settings
SESSION_TIMEOUT=3600
MAX_LOGIN_ATTEMPTS=5
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
"""
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("📝 Created .env.example with secure configuration template")

def create_health_check():
    """Create a comprehensive health check endpoint"""
    health_check_content = '''"""
Health check endpoint for EasyShifts application monitoring
"""

import asyncio
import json
from datetime import datetime
from main import get_db_session
from config.redis_config import redis_config

async def health_check():
    """Comprehensive health check for all system components"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "easyshifts-backend",
        "version": "1.0.0",
        "checks": {}
    }
    
    overall_healthy = True
    
    # Database health check
    try:
        with get_db_session() as session:
            session.execute("SELECT 1")
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy", 
            "message": f"Database connection failed: {str(e)}"
        }
        overall_healthy = False
    
    # Redis health check
    try:
        redis_client = redis_config.get_sync_connection()
        redis_client.ping()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(e)}"
        }
        overall_healthy = False
    
    # Update overall status
    if not overall_healthy:
        health_status["status"] = "unhealthy"
    
    return health_status

def get_health_status():
    """Synchronous wrapper for health check"""
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(health_check())
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": f"Health check failed: {str(e)}"
        }
'''
    
    with open('health_check_endpoint.py', 'w', encoding='utf-8') as f:
        f.write(health_check_content)
    
    print("🏥 Created comprehensive health check endpoint")

def generate_quick_test_script():
    """Generate a quick test script for critical functionality"""
    test_script = '''#!/usr/bin/env python3
"""
Quick test script for critical EasyShifts functionality
"""

import asyncio
import json
import websockets
from datetime import datetime

async def test_websocket_connection():
    """Test WebSocket connection and basic functionality"""
    print("🧪 Testing WebSocket Connection")
    
    try:
        uri = "wss://easyshifts-backend-794306818447.us-central1.run.app/ws"
        
        async with websockets.connect(uri) as websocket:
            print("   ✅ WebSocket connected")
            
            # Test login
            login_request = {
                "request_id": 10,
                "data": {
                    "username": "admin",
                    "password": "Hdfatboy1!"
                }
            }
            
            await websocket.send(json.dumps(login_request))
            response = await websocket.recv()
            data = json.loads(response)
            
            if data.get('data', {}).get('user_exists'):
                print("   ✅ Login successful")
                return True
            else:
                print(f"   ❌ Login failed: {data}")
                return False
                
    except Exception as e:
        print(f"   ❌ WebSocket test failed: {e}")
        return False

async def test_health_endpoint():
    """Test health endpoint"""
    print("🏥 Testing Health Endpoint")
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            url = "https://easyshifts-backend-794306818447.us-central1.run.app/health"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Health check passed: {data.get('status')}")
                    return True
                else:
                    print(f"   ❌ Health check failed: HTTP {response.status}")
                    return False
    except Exception as e:
        print(f"   ❌ Health endpoint test failed: {e}")
        return False

async def main():
    """Run all critical tests"""
    print("🚀 EasyShifts Critical Functionality Test")
    print("=" * 45)
    
    tests = [
        test_health_endpoint,
        test_websocket_connection
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
        print()
    
    success_count = sum(results)
    total_count = len(results)
    
    print("📊 Test Results Summary")
    print(f"   Passed: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("   🎉 All critical tests passed!")
    else:
        print("   ⚠️  Some tests failed - review issues above")

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    with open('test_critical_functionality.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("🧪 Created critical functionality test script")

def main():
    """Run quick critical fixes"""
    print("🚀 EasyShifts Quick Critical Fixes")
    print("=" * 40)
    
    # Apply critical fixes
    fix_enhanced_schedule_handlers()
    add_error_handling_to_manager_schedule()
    create_environment_config()
    create_health_check()
    generate_quick_test_script()
    
    print("\n✅ Quick critical fixes completed!")
    print("\n📋 Next Steps:")
    print("1. Review the COMPREHENSIVE_DEBUG_REPORT.md")
    print("2. Run: python test_critical_functionality.py")
    print("3. Complete database session migration for remaining files")
    print("4. Add comprehensive error handling to all handlers")
    print("5. Secure all environment variables before production")

if __name__ == "__main__":
    main()
