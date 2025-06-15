#!/usr/bin/env python3
"""
Admin User Creation Script for EasyShifts
Creates admin users or promotes existing users to admin status.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import get_db_session
from db.controllers.users_controller import UsersController
from security.password_security import hash_password
import getpass

def create_admin_user():
    """Create a new admin user or promote existing user to admin."""
    
    print("🔧 EasyShifts Admin User Creation Tool")
    print("=" * 50)
    
    try:
        with get_db_session() as session:
            users_controller = UsersController(session)
            
            # Get user input
            print("\n📝 Enter admin user details:")
            username = input("Username: ").strip()
            
            if not username:
                print("❌ Username cannot be empty!")
                return
            
            # Check if user already exists
            existing_user = users_controller.get_user_by_username(username)
            
            if existing_user:
                print(f"\n👤 User '{username}' already exists!")
                print(f"   Current status: Manager={existing_user.isManager}, Admin={existing_user.isAdmin}")
                
                if existing_user.isAdmin:
                    print("✅ User is already an admin!")
                    return
                
                promote = input("\n🔄 Promote this user to admin? (y/N): ").strip().lower()
                if promote == 'y':
                    # Promote existing user to admin
                    existing_user.isAdmin = True
                    existing_user.isManager = True  # Admins are also managers
                    existing_user.isApproval = True  # Ensure admin is approved
                    
                    session.commit()
                    print(f"✅ User '{username}' promoted to admin successfully!")
                    return
                else:
                    print("❌ Operation cancelled.")
                    return
            
            # Create new admin user
            print(f"\n🆕 Creating new admin user '{username}'...")
            
            name = input("Full Name: ").strip()
            if not name:
                print("❌ Name cannot be empty!")
                return
            
            email = input("Email: ").strip()
            if not email:
                print("❌ Email cannot be empty!")
                return
            
            # Get password securely
            while True:
                password = getpass.getpass("Password: ")
                if len(password) < 6:
                    print("❌ Password must be at least 6 characters!")
                    continue
                
                confirm_password = getpass.getpass("Confirm Password: ")
                if password != confirm_password:
                    print("❌ Passwords don't match!")
                    continue
                break
            
            # Hash the password
            hashed_password = hash_password(password)
            
            # Create admin user data
            admin_data = {
                'username': username,
                'password': hashed_password,
                'name': name,
                'email': email,
                'isManager': True,
                'isAdmin': True,
                'isActive': True,
                'isApproval': True,
                'client_company_id': None,
                'employee_type': None,
                'google_id': None
            }
            
            # Create the admin user
            new_admin = users_controller.create_entity(admin_data)
            
            if new_admin:
                print(f"\n✅ Admin user '{username}' created successfully!")
                print(f"   User ID: {new_admin.id}")
                print(f"   Name: {new_admin.name}")
                print(f"   Email: {new_admin.email}")
                print(f"   Admin: {new_admin.isAdmin}")
                print(f"   Manager: {new_admin.isManager}")
            else:
                print("❌ Failed to create admin user!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def list_admin_users():
    """List all admin users in the system."""
    
    print("\n👥 Current Admin Users:")
    print("-" * 30)
    
    try:
        with get_db_session() as session:
            users_controller = UsersController(session)
            
            # Get all users
            all_users = users_controller.get_all_entities()
            admin_users = [user for user in all_users if user.isAdmin]
            
            if not admin_users:
                print("❌ No admin users found!")
                return
            
            for user in admin_users:
                print(f"👤 {user.username} ({user.name})")
                print(f"   ID: {user.id}")
                print(f"   Email: {user.email}")
                print(f"   Active: {user.isActive}")
                print(f"   Approved: {user.isApproval}")
                print()
                
    except Exception as e:
        print(f"❌ Error listing admin users: {e}")

def main():
    """Main function with menu options."""
    
    while True:
        print("\n🎯 EasyShifts Admin Management")
        print("=" * 40)
        print("1. Create/Promote Admin User")
        print("2. List Admin Users")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            create_admin_user()
        elif choice == '2':
            list_admin_users()
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice! Please select 1-3.")

if __name__ == "__main__":
    main()
