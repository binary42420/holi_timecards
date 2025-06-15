"""
User Management Handlers for EasyShifts
Handles creation and management of managers and admins.
"""

from main import get_db_session
from db.controllers.users_controller import UsersController
from db.controllers.employee_certifications_controller import EmployeeCertificationsController
from user_session import UserSession
from datetime import datetime
import re


def handle_create_manager(data: dict, user_session: UserSession) -> dict:
    """
    Create a new manager account.
    Only admins can create managers.
    """
    request_id = 300
    if not user_session:
        return {"request_id": request_id, "success": False, "error": "User session not found."}
    
    try:
        # Verify permissions - only admins can create managers
        with get_db_session() as session:

            users_controller = UsersController(session)
        current_user = users_controller.get_entity(user_session.get_id)
        
        if not current_user.isAdmin:
            return {"request_id": request_id, "success": False, "error": "Only admins can create manager accounts."}
        
        # Validate required fields
        required_fields = ['username', 'password', 'name', 'email']
        for field in required_fields:
            if not data.get(field):
                return {"request_id": request_id, "success": False, "error": f"{field} is required."}
        
        # Validate email format
        email = data.get('email')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return {"request_id": request_id, "success": False, "error": "Invalid email format."}
        
        # Check if username already exists
        existing_user = users_controller.get_user_by_username(data['username'])
        if existing_user:
            return {"request_id": request_id, "success": False, "error": "Username already exists."}
        
        # Check if email already exists
        existing_email_user = users_controller.find_user_by_email(email)
        if existing_email_user:
            return {"request_id": request_id, "success": False, "error": "Email already exists."}
        
        # Create manager user
        user_data = {
            'username': data['username'],
            'password': data['password'],
            'name': data['name'],
            'email': email,
            'isManager': True,
            'isAdmin': False,
            'isActive': True,
            'isApproval': True,  # Managers are auto-approved
            'client_company_id': None,  # Agency manager, not client
            'employee_type': None,  # Managers don't have employee types
            'google_id': None
        }
        
        new_manager = users_controller.create_entity(user_data)
        
        if new_manager:
            return {
                "request_id": request_id, 
                "success": True, 
                "message": f"Manager '{data['username']}' created successfully.",
                "data": {
                    "id": new_manager.id,
                    "username": new_manager.username,
                    "name": new_manager.name,
                    "email": new_manager.email,
                    "isManager": new_manager.isManager,
                    "isAdmin": new_manager.isAdmin
                }
            }
        else:
            return {"request_id": request_id, "success": False, "error": "Failed to create manager account."}
            
    except Exception as e:
        print(f"Error creating manager: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to create manager account."}


def handle_create_admin(data: dict, user_session: UserSession) -> dict:
    """
    Create a new admin account.
    Only existing admins can create new admins.
    """
    request_id = 301
    if not user_session:
        return {"request_id": request_id, "success": False, "error": "User session not found."}
    
    try:
        # Verify permissions - only admins can create admins
        with get_db_session() as session:

            users_controller = UsersController(session)
        current_user = users_controller.get_entity(user_session.get_id)
        
        if not current_user.isAdmin:
            return {"request_id": request_id, "success": False, "error": "Only admins can create admin accounts."}
        
        # Validate required fields
        required_fields = ['username', 'password', 'name', 'email']
        for field in required_fields:
            if not data.get(field):
                return {"request_id": request_id, "success": False, "error": f"{field} is required."}
        
        # Validate email format
        email = data.get('email')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return {"request_id": request_id, "success": False, "error": "Invalid email format."}
        
        # Check if username already exists
        existing_user = users_controller.get_user_by_username(data['username'])
        if existing_user:
            return {"request_id": request_id, "success": False, "error": "Username already exists."}
        
        # Check if email already exists
        existing_email_user = users_controller.find_user_by_email(email)
        if existing_email_user:
            return {"request_id": request_id, "success": False, "error": "Email already exists."}
        
        # Create admin user
        user_data = {
            'username': data['username'],
            'password': data['password'],
            'name': data['name'],
            'email': email,
            'isManager': True,  # Admins are also managers
            'isAdmin': True,
            'isActive': True,
            'isApproval': True,  # Admins are auto-approved
            'client_company_id': None,  # Agency admin, not client
            'employee_type': None,  # Admins don't have employee types
            'google_id': None
        }
        
        new_admin = users_controller.create_entity(user_data)
        
        if new_admin:
            return {
                "request_id": request_id, 
                "success": True, 
                "message": f"Admin '{data['username']}' created successfully.",
                "data": {
                    "id": new_admin.id,
                    "username": new_admin.username,
                    "name": new_admin.name,
                    "email": new_admin.email,
                    "isManager": new_admin.isManager,
                    "isAdmin": new_admin.isAdmin
                }
            }
        else:
            return {"request_id": request_id, "success": False, "error": "Failed to create admin account."}
            
    except Exception as e:
        print(f"Error creating admin: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to create admin account."}


def handle_get_all_users(user_session: UserSession) -> dict:
    """
    Get all users for admin management.
    Only admins can access this.
    """
    request_id = 302
    if not user_session:
        return {"request_id": request_id, "success": False, "error": "User session not found."}
    
    try:
        # Verify permissions - only admins can view all users
        with get_db_session() as session:

            users_controller = UsersController(session)
        current_user = users_controller.get_entity(user_session.get_id)
        
        if not current_user.isAdmin:
            return {"request_id": request_id, "success": False, "error": "Only admins can view all users."}
        
        # Get all users
        all_users = users_controller.get_all_entities()
        
        users_data = []
        for user in all_users:
            user_dict = {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'isManager': user.isManager,
                'isAdmin': user.isAdmin,
                'isActive': user.isActive,
                'isApproval': user.isApproval,
                'client_company_id': user.client_company_id,
                'employee_type': user.employee_type.value if user.employee_type else None,
                'google_linked': bool(user.google_id),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'created_at': None  # Add if you have a created_at field
            }
            
            # Determine user role for display
            if user.isAdmin:
                user_dict['role'] = 'Admin'
            elif user.isManager:
                user_dict['role'] = 'Manager'
            elif user.client_company_id:
                user_dict['role'] = 'Client'
            else:
                user_dict['role'] = 'Employee'
            
            users_data.append(user_dict)
        
        # Sort by role (Admin, Manager, Client, Employee) then by name
        role_order = {'Admin': 0, 'Manager': 1, 'Client': 2, 'Employee': 3}
        users_data.sort(key=lambda x: (role_order.get(x['role'], 4), x['name']))
        
        return {
            "request_id": request_id, 
            "success": True, 
            "data": {
                "users": users_data,
                "total_count": len(users_data),
                "summary": {
                    "admins": len([u for u in users_data if u['role'] == 'Admin']),
                    "managers": len([u for u in users_data if u['role'] == 'Manager']),
                    "clients": len([u for u in users_data if u['role'] == 'Client']),
                    "employees": len([u for u in users_data if u['role'] == 'Employee']),
                    "active_users": len([u for u in users_data if u['isActive']]),
                    "approved_users": len([u for u in users_data if u['isApproval']])
                }
            }
        }
        
    except Exception as e:
        print(f"Error getting all users: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to retrieve users."}


def handle_update_user_role(data: dict, user_session: UserSession) -> dict:
    """
    Update a user's role (promote/demote).
    Only admins can update user roles.
    """
    request_id = 303
    if not user_session:
        return {"request_id": request_id, "success": False, "error": "User session not found."}
    
    try:
        # Verify permissions - only admins can update user roles
        with get_db_session() as session:

            users_controller = UsersController(session)
        current_user = users_controller.get_entity(user_session.get_id)
        
        if not current_user.isAdmin:
            return {"request_id": request_id, "success": False, "error": "Only admins can update user roles."}
        
        # Validate required fields
        user_id = data.get('user_id')
        new_role = data.get('new_role')  # 'admin', 'manager', 'employee'
        
        if not user_id or not new_role:
            return {"request_id": request_id, "success": False, "error": "user_id and new_role are required."}
        
        if new_role not in ['admin', 'manager', 'employee']:
            return {"request_id": request_id, "success": False, "error": "new_role must be 'admin', 'manager', or 'employee'."}
        
        # Get the target user
        target_user = users_controller.get_entity(user_id)
        if not target_user:
            return {"request_id": request_id, "success": False, "error": "User not found."}
        
        # Prevent self-demotion from admin
        if target_user.id == current_user.id and target_user.isAdmin and new_role != 'admin':
            return {"request_id": request_id, "success": False, "error": "You cannot demote yourself from admin."}
        
        # Update user role
        update_data = {}
        if new_role == 'admin':
            update_data['isAdmin'] = True
            update_data['isManager'] = True  # Admins are also managers
        elif new_role == 'manager':
            update_data['isAdmin'] = False
            update_data['isManager'] = True
        else:  # employee
            update_data['isAdmin'] = False
            update_data['isManager'] = False
        
        updated_user = users_controller.update_entity(user_id, update_data)
        
        if updated_user:
            return {
                "request_id": request_id, 
                "success": True, 
                "message": f"User '{target_user.username}' role updated to {new_role}.",
                "data": {
                    "id": updated_user.id,
                    "username": updated_user.username,
                    "name": updated_user.name,
                    "isManager": updated_user.isManager,
                    "isAdmin": updated_user.isAdmin,
                    "new_role": new_role
                }
            }
        else:
            return {"request_id": request_id, "success": False, "error": "Failed to update user role."}
            
    except Exception as e:
        print(f"Error updating user role: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update user role."}
