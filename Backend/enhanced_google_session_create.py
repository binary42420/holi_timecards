"""
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
