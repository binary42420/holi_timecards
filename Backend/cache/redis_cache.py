"""
Redis-based caching system for EasyShifts
Implements intelligent caching for database queries, API responses, and computed data
"""

import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List, Callable
from functools import wraps
from config.redis_config import cache_manager, redis_config

logger = logging.getLogger(__name__)

class SmartCache:
    """Intelligent caching system with automatic invalidation"""
    
    def __init__(self):
        self.cache_manager = cache_manager
        self.default_ttl = 3600  # 1 hour
        
        # Cache TTL configurations for different data types
        self.cache_ttls = {
            'user_profile': 1800,      # 30 minutes
            'shift_data': 900,         # 15 minutes
            'job_listings': 600,       # 10 minutes
            'employee_list': 1200,     # 20 minutes
            'client_companies': 3600,  # 1 hour
            'settings': 7200,          # 2 hours
            'certifications': 3600,    # 1 hour
            'schedule_data': 300,      # 5 minutes
            'timesheet_data': 600,     # 10 minutes
            'analytics': 1800,         # 30 minutes
        }
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a consistent cache key from arguments"""
        # Create a string representation of all arguments
        key_parts = [str(prefix)]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        
        # Create hash for long keys
        key_string = ":".join(key_parts)
        if len(key_string) > 200:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:hash:{key_hash}"
        
        return key_string.replace(" ", "_")
    
    def get(self, cache_type: str, *args, **kwargs) -> Optional[Any]:
        """Get cached data"""
        try:
            cache_key = self._generate_cache_key(cache_type, *args, **kwargs)
            return self.cache_manager.get_cache(cache_key)
        except Exception as e:
            logger.error(f"Cache get error for {cache_type}: {e}")
            return None
    
    def set(self, cache_type: str, data: Any, *args, ttl: Optional[int] = None, **kwargs) -> bool:
        """Set cached data with appropriate TTL"""
        try:
            cache_key = self._generate_cache_key(cache_type, *args, **kwargs)
            cache_ttl = ttl or self.cache_ttls.get(cache_type, self.default_ttl)
            
            return self.cache_manager.set_cache(cache_key, data, cache_ttl)
        except Exception as e:
            logger.error(f"Cache set error for {cache_type}: {e}")
            return False
    
    def delete(self, cache_type: str, *args, **kwargs) -> bool:
        """Delete specific cached data"""
        try:
            cache_key = self._generate_cache_key(cache_type, *args, **kwargs)
            return self.cache_manager.delete_cache(cache_key)
        except Exception as e:
            logger.error(f"Cache delete error for {cache_type}: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all cache entries matching pattern"""
        try:
            return self.cache_manager.clear_cache_pattern(pattern)
        except Exception as e:
            logger.error(f"Cache pattern invalidation error for {pattern}: {e}")
            return 0
    
    def invalidate_user_cache(self, user_id: int) -> int:
        """Invalidate all cache entries for a specific user"""
        patterns = [
            f"user_profile:{user_id}:*",
            f"*:user:{user_id}:*",
            f"employee_list:*",  # User changes might affect employee lists
        ]
        
        total_deleted = 0
        for pattern in patterns:
            total_deleted += self.invalidate_pattern(pattern)
        
        logger.info(f"Invalidated {total_deleted} cache entries for user {user_id}")
        return total_deleted
    
    def invalidate_shift_cache(self, job_id: int = None, shift_id: int = None) -> int:
        """Invalidate shift-related cache entries"""
        patterns = []
        
        if job_id:
            patterns.extend([
                f"shift_data:job:{job_id}:*",
                f"job_listings:*",
                f"schedule_data:*"
            ])
        
        if shift_id:
            patterns.extend([
                f"shift_data:*:{shift_id}:*",
                f"timesheet_data:shift:{shift_id}:*"
            ])
        
        total_deleted = 0
        for pattern in patterns:
            total_deleted += self.invalidate_pattern(pattern)
        
        logger.info(f"Invalidated {total_deleted} shift cache entries")
        return total_deleted

def cached(cache_type: str, ttl: Optional[int] = None, key_args: Optional[List[str]] = None):
    """
    Decorator for caching function results
    
    Args:
        cache_type: Type of cache for TTL configuration
        ttl: Custom TTL in seconds
        key_args: List of argument names to include in cache key
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from specified arguments
            cache_key_parts = [func.__name__]
            
            if key_args:
                # Use only specified arguments for cache key
                for i, arg_name in enumerate(key_args):
                    if i < len(args):
                        cache_key_parts.append(str(args[i]))
                    elif arg_name in kwargs:
                        cache_key_parts.append(str(kwargs[arg_name]))
            else:
                # Use all arguments for cache key
                cache_key_parts.extend(str(arg) for arg in args)
                cache_key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            
            cache_key = ":".join(cache_key_parts)
            
            # Try to get from cache
            cached_result = smart_cache.get(cache_type, cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}: {cache_key}")
                return cached_result
            
            # Execute function and cache result
            try:
                result = func(*args, **kwargs)
                smart_cache.set(cache_type, result, cache_key, ttl=ttl)
                logger.debug(f"Cache miss for {func.__name__}: {cache_key}")
                return result
            except Exception as e:
                logger.error(f"Function execution error in cached decorator: {e}")
                raise
        
        return wrapper
    return decorator

class CacheWarmer:
    """Proactively warm cache with frequently accessed data"""
    
    def __init__(self):
        self.smart_cache = smart_cache
    
    async def warm_user_cache(self, user_id: int):
        """Pre-load user-related data into cache"""
        try:
            from db.controllers.users_controller import UsersController
            from main import get_db_session
            
            with get_db_session() as session:
                users_controller = UsersController(session)
                
                # Cache user profile
                user = users_controller.get_entity(user_id)
                if user:
                    user_data = {
                        'id': user.id,
                        'username': user.username,
                        'name': user.name,
                        'is_manager': user.isManager,
                        'is_admin': user.isAdmin,
                        'email': user.email
                    }
                    self.smart_cache.set('user_profile', user_data, user_id)
                    logger.info(f"Warmed cache for user {user_id}")
                
        except Exception as e:
            logger.error(f"Failed to warm user cache for {user_id}: {e}")
    
    async def warm_shift_cache(self, job_id: int):
        """Pre-load shift data for a job"""
        try:
            from db.controllers.shifts_controller import ShiftsController
            from main import get_db_session
            
            with get_db_session() as session:
                shifts_controller = ShiftsController(session)
                
                # Cache shift data for job
                shifts = shifts_controller.get_shifts_by_job_id(job_id)
                shift_data = [
                    {
                        'id': shift.id,
                        'job_id': shift.job_id,
                        'shift_date': shift.shiftDate.isoformat() if shift.shiftDate else None,
                        'shift_part': shift.shiftPart,
                        'start_datetime': shift.shift_start_datetime.isoformat() if shift.shift_start_datetime else None,
                        'end_datetime': shift.shift_end_datetime.isoformat() if shift.shift_end_datetime else None
                    }
                    for shift in shifts
                ]
                
                self.smart_cache.set('shift_data', shift_data, 'job', job_id)
                logger.info(f"Warmed shift cache for job {job_id}")
                
        except Exception as e:
            logger.error(f"Failed to warm shift cache for job {job_id}: {e}")

class CacheMetrics:
    """Track cache performance metrics"""
    
    def __init__(self):
        self.metrics_key = "cache_metrics"
        
    def record_hit(self, cache_type: str):
        """Record cache hit"""
        try:
            redis_client = redis_config.get_sync_connection()
            key = f"{self.metrics_key}:hits:{cache_type}"
            redis_client.incr(key)
            redis_client.expire(key, 86400)  # 24 hours
        except Exception as e:
            logger.error(f"Failed to record cache hit: {e}")
    
    def record_miss(self, cache_type: str):
        """Record cache miss"""
        try:
            redis_client = redis_config.get_sync_connection()
            key = f"{self.metrics_key}:misses:{cache_type}"
            redis_client.incr(key)
            redis_client.expire(key, 86400)  # 24 hours
        except Exception as e:
            logger.error(f"Failed to record cache miss: {e}")
    
    def get_metrics(self) -> Dict[str, Dict[str, int]]:
        """Get cache performance metrics"""
        try:
            redis_client = redis_config.get_sync_connection()
            metrics = {}
            
            # Get all hit/miss keys
            for key in redis_client.scan_iter(match=f"{self.metrics_key}:*"):
                parts = key.split(':')
                if len(parts) >= 3:
                    metric_type = parts[2]  # hits or misses
                    cache_type = parts[3] if len(parts) > 3 else 'unknown'
                    
                    if cache_type not in metrics:
                        metrics[cache_type] = {'hits': 0, 'misses': 0}
                    
                    count = redis_client.get(key) or 0
                    metrics[cache_type][metric_type] = int(count)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get cache metrics: {e}")
            return {}

# Global instances
smart_cache = SmartCache()
cache_warmer = CacheWarmer()
cache_metrics = CacheMetrics()
