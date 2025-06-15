#!/usr/bin/env python3
"""
Minimal server for debugging deployment issues.
This server starts with minimal dependencies to isolate the problem.
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timezone
from aiohttp import web
import aiohttp_cors

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def handle_health(request):
    """Simple health check endpoint"""
    return web.Response(
        text=json.dumps({
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "easyshifts-backend-minimal",
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "environment": {
                "PORT": os.getenv('PORT', 'not set'),
                "HOST": os.getenv('HOST', 'not set'),
                "DB_HOST": os.getenv('DB_HOST', 'not set'),
                "DB_PORT": os.getenv('DB_PORT', 'not set'),
                "DB_USER": os.getenv('DB_USER', 'not set'),
                "DB_NAME": os.getenv('DB_NAME', 'not set')
            }
        }),
        content_type='application/json'
    )

async def handle_test_db(request):
    """Test database connection endpoint"""
    try:
        # Try to import and test database
        from sqlalchemy import create_engine, text

        # Get database password using the same method as main.py
        def get_database_password():
            db_password = os.getenv("DB_PASSWORD")
            if db_password:
                return db_password

            try:
                from config.private_password import PASSWORD
                return PASSWORD
            except ImportError:
                raise RuntimeError("Database password not configured")

        DB_HOST = os.getenv("DB_HOST", "miano.h.filess.io")
        DB_PORT = os.getenv("DB_PORT", "3305")
        DB_USER = os.getenv("DB_USER", "easyshiftsdb_danceshall")
        DB_NAME = os.getenv("DB_NAME", "easyshiftsdb_danceshall")
        PASSWORD = get_database_password()

        connection_url = f'mariadb+pymysql://{DB_USER}:{PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        
        engine = create_engine(
            connection_url,
            echo=False,
            pool_pre_ping=True,
            connect_args={'connect_timeout': 5}
        )
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            
        return web.Response(
            text=json.dumps({
                "status": "database_healthy",
                "connection": f"{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
                "test_result": str(row)
            }),
            content_type='application/json'
        )
        
    except Exception as e:
        return web.Response(
            text=json.dumps({
                "status": "database_error",
                "error": str(e),
                "error_type": type(e).__name__
            }),
            content_type='application/json',
            status=500
        )

async def handle_test_imports(request):
    """Test all imports endpoint"""
    import_results = {}
    
    # Test basic imports
    try:
        import json
        import asyncio
        import logging
        import_results["basic"] = "success"
    except Exception as e:
        import_results["basic"] = f"failed: {e}"
    
    # Test web framework
    try:
        import websockets
        from aiohttp import web
        import aiohttp_cors
        import_results["web_framework"] = "success"
    except Exception as e:
        import_results["web_framework"] = f"failed: {e}"
    
    # Test database
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        import pymysql
        import_results["database"] = "success"
    except Exception as e:
        import_results["database"] = f"failed: {e}"
    
    # Test Google auth
    try:
        from google.auth.transport import requests
        from google.oauth2 import id_token
        import_results["google_auth"] = "success"
    except Exception as e:
        import_results["google_auth"] = f"failed: {e}"
    
    # Test main module
    try:
        from main import initialize_database_and_session_factory
        import_results["main_module"] = "success"
    except Exception as e:
        import_results["main_module"] = f"failed: {e}"
    
    # Test handlers
    try:
        from handlers import login
        from handlers.google_auth import google_auth_handler
        import_results["handlers"] = "success"
    except Exception as e:
        import_results["handlers"] = f"failed: {e}"
    
    return web.Response(
        text=json.dumps({
            "status": "import_test_complete",
            "results": import_results
        }),
        content_type='application/json'
    )

async def create_minimal_app():
    """Create minimal aiohttp application"""
    app = web.Application()
    
    # Add CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Add routes
    app.router.add_get('/', handle_health)
    app.router.add_get('/health', handle_health)
    app.router.add_get('/test-db', handle_test_db)
    app.router.add_get('/test-imports', handle_test_imports)
    
    # Add CORS to all routes
    for route in list(app.router.routes()):
        cors.add(route)
    
    return app

async def start_minimal_server():
    """Start minimal server"""
    port = int(os.getenv('PORT', 8080))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"🚀 Starting minimal EasyShifts server...")
    logger.info(f"🐍 Python version: {sys.version}")
    logger.info(f"📁 Working directory: {os.getcwd()}")
    logger.info(f"🌍 Environment: PORT={port}, HOST={host}")
    
    try:
        app = await create_minimal_app()
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info(f"✅ Minimal server started on {host}:{port}")
        logger.info(f"🔍 Health check: http://{host}:{port}/health")
        logger.info(f"🔍 Database test: http://{host}:{port}/test-db")
        logger.info(f"🔍 Import test: http://{host}:{port}/test-imports")
        
        # Keep the server running
        await asyncio.Future()  # Run forever
        
    except Exception as e:
        logger.exception(f"❌ Failed to start minimal server: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(start_minimal_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception(f"Server crashed: {str(e)}")
        sys.exit(1)
