#!/usr/bin/env python3
"""
Holi Timesheets Server Startup with Environment Loading
"""

import os
import sys
from pathlib import Path

def load_environment():
    """Load environment variables from .env file"""
    env_file = Path('.env')
    
    if env_file.exists():
        print("📋 Loading environment variables...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Environment variables loaded")
    else:
        print("⚠️  No .env file found, using system environment")

def main():
    """Start server with environment loaded"""
    print("🚀 Starting Holi Timesheets Server with Environment")
    print("=" * 50)
    
    # Load environment first
    load_environment()
    
    # Import and start server
    try:
        print("🔌 Starting combined HTTP/WebSocket server...")

        # Test database connection first (but don't fail if it doesn't work)
        try:
            from main import get_db_session
            with get_db_session() as session:
                print("✅ Database connection test successful")
        except Exception as db_error:
            print(f"⚠️  Database connection test failed: {db_error}")
            print("   Server will start anyway - database will be retried on requests")

        # Start server regardless of database status
        import Server
        import asyncio
        asyncio.run(Server.start_combined_server())

    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        # Exit with error code for Cloud Run
        sys.exit(1)

if __name__ == "__main__":
    main()
