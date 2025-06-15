"""
Google Session Creation Handler
Creates secure sessions for Google OAuth authenticated users
"""

import logging
from typing import Dict, Any, Tuple, Optional
from security.secure_session import secure_session_manager
from db.controllers.users_controller import UsersController
from main import get_db_session
from user_session import UserSession
from fallback_session_manager import fallback_session_manager
from redis_session_persistence import redis_session_persistence

logger = logging.getLogger(__name__)

def handle_google_session_create(data: Dict[str, Any], client_ip: str) -> Tuple[Dict[str, Any], Optional[UserSession]]:
    """
    Create a secure session for Google authenticated users
    
    Args:
        data: Request data containing username, email, googleId, isManager
        client_ip: Client IP address for security logging
        
    Returns:
        Tuple of (response_dict, user_session_object)
    """
    try:
        username = data.get('username')
        email = data.get('email')
        google_id = data.get('googleId')
        is_manager = data.get('isManager', False)
        
        logger.info(f"Creating Google session for user '{username}' from IP {client_ip}")
        
        if not username:
            logger.warning(f"Google session creation failed: Missing username (IP: {client_ip})")
            response = {
                "success": False,
                "error": "Username is required"
            }
            return response, None
            
        with get_db_session() as session:
            users_controller = UsersController(session)
            
            # Get or create user
            try:
                user = users_controller.get_user_by_username(username)
                if not user:
                    logger.info(f"Creating new Google user '{username}' from IP {client_ip}")
                    # Create new user for Google authentication using the correct method
                    user_data = {
                        'username': username,
                        'name': username,  # Use username as name for now
                        'email': email,
                        'google_id': google_id,
                        'is_manager': is_manager,
                        'approved': True  # Auto-approve Google users
                    }
                    user = users_controller.create_user_with_google(user_data)
                else:
                    logger.info(f"Found existing user '{username}' for Google session")
                    # Update Google info if needed
                    if google_id and user.google_id != google_id:
                        user.google_id = google_id
                        user.is_google_user = True
                        session.commit()
                        
            except Exception as e:
                logger.error(f"Database error getting/creating Google user '{username}': {e}")
                response = {
                    "success": False,
                    "error": "User creation failed"
                }
                return response, None
            
            # Create user session object
            user_session = UserSession(
                user_id=user.id,
                username=user.username,
                is_manager=user.isManager,
                email=user.email
            )
            
            # Prepare user data for session
            user_data = {
                'user_id': user.id,
                'username': user.username,
                'is_manager': user.isManager,
                'email': user.email,
                'google_id': google_id,
                'login_method': 'google',
                'is_google_user': True
            }
            
            try:
                # Try secure session manager first, fallback to fallback manager
                try:
                    session_id, csrf_token = secure_session_manager.create_secure_session(user_data, client_ip)
                    logger.info(f"Google session created with secure session manager for user '{username}' from IP {client_ip}")
                except Exception as secure_error:
                    logger.warning(f"Secure session manager failed, using fallback: {secure_error}")

                    # Use fallback session manager
                    import secrets
                    session_id = secrets.token_urlsafe(32)
                    csrf_token = secrets.token_urlsafe(32)

                    # Create session with fallback manager
                    session_success = fallback_session_manager.create_session(session_id, user_data)
                    if not session_success:
                        raise Exception("Fallback session creation failed")

                    logger.info(f"Google session created with fallback manager for user '{username}' from IP {client_ip}")

                # Store session in Redis for persistence
                if redis_session_persistence.is_available():
                    redis_session_persistence.store_session(session_id, user_data)
                    logger.info(f"Session {session_id} stored in Redis for persistence")

                response = {
                    "success": True,
                    "sessionId": session_id,
                    "csrfToken": csrf_token,
                    "user_exists": True,
                    "is_manager": user.isManager,
                    "username": user.username,
                    "email": user.email,
                    "userId": user.id
                }

                return response, user_session

            except Exception as e:
                logger.error(f"Failed to create session for Google user '{username}': {e}")
                response = {
                    "success": False,
                    "error": f"Session creation failed: {type(e).__name__}"
                }
                return response, None
                
    except Exception as e:
        logger.error(f"Google session creation error for user '{username}': {e}")
        response = {
            "success": False,
            "error": "Google session creation failed"
        }
        return response, None
