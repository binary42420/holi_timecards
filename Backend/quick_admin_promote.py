#!/usr/bin/env python3
"""
Quick Admin Promotion Script
Promotes an existing user to admin status.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import get_db_session
from db.controllers.users_controller import UsersController

def promote_user_to_admin(username):
    """Promote a user to admin status."""
    
    try:
        with get_db_session() as session:
            users_controller = UsersController(session)
            
            # Find the user
            user = users_controller.get_user_by_username(username)
            
            if not user:
                print(f"❌ User '{username}' not found!")
                return False
            
            # Check current status
            print(f"👤 Found user: {user.name} ({user.username})")
            print(f"   Current: Manager={user.isManager}, Admin={user.isAdmin}")
            
            if user.isAdmin:
                print("✅ User is already an admin!")
                return True
            
            # Promote to admin
            user.isAdmin = True
            user.isManager = True  # Admins are also managers
            user.isApproval = True  # Ensure approved
            user.isActive = True   # Ensure active
            
            session.commit()
            
            print(f"✅ User '{username}' promoted to admin successfully!")
            print(f"   New status: Manager={user.isManager}, Admin={user.isAdmin}")
            return True
            
    except Exception as e:
        print(f"❌ Error promoting user: {e}")
        return False

def main():
    """Main function."""
    
    if len(sys.argv) != 2:
        print("Usage: python quick_admin_promote.py <username>")
        print("Example: python quick_admin_promote.py binary420")
        return
    
    username = sys.argv[1]
    promote_user_to_admin(username)

if __name__ == "__main__":
    main()
