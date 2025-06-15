#!/usr/bin/env python3
"""
Debug script for Google signup issues.
This script will help identify what's causing the "failed to create account" error.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import initialize_database_and_session
from sqlalchemy import text
from handlers.google_auth import GoogleAuthHandler
import logging

# Set up logging to see detailed errors
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_database_schema():
    """Check if the Google OAuth columns exist in the database."""
    print("🔍 Checking database schema...")
    
    try:
        db, _ = initialize_database_and_session()
        
        # Check if Google OAuth columns exist
        result = db.execute(text("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'users'
            AND COLUMN_NAME IN ('google_id', 'email', 'google_picture', 'last_login')
            ORDER BY COLUMN_NAME
        """))
        
        columns = result.fetchall()
        
        if len(columns) == 4:
            print("✅ All Google OAuth columns exist:")
            for col in columns:
                print(f"   - {col[0]}: {col[1]} (nullable: {col[2]})")
        else:
            print("❌ Missing Google OAuth columns:")
            existing_cols = [col[0] for col in columns]
            required_cols = ['google_id', 'email', 'google_picture', 'last_login']
            missing_cols = [col for col in required_cols if col not in existing_cols]
            print(f"   Missing: {missing_cols}")
            return False
        
        # Check if password column is nullable
        result = db.execute(text("""
            SELECT IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'users'
            AND COLUMN_NAME = 'password'
        """))
        
        password_nullable = result.fetchone()[0]
        if password_nullable == 'YES':
            print("✅ Password column is nullable (good for Google OAuth)")
        else:
            print("⚠️  Password column is NOT nullable (might cause issues)")
        
        return True
        
    except Exception as e:
        print(f"❌ Database schema check failed: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()

def test_google_signup_handler():
    """Test the Google signup handler with mock data."""
    print("\n🧪 Testing Google signup handler...")
    
    try:
        handler = GoogleAuthHandler()
        
        # Mock Google data (similar to what comes from frontend)
        mock_data = {
            'username': 'test_google_user',
            'name': 'Test Google User',
            'email': 'test@example.com',
            'googleData': {
                'sub': 'mock_google_id_12345',
                'picture': 'https://example.com/photo.jpg',
                'email': 'test@example.com',
                'name': 'Test Google User'
            }
        }
        
        print("📤 Testing manager signup...")
        response = handler.handle_google_signup_manager(mock_data)
        
        if response.get('success'):
            print("✅ Manager signup handler works!")
            print(f"   Created user: {response['data']['username']}")
        else:
            print(f"❌ Manager signup failed: {response.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Google signup handler test failed: {e}")
        logger.exception("Full error details:")
        return False

def test_database_connection():
    """Test basic database connectivity."""
    print("\n🔌 Testing database connection...")
    
    try:
        db, _ = initialize_database_and_session()
        
        # Test basic query
        result = db.execute(text("SELECT COUNT(*) as count FROM users"))
        count = result.fetchone()[0]
        print(f"✅ Database connected, {count} users found")
        
        # Test insert capability (without actually inserting)
        try:
            db.execute(text("SELECT 1"))
            print("✅ Database queries work")
        except Exception as e:
            print(f"❌ Database query failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()

def main():
    """Run all debug checks."""
    print("🔧 EasyShifts Google Signup Debug Tool")
    print("=" * 50)
    
    # Test 1: Database connection
    db_ok = test_database_connection()
    
    # Test 2: Database schema
    schema_ok = check_database_schema()
    
    # Test 3: Google signup handler (only if database is OK)
    handler_ok = False
    if db_ok and schema_ok:
        handler_ok = test_google_signup_handler()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Debug Summary:")
    print(f"   Database Connection: {'✅' if db_ok else '❌'}")
    print(f"   Database Schema: {'✅' if schema_ok else '❌'}")
    print(f"   Google Handler: {'✅' if handler_ok else '❌'}")
    
    if db_ok and schema_ok and handler_ok:
        print("\n🎉 Everything looks good!")
        print("   The issue might be in the frontend data or request format.")
        print("   Check the browser console and backend logs for more details.")
    else:
        print("\n🔧 Issues found:")
        if not db_ok:
            print("   - Fix database connection issues")
        if not schema_ok:
            print("   - Run the MySQL migration script to add Google OAuth columns")
        if not handler_ok:
            print("   - Check the detailed error logs above")
    
    print("\n💡 Next steps:")
    print("1. Fix any issues shown above")
    print("2. Restart your backend server")
    print("3. Try Google signup again")
    print("4. Check backend logs for detailed error messages")

if __name__ == "__main__":
    main()
