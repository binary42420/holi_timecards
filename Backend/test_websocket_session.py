#!/usr/bin/env python3
"""
Test session creation through WebSocket to replicate the exact frontend scenario
"""

import os
import sys
import json
import asyncio
import websockets
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

async def test_websocket_session_creation():
    """Test session creation through WebSocket like the frontend does"""
    print("🧪 Testing WebSocket Session Creation")
    print("=" * 40)
    
    ws_url = "ws://localhost:8080/ws"
    
    try:
        print(f"🔌 Connecting to WebSocket: {ws_url}")
        
        # Test multiple login attempts to see if there's a concurrency issue
        test_cases = [
            {"username": "admin", "password": "Hdfatboy1!", "expected": True},
            {"username": "manager", "password": "password", "expected": True},
            {"username": "employee", "password": "pass", "expected": True},
            {"username": "wrong_user", "password": "wrong_pass", "expected": False},
        ]
        
        for i, test_case in enumerate(test_cases):
            print(f"\n🔍 Test {i+1}: {test_case['username']}")
            
            try:
                async with websockets.connect(ws_url, timeout=10) as websocket:
                    print(f"   ✅ WebSocket connected")
                    
                    # Send login request
                    login_request = {
                        "request_id": 10,
                        "data": {
                            "username": test_case["username"],
                            "password": test_case["password"]
                        }
                    }
                    
                    print(f"   📤 Sending login request")
                    await websocket.send(json.dumps(login_request))
                    
                    # Wait for response with timeout
                    try:
                        response_data = await asyncio.wait_for(websocket.recv(), timeout=10)
                        response = json.loads(response_data)
                        
                        print(f"   📥 Received response")
                        
                        if response.get('data', {}).get('user_exists'):
                            if test_case['expected']:
                                print(f"   ✅ Login successful (expected)")
                                print(f"      Session ID: {response['data'].get('session_id', 'N/A')[:20]}...")
                                print(f"      CSRF Token: {response['data'].get('csrf_token', 'N/A')[:20]}...")
                            else:
                                print(f"   ❌ Login successful but should have failed")
                        else:
                            if not test_case['expected']:
                                print(f"   ✅ Login failed (expected)")
                                print(f"      Error: {response.get('data', {}).get('error', 'Unknown')}")
                            else:
                                print(f"   ❌ Login failed unexpectedly")
                                print(f"      Error: {response.get('data', {}).get('error', 'Unknown')}")
                                
                                # Check if it's a session creation error
                                error_msg = response.get('data', {}).get('error', '')
                                if 'session creation failed' in error_msg.lower():
                                    print(f"   🚨 SESSION CREATION FAILED ERROR DETECTED!")
                                    print(f"      Full response: {json.dumps(response, indent=6)}")
                                    return False
                        
                    except asyncio.TimeoutError:
                        print(f"   ❌ Response timeout")
                        return False
                        
            except websockets.exceptions.ConnectionRefused:
                print(f"   ❌ Connection refused - is the server running?")
                return False
            except Exception as e:
                print(f"   ❌ WebSocket error: {e}")
                traceback.print_exc()
                return False
        
        print(f"\n✅ All WebSocket session tests completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ WebSocket session test failed: {e}")
        traceback.print_exc()
        return False

async def test_concurrent_sessions():
    """Test multiple concurrent session creations"""
    print("\n🧪 Testing Concurrent Session Creation")
    print("=" * 40)
    
    ws_url = "ws://localhost:8080/ws"
    
    async def single_login_test(user_num):
        """Single login test for concurrent execution"""
        try:
            async with websockets.connect(ws_url, timeout=10) as websocket:
                login_request = {
                    "request_id": 10,
                    "data": {
                        "username": "admin",
                        "password": "Hdfatboy1!"
                    }
                }
                
                await websocket.send(json.dumps(login_request))
                response_data = await asyncio.wait_for(websocket.recv(), timeout=10)
                response = json.loads(response_data)
                
                if response.get('data', {}).get('user_exists'):
                    print(f"   ✅ Concurrent login {user_num}: Success")
                    return True
                else:
                    error_msg = response.get('data', {}).get('error', 'Unknown')
                    print(f"   ❌ Concurrent login {user_num}: Failed - {error_msg}")
                    
                    if 'session creation failed' in error_msg.lower():
                        print(f"   🚨 SESSION CREATION FAILED in concurrent test!")
                    
                    return False
                    
        except Exception as e:
            print(f"   ❌ Concurrent login {user_num}: Exception - {e}")
            return False
    
    # Run 5 concurrent login attempts
    print("🔄 Running 5 concurrent login attempts...")
    
    tasks = [single_login_test(i+1) for i in range(5)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    success_count = sum(1 for result in results if result is True)
    
    print(f"\n📊 Concurrent test results: {success_count}/5 successful")
    
    if success_count == 5:
        print("✅ All concurrent sessions created successfully")
        return True
    else:
        print("❌ Some concurrent sessions failed")
        return False

async def test_rapid_succession():
    """Test rapid succession login attempts"""
    print("\n🧪 Testing Rapid Succession Logins")
    print("=" * 40)
    
    ws_url = "ws://localhost:8080/ws"
    
    try:
        # Single connection, multiple rapid requests
        async with websockets.connect(ws_url, timeout=10) as websocket:
            print("🔌 Connected for rapid succession test")
            
            for i in range(3):
                print(f"\n   🔄 Rapid login attempt {i+1}")
                
                login_request = {
                    "request_id": 10,
                    "data": {
                        "username": "admin",
                        "password": "Hdfatboy1!"
                    }
                }
                
                await websocket.send(json.dumps(login_request))
                response_data = await asyncio.wait_for(websocket.recv(), timeout=10)
                response = json.loads(response_data)
                
                if response.get('data', {}).get('user_exists'):
                    print(f"      ✅ Rapid login {i+1}: Success")
                else:
                    error_msg = response.get('data', {}).get('error', 'Unknown')
                    print(f"      ❌ Rapid login {i+1}: Failed - {error_msg}")
                    
                    if 'session creation failed' in error_msg.lower():
                        print(f"      🚨 SESSION CREATION FAILED in rapid test!")
                        return False
                
                # Small delay between requests
                await asyncio.sleep(0.1)
            
            print("✅ All rapid succession logins successful")
            return True
            
    except Exception as e:
        print(f"❌ Rapid succession test failed: {e}")
        traceback.print_exc()
        return False

async def main():
    """Run all WebSocket session tests"""
    print("🚀 EasyShifts WebSocket Session Testing")
    print("=" * 50)
    
    tests = [
        ("Basic WebSocket Session Creation", test_websocket_session_creation),
        ("Concurrent Session Creation", test_concurrent_sessions),
        ("Rapid Succession Logins", test_rapid_succession)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*50}")
    print("WEBSOCKET SESSION TEST SUMMARY")
    print('='*50)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All WebSocket session tests passed!")
        print("Session creation is working correctly through WebSocket.")
    else:
        print("\n❌ Some WebSocket session tests failed.")
        print("This indicates the 'Session creation failed' error may be intermittent.")
        print("\nPossible causes:")
        print("1. Redis connection timeout under load")
        print("2. Concurrent session creation conflicts")
        print("3. WebSocket connection issues")
        print("4. Environment variable loading issues")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())
