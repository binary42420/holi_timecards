"""
Fixed Redis Configuration for EasyShifts
Addresses connection and session management issues
"""

import os
import redis
import aioredis
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class FixedRedisConfig:
    """Robust Redis configuration with better error handling"""
    
    def __init__(self):
        # Redis connection settings with fallbacks
        self.host = os.getenv('REDIS_HOST', 'redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com')
        self.port = int(os.getenv('REDIS_PORT', '12649'))
        self.password = os.getenv('REDIS_PASSWORD', 'AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa')
        self.db = int(os.getenv('REDIS_DB', '0'))
        
        # Session settings
        self.session_timeout = int(os.getenv('SESSION_TIMEOUT', '3600'))  # 1 hour
        self.max_connections = int(os.getenv('REDIS_MAX_CONNECTIONS', '20'))
        
        # Connection pool settings
        self.socket_timeout = 15
        self.socket_connect_timeout = 15
        self.retry_on_timeout = True
        self.health_check_interval = 30
        
        logger.info(f"Redis config initialized: {self.host}:{self.port}")
    
    def get_sync_connection(self) -> redis.Redis:
        """Get synchronous Redis connection with connection pooling"""
        try:
            connection_pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                max_connections=self.max_connections,
                socket_timeout=self.socket_timeout,
                socket_connect_timeout=self.socket_connect_timeout,
                retry_on_timeout=self.retry_on_timeout,
                health_check_interval=self.health_check_interval,
                decode_responses=True
            )
            
            client = redis.Redis(connection_pool=connection_pool)
            
            # Test connection
            client.ping()
            logger.debug("Sync Redis connection established successfully")
            return client
            
        except Exception as e:
            logger.error(f"Failed to create sync Redis connection: {e}")
            raise
    
    async def get_async_connection(self) -> aioredis.Redis:
        """Get asynchronous Redis connection"""
        try:
            redis_url = f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
            
            client = aioredis.from_url(
                redis_url,
                socket_timeout=self.socket_timeout,
                socket_connect_timeout=self.socket_connect_timeout,
                retry_on_timeout=self.retry_on_timeout,
                max_connections=self.max_connections,
                decode_responses=True
            )
            
            # Test connection
            await client.ping()
            logger.debug("Async Redis connection established successfully")
            return client
            
        except Exception as e:
            logger.error(f"Failed to create async Redis connection: {e}")
            raise

class FixedSessionManager:
    """Improved session manager with better error handling"""
    
    def __init__(self, redis_config: FixedRedisConfig):
        self.redis_config = redis_config
        self.session_prefix = "easyshifts:session:"
        
    def _get_session_key(self, session_id: str) -> str:
        """Get Redis key for session"""
        return f"{self.session_prefix}{session_id}"
    
    def create_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Create session with retry logic"""
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                redis_client = self.redis_config.get_sync_connection()
                
                # Add metadata
                enhanced_data = {
                    **session_data,
                    'created_at': datetime.utcnow().isoformat(),
                    'last_accessed': datetime.utcnow().isoformat(),
                    'session_id': session_id
                }
                
                # Store with expiration
                session_key = self._get_session_key(session_id)
                result = redis_client.setex(
                    session_key,
                    self.redis_config.session_timeout,
                    json.dumps(enhanced_data, default=str)
                )
                
                if result:
                    logger.info(f"Session created successfully: {session_id}")
                    return True
                else:
                    logger.warning(f"Session creation returned False: {session_id}")
                    
            except Exception as e:
                logger.error(f"Session creation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"Failed to create session after {max_retries} attempts")
        
        return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session with error handling"""
        try:
            redis_client = self.redis_config.get_sync_connection()
            session_key = self._get_session_key(session_id)
            
            session_data = redis_client.get(session_key)
            if session_data:
                parsed_data = json.loads(session_data)
                
                # Update last accessed time
                parsed_data['last_accessed'] = datetime.utcnow().isoformat()
                redis_client.setex(
                    session_key,
                    self.redis_config.session_timeout,
                    json.dumps(parsed_data, default=str)
                )
                
                logger.debug(f"Session retrieved successfully: {session_id}")
                return parsed_data
            else:
                logger.debug(f"Session not found: {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        try:
            redis_client = self.redis_config.get_sync_connection()
            session_key = self._get_session_key(session_id)
            result = redis_client.delete(session_key)
            
            if result:
                logger.info(f"Session deleted successfully: {session_id}")
                return True
            else:
                logger.warning(f"Session not found for deletion: {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False

# Global instances
fixed_redis_config = FixedRedisConfig()
fixed_session_manager = FixedSessionManager(fixed_redis_config)
