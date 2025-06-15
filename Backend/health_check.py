#!/usr/bin/env python3
"""
Simple health check script for debugging deployment issues.
This script can be run independently to test basic functionality.
"""

import os
import sys
import json
from datetime import datetime

def check_environment():
    """Check environment variables and basic setup"""
    print("=== Environment Check ===")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check environment variables
    host = os.getenv('HOST', '0.0.0.0')
    port = os.getenv('PORT', '8080')
    print(f"HOST: {host}")
    print(f"PORT: {port}")
    
    # Check if we can import required modules
    try:
        import aiohttp
        print(f"✅ aiohttp version: {aiohttp.__version__}")
    except ImportError as e:
        print(f"❌ aiohttp import failed: {e}")
        return False
    
    try:
        import aiohttp_cors
        print("✅ aiohttp_cors imported successfully")
    except ImportError as e:
        print(f"❌ aiohttp_cors import failed: {e}")
        return False
    
    try:
        import sqlalchemy
        print(f"✅ sqlalchemy version: {sqlalchemy.__version__}")
    except ImportError as e:
        print(f"❌ sqlalchemy import failed: {e}")
        return False
    
    try:
        import pymysql
        print(f"✅ pymysql version: {pymysql.__version__}")
    except ImportError as e:
        print(f"❌ pymysql import failed: {e}")
        return False
    
    return True

def check_database_connection():
    """Test database connection without creating tables"""
    print("\n=== Database Connection Check ===")

    try:
        # Get database password using the same method as main.py
        def get_database_password():
            import os
            db_password = os.getenv("DB_PASSWORD")
            if db_password:
                print("✅ Using database password from environment variable")
                return db_password

            try:
                from config.private_password import PASSWORD
                print("✅ Using database password from config file")
                return PASSWORD
            except ImportError:
                raise RuntimeError("Database password not configured")

        PASSWORD = get_database_password()
    except Exception as e:
        print(f"❌ Password configuration failed: {e}")
        return False

    try:
        from sqlalchemy import create_engine, text
        import os

        DB_HOST = os.getenv("DB_HOST", "miano.h.filess.io")
        DB_PORT = os.getenv("DB_PORT", "3305")
        DB_USER = os.getenv("DB_USER", "easyshiftsdb_danceshall")
        DB_NAME = os.getenv("DB_NAME", "easyshiftsdb_danceshall")

        print(f"Attempting connection to: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

        engine = create_engine(
            f'mariadb+pymysql://{DB_USER}:{PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={
                'connect_timeout': 10,
                'read_timeout': 10,
                'write_timeout': 10
            }
        )
        
        # Test the connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ Database connection successful: {row}")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_imports():
    """Test importing main application modules"""
    print("\n=== Application Import Check ===")
    
    try:
        from main import initialize_database_and_session
        print("✅ main.py imported successfully")
    except Exception as e:
        print(f"❌ main.py import failed: {e}")
        return False
    
    try:
        # Test importing handlers without initializing database
        import handlers
        print("✅ handlers package imported successfully")
    except Exception as e:
        print(f"❌ handlers import failed: {e}")
        return False
    
    return True

def main():
    """Run all health checks"""
    print("🏥 EasyShifts Backend Health Check")
    print("=" * 50)
    
    checks = [
        ("Environment", check_environment),
        ("Database Connection", check_database_connection),
        ("Application Imports", check_imports)
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ {name} check crashed: {e}")
            results[name] = False
    
    print("\n" + "=" * 50)
    print("🏥 Health Check Summary")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All health checks passed!")
        return 0
    else:
        print("\n⚠️  Some health checks failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
