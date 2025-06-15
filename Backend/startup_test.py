#!/usr/bin/env python3
"""
Startup test script to diagnose deployment issues.
This script tests each component that could cause startup failures.
"""

import os
import sys
import traceback
from datetime import datetime

def test_basic_imports():
    """Test basic Python imports"""
    print("🔍 Testing basic imports...")
    try:
        import json
        import asyncio
        import logging
        print("✅ Basic imports successful")
        return True
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return False

def test_web_framework_imports():
    """Test web framework imports"""
    print("🔍 Testing web framework imports...")
    try:
        import websockets
        from aiohttp import web
        import aiohttp_cors
        print("✅ Web framework imports successful")
        return True
    except Exception as e:
        print(f"❌ Web framework imports failed: {e}")
        return False

def test_database_imports():
    """Test database-related imports"""
    print("🔍 Testing database imports...")
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        import pymysql
        print("✅ Database imports successful")
        return True
    except Exception as e:
        print(f"❌ Database imports failed: {e}")
        return False

def test_google_auth_imports():
    """Test Google authentication imports"""
    print("🔍 Testing Google auth imports...")
    try:
        from google.auth.transport import requests
        from google.oauth2 import id_token
        print("✅ Google auth imports successful")
        return True
    except Exception as e:
        print(f"❌ Google auth imports failed: {e}")
        return False

def test_environment_variables():
    """Test environment variables"""
    print("🔍 Testing environment variables...")
    try:
        port = os.getenv('PORT', '8080')
        host = os.getenv('HOST', '0.0.0.0')
        print(f"✅ Environment variables - PORT: {port}, HOST: {host}")
        return True
    except Exception as e:
        print(f"❌ Environment variables failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    try:
        from sqlalchemy import create_engine, text

        # Get database password using the same method as main.py
        def get_database_password():
            db_password = os.getenv("DB_PASSWORD")
            if db_password:
                print("   Using database password from environment variable")
                return db_password

            try:
                from config.private_password import PASSWORD
                print("   Using database password from config file")
                return PASSWORD
            except ImportError:
                raise RuntimeError("Database password not configured")

        DB_HOST = os.getenv("DB_HOST", "miano.h.filess.io")
        DB_PORT = os.getenv("DB_PORT", "3305")
        DB_USER = os.getenv("DB_USER", "easyshiftsdb_danceshall")
        DB_NAME = os.getenv("DB_NAME", "easyshiftsdb_danceshall")
        PASSWORD = get_database_password()

        connection_url = f'mariadb+pymysql://{DB_USER}:{PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        print(f"   Connecting to: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        
        engine = create_engine(
            connection_url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={
                'connect_timeout': 10,
                'read_timeout': 10,
                'write_timeout': 10
            }
        )
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ Database connection successful: {row}")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        traceback.print_exc()
        return False

def test_main_module():
    """Test main module initialization"""
    print("🔍 Testing main module...")
    try:
        from main import initialize_database_and_session_factory
        initialize_database_and_session_factory()
        print("✅ Main module initialization successful")
        return True
    except Exception as e:
        print(f"❌ Main module initialization failed: {e}")
        traceback.print_exc()
        return False

def test_handlers_import():
    """Test handlers import"""
    print("🔍 Testing handlers import...")
    try:
        from handlers import login
        from handlers.google_auth import google_auth_handler
        print("✅ Handlers import successful")
        return True
    except Exception as e:
        print(f"❌ Handlers import failed: {e}")
        traceback.print_exc()
        return False

def test_server_startup():
    """Test basic server startup without actually starting"""
    print("🔍 Testing server startup components...")
    try:
        import asyncio
        from aiohttp import web
        
        async def test_app():
            app = web.Application()
            app.router.add_get('/health', lambda req: web.Response(text='OK'))
            return app
        
        # Test that we can create the app
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        app = loop.run_until_complete(test_app())
        loop.close()
        
        print("✅ Server startup components successful")
        return True
    except Exception as e:
        print(f"❌ Server startup components failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all startup tests"""
    print(f"🚀 EasyShifts Backend Startup Test")
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"⏰ Timestamp: {datetime.now()}")
    print("=" * 60)
    
    tests = [
        test_basic_imports,
        test_web_framework_imports,
        test_database_imports,
        test_google_auth_imports,
        test_environment_variables,
        test_database_connection,
        test_main_module,
        test_handlers_import,
        test_server_startup
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            traceback.print_exc()
            failed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Server should start successfully.")
        return 0
    else:
        print("💥 Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
