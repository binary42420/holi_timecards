#!/usr/bin/env python3
"""
Test the complete login flow including frontend response handling
"""

import os
import sys
import json
import asyncio
import websockets
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

async def test_websocket_login():
    """Test login via WebSocket like the frontend does"""
    print("🧪 Testing WebSocket Login Flow")
    print("=" * 40)
    
    # WebSocket server URL
    ws_url = "ws://localhost:8080/ws"
    
    try:
        print(f"🔌 Connecting to WebSocket: {ws_url}")
        
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connection established")
            
            # Test login request (same format as frontend)
            login_request = {
                "request_id": 10,
                "data": {
                    "username": "admin",
                    "password": "Hdfatboy1!"
                }
            }
            
            print(f"📤 Sending login request: {json.dumps(login_request, indent=2)}")
            
            # Send login request
            await websocket.send(json.dumps(login_request))
            
            # Wait for response
            print("⏳ Waiting for server response...")
            response_data = await websocket.recv()
            
            print(f"📥 Received response: {response_data}")
            
            # Parse response
            try:
                response = json.loads(response_data)
                print(f"📋 Parsed response: {json.dumps(response, indent=2)}")
                
                # Check response format
                if response.get('request_id') == 10:
                    print("✅ Response has correct request_id")
                    
                    if response.get('data', {}).get('user_exists'):
                        print("✅ Login successful!")
                        print(f"   Username: {response['data'].get('user_data', {}).get('username')}")
                        print(f"   Is Manager: {response['data'].get('is_manager')}")
                        print(f"   Is Admin: {response['data'].get('is_admin')}")
                        print(f"   Session ID: {response['data'].get('session_id', 'N/A')[:20]}...")
                        print(f"   CSRF Token: {response['data'].get('csrf_token', 'N/A')[:20]}...")
                        
                        # Test what frontend would do
                        print("\n🎯 Frontend Processing Simulation:")
                        
                        # Simulate frontend userData creation
                        frontend_user_data = {
                            "username": "admin",
                            "isManager": response['data'].get('is_manager'),
                            "isAdmin": response['data'].get('is_admin'),
                            "loginTime": "2025-06-11T07:45:00.000Z",
                            "sessionId": response['data'].get('session_id'),
                            "csrfToken": response['data'].get('csrf_token'),
                            "userId": response['data'].get('user_data', {}).get('user_id'),
                            "email": response['data'].get('user_data', {}).get('email')
                        }
                        
                        print(f"   Frontend userData: {json.dumps(frontend_user_data, indent=4)}")
                        
                        # Simulate localStorage data (without sensitive tokens)
                        persist_data = {
                            "username": frontend_user_data["username"],
                            "isManager": frontend_user_data["isManager"],
                            "isAdmin": frontend_user_data["isAdmin"],
                            "loginTime": frontend_user_data["loginTime"],
                            "userId": frontend_user_data["userId"],
                            "email": frontend_user_data["email"]
                        }
                        
                        print(f"   localStorage data: {json.dumps(persist_data, indent=4)}")
                        
                        # Simulate sessionStorage data (sensitive tokens)
                        session_data = {
                            "sessionId": frontend_user_data["sessionId"],
                            "csrfToken": frontend_user_data["csrfToken"]
                        }
                        
                        print(f"   sessionStorage data: {json.dumps(session_data, indent=4)}")
                        
                        return True
                        
                    else:
                        print("❌ Login failed!")
                        error_msg = response.get('data', {}).get('error', 'Unknown error')
                        print(f"   Error: {error_msg}")
                        return False
                else:
                    print(f"❌ Unexpected request_id: {response.get('request_id')}")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse response JSON: {e}")
                print(f"   Raw response: {response_data}")
                return False
                
    except websockets.exceptions.ConnectionRefused:
        print("❌ Connection refused - is the server running?")
        print("   Start the server with: cd Backend && python Server.py")
        return False
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

async def test_multiple_users():
    """Test login for multiple users"""
    print("\n🧪 Testing Multiple User Logins")
    print("=" * 35)
    
    test_users = [
        {"username": "admin", "password": "Hdfatboy1!", "expected_manager": True, "expected_admin": True},
        {"username": "manager", "password": "password", "expected_manager": True, "expected_admin": False},
        {"username": "employee", "password": "pass", "expected_manager": False, "expected_admin": False},
        {"username": "wrong_user", "password": "wrong_pass", "expected_manager": False, "expected_admin": False},
    ]
    
    ws_url = "ws://localhost:8080/ws"
    
    for user_test in test_users:
        print(f"\n🔍 Testing: {user_test['username']}")
        
        try:
            async with websockets.connect(ws_url) as websocket:
                login_request = {
                    "request_id": 10,
                    "data": {
                        "username": user_test["username"],
                        "password": user_test["password"]
                    }
                }
                
                await websocket.send(json.dumps(login_request))
                response_data = await websocket.recv()
                response = json.loads(response_data)
                
                if response.get('data', {}).get('user_exists'):
                    print(f"✅ {user_test['username']}: Login successful")
                    
                    # Verify role expectations
                    is_manager = response['data'].get('is_manager', False)
                    is_admin = response['data'].get('is_admin', False)
                    
                    if is_manager == user_test['expected_manager'] and is_admin == user_test['expected_admin']:
                        print(f"   ✅ Roles correct: Manager={is_manager}, Admin={is_admin}")
                    else:
                        print(f"   ⚠️ Role mismatch: Expected Manager={user_test['expected_manager']}, Admin={user_test['expected_admin']}")
                        print(f"      Got Manager={is_manager}, Admin={is_admin}")
                        
                else:
                    if user_test['username'] == 'wrong_user':
                        print(f"✅ {user_test['username']}: Login correctly failed (expected)")
                    else:
                        print(f"❌ {user_test['username']}: Login failed unexpectedly")
                        error_msg = response.get('data', {}).get('error', 'Unknown error')
                        print(f"   Error: {error_msg}")
                        
        except Exception as e:
            print(f"❌ {user_test['username']}: Exception - {e}")

async def main():
    """Run all WebSocket login tests"""
    print("🚀 EasyShifts WebSocket Login Test")
    print("=" * 50)
    
    # Test 1: Basic login flow
    success = await test_websocket_login()
    
    if success:
        # Test 2: Multiple users
        await test_multiple_users()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ WebSocket login testing completed successfully!")
        print("\nYour login system is working correctly.")
        print("The frontend should now be able to authenticate users.")
    else:
        print("❌ WebSocket login testing failed!")
        print("\nPlease check:")
        print("1. Is the backend server running? (python Server.py)")
        print("2. Are the user credentials correct?")
        print("3. Is the WebSocket endpoint accessible?")

if __name__ == "__main__":
    asyncio.run(main())
