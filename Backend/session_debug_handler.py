
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
