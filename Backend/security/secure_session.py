"""
Secure Session Management for EasyShifts
Implements secure session handling with Redis backend and proper security measures
"""

import os
import uuid
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import bcrypt
from config.redis_config import session_manager, redis_config

logger = logging.getLogger(__name__)

class SecureSessionManager:
    """Secure session management with Redis backend"""
    
    def __init__(self):
        self.session_manager = session_manager
        self.secret_key = os.getenv('SESSION_SECRET_KEY', self._generate_secret_key())
        self.csrf_secret = os.getenv('CSRF_SECRET_KEY', self._generate_secret_key())
        
    def _generate_secret_key(self) -> str:
        """Generate a secure secret key"""
        return secrets.token_urlsafe(32)
    
    def _generate_session_id(self) -> str:
        """Generate a cryptographically secure session ID"""
        return secrets.token_urlsafe(32)
    
    def _generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token for session"""
        message = f"{session_id}:{self.csrf_secret}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(message.encode()).hexdigest()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def create_secure_session(self, user_data: Dict[str, Any], client_ip: str = None) -> Tuple[str, str]:
        """
        Create a secure session with CSRF protection
        Returns: (session_id, csrf_token)
        """
        max_retries = 3
        retry_delay = 0.1  # 100ms

        for attempt in range(max_retries):
            try:
                session_id = self._generate_session_id()
                csrf_token = self._generate_csrf_token(session_id)

                # Prepare secure session data
                secure_session_data = {
                    'user_id': user_data.get('user_id'),
                    'username': user_data.get('username'),
                    'is_manager': user_data.get('is_manager', False),
                    'is_admin': user_data.get('is_admin', False),
                    'email': user_data.get('email'),
                    'google_linked': user_data.get('google_linked', False),
                    'csrf_token': csrf_token,
                    'client_ip': client_ip,
                    'created_at': datetime.utcnow().isoformat(),
                    'last_accessed': datetime.utcnow().isoformat(),
                    'login_method': user_data.get('login_method', 'password'),
                    'attempt': attempt + 1
                }

                # Create session in Redis with retry logic
                success = self.session_manager.create_session(session_id, secure_session_data)

                if success:
                    if attempt > 0:
                        logger.info(f"Created secure session for user {user_data.get('username')} from IP {client_ip} (attempt {attempt + 1})")
                    else:
                        logger.info(f"Created secure session for user {user_data.get('username')} from IP {client_ip}")
                    return session_id, csrf_token
                else:
                    if attempt < max_retries - 1:
                        logger.warning(f"Session creation attempt {attempt + 1} failed for user {user_data.get('username')}, retrying in {retry_delay}s...")
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        raise Exception(f"Failed to create session in Redis after {max_retries} attempts")

            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Session creation attempt {attempt + 1} failed for user {user_data.get('username')}: {e}, retrying in {retry_delay}s...")
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    logger.error(f"Failed to create secure session after {max_retries} attempts: {e}")
                    raise
    
    def validate_session(self, session_id: str, csrf_token: str = None, client_ip: str = None) -> Optional[Dict[str, Any]]:
        """
        Validate session and optionally check CSRF token and IP
        """
        try:
            if not session_id:
                return None
            
            # Get session from Redis
            session_data = self.session_manager.get_session(session_id)
            if not session_data:
                logger.warning(f"Session {session_id} not found")
                return None
            
            # Validate CSRF token if provided
            if csrf_token and session_data.get('csrf_token') != csrf_token:
                logger.warning(f"CSRF token mismatch for session {session_id}")
                return None
            
            # Optional IP validation (can be disabled for mobile users)
            if client_ip and os.getenv('VALIDATE_SESSION_IP', 'false').lower() == 'true':
                if session_data.get('client_ip') != client_ip:
                    logger.warning(f"IP mismatch for session {session_id}: {session_data.get('client_ip')} vs {client_ip}")
                    return None
            
            # Check session age
            created_at = datetime.fromisoformat(session_data.get('created_at'))
            max_age = timedelta(seconds=redis_config.session_timeout)
            
            if datetime.utcnow() - created_at > max_age:
                logger.warning(f"Session {session_id} expired")
                self.session_manager.delete_session(session_id)
                return None
            
            return session_data
            
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return None
    
    def refresh_session(self, session_id: str) -> bool:
        """Refresh session expiration"""
        try:
            updates = {
                'last_accessed': datetime.utcnow().isoformat()
            }
            return self.session_manager.update_session(session_id, updates)
            
        except Exception as e:
            logger.error(f"Failed to refresh session {session_id}: {e}")
            return False
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session"""
        try:
            return self.session_manager.delete_session(session_id)
            
        except Exception as e:
            logger.error(f"Failed to invalidate session {session_id}: {e}")
            return False
    
    def invalidate_all_user_sessions(self, user_id: int) -> int:
        """Invalidate all sessions for a user"""
        try:
            active_sessions = self.session_manager.get_active_sessions(user_id)
            count = 0
            
            for session in active_sessions:
                if self.session_manager.delete_session(session.get('session_id')):
                    count += 1
            
            logger.info(f"Invalidated {count} sessions for user {user_id}")
            return count
            
        except Exception as e:
            logger.error(f"Failed to invalidate sessions for user {user_id}: {e}")
            return 0

class PasswordSecurity:
    """Password security utilities"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt with secure settings"""
        # Use cost factor of 12 for good security/performance balance
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against bcrypt hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, list]:
        """
        Validate password strength
        Returns: (is_valid, list_of_issues)
        """
        issues = []
        
        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one number")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            issues.append("Password must contain at least one special character")
        
        # Check for common patterns
        common_patterns = ['123456', 'password', 'qwerty', 'abc123']
        if any(pattern in password.lower() for pattern in common_patterns):
            issues.append("Password contains common patterns")
        
        return len(issues) == 0, issues

class WebSocketSessionManager:
    """Manages WebSocket connections with Redis-backed sessions"""
    
    def __init__(self):
        self.secure_session = SecureSessionManager()
        self.websocket_prefix = redis_config.websocket_prefix
        
    def register_websocket_connection(self, session_id: str, websocket_id: str, client_info: Dict[str, Any]) -> bool:
        """Register WebSocket connection for a session"""
        try:
            redis_client = redis_config.get_sync_connection()
            ws_key = f"{self.websocket_prefix}{session_id}:{websocket_id}"
            
            connection_data = {
                'websocket_id': websocket_id,
                'session_id': session_id,
                'connected_at': datetime.utcnow().isoformat(),
                'client_info': client_info
            }
            
            # Store with 1 hour TTL (will be refreshed by heartbeat)
            redis_client.setex(ws_key, 3600, json.dumps(connection_data, default=str))
            
            logger.info(f"Registered WebSocket {websocket_id} for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register WebSocket connection: {e}")
            return False
    
    def unregister_websocket_connection(self, session_id: str, websocket_id: str) -> bool:
        """Unregister WebSocket connection"""
        try:
            redis_client = redis_config.get_sync_connection()
            ws_key = f"{self.websocket_prefix}{session_id}:{websocket_id}"
            
            result = redis_client.delete(ws_key)
            logger.info(f"Unregistered WebSocket {websocket_id} for session {session_id}")
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to unregister WebSocket connection: {e}")
            return False
    
    def get_session_websockets(self, session_id: str) -> list:
        """Get all WebSocket connections for a session"""
        try:
            redis_client = redis_config.get_sync_connection()
            pattern = f"{self.websocket_prefix}{session_id}:*"
            
            connections = []
            for key in redis_client.scan_iter(match=pattern):
                connection_data = redis_client.get(key)
                if connection_data:
                    connections.append(json.loads(connection_data))
            
            return connections
            
        except Exception as e:
            logger.error(f"Failed to get WebSocket connections for session {session_id}: {e}")
            return []

# Global instances
secure_session_manager = SecureSessionManager()
websocket_session_manager = WebSocketSessionManager()
password_security = PasswordSecurity()
