#!/usr/bin/env python3
"""
Simple WebSocket test to verify server is responding correctly
"""

import asyncio
import json
import sys

async def test_websocket_login():
    """Test WebSocket login with simple websockets library"""
    print("🧪 Testing WebSocket Login")
    print("=" * 30)
    
    try:
        # Use a simpler approach
        import websockets
        
        ws_url = "ws://localhost:8080/ws"
        print(f"🔌 Connecting to: {ws_url}")
        
        # Connect with a longer timeout
        async with websockets.connect(ws_url) as websocket:
            print("✅ Connected to WebSocket server")
            
            # Send login request
            login_request = {
                "request_id": 10,
                "data": {
                    "username": "admin",
                    "password": "Hdfatboy1!"
                }
            }
            
            print(f"📤 Sending: {json.dumps(login_request)}")
            await websocket.send(json.dumps(login_request))
            
            # Wait for response
            print("⏳ Waiting for response...")
            response_data = await websocket.recv()
            
            print(f"📥 Raw response: {response_data}")
            
            # Parse response
            response = json.loads(response_data)
            print(f"📋 Parsed response: {json.dumps(response, indent=2)}")
            
            # Check response
            if response.get('request_id') == 10:
                print("✅ Correct request_id received")
                
                if response.get('data', {}).get('user_exists'):
                    print("✅ Login successful!")
                    print(f"   Session ID: {response['data'].get('session_id', 'N/A')[:20]}...")
                    print(f"   CSRF Token: {response['data'].get('csrf_token', 'N/A')[:20]}...")
                    return True
                else:
                    print("❌ Login failed")
                    print(f"   Error: {response.get('data', {}).get('error')}")
                    return False
            else:
                print(f"❌ Wrong request_id: expected 10, got {response.get('request_id')}")
                return False
                
    except ConnectionRefusedError:
        print("❌ Connection refused - server not running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_multiple_requests():
    """Test multiple different requests to see response patterns"""
    print("\n🧪 Testing Multiple Request Types")
    print("=" * 40)
    
    test_requests = [
        {"request_id": 10, "data": {"username": "admin", "password": "Hdfatboy1!"}, "name": "Login"},
        {"request_id": 211, "data": {}, "name": "Get Jobs by Manager"},
        {"request_id": 999, "data": {}, "name": "Unknown Request"},
    ]
    
    try:
        import websockets
        
        for test_req in test_requests:
            print(f"\n🔍 Testing: {test_req['name']} (ID: {test_req['request_id']})")
            
            async with websockets.connect("ws://localhost:8080/ws") as websocket:
                await websocket.send(json.dumps(test_req))
                response_data = await websocket.recv()
                response = json.loads(response_data)
                
                print(f"   📤 Sent request_id: {test_req['request_id']}")
                print(f"   📥 Received request_id: {response.get('request_id')}")
                print(f"   📋 Success: {response.get('success', response.get('data', {}).get('user_exists', 'N/A'))}")
                
                if response.get('request_id') != test_req['request_id']:
                    print(f"   ⚠️ REQUEST ID MISMATCH!")
                    
    except Exception as e:
        print(f"❌ Multiple request test failed: {e}")

async def main():
    """Run WebSocket tests"""
    print("🚀 Simple WebSocket Test")
    print("=" * 30)
    
    # Test 1: Basic login
    login_success = await test_websocket_login()
    
    # Test 2: Multiple requests
    await test_multiple_requests()
    
    print(f"\n{'='*30}")
    if login_success:
        print("✅ WebSocket login test PASSED")
        print("The server is responding correctly to login requests.")
        print("\nIf you're still seeing request_id 211 in the frontend,")
        print("the issue is likely in the frontend WebSocket handling.")
    else:
        print("❌ WebSocket login test FAILED")
        print("Check the server logs and error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
