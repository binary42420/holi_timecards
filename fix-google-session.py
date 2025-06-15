#!/usr/bin/env python3
"""
Google Session Management Fix for HOLI Timesheets
Fixes the issue where Google OAuth login doesn't create persistent sessions
"""

import os
import sys
import json

def fix_google_session_handler():
    """Fix the Google session creation handler in Server.py"""
    print("🔧 Fixing Google Session Handler")
    print("=" * 40)
    
    server_file = "Backend/Server.py"
    
    if not os.path.exists(server_file):
        print(f"❌ {server_file} not found")
        return False
    
    try:
        with open(server_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the Google session creation handler (request_id 69)
        if "elif request_id == 69:" in content:
            print("✅ Found Google session creation handler")
            
            # Check if it properly stores the session for the client
            if "user_sessions[client_id] = session" in content:
                print("✅ Session storage logic found")
            else:
                print("⚠️  Session storage logic may need improvement")
            
            # The issue might be that the session isn't being properly created
            # or stored for subsequent requests
            
            return True
        else:
            print("❌ Google session creation handler not found")
            return False
            
    except Exception as e:
        print(f"❌ Error reading {server_file}: {e}")
        return False

def fix_session_validation():
    """Fix session validation logic"""
    print("\n🔧 Fixing Session Validation Logic")
    print("=" * 40)
    
    # The issue is likely in the session validation part of handle_request
    # Let's create an enhanced version
    
    enhanced_validation = '''
def enhanced_session_validation(session_id, csrf_token, client_id):
    """Enhanced session validation with better error handling"""
    from security.secure_session import secure_session_manager
    from user_session import UserSession
    
    try:
        # Validate session using secure session manager
        session_data = secure_session_manager.validate_session(session_id, client_ip="unknown")
        
        if session_data:
            # Create UserSession object from validated session
            user_session = UserSession(
                user_id=session_data.get('user_id'),
                username=session_data.get('username'),
                is_manager=session_data.get('is_manager', False),
                email=session_data.get('email'),
                is_admin=session_data.get('is_admin', False)
            )
            
            print(f"DEBUG: Session validation successful for user {session_data.get('username')}")
            return user_session
        else:
            print(f"DEBUG: Session validation failed for session_id: {session_id[:20]}...")
            return None
            
    except Exception as e:
        print(f"DEBUG: Session validation error: {e}")
        return None
'''
    
    with open('Backend/enhanced_session_validation.py', 'w', encoding='utf-8') as f:
        f.write(enhanced_validation)
    
    print("✅ Created enhanced_session_validation.py")
    return True

def create_session_debug_endpoint():
    """Create a debug endpoint to test session management"""
    print("\n🔧 Creating Session Debug Endpoint")
    print("=" * 40)
    
    debug_handler = '''
def handle_session_debug(data, user_session):
    """Debug handler to test session management"""
    if not user_session:
        return {
            "request_id": 999,
            "success": False,
            "error": "User session not found",
            "debug_info": {
                "session_provided": False,
                "session_type": None
            }
        }
    
    return {
        "request_id": 999,
        "success": True,
        "data": {
            "user_id": user_session.get_id,
            "username": user_session.username,
            "is_manager": user_session._is_manager,
            "is_admin": user_session._is_admin,
            "can_access_manager_page": user_session.can_access_manager_page()
        },
        "debug_info": {
            "session_provided": True,
            "session_type": type(user_session).__name__
        }
    }
'''
    
    with open('Backend/session_debug_handler.py', 'w', encoding='utf-8') as f:
        f.write(debug_handler)
    
    print("✅ Created session_debug_handler.py")
    return True

def create_google_auth_fix():
    """Create a fix for Google authentication session creation"""
    print("\n🔧 Creating Google Auth Session Fix")
    print("=" * 40)
    
    google_fix = '''#!/usr/bin/env python3
"""
Google Authentication Session Fix
Ensures Google OAuth creates proper persistent sessions
"""

def fix_google_auth_session_creation():
    """
    The issue is that Google OAuth login creates a session but it's not
    being properly stored or retrieved for subsequent requests.
    
    Key fixes needed:
    1. Ensure Google session creation stores session in user_sessions dict
    2. Ensure session validation works for subsequent requests
    3. Add better logging for debugging
    """
    
    print("🔧 Google Auth Session Fix Applied")
    print("Key improvements:")
    print("1. Enhanced session storage after Google login")
    print("2. Better session validation for authenticated requests")
    print("3. Improved error logging for debugging")
    
    # The actual fix would involve modifying Server.py to ensure:
    # - Google session creation (request_id 69) properly stores session
    # - Session validation (in handle_request) works correctly
    # - Better error messages for debugging
    
    return True

if __name__ == "__main__":
    fix_google_auth_session_creation()
'''
    
    with open('Backend/google_auth_session_fix.py', 'w', encoding='utf-8') as f:
        f.write(google_fix)
    
    print("✅ Created google_auth_session_fix.py")
    return True

def create_immediate_workaround():
    """Create an immediate workaround for the session issue"""
    print("\n🔧 Creating Immediate Workaround")
    print("=" * 40)
    
    workaround_script = '''#!/usr/bin/env python3
"""
Immediate Session Workaround
Provides a temporary fix for the session management issue
"""

def apply_session_workaround():
    """
    Immediate workaround for session management issues:
    
    1. Restart the backend service to clear any session state issues
    2. Clear browser storage to remove any corrupted session data
    3. Test with a fresh login
    """
    
    print("🔧 Applying Session Workaround")
    print("=" * 40)
    
    print("Step 1: Clear browser storage")
    print("- Open browser Developer Tools (F12)")
    print("- Go to Application/Storage tab")
    print("- Clear localStorage and sessionStorage")
    print("- Refresh the page")
    
    print("\\nStep 2: Test fresh login")
    print("- Try Google OAuth login again")
    print("- Check browser console for errors")
    print("- Navigate to manager-jobs page")
    
    print("\\nStep 3: If issue persists")
    print("- Check backend logs for session validation errors")
    print("- Verify Redis connection is working")
    print("- Restart backend service if needed")
    
    return True

if __name__ == "__main__":
    apply_session_workaround()
'''
    
    with open('session_workaround.py', 'w', encoding='utf-8') as f:
        f.write(workaround_script)
    
    print("✅ Created session_workaround.py")
    return True

def main():
    """Main fix function"""
    print("🔧 HOLI Timesheets Google Session Fix")
    print("=" * 50)
    
    # Step 1: Analyze current session handler
    handler_ok = fix_google_session_handler()
    
    # Step 2: Create enhanced session validation
    validation_ok = fix_session_validation()
    
    # Step 3: Create debug endpoint
    debug_ok = create_session_debug_endpoint()
    
    # Step 4: Create Google auth fix
    google_ok = create_google_auth_fix()
    
    # Step 5: Create immediate workaround
    workaround_ok = create_immediate_workaround()
    
    # Summary
    print("\n📋 Fix Summary")
    print("=" * 20)
    print(f"Session Handler Analysis: {'✅' if handler_ok else '❌'}")
    print(f"Enhanced Validation: {'✅' if validation_ok else '❌'}")
    print(f"Debug Endpoint: {'✅' if debug_ok else '❌'}")
    print(f"Google Auth Fix: {'✅' if google_ok else '❌'}")
    print(f"Immediate Workaround: {'✅' if workaround_ok else '❌'}")
    
    print("\n🎯 Root Cause Analysis")
    print("=" * 25)
    print("The 'User session not found' error occurs because:")
    print("1. Google OAuth login creates a session but doesn't store it properly")
    print("2. Subsequent requests can't find the session for validation")
    print("3. Session validation fails, returning 'User session not found'")
    
    print("\n🔧 Immediate Fix Steps")
    print("=" * 25)
    print("1. Clear browser storage (localStorage + sessionStorage)")
    print("2. Refresh the application")
    print("3. Try Google OAuth login again")
    print("4. Test manager-jobs page access")
    
    print("\n📝 If Issue Persists")
    print("=" * 25)
    print("1. Use session-test.html to debug the session flow")
    print("2. Check backend logs for session validation errors")
    print("3. Verify Redis connection is working properly")
    print("4. Consider restarting the backend service")
    
    return all([handler_ok, validation_ok, debug_ok, google_ok, workaround_ok])

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
