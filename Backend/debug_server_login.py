#!/usr/bin/env python3
"""
Debug the server login handling to see what's causing the "invalid" error
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the server's handle_request function
from Server import handle_request

def test_server_login():
    """Test the server's login handling directly"""
    print("🧪 Testing Server Login Handling")
    print("=" * 40)
    
    # Test login request
    test_data = {
        "username": "admin",
        "password": "Hdfatboy1!"
    }
    
    print(f"🔍 Testing login with data: {test_data}")
    
    try:
        # Call the server's handle_request function directly
        response = handle_request(10, test_data, client_id="test_client")
        
        print(f"📤 Server response: {json.dumps(response, indent=2)}")
        
        # Check if response indicates success
        if response.get('data', {}).get('user_exists'):
            print("✅ Login successful according to server response")
        else:
            print("❌ Login failed according to server response")
            print(f"   Error: {response.get('data', {}).get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception during server login test: {e}")
        import traceback
        traceback.print_exc()

def test_multiple_users():
    """Test login for multiple users"""
    print("\n🧪 Testing Multiple Users")
    print("=" * 30)
    
    test_users = [
        {"username": "admin", "password": "Hdfatboy1!"},
        {"username": "manager", "password": "password"},
        {"username": "employee", "password": "pass"},
        {"username": "wrong_user", "password": "wrong_pass"},
    ]
    
    for user_data in test_users:
        print(f"\n🔍 Testing: {user_data['username']}")
        
        try:
            response = handle_request(10, user_data, client_id="test_client")
            
            if response.get('data', {}).get('user_exists'):
                print(f"✅ {user_data['username']}: Login successful")
                print(f"   Manager: {response.get('data', {}).get('is_manager')}")
                print(f"   Admin: {response.get('data', {}).get('is_admin')}")
            else:
                print(f"❌ {user_data['username']}: Login failed")
                print(f"   Error: {response.get('data', {}).get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ {user_data['username']}: Exception - {e}")

def test_request_format():
    """Test the exact request format that would come from frontend"""
    print("\n🧪 Testing Frontend Request Format")
    print("=" * 40)
    
    # Simulate the exact JSON that would come from frontend
    frontend_request = {
        "request_id": 10,
        "data": {
            "username": "admin",
            "password": "Hdfatboy1!"
        }
    }
    
    print(f"📨 Frontend request: {json.dumps(frontend_request, indent=2)}")
    
    try:
        # Test the exact format
        response = handle_request(
            frontend_request['request_id'], 
            frontend_request['data'], 
            client_id="test_client"
        )
        
        print(f"📤 Server response: {json.dumps(response, indent=2)}")
        
        # Check response format
        if 'request_id' in response and 'data' in response:
            print("✅ Response format is correct")
            
            if response['data'].get('user_exists'):
                print("✅ Login successful")
            else:
                print("❌ Login failed")
                print(f"   Error: {response['data'].get('error')}")
        else:
            print("❌ Response format is incorrect")
            print(f"   Expected: {{'request_id': 10, 'data': {{...}}}}")
            print(f"   Got: {response}")
            
    except Exception as e:
        print(f"❌ Exception during frontend format test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all debug tests"""
    print("🚀 EasyShifts Server Login Debug")
    print("=" * 50)
    
    # Test 1: Basic server login
    test_server_login()
    
    # Test 2: Multiple users
    test_multiple_users()
    
    # Test 3: Frontend request format
    test_request_format()
    
    print("\n" + "=" * 50)
    print("🔍 Debug testing completed!")
    print("\nIf you see 'invalid' errors, check:")
    print("1. The response format matches what frontend expects")
    print("2. The error messages are being properly returned")
    print("3. The session handling is working correctly")

if __name__ == "__main__":
    main()
