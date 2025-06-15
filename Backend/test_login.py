#!/usr/bin/env python3
"""
Test login functionality with the new bcrypt password system
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.login import handle_login
from handlers.auth.authentication import BackendAuthenticationUser
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_login_handler():
    """Test the login handler with known users"""
    print("🧪 Testing Login Handler")
    print("=" * 30)
    
    # Test users (from backup file - actual passwords)
    test_users = [
        {"username": "admin", "password": "Hdfatboy1!"},
        {"username": "manager", "password": "password"},
        {"username": "employee", "password": "pass"},
        {"username": "addy", "password": "pass"},
        {"username": "eddie", "password": "CantWin1!"},
    ]
    
    for user_data in test_users:
        print(f"\n🔍 Testing login for user: {user_data['username']}")
        
        try:
            response, user_session = handle_login(user_data, client_ip="127.0.0.1")
            
            if response.get("user_exists"):
                print(f"✅ Login successful for {user_data['username']}")
                print(f"   Is Manager: {response.get('is_manager')}")
                print(f"   Is Admin: {response.get('is_admin')}")
                print(f"   Session ID: {response.get('session_id', 'N/A')[:20]}...")
                print(f"   CSRF Token: {response.get('csrf_token', 'N/A')[:20]}...")
            else:
                print(f"❌ Login failed for {user_data['username']}")
                print(f"   Error: {response.get('error')}")
                
        except Exception as e:
            print(f"❌ Exception during login for {user_data['username']}: {e}")

def test_authentication_class():
    """Test the BackendAuthenticationUser class"""
    print("\n🧪 Testing Authentication Class")
    print("=" * 35)
    
    # Test users (from backup file - actual passwords)
    test_users = [
        {"username": "admin", "password": "Hdfatboy1!"},
        {"username": "manager", "password": "password"},
        {"username": "employee", "password": "pass"},
        {"username": "addy", "password": "pass"},
        {"username": "eddie", "password": "CantWin1!"},
        {"username": "nonexistent", "password": "wrongpass"},
    ]
    
    for user_data in test_users:
        print(f"\n🔍 Testing authentication for user: {user_data['username']}")
        
        try:
            auth = BackendAuthenticationUser(user_data['username'], user_data['password'])
            is_valid = auth.validate_login()
            
            if is_valid:
                print(f"✅ Authentication successful for {user_data['username']}")
            else:
                print(f"❌ Authentication failed for {user_data['username']}")
                print(f"   Error: {auth.get_error_message()}")
                
        except Exception as e:
            print(f"❌ Exception during authentication for {user_data['username']}: {e}")

def test_password_verification():
    """Test password verification directly"""
    print("\n🧪 Testing Password Verification")
    print("=" * 35)
    
    from security.secure_session import password_security
    from main import get_db_session
    from db.models import User
    
    try:
        with get_db_session() as session:
            # Get a user with hashed password
            user = session.query(User).filter(User.password.like('$2b$%')).first()
            
            if user:
                print(f"🔍 Testing password verification for user: {user.username}")
                print(f"   Password hash: {user.password[:30]}...")
                
                # Test with correct password (from backup file)
                test_passwords = {
                    "admin": "Hdfatboy1!",
                    "manager": "password",
                    "employee": "pass",
                    "addy": "pass",
                    "eddie": "CantWin1!",
                    "test_emp_ws": "password123"
                }
                
                if user.username in test_passwords:
                    test_password = test_passwords[user.username]
                    is_valid = password_security.verify_password(test_password, user.password)
                    
                    if is_valid:
                        print(f"✅ Password verification successful for {user.username}")
                    else:
                        print(f"❌ Password verification failed for {user.username}")
                else:
                    print(f"⚠️ No test password available for {user.username}")
            else:
                print("❌ No users with hashed passwords found")
                
    except Exception as e:
        print(f"❌ Exception during password verification test: {e}")

def main():
    """Run all login tests"""
    print("🚀 EasyShifts Login System Test")
    print("=" * 40)
    
    # Test 1: Direct password verification
    test_password_verification()
    
    # Test 2: Authentication class
    test_authentication_class()
    
    # Test 3: Login handler
    test_login_handler()
    
    print("\n" + "=" * 40)
    print("✅ Login testing completed!")
    print("\nIf all tests passed, your login system is working correctly.")
    print("If any tests failed, check the error messages above.")

if __name__ == "__main__":
    main()
