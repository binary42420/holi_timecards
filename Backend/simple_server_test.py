#!/usr/bin/env python3
"""
Simple server test to verify the server can start
"""

import os
import sys
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_server_startup():
    """Test if we can start the server components"""
    print("🧪 Testing Server Startup")
    print("=" * 30)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from aiohttp import web
        import aiohttp_cors
        print("✅ aiohttp imports successful")
        
        # Test server creation
        print("🔧 Testing server creation...")
        
        async def handle_test(request):
            return web.Response(text="Test server working", content_type='text/plain')
        
        app = web.Application()
        app.router.add_get('/test', handle_test)
        
        print("✅ Server app created successfully")
        
        # Try to start on different ports
        ports_to_try = [8081, 8082, 8083, 8084]
        
        for port in ports_to_try:
            try:
                print(f"🔌 Trying to start server on port {port}...")
                
                runner = web.AppRunner(app)
                await runner.setup()
                
                site = web.TCPSite(runner, '0.0.0.0', port)
                await site.start()
                
                print(f"✅ Server started successfully on port {port}")
                print(f"🌐 Test URL: http://localhost:{port}/test")
                
                # Test the server
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'http://localhost:{port}/test') as resp:
                        text = await resp.text()
                        if text == "Test server working":
                            print("✅ Server responding correctly")
                        else:
                            print(f"❌ Unexpected response: {text}")
                
                # Clean up
                await runner.cleanup()
                print(f"✅ Server stopped cleanly")
                return port
                
            except OSError as e:
                if "Address already in use" in str(e):
                    print(f"⚠️ Port {port} already in use")
                    continue
                else:
                    print(f"❌ Error on port {port}: {e}")
                    continue
            except Exception as e:
                print(f"❌ Error starting server on port {port}: {e}")
                continue
        
        print("❌ Could not start server on any port")
        return None
        
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_holi_server():
    """Test the actual EasyShifts server"""
    print("\n🧪 Testing EasyShifts Server")
    print("=" * 35)
    
    try:
        # Set a custom port
        os.environ['PORT'] = '8085'
        
        print("📦 Importing Server module...")
        import Server
        
        print("✅ Server module imported")
        
        print("🔧 Creating server app...")
        app = await Server.create_combined_app()
        
        print("✅ Server app created")
        
        print("🔌 Starting server on port 8085...")
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', 8085)
        await site.start()
        
        print("✅ EasyShifts server started on port 8085")
        print("🌐 Health check: http://localhost:8085/health")
        print("🔌 WebSocket: ws://localhost:8085/ws")
        
        # Test health endpoint
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8085/health') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Health check passed: {data}")
                else:
                    print(f"❌ Health check failed: {resp.status}")
        
        # Keep server running for a bit
        print("⏳ Server running... (will stop in 5 seconds)")
        await asyncio.sleep(5)
        
        # Clean up
        await runner.cleanup()
        print("✅ EasyShifts server stopped cleanly")
        
        return True
        
    except Exception as e:
        print(f"❌ EasyShifts server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run server tests"""
    print("🚀 EasyShifts Server Test")
    print("=" * 30)
    
    # Test 1: Basic server startup
    port = await test_server_startup()
    
    if port:
        print(f"\n✅ Basic server test passed on port {port}")
        
        # Test 2: EasyShifts server
        holi_ok = await test_holi_server()
        
        if holi_ok:
            print("\n🎉 All server tests passed!")
            print("The EasyShifts server can start successfully.")
            print("\nTo start the server manually:")
            print("cd Backend")
            print("set PORT=8085")
            print("python Server.py")
        else:
            print("\n❌ EasyShifts server test failed")
    else:
        print("\n❌ Basic server test failed")

if __name__ == "__main__":
    asyncio.run(main())
