#!/usr/bin/env python3
"""
Test the newly deployed Cloud Run service
"""

import asyncio
import json
import websockets
import aiohttp

async def test_new_deployment():
    """Test the newly deployed service"""
    print("🧪 Testing New Cloud Run Deployment")
    print("=" * 40)
    
    # New service URL from deployment
    base_url = "https://easyshifts-backend-794306818447.us-central1.run.app"
    ws_url = "wss://easyshifts-backend-794306818447.us-central1.run.app/ws"
    
    print(f"🌐 Service URL: {base_url}")
    print(f"🔌 WebSocket URL: {ws_url}")
    
    # Test 1: Health endpoint
    print("\n1️⃣ Testing Health Endpoint...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health", timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"   ✅ Health check passed:")
                    print(f"      Status: {data.get('status')}")
                    print(f"      Service: {data.get('service')}")
                    print(f"      Timestamp: {data.get('timestamp')}")
                else:
                    print(f"   ❌ Health check failed: HTTP {resp.status}")
                    return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: WebSocket connection
    print("\n2️⃣ Testing WebSocket Connection...")
    try:
        async with websockets.connect(ws_url) as websocket:
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
            
            print(f"   📥 Response received:")
            print(f"      Request ID: {response.get('request_id')}")
            print(f"      User Exists: {response.get('data', {}).get('user_exists')}")
            
            if response.get('request_id') == 10:
                print("   ✅ Correct request_id received")
                
                if response.get('data', {}).get('user_exists'):
                    print("   🎉 LOGIN SUCCESSFUL!")
                    print(f"      Session ID: {response['data'].get('session_id', 'N/A')[:20]}...")
                    print(f"      CSRF Token: {response['data'].get('csrf_token', 'N/A')[:20]}...")
                    print(f"      Is Manager: {response['data'].get('is_manager')}")
                    print(f"      Is Admin: {response['data'].get('is_admin')}")
                    print(f"      User ID: {response['data'].get('user_id')}")
                    return True
                else:
                    error = response.get('data', {}).get('error', 'Unknown error')
                    print(f"   ❌ Login failed: {error}")
                    
                    if "Session service temporarily unavailable" in error:
                        print("   🔧 Redis connection still has issues")
                    elif "Invalid username or password" in error:
                        print("   🔧 Database connection issue or wrong credentials")
                    
                    return False
            else:
                print(f"   ❌ Wrong request_id: expected 10, got {response.get('request_id')}")
                return False
                
    except Exception as e:
        print(f"   ❌ WebSocket test failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_new_deployment())
    
    print(f"\n{'='*40}")
    if result:
        print("🎉 ALL TESTS PASSED!")
        print("The new deployment is working perfectly!")
        print("✅ WebSocket connection: Working")
        print("✅ Login system: Working") 
        print("✅ Session creation: Working")
        print("✅ Redis connection: Working")
        print("\n🔄 UPDATE FRONTEND:")
        print("Update your frontend to use the new WebSocket URL:")
        print("wss://easyshifts-backend-794306818447.us-central1.run.app/ws")
    else:
        print("❌ SOME TESTS FAILED")
        print("Check the error messages above for details.")
    
    print(f"{'='*40}")
