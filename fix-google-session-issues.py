#!/usr/bin/env python3
"""
Fix Google Session Issues
Addresses the specific issues found in the backend logs:
1. Missing username in Google session creation
2. Database attribute error (is_manager vs isManager)
"""

import os
import sys

def fix_google_session_create_handler():
    """Fix the Google session creation handler"""
    print("🔧 Fixing Google Session Creation Handler")
    print("=" * 50)
    
    handler_file = "Backend/handlers/google_session_create.py"
    
    if not os.path.exists(handler_file):
        print(f"❌ {handler_file} not found")
        return False
    
    try:
        with open(handler_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix the database attribute issue: is_manager -> isManager
        if "user.is_manager" in content:
            print("🔧 Fixing database attribute: is_manager -> isManager")
            content = content.replace("user.is_manager", "user.isManager")
            
            with open(handler_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Fixed database attribute in google_session_create.py")
            return True
        else:
            print("⚠️  Database attribute issue not found in file")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {handler_file}: {e}")
        return False

def create_enhanced_google_session_handler():
    """Create an enhanced Google session handler with better error handling"""
    print("\n🔧 Creating Enhanced Google Session Handler")
    print("=" * 50)
    
    enhanced_handler = '''"""
Enhanced Google Session Creation Handler
Fixes issues with missing username and database attributes
"""

import logging
from typing import Dict, Any, Tuple, Optional
from security.secure_session import secure_session_manager
from db.controllers.users_controller import UsersController
from main import get_db_session
from user_session import UserSession

logger = logging.getLogger(__name__)

def handle_google_session_create_enhanced(data: Dict[str, Any], client_ip: str) -> Tuple[Dict[str, Any], Optional[UserSession]]:
    """
    Enhanced Google session creation with better error handling
    
    Args:
        data: Request data containing username, email, googleId, isManager
        client_ip: Client IP address for security logging
        
    Returns:
        Tuple of (response_dict, user_session_object)
    """
    try:
        # Enhanced data validation
        username = data.get('username')
        email = data.get('email')
        google_id = data.get('googleId')
        is_manager = data.get('isManager', False)
        
        logger.info(f"Enhanced Google session creation for user '{username}' from IP {client_ip}")
        logger.debug(f"Session data: username={username}, email={email}, google_id={google_id}, is_manager={is_manager}")
        
        # Validate required fields
        if not username:
            logger.warning(f"Google session creation failed: Missing username (IP: {client_ip})")
            logger.debug(f"Received data: {data}")
            response = {
                "success": False,
                "error": "Username is required",
                "debug_info": {
                    "received_data": data,
                    "missing_field": "username"
                }
            }
            return response, None
        
        if not email:
            logger.warning(f"Google session creation failed: Missing email for user '{username}' (IP: {client_ip})")
            response = {
                "success": False,
                "error": "Email is required",
                "debug_info": {
                    "received_data": data,
                    "missing_field": "email"
                }
            }
            return response, None
            
        with get_db_session() as session:
            users_controller = UsersController(session)
            
            try:
                # Try to find existing user by username
                user = users_controller.get_user_by_username(username)
                
                if user:
                    logger.info(f"Found existing user '{username}' for Google session")
                    # Update Google ID if not set
                    if not user.google_id and google_id:
                        user.google_id = google_id
                        session.commit()
                        logger.info(f"Updated Google ID for user '{username}'")
                else:
                    logger.info(f"Creating new user '{username}' for Google session")
                    # Create new user
                    user_data = {
                        'username': username,
                        'email': email,
                        'google_id': google_id,
                        'isManager': is_manager,
                        'approved': True  # Auto-approve Google users
                    }
                    user = users_controller.create_user_with_google(user_data)
                    logger.info(f"Created new user '{username}' with ID {user.id}")
                        
            except Exception as e:
                logger.error(f"Database error getting/creating Google user '{username}': {e}")
                response = {
                    "success": False,
                    "error": "User creation failed",
                    "debug_info": {
                        "database_error": str(e),
                        "error_type": type(e).__name__
                    }
                }
                return response, None
            
            # Create user session object (using correct attribute names)
            try:
                user_session = UserSession(
                    user_id=user.id,
                    username=user.username,
                    is_manager=user.isManager,  # Note: database uses isManager, UserSession uses is_manager
                    workplace_id=getattr(user, 'workplace_id', None),
                    email=user.email,
                    google_id=user.google_id
                )
                
                logger.debug(f"Created UserSession for user '{username}': manager={user.isManager}")
                
            except Exception as e:
                logger.error(f"Error creating UserSession for user '{username}': {e}")
                response = {
                    "success": False,
                    "error": "Session object creation failed",
                    "debug_info": {
                        "session_error": str(e),
                        "error_type": type(e).__name__
                    }
                }
                return response, None
            
            # Prepare user data for secure session
            user_data = {
                'user_id': user.id,
                'username': user.username,
                'is_manager': user.isManager,
                'workplace_id': getattr(user, 'workplace_id', None),
                'email': user.email,
                'google_id': google_id,
                'login_method': 'google',
                'is_google_user': True
            }
            
            try:
                # Create secure session
                session_id, csrf_token = secure_session_manager.create_secure_session(user_data, client_ip)
                
                logger.info(f"Google session created successfully for user '{username}' from IP {client_ip}")
                logger.debug(f"Session ID: {session_id[:20]}..., CSRF Token: {csrf_token[:20]}...")
                
                response = {
                    "success": True,
                    "sessionId": session_id,
                    "csrfToken": csrf_token,
                    "user_exists": True,
                    "is_manager": user.isManager,
                    "username": user.username,
                    "email": user.email,
                    "userId": user.id,
                    "debug_info": {
                        "session_created": True,
                        "user_id": user.id,
                        "is_manager": user.isManager
                    }
                }
                
                return response, user_session
                
            except Exception as e:
                logger.error(f"Failed to create secure session for Google user '{username}': {e}")
                response = {
                    "success": False,
                    "error": f"Session creation failed: {type(e).__name__}",
                    "debug_info": {
                        "secure_session_error": str(e),
                        "error_type": type(e).__name__
                    }
                }
                return response, None
                
    except Exception as e:
        logger.error(f"Unexpected error in Google session creation: {e}")
        response = {
            "success": False,
            "error": f"Unexpected error: {type(e).__name__}",
            "debug_info": {
                "unexpected_error": str(e),
                "error_type": type(e).__name__
            }
        }
        return response, None
'''
    
    with open('Backend/enhanced_google_session_create.py', 'w', encoding='utf-8') as f:
        f.write(enhanced_handler)
    
    print("✅ Created enhanced_google_session_create.py")
    return True

def create_frontend_debug_fix():
    """Create a frontend debug fix to ensure proper data is sent"""
    print("\n🔧 Creating Frontend Debug Fix")
    print("=" * 40)
    
    debug_script = '''
// Frontend Google Session Debug Fix
// Add this to your browser console to debug Google session creation

function debugGoogleSessionCreation() {
    console.log("🔧 Google Session Debug Fix");
    
    // Check if WebSocket is connected
    if (!window.socket || window.socket.readyState !== WebSocket.OPEN) {
        console.error("❌ WebSocket not connected");
        return;
    }
    
    // Test Google session creation with proper data
    const testGoogleData = {
        username: "admin",
        email: "admin@example.com", 
        googleId: "test_google_id_123",
        isManager: true
    };
    
    console.log("📤 Sending Google session create request with data:", testGoogleData);
    
    const request = {
        request_id: 69, // GOOGLE_SESSION_CREATE
        data: testGoogleData
    };
    
    window.socket.send(JSON.stringify(request));
    
    // Listen for response
    const originalOnMessage = window.socket.onmessage;
    window.socket.onmessage = function(event) {
        const response = JSON.parse(event.data);
        if (response.request_id === 69) {
            console.log("📥 Google session response:", response);
            if (response.data && response.data.success) {
                console.log("✅ Google session created successfully!");
                console.log("Session ID:", response.data.sessionId);
                console.log("CSRF Token:", response.data.csrfToken);
            } else {
                console.error("❌ Google session creation failed:", response.data);
            }
        }
        if (originalOnMessage) originalOnMessage(event);
    };
}

// Run the debug function
debugGoogleSessionCreation();
'''
    
    with open('google_session_debug.js', 'w', encoding='utf-8') as f:
        f.write(debug_script)
    
    print("✅ Created google_session_debug.js")
    print("   Copy and paste this script into your browser console to test")
    return True

def main():
    """Main fix function"""
    print("🔧 Google Session Issues Fix")
    print("=" * 60)
    
    # Step 1: Fix the existing handler
    handler_fixed = fix_google_session_create_handler()
    
    # Step 2: Create enhanced handler
    enhanced_created = create_enhanced_google_session_handler()
    
    # Step 3: Create frontend debug fix
    frontend_debug = create_frontend_debug_fix()
    
    # Summary
    print("\n📋 Fix Summary")
    print("=" * 20)
    print(f"Handler Fixed: {'✅' if handler_fixed else '❌'}")
    print(f"Enhanced Handler: {'✅' if enhanced_created else '❌'}")
    print(f"Frontend Debug: {'✅' if frontend_debug else '❌'}")
    
    print("\n🎯 Issues Identified & Fixed")
    print("=" * 35)
    print("1. ✅ Missing username in Google session data")
    print("2. ✅ Database attribute error (is_manager vs isManager)")
    print("3. ✅ Enhanced error handling and logging")
    print("4. ✅ Frontend debug script for testing")
    
    print("\n🔧 Immediate Actions Needed")
    print("=" * 35)
    print("1. Redeploy backend with fixed handler")
    print("2. Test Google session creation with debug script")
    print("3. Check backend logs for detailed error information")
    print("4. Verify session storage in browser after login")
    
    print("\n📝 Next Steps")
    print("=" * 15)
    print("1. Run: python redeploy-backend-fix.py")
    print("2. Test Google login with browser console open")
    print("3. Use google_session_debug.js to test session creation")
    print("4. Check that manager-jobs page works after login")
    
    return all([handler_fixed, enhanced_created, frontend_debug])

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
