from main import get_db_session
from db.controllers.users_controller import UsersController
from db.controllers.employee_certifications_controller import EmployeeCertificationsController
from user_session import UserSession
import re
from datetime import datetime

def handle_employee_list(user_session: UserSession) -> dict:
    request_id = 60
    if user_session is None:
        print("User session not found.")
        return {"request_id": request_id, "success": False, "error": "User session not found."}

    if user_session.can_access_manager_page():
        try:
            with get_db_session() as session:
                users_controller = UsersController(session)

                # For Hands on Labor: All managers can see all employees (no workplace restrictions)
                all_users = users_controller.get_all_entities()

                active_workers = []
                for user in all_users:
                    # Only include non-manager users (employees)
                    if not user.isManager and user.isActive:
                        active_workers.append({
                            "userName": user.username,
                            "name": user.name,
                            "approved": user.isApproval
                        })

                return {"request_id": request_id, "success": True, "data": active_workers}
        except Exception as e:
            print(f"Error fetching employee list: {e}")
            return {"request_id": request_id, "success": False, "error": f"An error occurred while fetching employee list: {str(e)}"}
    else:
        print("User does not have access to manager-specific pages.")
        return {"request_id": request_id, "success": False, "error": "User does not have access to manager-specific pages."}


def handle_get_all_approved_worker_details(user_session: UserSession) -> dict:
    """
    Get all approved workers with their certification details for Hands on Labor.
    Since there's only one company, all managers can see all approved workers.
    """
    request_id = 94
    if user_session is None:
        return {"request_id": request_id, "success": False, "error": "User session not found."}

    if user_session.can_access_manager_page():
        try:
            with get_db_session() as session:
                certifications_controller = EmployeeCertificationsController(session)

                # Get all employees with certifications for Hands on Labor (no workplace restriction)
                employees_with_certs = certifications_controller.get_all_employees_with_certifications(None)

                return {"request_id": request_id, "success": True, "data": employees_with_certs}

        except Exception as e:
            print(f"Error fetching employee details with certifications: {e}")
            return {"request_id": request_id, "success": False, "error": f"An error occurred: {str(e)}"}
    else:
        return {"request_id": request_id, "success": False, "error": "User does not have access to manager-specific pages."}


def handle_employee_approval(data: dict, user_session: UserSession) -> dict:
    request_id = 62
    if user_session is None:
        print("User session not found.")
        return {"request_id": request_id, "success": False, "error": "User session not found."}

    if user_session.can_access_manager_page():
        user_name = data.get('userName')
        if user_name:
            try:
                with get_db_session() as session:
                    users_controller_instance = UsersController(session)
                    users_controller_instance.approve_user(user_name)
                    return {"request_id": request_id, "success": True, "message": f"User {user_name} approved successfully."}
            except Exception as e:
                print(f"Error approving employee {user_name}: {e}")
                return {"request_id": request_id, "success": False, "error": f"Failed to approve user {user_name}: {str(e)}"}
        else:
            print("Employee userName not provided in the data.")
            return {"request_id": request_id, "success": False, "error": "Employee userName not provided."}
    else:
        print("User does not have access to manager-specific pages.")
        return {"request_id": request_id, "success": False, "error": "User does not have access to manager-specific pages."}


def handle_employee_rejection(data: dict, user_session: UserSession) -> dict:
    request_id = 64
    if user_session is None:
        print("User session not found.")
        return {"request_id": request_id, "success": False, "error": "User session not found."}

    if user_session.can_access_manager_page():
        user_name = data.get('userName')

        if not user_name:
            return {"request_id": request_id, "success": False, "error": "Employee userName not provided."}

        try:
            with get_db_session() as session:
                users_controller = UsersController(session)
                user_id = users_controller.get_user_id_by_username(user_name)

                if user_id is not None:
                    # For Hands on Labor: No workplace entries to delete, just delete the user
                    deleted_user_entity = users_controller.delete_entity(user_id)

                    if deleted_user_entity:
                        print(f"Employee with userName {user_name} has been successfully deleted.")
                        return {"request_id": request_id, "success": True, "message": f"Employee {user_name} rejected and deleted."}
                    else:
                        print(f"Failed to delete employee with userName {user_name}, entity might not have been found for deletion.")
                        return {"request_id": request_id, "success": False, "error": f"Failed to delete user {user_name}, user might have already been deleted."}
                else:
                    print(f"No user found with userName {user_name}.")
                    return {"request_id": request_id, "success": False, "error": f"No user found with userName {user_name}."}
        except Exception as e:
            print(f"Error rejecting employee {user_name}: {e}")
            return {"request_id": request_id, "success": False, "error": f"An error occurred while rejecting employee {user_name}: {str(e)}"}
    else:
        print("User does not have access to manager-specific pages.")
        return {"request_id": request_id, "success": False, "error": "User does not have access to manager-specific pages."}


def handle_create_employee_by_manager(data: dict, user_session: UserSession) -> dict:
    """
    Create a new employee account by a manager.
    For Hands on Labor: Managers can create employee accounts directly.
    """
    request_id = 65
    if user_session is None:
        return {"request_id": request_id, "success": False, "error": "User session not found."}

    if not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "User does not have access to manager-specific pages."}

    try:
        # Validate required fields
        required_fields = ['username', 'password', 'name', 'email']
        for field in required_fields:
            if not data.get(field):
                return {"request_id": request_id, "success": False, "error": f"{field} is required."}

        # Validate email format
        email = data.get('email')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return {"request_id": request_id, "success": False, "error": "Invalid email format."}

        with get_db_session() as session:
            users_controller = UsersController(session)

            # Check if username already exists
            try:
                existing_user = users_controller.get_entity(data['username'])
                if existing_user:
                    return {"request_id": request_id, "success": False, "error": "Username already exists."}
            except:
                # User doesn't exist, which is what we want
                pass

            # Create employee user data
            user_data = {
                'username': data['username'],
                'password': data['password'],
                'name': data['name'],
                'email': email,
                'isManager': False,
                'isAdmin': False,
                'isActive': True,
                'isApproval': True,  # Auto-approve employees created by managers
                'client_company_id': None,  # Agency employee, not client
                'employee_type': 'stagehand',  # Default employee type
                'google_id': None
            }

            # Create the user
            new_employee = users_controller.create_entity(user_data)

            if new_employee:
                # Handle certifications if provided
                certifications = data.get('certifications', {})
                if certifications:
                    try:
                        certifications_controller = EmployeeCertificationsController(session)

                        # Create certification record
                        cert_data = {
                            'user_id': new_employee.id,
                            'can_crew_chief': certifications.get('canCrewChief', False),
                            'can_forklift': certifications.get('canForklift', False),
                            'can_truck': certifications.get('canTruck', False),
                            'created_at': datetime.now(),
                            'updated_at': datetime.now()
                        }

                        certifications_controller.create_entity(cert_data)

                    except Exception as cert_error:
                        print(f"Warning: Failed to create certifications for employee {data['username']}: {cert_error}")
                        # Don't fail the entire operation if certifications fail

                return {
                    "request_id": request_id,
                    "success": True,
                    "message": f"Employee '{data['username']}' created successfully.",
                    "data": {
                        "id": new_employee.id,
                        "username": new_employee.username,
                        "name": new_employee.name,
                        "email": new_employee.email,
                        "approved": new_employee.isApproval
                    }
                }
            else:
                return {"request_id": request_id, "success": False, "error": "Failed to create employee account."}

    except Exception as e:
        print(f"Error creating employee: {e}")
        return {"request_id": request_id, "success": False, "error": f"Failed to create employee account: {str(e)}"}


def handle_manager_update_employee_certifications(data: dict, user_session: UserSession) -> dict:
    """
    Handle manager updating employee certifications.
    Request ID: 410
    """
    request_id = 410

    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Manager access required."}

    employee_id = data.get("employee_id")
    certifications = data.get("certifications", {})

    if not employee_id:
        return {"request_id": request_id, "success": False, "error": "employee_id is required."}

    try:
        with get_db_session() as session:
            # Verify employee exists
            users_controller = UsersController(session)
            employee = users_controller.get_entity(employee_id)

            if not employee:
                return {"request_id": request_id, "success": False, "error": "Employee not found."}

            # Update certifications
            certifications_controller = EmployeeCertificationsController(session)

            # Prepare certification data
            cert_data = {
                'can_crew_chief': certifications.get('can_crew_chief', False),
                'can_forklift': certifications.get('can_forklift', False),
                'can_truck': certifications.get('can_truck', False)
            }

            # Create or update certification record
            updated_cert = certifications_controller.create_or_update_certification(employee_id, cert_data)

            if updated_cert:
                return {
                    "request_id": request_id,
                    "success": True,
                    "message": f"Certifications updated for {employee.name}",
                    "data": {
                        "employee_id": employee_id,
                        "employee_name": employee.name,
                        "certifications": updated_cert.to_dict(),
                        "available_roles": updated_cert.get_role_list()
                    }
                }
            else:
                return {"request_id": request_id, "success": False, "error": "Failed to update certifications."}

    except Exception as e:
        print(f"Error updating employee certifications: {e}")
        return {"request_id": request_id, "success": False, "error": f"Failed to update certifications: {str(e)}"}
