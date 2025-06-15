"""
Redis-based Session Persistence for HOLI Timesheets
Simple solution to persist sessions through deployments using Redis
"""

import logging
import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import redis
import os

logger = logging.getLogger(__name__)

class RedisSessionPersistence:
    """Redis-based session persistence manager"""
    
    def __init__(self):
        self.redis_client = None
        self.session_timeout = 7 * 24 * 3600  # 7 days
        self.redis_prefix = "holi_session:"
        
        # Initialize Redis connection
        self._init_redis()
        
        logger.info("RedisSessionPersistence initialized")
    
    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            redis_password = os.getenv('REDIS_PASSWORD', None)
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info(f"✅ Redis connection established: {redis_host}:{redis_port}")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            logger.warning("Session persistence will be disabled")
            self.redis_client = None
    
    def store_session(self, session_id: str, user_data: Dict[str, Any]) -> bool:
        """Store session data in Redis"""
        if not self.redis_client:
            return False
        
        try:
            # Prepare session data
            session_data = {
                'user_id': user_data.get('user_id'),
                'username': user_data.get('username'),
                'email': user_data.get('email'),
                'is_manager': user_data.get('is_manager', False),
                'is_admin': user_data.get('is_admin', False),
                'login_method': user_data.get('login_method', 'password'),
                'google_id': user_data.get('google_id'),
                'created_at': datetime.utcnow().isoformat(),
                'last_accessed': datetime.utcnow().isoformat()
            }
            
            # Store in Redis with expiration
            redis_key = f"{self.redis_prefix}{session_id}"
            self.redis_client.setex(
                redis_key,
                self.session_timeout,
                json.dumps(session_data)
            )
            
            logger.info(f"✅ Session {session_id} stored in Redis for user {user_data.get('username')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store session {session_id} in Redis: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data from Redis"""
        if not self.redis_client:
            return None
        
        try:
            redis_key = f"{self.redis_prefix}{session_id}"
            session_data_str = self.redis_client.get(redis_key)
            
            if session_data_str:
                session_data = json.loads(session_data_str)
                
                # Update last accessed time
                session_data['last_accessed'] = datetime.utcnow().isoformat()
                self.redis_client.setex(
                    redis_key,
                    self.session_timeout,
                    json.dumps(session_data)
                )
                
                logger.info(f"✅ Session {session_id} retrieved from Redis")
                return session_data
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve session {session_id} from Redis: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session from Redis"""
        if not self.redis_client:
            return False
        
        try:
            redis_key = f"{self.redis_prefix}{session_id}"
            result = self.redis_client.delete(redis_key)
            
            if result:
                logger.info(f"✅ Session {session_id} deleted from Redis")
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"❌ Failed to delete session {session_id} from Redis: {e}")
            return False
    
    def extend_session(self, session_id: str) -> bool:
        """Extend session expiration in Redis"""
        if not self.redis_client:
            return False
        
        try:
            redis_key = f"{self.redis_prefix}{session_id}"
            
            # Check if session exists
            if self.redis_client.exists(redis_key):
                # Extend expiration
                self.redis_client.expire(redis_key, self.session_timeout)
                logger.info(f"✅ Session {session_id} expiration extended")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to extend session {session_id}: {e}")
            return False
    
    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active sessions (for debugging/monitoring)"""
        if not self.redis_client:
            return {}
        
        try:
            pattern = f"{self.redis_prefix}*"
            session_keys = self.redis_client.keys(pattern)
            
            sessions = {}
            for key in session_keys:
                session_id = key.replace(self.redis_prefix, '')
                session_data_str = self.redis_client.get(key)
                
                if session_data_str:
                    sessions[session_id] = json.loads(session_data_str)
            
            logger.info(f"📊 Retrieved {len(sessions)} active sessions from Redis")
            return sessions
            
        except Exception as e:
            logger.error(f"❌ Failed to get all sessions: {e}")
            return {}
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions (Redis handles this automatically, but we can get stats)"""
        if not self.redis_client:
            return 0
        
        try:
            pattern = f"{self.redis_prefix}*"
            session_keys = self.redis_client.keys(pattern)
            active_count = len(session_keys)
            
            logger.info(f"📊 {active_count} active sessions in Redis")
            return active_count
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup sessions: {e}")
            return 0
    
    def is_available(self) -> bool:
        """Check if Redis is available"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.ping()
            return True
        except:
            return False

# Global instance
redis_session_persistence = RedisSessionPersistence()
