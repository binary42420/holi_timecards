#!/usr/bin/env python3
"""
Test authentication flow to understand the client directory issue.
"""

import asyncio
import websockets
import json

async def test_auth_flow():
    """Test the complete authentication flow."""
    uri = "wss://easyshifts-backend-794306818447.us-central1.run.app/ws"
    
    try:
        print(f"🔗 Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established")
            
            # Step 1: Test login
            print("\n🔐 Step 1: Testing login...")
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
            
            # Step 2: Test client directory WITHOUT authentication
            print("\n🏢 Step 2: Testing client directory WITHOUT authentication...")
            client_dir_request = {
                "request_id": 212
            }
            
            await websocket.send(json.dumps(client_dir_request))
            client_dir_response = await websocket.recv()
            client_dir_data = json.loads(client_dir_response)
            
            print(f"✅ Client directory response (no auth): {client_dir_data}")
            
            # Step 3: Check if we need to authenticate first
            if not client_dir_data.get('success'):
                print("\n🔑 Step 3: Authentication required, testing Google auth flow...")
                
                # Simulate Google authentication
                google_auth_request = {
                    "request_id": 1,
                    "data": {
                        "credential": "fake_google_token_for_testing"
                    }
                }
                
                await websocket.send(json.dumps(google_auth_request))
                google_auth_response = await websocket.recv()
                google_auth_data = json.loads(google_auth_response)
                
                print(f"✅ Google auth response: {google_auth_data}")
                
                # Step 4: Try client directory again after auth
                print("\n🏢 Step 4: Testing client directory AFTER authentication...")
                await websocket.send(json.dumps(client_dir_request))
                client_dir_response2 = await websocket.recv()
                client_dir_data2 = json.loads(client_dir_response2)
                
                print(f"✅ Client directory response (after auth): {client_dir_data2}")
            
            # Step 5: Test profile request to see if user session exists
            print("\n👤 Step 5: Testing profile request...")
            profile_request = {
                "request_id": 70
            }
            
            await websocket.send(json.dumps(profile_request))
            profile_response = await websocket.recv()
            profile_data = json.loads(profile_response)
            
            print(f"✅ Profile response: {profile_data}")
                
    except Exception as e:
        print(f"❌ Auth flow test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_auth_flow())
