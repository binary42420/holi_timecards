#!/usr/bin/env python3
"""
Debug Server for EasyShifts
Minimal server to test Cloud Run deployment
"""

import os
import sys
import json
from datetime import datetime
from aiohttp import web
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def health_check(request):
    """Simple health check endpoint"""
    return web.Response(
        text=json.dumps({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "easyshifts-backend-debug",
            "port": os.getenv('PORT', '8080'),
            "host": os.getenv('HOST', '0.0.0.0'),
            "environment": {
                "DB_HOST": os.getenv('DB_HOST', 'not set'),
                "DB_PORT": os.getenv('DB_PORT', 'not set'),
                "REDIS_HOST": os.getenv('REDIS_HOST', 'not set'),
                "PYTHONPATH": os.getenv('PYTHONPATH', 'not set')
            }
        }),
        content_type='application/json'
    )

async def root_handler(request):
    """Root endpoint"""
    return web.Response(
        text=json.dumps({
            "message": "EasyShifts Backend Debug Server",
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "endpoints": [
                "/health",
                "/debug",
                "/test"
            ]
        }),
        content_type='application/json'
    )

async def debug_handler(request):
    """Debug information endpoint"""
    return web.Response(
        text=json.dumps({
            "debug_info": {
                "python_version": sys.version,
                "working_directory": os.getcwd(),
                "environment_variables": dict(os.environ),
                "request_info": {
                    "method": request.method,
                    "path": request.path,
                    "headers": dict(request.headers)
                }
            }
        }),
        content_type='application/json'
    )

async def test_db_handler(request):
    """Test database connection"""
    try:
        from main import get_db_session
        with get_db_session() as session:
            return web.Response(
                text=json.dumps({
                    "database": "connected",
                    "status": "success",
                    "timestamp": datetime.now().isoformat()
                }),
                content_type='application/json'
            )
    except Exception as e:
        return web.Response(
            text=json.dumps({
                "database": "failed",
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }),
            content_type='application/json',
            status=500
        )

async def create_app():
    """Create the web application"""
    app = web.Application()
    
    # Add routes
    app.router.add_get('/', root_handler)
    app.router.add_get('/health', health_check)
    app.router.add_get('/debug', debug_handler)
    app.router.add_get('/test-db', test_db_handler)
    
    return app

async def start_debug_server():
    """Start the debug server"""
    port = int(os.getenv('PORT', 8080))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"🚀 Starting EasyShifts Debug Server")
    logger.info(f"📍 Host: {host}")
    logger.info(f"🔌 Port: {port}")
    logger.info(f"🐍 Python: {sys.version}")
    logger.info(f"📁 Working Dir: {os.getcwd()}")
    
    # Print environment variables
    logger.info("🌍 Environment Variables:")
    for key, value in os.environ.items():
        if 'PASSWORD' in key or 'SECRET' in key:
            logger.info(f"   {key}: [HIDDEN]")
        else:
            logger.info(f"   {key}: {value}")
    
    try:
        app = await create_app()
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info(f"✅ Debug server started successfully!")
        logger.info(f"🔍 Health check: http://{host}:{port}/health")
        logger.info(f"🐛 Debug info: http://{host}:{port}/debug")
        logger.info(f"🗄️  Database test: http://{host}:{port}/test-db")
        logger.info(f"🎯 Server is ready to accept connections!")
        
        # Keep running
        await asyncio.Future()
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    """Main entry point"""
    print("🐛 EasyShifts Debug Server Starting...")
    print("=" * 40)
    
    try:
        asyncio.run(start_debug_server())
    except KeyboardInterrupt:
        print("\n⏹️  Debug server stopped by user")
    except Exception as e:
        print(f"\n❌ Debug server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
