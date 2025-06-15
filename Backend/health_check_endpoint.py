"""
Health check endpoint for EasyShifts application monitoring
"""

import asyncio
import json
from datetime import datetime
from main import get_db_session
from config.redis_config import redis_config

async def health_check():
    """Comprehensive health check for all system components"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "holi-timesheets-backend",
        "version": "1.0.0",
        "checks": {}
    }
    
    overall_healthy = True
    
    # Database health check
    try:
        with get_db_session() as session:
            session.execute("SELECT 1")
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy", 
            "message": f"Database connection failed: {str(e)}"
        }
        overall_healthy = False
    
    # Redis health check
    try:
        redis_client = redis_config.get_sync_connection()
        redis_client.ping()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(e)}"
        }
        overall_healthy = False
    
    # Update overall status
    if not overall_healthy:
        health_status["status"] = "unhealthy"
    
    return health_status

def get_health_status():
    """Synchronous wrapper for health check"""
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(health_check())
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": f"Health check failed: {str(e)}"
        }
