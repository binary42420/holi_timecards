#!/usr/bin/env python3
"""
Debug the login issue - check database and user authentication
"""

import asyncio
import json
import websockets
import traceback

async def test_login_with_different_credentials():
    """Test login with various credentials to debug the issue"""
    print("🔍 Debugging Login Issue")
    print("=" * 30)
    
    ws_url = "wss://holi-timesheets-backend-2ma525uu2a-uc.a.run.app/ws"
    
    # Test different credential combinations
    test_credentials = [
        {"username": "admin", "password": "Hdfatboy1!", "description": "Original admin credentials"},
        {"username": "admin", "password": "admin", "description": "Simple admin password"},
        {"username": "manager", "password": "manager", "description": "Manager credentials"},
        {"username": "test", "password": "test", "description": "Test credentials"},
        {"username": "Admin", "password": "Hdfatboy1!", "description": "Capitalized admin"},
        {"username": "admin", "password": "password", "description": "Default password"},
    ]
    
    for i, creds in enumerate(test_credentials, 1):
        print(f"\n{i}️⃣ Testing: {creds['description']}")
        print(f"   Username: {creds['username']}")
        print(f"   Password: {creds['password']}")
        
        try:
            async with websockets.connect(ws_url) as websocket:
                login_request = {
                    "request_id": 10,
                    "data": {
                        "username": creds['username'],
                        "password": creds['password']
                    }
                }
                
                await websocket.send(json.dumps(login_request))
                response_data = await asyncio.wait_for(websocket.recv(), timeout=10)
                response = json.loads(response_data)
                
                data = response.get('data', {})
                if data.get('user_exists'):
                    print(f"   ✅ SUCCESS! Login worked")
                    print(f"      User ID: {data.get('user_id')}")
                    print(f"      Is Manager: {data.get('is_manager')}")
                    print(f"      Is Admin: {data.get('is_admin')}")
                    print(f"      Session ID: {data.get('session_id', 'N/A')[:20]}...")
                    return creds
                else:
                    error = data.get('error', 'Unknown error')
                    print(f"   ❌ Failed: {error}")
                    
                    # Check for specific error types
                    if "Invalid username or password" in error:
                        print(f"      → User not found or wrong password")
                    elif "Database" in error:
                        print(f"      → Database connection issue")
                    elif "Session" in error:
                        print(f"      → Session creation issue")
                        
        except Exception as e:
            print(f"   ❌ Connection error: {e}")
    
    print(f"\n❌ None of the test credentials worked")
    return None

async def test_raw_database_query():
    """Test a raw database query to see what users exist"""
    print("\n🗄️ Testing Database Query")
    print("=" * 25)
    
    # This will test if we can query the database directly
    ws_url = "wss://easyshifts-backend-794306818447.us-central1.run.app/ws"
    
    try:
        async with websockets.connect(ws_url) as websocket:
            # Send a request that might give us more debug info
            debug_request = {
                "request_id": 999,  # Unknown request to see server response
                "data": {"debug": "list_users"}
            }
            
            await websocket.send(json.dumps(debug_request))
            response_data = await asyncio.wait_for(websocket.recv(), timeout=10)
            response = json.loads(response_data)
            
            print(f"   Debug response: {response}")
            
    except Exception as e:
        print(f"   ❌ Debug query failed: {e}")

async def test_detailed_login_response():
    """Get detailed login response to understand the issue"""
    print("\n🔬 Detailed Login Analysis")
    print("=" * 30)
    
    ws_url = "wss://easyshifts-backend-794306818447.us-central1.run.app/ws"
    
    try:
        async with websockets.connect(ws_url) as websocket:
            login_request = {
                "request_id": 10,
                "data": {
                    "username": "admin",
                    "password": "Hdfatboy1!"
                }
            }
            
            print("   📤 Sending detailed login request...")
            await websocket.send(json.dumps(login_request))
            
            response_data = await asyncio.wait_for(websocket.recv(), timeout=10)
            response = json.loads(response_data)
            
            print(f"   📥 Full response:")
            print(json.dumps(response, indent=4))
            
            # Analyze the response structure
            data = response.get('data', {})
            print(f"\n   📊 Response Analysis:")
            print(f"      Request ID: {response.get('request_id')}")
            print(f"      Has Data: {bool(data)}")
            print(f"      User Exists: {data.get('user_exists')}")
            print(f"      Error: {data.get('error')}")
            print(f"      Success: {response.get('success')}")
            
            # Check for any additional fields
            for key, value in data.items():
                if key not in ['user_exists', 'error']:
                    print(f"      {key}: {value}")
                    
    except Exception as e:
        print(f"   ❌ Detailed analysis failed: {e}")
        traceback.print_exc()

async def main():
    """Run all debug tests"""
    print("🚀 EasyShifts Login Debug Session")
    print("=" * 40)
    
    # Test 1: Try different credentials
    working_creds = await test_login_with_different_credentials()
    
    # Test 2: Raw database query
    await test_raw_database_query()
    
    # Test 3: Detailed response analysis
    await test_detailed_login_response()
    
    print(f"\n{'='*40}")
    print("DEBUG SESSION SUMMARY")
    print('='*40)
    
    if working_creds:
        print(f"✅ FOUND WORKING CREDENTIALS:")
        print(f"   Username: {working_creds['username']}")
        print(f"   Password: {working_creds['password']}")
        print(f"   Description: {working_creds['description']}")
    else:
        print("❌ NO WORKING CREDENTIALS FOUND")
        print("\nPossible issues:")
        print("1. Database connection problem")
        print("2. User table is empty or different")
        print("3. Password hashing mismatch")
        print("4. Database schema differences")
        print("5. Environment variable issues")
    
    print(f"{'='*40}")

if __name__ == "__main__":
    asyncio.run(main())
