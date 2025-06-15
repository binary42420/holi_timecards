#!/usr/bin/env python3
"""
Robust Timesheets Server Startup Script
Handles environment setup and graceful error handling.
"""

import os
import sys
import asyncio
import traceback

def setup_environment():
    """Setup required environment variables"""
    # Set defaults for missing environment variables
    env_defaults = {
        'PORT': '8080',
        'HOST': '0.0.0.0',
        'DB_PASSWORD': 'a61d15d9b4f2671739338d1082cc7b75c0084e21',
        'REDIS_PASSWORD': 'AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa',
        'DB_HOST': 'miano.h.filess.io',
        'DB_PORT': '3305',
        'DB_USER': 'easyshiftsdb_danceshall',
        'DB_NAME': 'easyshiftsdb_danceshall'
    }
    
    for key, default_value in env_defaults.items():
        if not os.getenv(key):
            os.environ[key] = default_value
            print(f"Set {key} to default value")

async def start_server_with_retries():
    """Start server with retry logic"""
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            print(f"🚀 Starting server (attempt {attempt + 1}/{max_retries})")
            
            import Server
            await Server.start_combined_server()
            break  # Success
            
        except Exception as e:
            print(f"❌ Server start failed (attempt {attempt + 1}): {e}")
            
            if attempt < max_retries - 1:
                print(f"⏳ Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print("💥 All retry attempts failed")
                raise

def main():
    """Main startup function"""
    print("🚀 Holi Timesheets Robust Server Startup")
    print("=" * 50)
    
    try:
        # Setup environment
        setup_environment()
        
        # Start server with retries
        asyncio.run(start_server_with_retries())
        
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Fatal server error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
