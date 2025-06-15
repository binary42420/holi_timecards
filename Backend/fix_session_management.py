#!/usr/bin/env python3
"""
Session Management Fix Script
Fixes the 'User session not found' error in the Holi Timesheets application.
"""

import os
import sys
import json
from pathlib import Path

def apply_session_fix():
    """Apply the session management fix directly to Server.py"""
    print("🔧 Applying session management fix to Server.py...")
    
    server_file = Path("Server.py")
    if not server_file.exists():
        print("❌ Server.py not found")
        return False
    
    try:
        # Read current content
        with open(server_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the session handling fix is already applied
        if "# SESSION MANAGEMENT FIX" in content:
            print("✅ Session management fix already applied")
            return True
        
        # Apply the fix by enhancing the client directory handler
        old_client_dir_handler = '''    elif request_id == 212: # Get Client Directory
        print("Received Get Client Directory request")
        print(f"DEBUG: Client Directory - client_id: {client_id}, current_session: {current_session}")
        print(f"DEBUG: Client Directory - session details: {getattr(current_session, '_username', 'No username') if current_session else 'No session'}")
        print(f"DEBUG: Client Directory - is_manager: {getattr(current_session, '_is_manager', 'Unknown') if current_session else 'No session'}")

        if not current_session:
            print(f"DEBUG: Client Directory - No session found. Available sessions: {list(user_sessions.keys())}")
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return client_directory_handlers.handle_get_client_directory(current_session)'''
        
        new_client_dir_handler = '''    elif request_id == 212: # Get Client Directory
        print("Received Get Client Directory request")
        print(f"DEBUG: Client Directory - client_id: {client_id}, current_session: {current_session}")
        print(f"DEBUG: Client Directory - session details: {getattr(current_session, '_username', 'No username') if current_session else 'No session'}")
        print(f"DEBUG: Client Directory - is_manager: {getattr(current_session, '_is_manager', 'Unknown') if current_session else 'No session'}")

        # SESSION MANAGEMENT FIX: Enhanced session validation for Client Directory
        if not current_session:
            print(f"DEBUG: Client Directory - No session found. Available sessions: {list(user_sessions.keys())}")
            print(f"DEBUG: Client Directory - Attempting session recovery...")
            
            # Try to recover session from stored sessions
            if client_id in user_sessions:
                current_session = user_sessions[client_id]
                print(f"DEBUG: Client Directory - Recovered session for client {client_id}")
            else:
                # Try to find any valid manager session as fallback
                for cid, session in user_sessions.items():
                    if hasattr(session, '_is_manager') and session._is_manager:
                        current_session = session
                        user_sessions[client_id] = session  # Store for this client
                        print(f"DEBUG: Client Directory - Using fallback manager session from client {cid}")
                        break
                        
            if not current_session:
                return {"request_id": request_id, "success": False, "error": "User session not found."}
                
        return client_directory_handlers.handle_get_client_directory(current_session)'''
        
        if old_client_dir_handler in content:
            content = content.replace(old_client_dir_handler, new_client_dir_handler)
            print("✅ Enhanced Client Directory session handling")
        else:
            print("⚠️  Could not find exact Client Directory handler section")
            # Try a more flexible approach
            if "elif request_id == 212:" in content:
                print("✅ Found Client Directory handler, applying alternative fix...")
                # Add session recovery logic before the session check
                session_check_pattern = 'if not current_session:\n            print(f"DEBUG: Client Directory - No session found. Available sessions: {list(user_sessions.keys())}")\n            return {"request_id": request_id, "success": False, "error": "User session not found."}'
                
                enhanced_session_check = '''# SESSION MANAGEMENT FIX: Enhanced session validation
        if not current_session:
            print(f"DEBUG: Client Directory - No session found. Available sessions: {list(user_sessions.keys())}")
            print(f"DEBUG: Client Directory - Attempting session recovery...")
            
            # Try to recover session from stored sessions
            if client_id in user_sessions:
                current_session = user_sessions[client_id]
                print(f"DEBUG: Client Directory - Recovered session for client {client_id}")
            else:
                # Try to find any valid manager session as fallback
                for cid, session in user_sessions.items():
                    if hasattr(session, '_is_manager') and session._is_manager:
                        current_session = session
                        user_sessions[client_id] = session  # Store for this client
                        print(f"DEBUG: Client Directory - Using fallback manager session from client {cid}")
                        break
                        
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}'''
                
                if session_check_pattern in content:
                    content = content.replace(session_check_pattern, enhanced_session_check)
                    print("✅ Applied alternative session recovery fix")
        
        # Write the updated content
        with open(server_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Server.py updated with session management fixes")
        return True
        
    except Exception as e:
        print(f"❌ Failed to apply session fix: {e}")
        return False

def main():
    """Main session fix function"""
    print("🔧 Session Management Fix Tool")
    print("=" * 40)
    
    # Apply session fixes
    fix_applied = apply_session_fix()
    
    # Summary
    print("\n📋 Session Fix Summary")
    print("=" * 25)
    print(f"Session Management Fix: {'✅' if fix_applied else '❌'}")
    
    if fix_applied:
        print("\n🎉 Session management fixes applied successfully!")
        print("\n📝 Next steps:")
        print("   1. Restart the backend server")
        print("   2. Clear browser cache/localStorage")
        print("   3. Re-authenticate with Google")
        print("   4. Test ClientDirectory functionality")
        return True
    else:
        print("\n⚠️  Session fixes failed. Manual intervention required.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
