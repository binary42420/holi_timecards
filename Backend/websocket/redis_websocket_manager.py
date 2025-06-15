"""
Redis-based WebSocket Connection Manager for EasyShifts
Manages WebSocket connections with Redis for scalability and session persistence
"""

import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from config.redis_config import redis_config
from security.secure_session import secure_session_manager

logger = logging.getLogger(__name__)

class RedisWebSocketManager:
    """Manages WebSocket connections using Redis for persistence and scalability"""
    
    def __init__(self):
        self.redis_config = redis_config
        self.connections: Dict[str, object] = {}  # websocket_id -> websocket object
        self.user_connections: Dict[int, Set[str]] = {}  # user_id -> set of websocket_ids
        self.connection_sessions: Dict[str, str] = {}  # websocket_id -> session_id
        
        # Redis keys
        self.ws_connections_key = "easyshifts:ws:connections"
        self.ws_user_mapping_key = "easyshifts:ws:user_mapping"
        self.ws_heartbeat_key = "easyshifts:ws:heartbeat"
        
    def register_connection(self, websocket, websocket_id: str, session_id: str, user_data: Dict) -> bool:
        """Register a new WebSocket connection"""
        try:
            # Validate session
            session_data = secure_session_manager.validate_session(session_id)
            if not session_data:
                logger.warning(f"Invalid session for WebSocket connection: {session_id}")
                return False
            
            user_id = session_data.get('user_id')
            if not user_id:
                logger.warning(f"No user_id in session data for WebSocket: {websocket_id}")
                return False
            
            # Store connection locally
            self.connections[websocket_id] = websocket
            self.connection_sessions[websocket_id] = session_id
            
            # Track user connections
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(websocket_id)
            
            # Store in Redis for persistence
            redis_client = self.redis_config.get_sync_connection()
            
            connection_data = {
                'websocket_id': websocket_id,
                'session_id': session_id,
                'user_id': user_id,
                'username': session_data.get('username'),
                'is_manager': session_data.get('is_manager', False),
                'connected_at': datetime.utcnow().isoformat(),
                'last_heartbeat': datetime.utcnow().isoformat()
            }
            
            # Store connection data with 1 hour TTL
            redis_client.hset(
                self.ws_connections_key,
                websocket_id,
                json.dumps(connection_data)
            )
            redis_client.expire(self.ws_connections_key, 3600)

            # Update user mapping
            redis_client.sadd(f"{self.ws_user_mapping_key}:{user_id}", websocket_id)
            redis_client.expire(f"{self.ws_user_mapping_key}:{user_id}", 3600)
            
            logger.info(f"Registered WebSocket connection {websocket_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register WebSocket connection {websocket_id}: {e}")
            return False
    
    def unregister_connection(self, websocket_id: str) -> bool:
        """Unregister a WebSocket connection"""
        try:
            # Get connection data before removal
            session_id = self.connection_sessions.get(websocket_id)
            user_id = None

            if session_id:
                session_data = secure_session_manager.validate_session(session_id)
                if session_data:
                    user_id = session_data.get('user_id')

            # Remove from local storage
            self.connections.pop(websocket_id, None)
            self.connection_sessions.pop(websocket_id, None)

            if user_id and user_id in self.user_connections:
                self.user_connections[user_id].discard(websocket_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]

            # Remove from Redis
            redis_client = self.redis_config.get_sync_connection()

            redis_client.hdel(self.ws_connections_key, websocket_id)

            if user_id:
                redis_client.srem(f"{self.ws_user_mapping_key}:{user_id}", websocket_id)

            logger.info(f"Unregistered WebSocket connection {websocket_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to unregister WebSocket connection {websocket_id}: {e}")
            return False
    
    async def send_to_user(self, user_id: int, message: Dict) -> int:
        """Send message to all connections for a specific user"""
        try:
            sent_count = 0

            # Get user's connections from Redis
            redis_client = self.redis_config.get_sync_connection()
            websocket_ids = redis_client.smembers(f"{self.ws_user_mapping_key}:{user_id}")

            for websocket_id in websocket_ids:
                websocket = self.connections.get(websocket_id)
                if websocket:
                    try:
                        await websocket.send(json.dumps(message))
                        sent_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to send message to WebSocket {websocket_id}: {e}")
                        # Clean up dead connection
                        self.unregister_connection(websocket_id)

            return sent_count

        except Exception as e:
            logger.error(f"Failed to send message to user {user_id}: {e}")
            return 0
    
    async def send_to_managers(self, message: Dict) -> int:
        """Send message to all manager connections"""
        try:
            sent_count = 0

            # Get all connections from Redis
            redis_client = self.redis_config.get_sync_connection()
            all_connections = redis_client.hgetall(self.ws_connections_key)

            for websocket_id, connection_data_str in all_connections.items():
                try:
                    connection_data = json.loads(connection_data_str)
                    if connection_data.get('is_manager'):
                        websocket = self.connections.get(websocket_id)
                        if websocket:
                            await websocket.send(json.dumps(message))
                            sent_count += 1
                except Exception as e:
                    logger.warning(f"Failed to send message to manager WebSocket {websocket_id}: {e}")

            return sent_count

        except Exception as e:
            logger.error(f"Failed to send message to managers: {e}")
            return 0
    
    async def broadcast_to_all(self, message: Dict) -> int:
        """Broadcast message to all connected users"""
        try:
            sent_count = 0

            for websocket_id, websocket in self.connections.items():
                try:
                    await websocket.send(json.dumps(message))
                    sent_count += 1
                except Exception as e:
                    logger.warning(f"Failed to broadcast to WebSocket {websocket_id}: {e}")
                    # Clean up dead connection
                    self.unregister_connection(websocket_id)

            return sent_count

        except Exception as e:
            logger.error(f"Failed to broadcast message: {e}")
            return 0
    
    def update_heartbeat(self, websocket_id: str) -> bool:
        """Update heartbeat timestamp for a connection"""
        try:
            redis_client = self.redis_config.get_sync_connection()

            # Check if redis_client is None
            if redis_client is None:
                logger.warning(f"Redis client is None, cannot update heartbeat for {websocket_id}")
                return False

            # Update heartbeat in connection data
            connection_data_str = redis_client.hget(self.ws_connections_key, websocket_id)
            if connection_data_str:
                connection_data = json.loads(connection_data_str)
                connection_data['last_heartbeat'] = datetime.utcnow().isoformat()

                redis_client.hset(
                    self.ws_connections_key,
                    websocket_id,
                    json.dumps(connection_data)
                )
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to update heartbeat for WebSocket {websocket_id}: {e}")
            return False
    
    def cleanup_stale_connections(self) -> int:
        """Clean up stale connections that haven't sent heartbeat"""
        try:
            redis_client = self.redis_config.get_sync_connection()

            # Check if redis_client is None
            if redis_client is None:
                logger.warning("Redis client is None, cannot cleanup stale connections")
                return 0

            all_connections = redis_client.hgetall(self.ws_connections_key)

            stale_threshold = datetime.utcnow() - timedelta(minutes=5)
            cleaned_count = 0

            for websocket_id, connection_data_str in all_connections.items():
                try:
                    connection_data = json.loads(connection_data_str)
                    last_heartbeat = datetime.fromisoformat(connection_data.get('last_heartbeat'))

                    if last_heartbeat < stale_threshold:
                        self.unregister_connection(websocket_id)
                        cleaned_count += 1

                except Exception as e:
                    logger.warning(f"Error checking connection {websocket_id}: {e}")
                    self.unregister_connection(websocket_id)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} stale WebSocket connections")

            return cleaned_count

        except Exception as e:
            logger.error(f"Failed to cleanup stale connections: {e}")
            return 0
    
    def get_connection_stats(self) -> Dict:
        """Get statistics about current connections"""
        try:
            redis_client = self.redis_config.get_sync_connection()
            all_connections = redis_client.hgetall(self.ws_connections_key)
            
            stats = {
                'total_connections': len(all_connections),
                'local_connections': len(self.connections),
                'manager_connections': 0,
                'employee_connections': 0,
                'unique_users': len(self.user_connections)
            }
            
            for connection_data_str in all_connections.values():
                try:
                    connection_data = json.loads(connection_data_str)
                    if connection_data.get('is_manager'):
                        stats['manager_connections'] += 1
                    else:
                        stats['employee_connections'] += 1
                except Exception:
                    pass
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get connection stats: {e}")
            return {}
    
    async def start_heartbeat_monitor(self):
        """Start background task to monitor connection health"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                self.cleanup_stale_connections()
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
                await asyncio.sleep(60)

# Global WebSocket manager instance
redis_websocket_manager = RedisWebSocketManager()
