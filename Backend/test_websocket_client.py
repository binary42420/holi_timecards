#!/usr/bin/env python3
"""
Test WebSocket client to verify the backend WebSocket functionality.
"""

import asyncio
import websockets
import json

async def test_websocket():
    """Test WebSocket connection and client directory request."""
    uri = "wss://easyshifts-backend-s5b2sxgpsa-uc.a.run.app/ws"
    
    try:
        print(f"🔗 Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established")
            
            # Test login first
            print("\n🔐 Testing login...")
            login_request = {
                "request_id": 10,
                "data": {
                    "username": "manager",
                    "password": "password"
                }
            }
            
            await websocket.send(json.dumps(login_request))
            login_response = await websocket.recv()
            login_data = json.loads(login_response)
            
            print(f"✅ Login response: {login_data}")

            # Check if login was successful (user exists and is manager)
            login_success = (login_data.get('data', {}).get('user_exists') and
                           login_data.get('data', {}).get('is_manager'))

            if login_success:
                print("✅ Login successful")
                
                # Test client directory request
                print("\n🏢 Testing client directory request...")
                client_dir_request = {
                    "request_id": 212
                }
                
                await websocket.send(json.dumps(client_dir_request))
                client_dir_response = await websocket.recv()
                client_dir_data = json.loads(client_dir_response)
                
                print(f"✅ Client directory response: {client_dir_data}")
                
                if client_dir_data.get('success'):
                    companies = client_dir_data.get('data', {}).get('companies', [])
                    summary = client_dir_data.get('data', {}).get('summary', {})
                    print(f"✅ Found {len(companies)} companies")
                    print(f"✅ Summary: {summary}")
                    
                    for company in companies:
                        print(f"   - {company['name']} (ID: {company['id']}) - {company['statistics']['total_jobs']} jobs")
                else:
                    print(f"❌ Client directory request failed: {client_dir_data.get('error')}")
            else:
                print(f"❌ Login failed: User exists: {login_data.get('data', {}).get('user_exists')}, Is manager: {login_data.get('data', {}).get('is_manager')}")
                
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_websocket())
