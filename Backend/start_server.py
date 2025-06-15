#!/usr/bin/env python3
"""
Start the EasyShifts server with proper error handling
"""

import os
import sys
import asyncio
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

def main():
    """Start the server with comprehensive error handling"""
    print("🚀 Starting EasyShifts Server")
    print("=" * 30)
    
    try:
        # Check environment
        print("📋 Environment Check:")
        print(f"   HOST: {os.getenv('HOST', 'not set')}")
        print(f"   PORT: {os.getenv('PORT', 'not set')}")
        print(f"   DB_PASSWORD: {'set' if os.getenv('DB_PASSWORD') else 'not set'}")
        print(f"   REDIS_PASSWORD: {'set' if os.getenv('REDIS_PASSWORD') else 'not set'}")
        
        # Import server module
        print("\n📦 Importing Server module...")
        import Server
        print("✅ Server module imported successfully")
        
        # Start the server
        print("\n🔌 Starting server...")
        asyncio.run(Server.start_combined_server())
        
    except KeyboardInterrupt:
        print("\n⏹️ Server stopped by user (Ctrl+C)")
        sys.exit(0)
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Server Error: {e}")
        print(f"Error Type: {type(e).__name__}")
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
