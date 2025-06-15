#!/usr/bin/env python3
"""
Install Redis dependencies for EasyShifts
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Install all required Redis dependencies"""
    print("🚀 Installing Redis dependencies for EasyShifts...")
    
    # List of required packages
    packages = [
        "redis>=4.5.0",
        "aioredis>=2.0.0", 
        "hiredis>=2.0.0",
        "bcrypt>=4.0.0",
        "python-dotenv>=1.0.0"
    ]
    
    failed_packages = []
    
    for package in packages:
        print(f"📦 Installing {package}...")
        if install_package(package):
            print(f"✅ {package} installed successfully")
        else:
            print(f"❌ Failed to install {package}")
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n❌ Failed to install: {', '.join(failed_packages)}")
        print("Please install manually using:")
        for package in failed_packages:
            print(f"  pip install {package}")
        return False
    else:
        print("\n✅ All Redis dependencies installed successfully!")
        print("\nNext steps:")
        print("1. Test Redis connection: python test_redis_connection.py")
        print("2. Run migration: python migrations/migrate_to_redis_sessions.py")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
