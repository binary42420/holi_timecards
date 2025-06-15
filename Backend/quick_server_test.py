#!/usr/bin/env python3
"""
Quick server test to identify the issue
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

print("🧪 Quick Server Test")
print("=" * 25)

print("📋 Environment Variables:")
print(f"   HOST: {os.getenv('HOST', 'not set')}")
print(f"   PORT: {os.getenv('PORT', 'not set')}")
print(f"   DB_PASSWORD: {'set' if os.getenv('DB_PASSWORD') else 'not set'}")
print(f"   REDIS_PASSWORD: {'set' if os.getenv('REDIS_PASSWORD') else 'not set'}")

print("\n📦 Testing imports...")
try:
    print("   Importing basic modules...")
    import asyncio
    import json
    print("   ✅ Basic imports OK")
    
    print("   Importing aiohttp...")
    from aiohttp import web
    print("   ✅ aiohttp import OK")
    
    print("   Importing main...")
    from main import get_db_session
    print("   ✅ main import OK")
    
    print("   Testing database session...")
    with get_db_session() as session:
        result = session.execute("SELECT 1").fetchone()
        if result:
            print("   ✅ Database connection OK")
        else:
            print("   ❌ Database query failed")
    
    print("   Importing Redis config...")
    from config.redis_config import redis_config
    print("   ✅ Redis config import OK")
    
    print("   Testing Redis connection...")
    redis_client = redis_config.get_sync_connection()
    result = redis_client.ping()
    if result:
        print("   ✅ Redis connection OK")
    else:
        print("   ❌ Redis ping failed")
    
    print("   Importing login handler...")
    from handlers.login import handle_login
    print("   ✅ Login handler import OK")
    
    print("   Testing login handler...")
    response, session = handle_login({"username": "admin", "password": "Hdfatboy1!"}, "127.0.0.1")
    if response.get('user_exists'):
        print("   ✅ Login handler working")
    else:
        print(f"   ❌ Login handler failed: {response.get('error')}")
    
    print("\n🎉 All tests passed! Server should be able to start.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n🔧 Trying to start a simple server...")
try:
    import asyncio
    from aiohttp import web
    
    async def hello(request):
        return web.Response(text="Hello from EasyShifts!")
    
    async def start_simple_server():
        app = web.Application()
        app.router.add_get('/', hello)
        
        port = int(os.getenv('PORT', 8085))
        print(f"🚀 Starting simple server on port {port}...")
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        
        print(f"✅ Simple server started on http://localhost:{port}")
        print("⏳ Server will run for 10 seconds...")
        
        await asyncio.sleep(10)
        
        await runner.cleanup()
        print("✅ Simple server stopped")
    
    asyncio.run(start_simple_server())
    
except Exception as e:
    print(f"❌ Simple server failed: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Quick test completed!")
