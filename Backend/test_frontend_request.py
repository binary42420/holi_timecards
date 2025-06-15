#!/usr/bin/env python3
"""
Test script to simulate the exact request that should come from the frontend.
This helps debug the "failed to create account" issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from handlers.google_auth import google_auth_handler

def test_google_signup_request():
    """Test the exact request format that should come from frontend."""
    print("🧪 Testing Google signup request format...")
    
    # This simulates the exact data structure that comes from GoogleSignupCompletion.jsx
    frontend_request_data = {
        'username': 'ryley_test',
        'name': 'Ryley Holmes',
        'email': 'ilovekeyslovkeys@gmail.com',
        'googleData': {
            'sub': '108479393942935623059',  # Your actual Google ID from the logs
            'email': 'ilovekeyslovkeys@gmail.com',
            'name': 'Ryley Holmes',
            'picture': 'https://lh3.googleusercontent.com/a/ACg8ocJymmP_yj32HC8J8Cj28-S2Fexv7z5PztI3QX8pC40vPqt6Ww=s96-c',
            'email_verified': True
        }
    }
    
    print("📤 Testing Manager Signup (Request ID 70)...")
    print(f"Request data: {json.dumps(frontend_request_data, indent=2)}")
    
    try:
        response = google_auth_handler.handle_google_signup_manager(frontend_request_data)
        
        print(f"\n📥 Response: {json.dumps(response, indent=2, default=str)}")
        
        if response.get('success'):
            print("✅ Manager signup successful!")
            return True
        else:
            print(f"❌ Manager signup failed: {response.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during signup: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_employee_signup():
    """Test employee signup with additional fields."""
    print("\n🧪 Testing Employee Signup (Request ID 69)...")
    
    employee_request_data = {
        'username': 'ryley_employee',
        'name': 'Ryley Holmes',
        'email': 'ilovekeyslovkeys@gmail.com',
        'businessName': 'Test Business',
        'googleData': {
            'sub': '108479393942935623059_emp',  # Different ID to avoid conflicts
            'email': 'ilovekeyslovkeys@gmail.com',
            'name': 'Ryley Holmes',
            'picture': 'https://lh3.googleusercontent.com/a/ACg8ocJymmP_yj32HC8J8Cj28-S2Fexv7z5PztI3QX8pC40vPqt6Ww=s96-c',
            'email_verified': True
        },
        'certifications': {
            'canCrewChief': True,
            'canForklift': False,
            'canTruck': True
        }
    }
    
    try:
        response = google_auth_handler.handle_google_signup_employee(employee_request_data)
        
        print(f"📥 Employee Response: {json.dumps(response, indent=2, default=str)}")
        
        if response.get('success'):
            print("✅ Employee signup successful!")
            return True
        else:
            print(f"❌ Employee signup failed: {response.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during employee signup: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_client_signup():
    """Test client signup."""
    print("\n🧪 Testing Client Signup (Request ID 71)...")
    
    client_request_data = {
        'username': 'ryley_client',
        'name': 'Ryley Holmes',
        'email': 'ilovekeyslovkeys@gmail.com',
        'companyName': 'Holmes Productions',
        'googleData': {
            'sub': '108479393942935623059_client',  # Different ID to avoid conflicts
            'email': 'ilovekeyslovkeys@gmail.com',
            'name': 'Ryley Holmes',
            'picture': 'https://lh3.googleusercontent.com/a/ACg8ocJymmP_yj32HC8J8Cj28-S2Fexv7z5PztI3QX8pC40vPqt6Ww=s96-c',
            'email_verified': True
        }
    }
    
    try:
        response = google_auth_handler.handle_google_signup_client(client_request_data)
        
        print(f"📥 Client Response: {json.dumps(response, indent=2, default=str)}")
        
        if response.get('success'):
            print("✅ Client signup successful!")
            return True
        else:
            print(f"❌ Client signup failed: {response.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during client signup: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all signup tests."""
    print("🔧 Frontend Request Format Test")
    print("=" * 50)
    print("This simulates the exact requests that should come from the frontend.")
    print()
    
    # Test all three signup types
    manager_ok = test_google_signup_request()
    employee_ok = test_employee_signup()
    client_ok = test_client_signup()
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print(f"   Manager Signup: {'✅' if manager_ok else '❌'}")
    print(f"   Employee Signup: {'✅' if employee_ok else '❌'}")
    print(f"   Client Signup: {'✅' if client_ok else '❌'}")
    
    if manager_ok and employee_ok and client_ok:
        print("\n🎉 All backend handlers work correctly!")
        print("   The issue is likely in the frontend request format or WebSocket communication.")
        print("\n💡 Next steps:")
        print("   1. Check browser console for frontend errors")
        print("   2. Check backend logs when you try signup from the browser")
        print("   3. Verify the WebSocket connection is working")
    else:
        print("\n🔧 Some handlers have issues - check the error details above.")

if __name__ == "__main__":
    main()
