
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
