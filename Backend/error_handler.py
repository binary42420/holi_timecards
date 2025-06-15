#!/usr/bin/env python3
"""
Centralized Error Handling and Logging System for HOLI Timecards Backend
Provides standardized error handling, logging, and response formatting.
"""

import logging
import traceback
import json
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('holi_timecards.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling and logging"""
    
    @staticmethod
    def log_error(component: str, error: Exception, context: Dict[str, Any] = None):
        """Log error with context information"""
        error_info = {
            'component': component,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
            'context': context or {}
        }
        
        logger.error(f"Error in {component}: {error_info}")
        
        # In production, you might want to send to external logging service
        # Example: send_to_logging_service(error_info)
        
        return error_info
    
    @staticmethod
    def format_error_response(request_id: Optional[int], error: Exception, 
                            component: str = "Unknown") -> Dict[str, Any]:
        """Format standardized error response"""
        error_info = ErrorHandler.log_error(component, error)
        
        return {
            "request_id": request_id,
            "success": False,
            "error": f"Operation failed: {str(error)}",
            "error_type": type(error).__name__,
            "timestamp": error_info['timestamp']
        }
    
    @staticmethod
    def format_success_response(request_id: Optional[int], data: Any = None, 
                              message: str = "Operation successful") -> Dict[str, Any]:
        """Format standardized success response"""
        response = {
            "request_id": request_id,
            "success": True,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        if data is not None:
            response["data"] = data
            
        return response

def handle_errors(component_name: str = None):
    """Decorator for automatic error handling in handler functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            component = component_name or func.__name__
            try:
                logger.info(f"Processing {component} request")
                result = func(*args, **kwargs)
                
                # If result is already a dict with success/error structure, return as-is
                if isinstance(result, dict) and 'success' in result:
                    return result
                
                # Otherwise, wrap in success response
                request_id = kwargs.get('request_id') or (args[0].get('request_id') if args and isinstance(args[0], dict) else None)
                return ErrorHandler.format_success_response(request_id, result)
                
            except Exception as e:
                request_id = kwargs.get('request_id') or (args[0].get('request_id') if args and isinstance(args[0], dict) else None)
                return ErrorHandler.format_error_response(request_id, e, component)
        
        return wrapper
    return decorator

def handle_database_errors(func):
    """Decorator specifically for database operation error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log database-specific error details
            error_context = {
                'function': func.__name__,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys()) if kwargs else []
            }
            
            ErrorHandler.log_error(f"Database.{func.__name__}", e, error_context)
            
            # Re-raise with more context
            raise Exception(f"Database operation failed in {func.__name__}: {str(e)}") from e
    
    return wrapper

def handle_websocket_errors(func):
    """Decorator for WebSocket handler error handling"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"WebSocket error in {func.__name__}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Return error response for WebSocket
            return {
                "success": False,
                "error": f"WebSocket operation failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    return wrapper

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass

class DatabaseError(Exception):
    """Custom exception for database errors"""
    pass

class BusinessLogicError(Exception):
    """Custom exception for business logic errors"""
    pass

def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
    """Validate that required fields are present in data"""
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

def validate_user_session(user_session) -> None:
    """Validate user session"""
    if not user_session:
        raise AuthenticationError("User session not found")
    
    if not hasattr(user_session, 'get_id') or not user_session.get_id:
        raise AuthenticationError("Invalid user session - no user ID")

# Health check function
def system_health_check() -> Dict[str, Any]:
    """Perform system health check"""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'error_handler': 'operational',
                'logging': 'operational'
            }
        }
        
        # Test database connection
        try:
            from main import get_db_session
            with get_db_session() as session:
                session.execute("SELECT 1")
            health_status['components']['database'] = 'operational'
        except Exception as e:
            health_status['components']['database'] = f'error: {str(e)}'
            health_status['status'] = 'degraded'
        
        return health_status
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

# Export commonly used functions
__all__ = [
    'ErrorHandler',
    'handle_errors',
    'handle_database_errors', 
    'handle_websocket_errors',
    'ValidationError',
    'AuthenticationError',
    'DatabaseError',
    'BusinessLogicError',
    'validate_required_fields',
    'validate_user_session',
    'system_health_check',
    'logger'
]
