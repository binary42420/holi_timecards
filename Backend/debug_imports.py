#!/usr/bin/env python3
"""
Debug imports to find what's causing the hang
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

def test_import(module_name, description):
    """Test importing a module with timing"""
    print(f"📦 Importing {description}...")
    start_time = time.time()
    
    try:
        if module_name == "Server":
            import Server
        elif module_name == "main":
            from main import get_db_session
        elif module_name == "handlers.login":
            from handlers.login import handle_login
        elif module_name == "aiohttp":
            from aiohttp import web
        elif module_name == "redis":
            from config.redis_config import redis_config
        else:
            exec(f"import {module_name}")
        
        end_time = time.time()
        print(f"   ✅ {description} imported successfully ({end_time - start_time:.2f}s)")
        return True
        
    except Exception as e:
        end_time = time.time()
        print(f"   ❌ {description} import failed ({end_time - start_time:.2f}s): {e}")
        return False

def main():
    """Test imports step by step"""
    print("🧪 Debug Import Test")
    print("=" * 25)
    
    imports_to_test = [
        ("os", "OS module"),
        ("sys", "Sys module"),
        ("asyncio", "AsyncIO"),
        ("json", "JSON"),
        ("aiohttp", "aiohttp web framework"),
        ("main", "Database main module"),
        ("redis", "Redis config"),
        ("handlers.login", "Login handler"),
        ("Server", "EasyShifts Server module")
    ]
    
    for module_name, description in imports_to_test:
        success = test_import(module_name, description)
        if not success:
            print(f"\n❌ Import failed at: {description}")
            print("Stopping import test here.")
            break
        time.sleep(0.5)  # Small delay between imports
    
    print("\n✅ Import test completed!")

if __name__ == "__main__":
    main()
