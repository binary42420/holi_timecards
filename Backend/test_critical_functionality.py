#!/usr/bin/env python3
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
