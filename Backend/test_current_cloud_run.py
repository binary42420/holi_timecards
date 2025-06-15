#!/usr/bin/env python3
"""
Test the current Cloud Run WebSocket connection
"""

import asyncio
import json
import websockets
import aiohttp

async def test_current_cloud_run():
    """Test the current Cloud Run service"""
    print("🧪 Testing Current Cloud Run Service")
    print("=" * 40)
    
    # Test 1: Health endpoint
    print("1️⃣ Testing Health Endpoint...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://easyshifts-backend-794306818447.us-central1.run.app/health", timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"   ✅ Health check passed: {data}")
                else:
                    print(f"   ❌ Health check failed: HTTP {resp.status}")
                    return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: WebSocket connection
    print("\n2️⃣ Testing WebSocket Connection...")
    try:
        async with websockets.connect("wss://easyshifts-backend-794306818447.us-central1.run.app/ws") as websocket:
            print("   ✅ WebSocket connected successfully")
            
            # Test 3: Login request
            print("\n3️⃣ Testing Login Request...")
            login_request = {
                "request_id": 10,
                "data": {
                    "username": "admin",
                    "password": "Hdfatboy1!"
                }
            }
            
            await websocket.send(json.dumps(login_request))
            print("   📤 Login request sent")
            
            response_data = await asyncio.wait_for(websocket.recv(), timeout=15)
            response = json.loads(response_data)
            
            print(f"   📥 Response received: {response}")
            
            if response.get('request_id') == 10:
                print("   ✅ Correct request_id received")
                
                if response.get('data', {}).get('user_exists'):
                    print("   🎉 LOGIN SUCCESSFUL!")
                    print(f"      Session ID: {response['data'].get('session_id', 'N/A')[:20]}...")
                    print(f"      Is Manager: {response['data'].get('is_manager')}")
                    print(f"      Is Admin: {response['data'].get('is_admin')}")
                    return True
                else:
                    error = response.get('data', {}).get('error', 'Unknown error')
                    print(f"   ❌ Login failed: {error}")
                    
                    if "Session service temporarily unavailable" in error:
                        print("   🔧 This indicates a Redis connection issue on Cloud Run")
                        print("   💡 The environment variables need to be updated on Cloud Run")
                    
                    return False
            else:
                print(f"   ❌ Wrong request_id: expected 10, got {response.get('request_id')}")
                return False
                
    except Exception as e:
        print(f"   ❌ WebSocket test failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_current_cloud_run())
    
    print(f"\n{'='*40}")
    if result:
        print("🎉 ALL TESTS PASSED!")
        print("The Cloud Run service is working correctly.")
        print("You can now test the frontend login.")
    else:
        print("❌ TESTS FAILED")
        print("The Redis connection issue still exists on Cloud Run.")
        print("Environment variables need to be updated on the Cloud Run service.")
    
    print(f"{'='*40}")
