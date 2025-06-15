"""
Redis Configuration for EasyShifts Application
Handles Redis connection, session management, and caching
"""

import os
import json
import asyncio
import logging
from typing import Optional, Dict, Any, Union
from datetime import datetime, timedelta
import redis
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class RedisConfig:
    """Redis configuration and connection management"""
    
    def __init__(self):
        # Redis Cloud configuration
        self.host = os.getenv('REDIS_HOST', 'redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com')
        self.port = int(os.getenv('REDIS_PORT', '12649'))
        self.password = os.getenv('REDIS_PASSWORD')
        self.db = int(os.getenv('REDIS_DB', '0'))
        
        # Connection settings
        self.max_connections = int(os.getenv('REDIS_MAX_CONNECTIONS', '20'))
        self.socket_timeout = int(os.getenv('REDIS_SOCKET_TIMEOUT', '5'))
        self.socket_connect_timeout = int(os.getenv('REDIS_CONNECT_TIMEOUT', '5'))
        self.retry_on_timeout = True
        self.health_check_interval = 30
        
        # Session settings
        self.session_timeout = int(os.getenv('SESSION_TIMEOUT_MINUTES', '480')) * 60  # 8 hours in seconds
        self.session_prefix = 'easyshifts:session:'
        self.cache_prefix = 'easyshifts:cache:'
        self.websocket_prefix = 'easyshifts:ws:'
        
        # Initialize connections
        self._sync_pool = None
        self._async_pool = None
        
    def get_redis_url(self) -> str:
        """Get Redis connection URL"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"
    
    def get_sync_connection(self) -> redis.Redis:
        """Get synchronous Redis connection with connection pooling"""
        if not self._sync_pool:
            self._sync_pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                max_connections=self.max_connections,
                socket_timeout=self.socket_timeout,
                socket_connect_timeout=self.socket_connect_timeout,
                retry_on_timeout=self.retry_on_timeout,
                decode_responses=True
            )
        
        return redis.Redis(connection_pool=self._sync_pool)
    
    async def get_async_connection(self) -> redis.Redis:
        """Get asynchronous Redis connection using redis-py (compatible with Python 3.13)"""
        # For now, return sync connection - we'll upgrade to async later when aioredis is compatible
        return self.get_sync_connection()
    
    async def close_connections(self):
        """Close all Redis connections"""
        if self._sync_pool:
            self._sync_pool.disconnect()

# Global Redis configuration instance
redis_config = RedisConfig()

class RedisSessionManager:
    """Manages user sessions in Redis"""
    
    def __init__(self, config: RedisConfig = None):
        self.config = config or redis_config
        
    def _get_session_key(self, session_id: str) -> str:
        """Get Redis key for session"""
        return f"{self.config.session_prefix}{session_id}"
    
    def create_session(self, session_id: str, user_data: Dict[str, Any]) -> bool:
        """Create a new session in Redis with connection validation"""
        try:
            redis_client = self.config.get_sync_connection()

            # Test Redis connection before proceeding
            try:
                redis_client.ping()
            except Exception as ping_error:
                logger.error(f"Redis ping failed during session creation for {session_id}: {ping_error}")
                return False

            session_key = self._get_session_key(session_id)

            # Add metadata
            session_data = {
                **user_data,
                'created_at': datetime.utcnow().isoformat(),
                'last_accessed': datetime.utcnow().isoformat(),
                'session_id': session_id
            }

            # Store session with expiration
            result = redis_client.setex(
                session_key,
                self.config.session_timeout,
                json.dumps(session_data, default=str)
            )

            if result:
                logger.info(f"Created session {session_id} for user {user_data.get('username')}")
                return True
            else:
                logger.error(f"Redis setex returned False for session {session_id}")
                return False

        except Exception as e:
            logger.error(f"Failed to create session {session_id}: {e}")
            logger.error(f"Session creation error type: {type(e).__name__}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data from Redis"""
        try:
            redis_client = self.config.get_sync_connection()
            session_key = self._get_session_key(session_id)
            
            session_data = redis_client.get(session_key)
            if not session_data:
                return None
            
            # Update last accessed time
            data = json.loads(session_data)
            data['last_accessed'] = datetime.utcnow().isoformat()
            
            # Refresh session expiration
            redis_client.setex(
                session_key,
                self.config.session_timeout,
                json.dumps(data, default=str)
            )
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data in Redis"""
        try:
            redis_client = self.config.get_sync_connection()
            session_key = self._get_session_key(session_id)
            
            # Get existing session
            existing_data = redis_client.get(session_key)
            if not existing_data:
                return False
            
            # Merge updates
            session_data = json.loads(existing_data)
            session_data.update(updates)
            session_data['last_accessed'] = datetime.utcnow().isoformat()
            
            # Save updated session
            redis_client.setex(
                session_key,
                self.config.session_timeout,
                json.dumps(session_data, default=str)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update session {session_id}: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session from Redis"""
        try:
            redis_client = self.config.get_sync_connection()
            session_key = self._get_session_key(session_id)
            
            result = redis_client.delete(session_key)
            logger.info(f"Deleted session {session_id}")
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    def get_active_sessions(self, user_id: int) -> list:
        """Get all active sessions for a user"""
        try:
            redis_client = self.config.get_sync_connection()
            pattern = f"{self.config.session_prefix}*"
            
            active_sessions = []
            for key in redis_client.scan_iter(match=pattern):
                session_data = redis_client.get(key)
                if session_data:
                    data = json.loads(session_data)
                    if data.get('user_id') == user_id:
                        active_sessions.append(data)
            
            return active_sessions
            
        except Exception as e:
            logger.error(f"Failed to get active sessions for user {user_id}: {e}")
            return []

# Global session manager instance
session_manager = RedisSessionManager()

class RedisCacheManager:
    """Manages application caching in Redis"""
    
    def __init__(self, config: RedisConfig = None):
        self.config = config or redis_config
        
    def _get_cache_key(self, key: str) -> str:
        """Get Redis key for cache"""
        return f"{self.config.cache_prefix}{key}"
    
    def set_cache(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set cache value with TTL"""
        try:
            redis_client = self.config.get_sync_connection()
            cache_key = self._get_cache_key(key)
            
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(value, default=str)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set cache {key}: {e}")
            return False
    
    def get_cache(self, key: str) -> Optional[Any]:
        """Get cache value"""
        try:
            redis_client = self.config.get_sync_connection()
            cache_key = self._get_cache_key(key)
            
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cache {key}: {e}")
            return None
    
    def delete_cache(self, key: str) -> bool:
        """Delete cache value"""
        try:
            redis_client = self.config.get_sync_connection()
            cache_key = self._get_cache_key(key)
            
            result = redis_client.delete(cache_key)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to delete cache {key}: {e}")
            return False
    
    def clear_cache_pattern(self, pattern: str) -> int:
        """Clear cache entries matching pattern"""
        try:
            redis_client = self.config.get_sync_connection()
            cache_pattern = f"{self.config.cache_prefix}{pattern}"
            
            keys = list(redis_client.scan_iter(match=cache_pattern))
            if keys:
                return redis_client.delete(*keys)
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to clear cache pattern {pattern}: {e}")
            return 0

# Global cache manager instance
cache_manager = RedisCacheManager()
