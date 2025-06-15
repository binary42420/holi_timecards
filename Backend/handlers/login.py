from db.controllers.users_controller import UsersController
from user_session import UserSession
from main import get_db_session
from security.secure_session import secure_session_manager, password_security
from cache.redis_cache import smart_cache
import logging

logger = logging.getLogger(__name__)


def handle_login(data, client_ip=None):
    """
    Handles user login with secure password verification and Redis session management.

    Args:
        data (dict): A dictionary containing 'username' and 'password'.
        client_ip (str): Client IP address for security logging.

    Returns:
        tuple: A tuple containing the response dictionary and user session object.
    """
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        logger.warning(f"Login attempt with missing credentials from IP {client_ip}")
        response = {
            "user_exists": False,
            "is_manager": False,
            "error": "Username and password are required"
        }
        return response, None

    try:
        with get_db_session() as session:
            users_controller = UsersController(session)

            # Get user by username
            try:
                user = users_controller.get_user_by_username(username)
                if not user:
                    logger.warning(f"Login failed: User '{username}' does not exist (IP: {client_ip})")
                    response = {
                        "user_exists": False,
                        "is_manager": False,
                        "error": "Invalid username or password"
                    }
                    return response, None
            except Exception as e:
                logger.error(f"Database error getting user '{username}': {e}")
                response = {
                    "user_exists": False,
                    "is_manager": False,
                    "error": "Invalid username or password"
                }
                return response, None

            # Verify password using secure method
            password_valid = False
            if user.password:
                if user.password.startswith('$2b$'):
                    # Hashed password
                    password_valid = password_security.verify_password(password, user.password)
                else:
                    # Legacy plain text password - verify and upgrade
                    if user.password == password:
                        password_valid = True
                        # Upgrade to hashed password
                        hashed_password = password_security.hash_password(password)
                        # Note: Need to add update_user_password method to controller
                        logger.info(f"Password upgrade needed for user {username}")

            if not password_valid:
                logger.warning(f"Login failed: Invalid password for user '{username}' (IP: {client_ip})")
                response = {
                    "user_exists": False,
                    "is_manager": False,
                    "error": "Invalid username or password"
                }
                return response, None

            # Check if user is active
            if not user.isActive:
                logger.warning(f"Login failed: Inactive user '{username}' (IP: {client_ip})")
                response = {
                    "user_exists": False,
                    "is_manager": False,
                    "error": "Account is inactive"
                }
                return response, None

            # Create secure session
            user_data = {
                'user_id': user.id,
                'username': user.username,
                'is_manager': user.isManager,
                'is_admin': user.isAdmin,
                'email': user.email,
                'login_method': 'password'
            }

            try:
                # Test Redis connection before creating session
                from config.redis_config import redis_config
                try:
                    redis_client = redis_config.get_sync_connection()
                    redis_client.ping()
                    logger.debug(f"Redis connection verified for user '{username}'")
                except Exception as redis_error:
                    logger.error(f"Redis connection failed for user '{username}': {redis_error}")
                    response = {
                        "user_exists": False,
                        "is_manager": False,
                        "error": "Session service temporarily unavailable"
                    }
                    return response, None

                session_id, csrf_token = secure_session_manager.create_secure_session(user_data, client_ip)

                # Cache user profile for performance
                try:
                    smart_cache.set('user_profile', user_data, user.id)
                except Exception as cache_error:
                    logger.warning(f"Failed to cache user profile for '{username}': {cache_error}")
                    # Continue anyway, caching is not critical

                logger.info(f"Successful login for user '{username}' (IP: {client_ip})")

                # Create legacy UserSession for backward compatibility with admin status
                user_session = UserSession(
                    user_id=user.id,
                    is_manager=user.isManager,
                    username=user.username,
                    email=user.email,
                    is_admin=user.isAdmin
                )
                user_session.session_id = session_id
                user_session.csrf_token = csrf_token

                response = {
                    "user_exists": True,
                    "is_manager": user.isManager,
                    "is_admin": user.isAdmin,
                    "session_id": session_id,
                    "csrf_token": csrf_token,
                    "user_data": user_data
                }
                return response, user_session

            except Exception as e:
                logger.error(f"Failed to create secure session for user '{username}': {e}")
                logger.error(f"Session creation error type: {type(e).__name__}")
                logger.error(f"Session creation error details: {str(e)}")

                # Import traceback for detailed error logging
                import traceback
                logger.error(f"Session creation traceback: {traceback.format_exc()}")

                response = {
                    "user_exists": False,
                    "is_manager": False,
                    "error": f"Session creation failed: {type(e).__name__}"
                }
                return response, None

    except Exception as e:
        logger.error(f"Database error during login for user '{username}': {e}")
        response = {
            "user_exists": False,
            "is_manager": False,
            "error": "Authentication service temporarily unavailable"
        }
        return response, None
