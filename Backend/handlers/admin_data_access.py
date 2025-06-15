"""
Admin Data Access Handlers
Provides enhanced data access for admin users with elevated permissions.
"""

from main import get_db_session
from db.controllers.users_controller import UsersController
from db.controllers.jobs_controller import JobsController
from db.controllers.shifts_controller import ShiftsController
from db.controllers.client_companies_controller import ClientCompaniesController
from db.controllers.shiftWorkers_controller import ShiftWorkersController
from user_session import UserSession
import logging

logger = logging.getLogger(__name__)

def handle_admin_get_all_data(user_session: UserSession) -> dict:
    """
    Get comprehensive system data for admin users.
    Request ID: 950
    """
    request_id = 950
    
    if not user_session or not user_session.is_admin():
        return {
            "request_id": request_id, 
            "success": False, 
            "error": "Admin access required."
        }
    
    try:
        with get_db_session() as session:
            users_controller = UsersController(session)
            jobs_controller = JobsController(session)
            shifts_controller = ShiftsController(session)
            client_companies_controller = ClientCompaniesController(session)
            shift_workers_controller = ShiftWorkersController(session)
            
            # Get comprehensive data
            all_users = users_controller.get_all_entities()
            all_jobs = jobs_controller.get_all_entities()
            all_shifts = shifts_controller.get_all_entities()
            all_clients = client_companies_controller.get_all_entities()
            
            # Process users data
            users_data = []
            for user in all_users:
                user_data = {
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
                    'google_id': user.google_id,
                    'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None
                }
                users_data.append(user_data)
            
            # Process jobs data
            jobs_data = []
            for job in all_jobs:
                job_data = {
                    'id': job.id,
                    'name': job.name,
                    'client_company_id': job.client_company_id,
                    'venue_name': job.venue_name,
                    'venue_address': job.venue_address,
                    'venue_contact_info': job.venue_contact_info,
                    'description': job.description,
                    'created_by': job.created_by,
                    'created_at': job.created_at.isoformat() if job.created_at else None,
                    'is_active': job.is_active,
                    'estimated_start_date': job.estimated_start_date.isoformat() if job.estimated_start_date else None,
                    'estimated_end_date': job.estimated_end_date.isoformat() if job.estimated_end_date else None
                }
                
                # Add client company name
                if job.client_company_id:
                    client = client_companies_controller.get_entity(job.client_company_id)
                    if client:
                        job_data['client_company_name'] = client.name
                
                jobs_data.append(job_data)
            
            # Process shifts data
            shifts_data = []
            for shift in all_shifts:
                shift_data = {
                    'id': shift.id,
                    'job_id': shift.job_id,
                    'shift_start_datetime': shift.shift_start_datetime.isoformat() if shift.shift_start_datetime else None,
                    'shift_end_datetime': shift.shift_end_datetime.isoformat() if shift.shift_end_datetime else None,
                    'client_po_number': shift.client_po_number,
                    'required_employee_counts': shift.required_employee_counts,
                    'shiftDate': shift.shiftDate.isoformat() if shift.shiftDate else None,
                    'shiftPart': shift.shiftPart.value if shift.shiftPart else None
                }
                
                # Add job name
                if shift.job_id:
                    job = jobs_controller.get_entity(shift.job_id)
                    if job:
                        shift_data['job_name'] = job.name
                        shift_data['client_company_id'] = job.client_company_id
                
                # Get assigned workers count
                assigned_workers = shift_workers_controller.get_shift_workers_by_shift_id(shift.id)
                shift_data['assigned_workers_count'] = len(assigned_workers)
                
                shifts_data.append(shift_data)
            
            # Process clients data
            clients_data = []
            for client in all_clients:
                client_data = {
                    'id': client.id,
                    'name': client.name,
                    'contact_person': client.contact_person,
                    'contact_email': client.contact_email,
                    'contact_phone': client.contact_phone,
                    'address': client.address,
                    'billing_address': client.billing_address,
                    'notes': client.notes,
                    'created_at': client.created_at.isoformat() if hasattr(client, 'created_at') and client.created_at else None
                }
                
                # Count jobs for this client
                client_jobs = [job for job in all_jobs if job.client_company_id == client.id]
                client_data['jobs_count'] = len(client_jobs)
                
                clients_data.append(client_data)
            
            # System statistics
            stats = {
                'total_users': len(all_users),
                'total_managers': len([u for u in all_users if u.isManager]),
                'total_admins': len([u for u in all_users if u.isAdmin]),
                'total_employees': len([u for u in all_users if not u.isManager]),
                'active_users': len([u for u in all_users if u.isActive]),
                'approved_users': len([u for u in all_users if u.isApproval]),
                'total_jobs': len(all_jobs),
                'active_jobs': len([j for j in all_jobs if j.is_active]),
                'total_shifts': len(all_shifts),
                'total_clients': len(all_clients)
            }
            
            return {
                "request_id": request_id,
                "success": True,
                "data": {
                    "users": users_data,
                    "jobs": jobs_data,
                    "shifts": shifts_data,
                    "clients": clients_data,
                    "statistics": stats,
                    "admin_privileges": {
                        "can_create_users": True,
                        "can_delete_users": True,
                        "can_modify_all_data": True,
                        "can_view_system_logs": True,
                        "can_manage_settings": True
                    }
                }
            }
            
    except Exception as e:
        logger.error(f"Error in admin data access: {e}")
        return {
            "request_id": request_id,
            "success": False,
            "error": f"Failed to retrieve admin data: {str(e)}"
        }

def handle_admin_user_management(data: dict, user_session: UserSession) -> dict:
    """
    Advanced user management for admins.
    Request ID: 951
    """
    request_id = 951
    
    if not user_session or not user_session.is_admin():
        return {
            "request_id": request_id,
            "success": False,
            "error": "Admin access required."
        }
    
    action = data.get('action')
    user_id = data.get('user_id')
    
    if not action or not user_id:
        return {
            "request_id": request_id,
            "success": False,
            "error": "Action and user_id are required."
        }
    
    try:
        with get_db_session() as session:
            users_controller = UsersController(session)
            target_user = users_controller.get_entity(user_id)
            
            if not target_user:
                return {
                    "request_id": request_id,
                    "success": False,
                    "error": "User not found."
                }
            
            if action == 'promote_to_admin':
                target_user.isAdmin = True
                target_user.isManager = True
                session.commit()
                message = f"User {target_user.username} promoted to admin."
                
            elif action == 'demote_from_admin':
                target_user.isAdmin = False
                session.commit()
                message = f"User {target_user.username} demoted from admin."
                
            elif action == 'promote_to_manager':
                target_user.isManager = True
                session.commit()
                message = f"User {target_user.username} promoted to manager."
                
            elif action == 'demote_from_manager':
                target_user.isManager = False
                target_user.isAdmin = False  # Can't be admin without being manager
                session.commit()
                message = f"User {target_user.username} demoted from manager."
                
            elif action == 'activate':
                target_user.isActive = True
                session.commit()
                message = f"User {target_user.username} activated."
                
            elif action == 'deactivate':
                target_user.isActive = False
                session.commit()
                message = f"User {target_user.username} deactivated."
                
            elif action == 'approve':
                target_user.isApproval = True
                session.commit()
                message = f"User {target_user.username} approved."
                
            elif action == 'unapprove':
                target_user.isApproval = False
                session.commit()
                message = f"User {target_user.username} unapproved."
                
            else:
                return {
                    "request_id": request_id,
                    "success": False,
                    "error": f"Unknown action: {action}"
                }
            
            return {
                "request_id": request_id,
                "success": True,
                "message": message,
                "data": {
                    "user_id": target_user.id,
                    "username": target_user.username,
                    "isManager": target_user.isManager,
                    "isAdmin": target_user.isAdmin,
                    "isActive": target_user.isActive,
                    "isApproval": target_user.isApproval
                }
            }
            
    except Exception as e:
        logger.error(f"Error in admin user management: {e}")
        return {
            "request_id": request_id,
            "success": False,
            "error": f"Failed to manage user: {str(e)}"
        }
