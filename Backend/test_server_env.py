#!/usr/bin/env python3
"""
Test if the server is loading environment variables correctly
"""

import os
import sys
import asyncio
import websockets
import json
from dotenv import load_dotenv

# Load environment variables the same way the server does
load_dotenv('.env.production')

async def test_server_environment():
    """Test if server has correct environment variables"""
    print("🧪 Testing Server Environment Variables")
    print("=" * 45)
    
    # Check local environment first
    print("📋 Local Environment Check:")
    required_vars = [
        'REDIS_HOST',
        'REDIS_PORT', 
        'REDIS_PASSWORD',
        'SESSION_SECRET_KEY',
        'CSRF_SECRET_KEY'
    ]
    
    local_env_ok = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            display_value = '*' * 10 if 'PASSWORD' in var or 'KEY' in var else value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ❌ {var}: Not set")
            local_env_ok = False
    
    if not local_env_ok:
        print("\n❌ Local environment variables missing!")
        return False
    
    # Test server connection and login
    print(f"\n🔌 Testing Server Connection:")
    ws_url = "ws://localhost:8080/ws"
    
    try:
        async with websockets.connect(ws_url, timeout=10) as websocket:
            print("   ✅ WebSocket connection established")
            
            # Send a login request to test session creation
            login_request = {
                "request_id": 10,
                "data": {
                    "username": "admin",
                    "password": "Hdfatboy1!"
                }
            }
            
            print("   📤 Sending login request...")
            await websocket.send(json.dumps(login_request))
            
            # Wait for response
            response_data = await asyncio.wait_for(websocket.recv(), timeout=15)
            response = json.loads(response_data)
            
            print(f"   📥 Received response")
            
            # Check if login was successful
            if response.get('data', {}).get('user_exists'):
                print("   ✅ Login successful - server environment is working")
                print(f"      Session ID: {response['data'].get('session_id', 'N/A')[:20]}...")
                print(f"      CSRF Token: {response['data'].get('csrf_token', 'N/A')[:20]}...")
                return True
            else:
                error_msg = response.get('data', {}).get('error', 'Unknown error')
                print(f"   ❌ Login failed: {error_msg}")
                
                # Check for specific session creation errors
                if 'session creation failed' in error_msg.lower():
                    print("   🚨 SESSION CREATION FAILED - Environment issue detected!")
                elif 'session service temporarily unavailable' in error_msg.lower():
                    print("   🚨 REDIS CONNECTION FAILED - Redis environment issue!")
                
                print(f"   📋 Full response: {json.dumps(response, indent=6)}")
                return False
                
    except websockets.exceptions.ConnectionRefused:
        print("   ❌ Connection refused - server not running")
        print("   💡 Start server with: cd Backend && python Server.py")
        return False
    except asyncio.TimeoutError:
        print("   ❌ Connection timeout - server may be overloaded")
        return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False

async def test_multiple_attempts():
    """Test multiple login attempts to see if error is consistent"""
    print("\n🔄 Testing Multiple Login Attempts")
    print("=" * 40)
    
    ws_url = "ws://localhost:8080/ws"
    success_count = 0
    total_attempts = 3
    
    for i in range(total_attempts):
        print(f"\n   🔍 Attempt {i+1}/{total_attempts}")
        
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
                    print(f"      ✅ Success")
                    success_count += 1
                else:
                    error_msg = response.get('data', {}).get('error', 'Unknown')
                    print(f"      ❌ Failed: {error_msg}")
                    
        except Exception as e:
            print(f"      ❌ Exception: {e}")
    
    print(f"\n📊 Results: {success_count}/{total_attempts} successful")
    
    if success_count == total_attempts:
        print("✅ All attempts successful - no environment issues")
        return True
    elif success_count == 0:
        print("❌ All attempts failed - consistent environment issue")
        return False
    else:
        print("⚠️ Intermittent failures - possible race condition or timeout")
        return False

def check_env_file():
    """Check if .env.production file exists and is readable"""
    print("\n📁 Checking Environment File")
    print("=" * 30)
    
    env_file = '.env.production'
    
    if os.path.exists(env_file):
        print(f"   ✅ {env_file} exists")
        
        try:
            with open(env_file, 'r') as f:
                lines = f.readlines()
            
            print(f"   ✅ {env_file} is readable ({len(lines)} lines)")
            
            # Check for required variables
            required_vars = ['REDIS_HOST', 'REDIS_PASSWORD', 'SESSION_SECRET_KEY', 'CSRF_SECRET_KEY']
            found_vars = []
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    for var in required_vars:
                        if line.startswith(f"{var}="):
                            found_vars.append(var)
            
            print(f"   📋 Found variables: {', '.join(found_vars)}")
            
            missing_vars = set(required_vars) - set(found_vars)
            if missing_vars:
                print(f"   ❌ Missing variables: {', '.join(missing_vars)}")
                return False
            else:
                print(f"   ✅ All required variables present")
                return True
                
        except Exception as e:
            print(f"   ❌ Error reading {env_file}: {e}")
            return False
    else:
        print(f"   ❌ {env_file} not found")
        return False

async def main():
    """Run all environment tests"""
    print("🚀 EasyShifts Server Environment Test")
    print("=" * 50)
    
    # Test 1: Check environment file
    env_file_ok = check_env_file()
    
    # Test 2: Test server environment
    server_env_ok = await test_server_environment()
    
    # Test 3: Test multiple attempts if first test passed
    if server_env_ok:
        multiple_ok = await test_multiple_attempts()
    else:
        multiple_ok = False
    
    # Summary
    print(f"\n{'='*50}")
    print("ENVIRONMENT TEST SUMMARY")
    print('='*50)
    print(f"Environment file: {'✅ OK' if env_file_ok else '❌ FAILED'}")
    print(f"Server environment: {'✅ OK' if server_env_ok else '❌ FAILED'}")
    print(f"Multiple attempts: {'✅ OK' if multiple_ok else '❌ FAILED'}")
    
    if env_file_ok and server_env_ok and multiple_ok:
        print("\n🎉 All environment tests passed!")
        print("The 'Session creation failed' error is likely intermittent.")
    elif not env_file_ok:
        print("\n❌ Environment file issues detected.")
        print("Check that .env.production exists and contains all required variables.")
    elif not server_env_ok:
        print("\n❌ Server environment issues detected.")
        print("The server may not be loading environment variables correctly.")
    else:
        print("\n⚠️ Intermittent issues detected.")
        print("The error may be related to timing or load conditions.")

if __name__ == "__main__":
    asyncio.run(main())
