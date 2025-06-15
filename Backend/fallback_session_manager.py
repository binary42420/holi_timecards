"""
Fallback Session Manager for HOLI Timesheets
Provides in-memory session storage when Redis is unavailable
"""

import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class SessionData:
    """Session data structure"""
    session_id: str
    user_id: int
    username: str
    is_manager: bool
    email: str
    google_id: str
    created_at: datetime
    last_accessed: datetime
    login_method: str = 'google'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_accessed'] = self.last_accessed.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionData':
        """Create from dictionary"""
        data = data.copy()
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        return cls(**data)

class FallbackSessionManager:
    """In-memory session manager with Redis fallback"""
    
    def __init__(self, session_timeout: int = 3600):
        self.session_timeout = session_timeout
        self.sessions: Dict[str, SessionData] = {}
        self.lock = threading.RLock()
        self.redis_available = False
        self.redis_manager = None
        
        # Try to initialize Redis
        self._init_redis()
        
        logger.info(f"FallbackSessionManager initialized (Redis: {'Available' if self.redis_available else 'Unavailable'})")
    
    def _init_redis(self):
        """Initialize Redis connection if available"""
        try:
            from config.redis_config import redis_config, session_manager
            
            # Test Redis connection
            redis_client = redis_config.get_sync_connection()
            redis_client.ping()
            
            self.redis_manager = session_manager
            self.redis_available = True
            logger.info("✅ Redis connection established for session management")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis unavailable, using in-memory sessions: {e}")
            self.redis_available = False
    
    def create_session(self, session_id: str, user_data: Dict[str, Any]) -> bool:
        """Create a new session with Redis fallback"""
        try:
            # Try Redis first if available
            if self.redis_available and self.redis_manager:
                try:
                    result = self.redis_manager.create_session(session_id, user_data)
                    if result:
                        logger.info(f"✅ Session created in Redis: {session_id}")
                        return True
                    else:
                        logger.warning(f"⚠️ Redis session creation failed, falling back to memory")
                except Exception as e:
                    logger.error(f"❌ Redis session creation error: {e}")
                    self.redis_available = False
            
            # Fallback to in-memory storage
            with self.lock:
                session_data = SessionData(
                    session_id=session_id,
                    user_id=user_data.get('user_id', 0),
                    username=user_data.get('username', ''),
                    is_manager=user_data.get('is_manager', False),
                    email=user_data.get('email', ''),
                    google_id=user_data.get('google_id', ''),
                    created_at=datetime.utcnow(),
                    last_accessed=datetime.utcnow(),
                    login_method=user_data.get('login_method', 'google')
                )
                
                self.sessions[session_id] = session_data
                logger.info(f"✅ Session created in memory: {session_id}")
                
                # Clean up expired sessions
                self._cleanup_expired_sessions()
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to create session {session_id}: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data with Redis fallback"""
        try:
            # Try Redis first if available
            if self.redis_available and self.redis_manager:
                try:
                    session_data = self.redis_manager.get_session(session_id)
                    if session_data:
                        logger.debug(f"✅ Session retrieved from Redis: {session_id}")
                        return session_data
                except Exception as e:
                    logger.error(f"❌ Redis session retrieval error: {e}")
                    self.redis_available = False
            
            # Fallback to in-memory storage
            with self.lock:
                session_data = self.sessions.get(session_id)
                if session_data:
                    # Check if session is expired
                    if datetime.utcnow() - session_data.last_accessed > timedelta(seconds=self.session_timeout):
                        del self.sessions[session_id]
                        logger.debug(f"🗑️ Expired session removed: {session_id}")
                        return None
                    
                    # Update last accessed time
                    session_data.last_accessed = datetime.utcnow()
                    logger.debug(f"✅ Session retrieved from memory: {session_id}")
                    return session_data.to_dict()
                
                logger.debug(f"❌ Session not found: {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get session {session_id}: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session with Redis fallback"""
        try:
            success = False
            
            # Try Redis first if available
            if self.redis_available and self.redis_manager:
                try:
                    redis_success = self.redis_manager.delete_session(session_id)
                    if redis_success:
                        success = True
                        logger.info(f"✅ Session deleted from Redis: {session_id}")
                except Exception as e:
                    logger.error(f"❌ Redis session deletion error: {e}")
                    self.redis_available = False
            
            # Also remove from in-memory storage
            with self.lock:
                if session_id in self.sessions:
                    del self.sessions[session_id]
                    success = True
                    logger.info(f"✅ Session deleted from memory: {session_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to delete session {session_id}: {e}")
            return False
    
    def _cleanup_expired_sessions(self):
        """Clean up expired in-memory sessions"""
        try:
            current_time = datetime.utcnow()
            expired_sessions = []
            
            for session_id, session_data in self.sessions.items():
                if current_time - session_data.last_accessed > timedelta(seconds=self.session_timeout):
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.sessions[session_id]
                logger.debug(f"🗑️ Cleaned up expired session: {session_id}")
                
        except Exception as e:
            logger.error(f"❌ Error cleaning up expired sessions: {e}")
    
    def get_session_count(self) -> Dict[str, int]:
        """Get session statistics"""
        try:
            with self.lock:
                memory_count = len(self.sessions)
            
            redis_count = 0
            if self.redis_available and self.redis_manager:
                try:
                    # This would need to be implemented in the Redis manager
                    redis_count = getattr(self.redis_manager, 'get_session_count', lambda: 0)()
                except Exception:
                    pass
            
            return {
                'memory_sessions': memory_count,
                'redis_sessions': redis_count,
                'redis_available': self.redis_available
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting session count: {e}")
            return {'memory_sessions': 0, 'redis_sessions': 0, 'redis_available': False}

# Global fallback session manager instance
fallback_session_manager = FallbackSessionManager()
