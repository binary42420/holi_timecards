#!/usr/bin/env python3
"""
Test the original Cloud Run service to see if it's working
"""

import asyncio
import json
import websockets
import aiohttp

async def test_original_service():
    """Test the original service"""
    print("🧪 Testing Original Cloud Run Service")
    print("=" * 40)
    
    # Original service URL
    base_url = "https://easyshifts-backend-s5b2sxgpsa-uc.a.run.app"
    ws_url = "wss://easyshifts-backend-s5b2sxgpsa-uc.a.run.app/ws"
    
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
            
            print(f"   📥 Full Response:")
            print(json.dumps(response, indent=4))
            
            if response.get('request_id') == 10:
                print("   ✅ Correct request_id received")
                
                data = response.get('data', {})
                if data.get('user_exists'):
                    print("   🎉 LOGIN SUCCESSFUL!")
                    return True
                else:
                    error = data.get('error', 'Unknown error')
                    print(f"   ❌ Login failed: {error}")
                    return False
            else:
                print(f"   ❌ Wrong request_id: expected 10, got {response.get('request_id')}")
                return False
                
    except Exception as e:
        print(f"   ❌ WebSocket test failed: {e}")
        return False

async def test_new_service():
    """Test the new service"""
    print("\n🧪 Testing New Cloud Run Service")
    print("=" * 40)
    
    # New service URL
    base_url = "https://easyshifts-backend-794306818447.us-central1.run.app"
    ws_url = "wss://easyshifts-backend-794306818447.us-central1.run.app/ws"
    
    print(f"🌐 Service URL: {base_url}")
    print(f"🔌 WebSocket URL: {ws_url}")
    
    # Test health endpoint
    print("\n1️⃣ Testing Health Endpoint...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health", timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"   ✅ Health check passed:")
                    print(f"      Status: {data.get('status')}")
                    return True
                else:
                    print(f"   ❌ Health check failed: HTTP {resp.status}")
                    return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("🚀 Cloud Run Service Comparison")
        print("=" * 35)
        
        # Test original service
        original_works = await test_original_service()
        
        # Test new service
        new_works = await test_new_service()
        
        print(f"\n{'='*35}")
        print("SERVICE COMPARISON RESULTS")
        print('='*35)
        print(f"Original Service: {'✅ WORKING' if original_works else '❌ FAILED'}")
        print(f"New Service: {'✅ WORKING' if new_works else '❌ FAILED'}")
        
        if original_works:
            print("\n💡 RECOMMENDATION: Use the original service")
            print("The original service is working and has the database data.")
            print("Update frontend to use:")
            print("wss://easyshifts-backend-s5b2sxgpsa-uc.a.run.app/ws")
        elif new_works:
            print("\n💡 RECOMMENDATION: Use the new service")
            print("But check why login is failing - might be database issue.")
        else:
            print("\n❌ BOTH SERVICES HAVE ISSUES")
            print("Need to investigate Cloud Run deployment problems.")
    
    asyncio.run(main())
