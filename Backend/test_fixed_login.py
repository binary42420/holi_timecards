#!/usr/bin/env python3
"""
Test the login with the correct admin password
"""

import asyncio
import json
import websockets

async def test_correct_admin_login():
    """Test login with the correct admin credentials"""
    print("🧪 Testing Correct Admin Login")
    print("=" * 35)
    
    ws_url = "wss://easyshifts-backend-794306818447.us-central1.run.app/ws"
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connected successfully")
            
            # Test with correct admin credentials
            login_request = {
                "request_id": 10,
                "data": {
                    "username": "admin",
                    "password": "Hdfatboy1!"
                }
            }
            
            print("📤 Sending login request with correct admin password...")
            await websocket.send(json.dumps(login_request))
            
            response_data = await asyncio.wait_for(websocket.recv(), timeout=15)
            response = json.loads(response_data)
            
            print("📥 Response received:")
            print(json.dumps(response, indent=2))
            
            data = response.get('data', {})
            if data.get('user_exists'):
                print("\n🎉 LOGIN SUCCESSFUL!")
                print(f"   Session ID: {data.get('session_id', 'N/A')[:20]}...")
                print(f"   CSRF Token: {data.get('csrf_token', 'N/A')[:20]}...")
                print(f"   Is Manager: {data.get('is_manager')}")
                print(f"   Is Admin: {data.get('is_admin')}")
                print(f"   User ID: {data.get('user_id')}")
                return True
            else:
                error = data.get('error', 'Unknown error')
                print(f"\n❌ Login failed: {error}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_correct_admin_login())
    
    print(f"\n{'='*35}")
    if result:
        print("✅ ADMIN LOGIN TEST PASSED!")
        print("The correct admin password (Hdfatboy1!) is working.")
        print("Frontend should now be able to login successfully.")
    else:
        print("❌ ADMIN LOGIN TEST FAILED")
        print("There may still be an issue with the credentials or server.")
    print(f"{'='*35}")
