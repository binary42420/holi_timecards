from datetime import datetime
import json
from main import get_db_session
from db.controllers.shifts_controller import ShiftsController
from db.controllers.shiftWorkers_controller import ShiftWorkersController
from db.controllers.employee_certifications_controller import EmployeeCertificationsController
from db.controllers.users_controller import UsersController
from db.models import ShiftPart, EmployeeType # Import Enums
from user_session import UserSession

def handle_create_shift(data: dict, user_session: UserSession):
    """
    Handles the request to create a new shift.
    'data' should include: job_id, shift_start_datetime (ISO format), shift_end_datetime (optional),
                         required_employee_counts (JSON string or dict), client_po_number (optional)

    For backward compatibility, also accepts: shiftDate (YYYY-MM-DD), shiftPart (morning/noon/evening)
    """
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": 220, "success": False, "error": "Unauthorized access."}

    try:
        job_id = data.get("job_id")
        required_counts_input = data.get("required_employee_counts")
        client_po_number = data.get("client_po_number")

        # Check for new datetime format first
        shift_start_datetime_str = data.get("shift_start_datetime")
        shift_end_datetime_str = data.get("shift_end_datetime")

        # Legacy format support
        shift_date_str = data.get("shiftDate")
        shift_part_str = data.get("shiftPart")

        if not job_id:
            return {"request_id": 220, "success": False, "error": "Missing required field: job_id."}

        # Process required employee counts
        if isinstance(required_counts_input, str):
            required_employee_counts = json.loads(required_counts_input)
        elif isinstance(required_counts_input, dict):
            required_employee_counts = required_counts_input
        else:
            required_employee_counts = {}

        # Validate required_employee_counts keys against EmployeeType enum
        for role_key in required_employee_counts.keys():
            if role_key not in EmployeeType._value2member_map_:
                return {"request_id": 220, "success": False, "error": f"Invalid role '{role_key}' in required_employee_counts."}

        shift_data = {
            "job_id": int(job_id),
            "required_employee_counts": required_employee_counts,
            "client_po_number": client_po_number
        }

        # Handle new datetime format
        if shift_start_datetime_str:
            try:
                # Parse ISO datetime string
                shift_start_datetime = datetime.fromisoformat(shift_start_datetime_str.replace('Z', '+00:00'))
                shift_data["shift_start_datetime"] = shift_start_datetime

                if shift_end_datetime_str:
                    shift_end_datetime = datetime.fromisoformat(shift_end_datetime_str.replace('Z', '+00:00'))
                    shift_data["shift_end_datetime"] = shift_end_datetime

            except ValueError as e:
                return {"request_id": 220, "success": False, "error": f"Invalid datetime format: {str(e)}"}

        # Handle legacy format for backward compatibility
        elif shift_date_str and shift_part_str:
            try:
                shift_date = datetime.strptime(shift_date_str, "%Y-%m-%d").date()
                shift_data["shiftDate"] = shift_date
                shift_data["shiftPart"] = ShiftPart(shift_part_str)
            except ValueError as e:
                return {"request_id": 220, "success": False, "error": f"Invalid legacy format: {str(e)}"}
        else:
            return {"request_id": 220, "success": False, "error": "Missing required fields. Provide either shift_start_datetime or both shiftDate and shiftPart."}

        with get_db_session() as session:
            controller = ShiftsController(session)
            created_shift = controller.create_entity(shift_data)
        # Assuming create_entity returns the model instance, convert it for client
        # The convert_shift_for_client function needs to be accessible or redefined here
        # For simplicity, let's assume the controller's get_entity can re-fetch and convert
        
            # Re-fetch and convert to include all details like ID
            new_shift_details = controller.get_entity(created_shift.id) # Base controller get_entity

            # Manually construct the response if get_entity doesn't format it
            response_data = {
                "id": new_shift_details.id,
                "job_id": new_shift_details.job_id,
                "required_employee_counts": new_shift_details.required_employee_counts,
                "client_po_number": new_shift_details.client_po_number,
                "workers": [] # New shift has no workers initially
            }

            # Add datetime fields if available
            if hasattr(new_shift_details, 'shift_start_datetime') and new_shift_details.shift_start_datetime:
                response_data["shift_start_datetime"] = new_shift_details.shift_start_datetime.isoformat()
                if hasattr(new_shift_details, 'shift_end_datetime') and new_shift_details.shift_end_datetime:
                    response_data["shift_end_datetime"] = new_shift_details.shift_end_datetime.isoformat()

            # Add legacy fields for backward compatibility
            if hasattr(new_shift_details, 'shiftDate') and new_shift_details.shiftDate:
                response_data["shiftDate"] = new_shift_details.shiftDate.isoformat()
            if hasattr(new_shift_details, 'shiftPart') and new_shift_details.shiftPart:
                response_data["shiftPart"] = new_shift_details.shiftPart.value
            return {"request_id": 220, "success": True, "data": response_data}
    except ValueError as ve:
        return {"request_id": 220, "success": False, "error": f"Invalid data: {str(ve)}"}
    except Exception as e:
        print(f"Error in handle_create_shift: {e}")
        return {"request_id": 220, "success": False, "error": "An unexpected error occurred."}

def handle_get_shifts_by_job(data: dict, user_session: UserSession):
    """
    Handles the request to get all shifts for a specific job.
    'data' should include: job_id
    """
    print(f"DEBUG: handle_get_shifts_by_job called with user_session: {user_session}")
    print(f"DEBUG: user_session type: {type(user_session)}")
    if user_session:
        print(f"DEBUG: user_session.can_access_manager_page(): {user_session.can_access_manager_page()}")

    if not user_session or not user_session.can_access_manager_page(): # Or other appropriate permission
        print(f"DEBUG: Authorization failed - user_session: {user_session}, can_access: {user_session.can_access_manager_page() if user_session else 'N/A'}")
        return {"request_id": 221, "success": False, "error": "Unauthorized access."}

    job_id = data.get("job_id")
    if job_id is None:
        return {"request_id": 221, "success": False, "error": "job_id is required."}

    try:
        print(f"DEBUG: Attempting to get shifts for job_id: {job_id}")
        with get_db_session() as session:
            controller = ShiftsController(session)
            shifts = controller.get_shifts_by_job_id(int(job_id)) # This method now returns formatted dicts
            print(f"DEBUG: Successfully retrieved {len(shifts)} shifts")
            return {"request_id": 221, "success": True, "data": shifts}
    except Exception as e:
        print(f"Error in handle_get_shifts_by_job: {e}")
        import traceback
        traceback.print_exc()
        return {"request_id": 221, "success": False, "error": f"Database error: {str(e)}"}

def _validate_role_assignment(user_id: int, role_assigned: str) -> tuple[bool, str]:
    """
    Validate if a user can be assigned to a specific role based on their certifications.

    Args:
        user_id (int): The user's ID
        role_assigned (str): The role to assign (EmployeeType value)

    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    try:
        with get_db_session() as session:
            certifications_controller = EmployeeCertificationsController(session)
            cert = certifications_controller.get_certification_by_user_id(user_id)

            # If no certification record exists, create a default one (everyone can be stagehand)
            if not cert:
                cert_data = {
                    'can_crew_chief': False,
                    'can_forklift': False,
                    'can_truck': False
                }
                cert = certifications_controller.create_or_update_certification(user_id, cert_data)

            # Check if user can fill the requested role
            if cert.can_fill_role(role_assigned):
                return True, ""
            else:
                users_controller = UsersController(session)
                user = users_controller.get_entity(user_id)
                user_name = user.name if user else f"User {user_id}"
                return False, f"{user_name} is not certified for the role: {role_assigned}"

    except Exception as e:
        return False, f"Error validating role assignment: {str(e)}"


def handle_assign_worker_to_shift(data: dict, user_session: UserSession):
    """
    Handles assigning a worker to a shift.
    'data' should include: shift_id, user_id (employee_id), role_assigned (string value of EmployeeType)
    """
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": 230, "success": False, "error": "Unauthorized access."}

    try:
        shift_id = data.get("shift_id")
        user_id = data.get("user_id")
        role_assigned_str = data.get("role_assigned")

        if not all([shift_id, user_id, role_assigned_str]):
            return {"request_id": 230, "success": False, "error": "Missing required fields (shift_id, user_id, role_assigned)."}

        # Validate role_assigned_str against EmployeeType enum
        if role_assigned_str not in EmployeeType._value2member_map_:
             return {"request_id": 230, "success": False, "error": f"Invalid role: {role_assigned_str}"}

        role_assigned = EmployeeType(role_assigned_str)

        # Validate that the user is certified for this role
        is_valid, error_msg = _validate_role_assignment(int(user_id), role_assigned_str)
        if not is_valid:
            return {"request_id": 230, "success": False, "error": error_msg}

        with get_db_session() as session:
            shift_worker_data = {
                "shiftID": int(shift_id),
                "userID": int(user_id),
                "role_assigned": role_assigned
            }
            controller = ShiftWorkersController(session)
            created_assignment = controller.create_entity(shift_worker_data)

            # Format response
            response_data = {
                "shiftID": created_assignment.shiftID,
                "userID": created_assignment.userID,
                "role_assigned": created_assignment.role_assigned.value
            }
            return {"request_id": 230, "success": True, "data": response_data}
    except ValueError as ve: # For int conversion or invalid enum value
        return {"request_id": 230, "success": False, "error": f"Invalid data: {str(ve)}"}
    except Exception as e:
        print(f"Error in handle_assign_worker_to_shift: {e}")
        # Consider checking for specific database errors like integrity violations (e.g., duplicate assignment)
        return {"request_id": 230, "success": False, "error": "An unexpected error occurred or assignment already exists."}


def handle_unassign_worker_from_shift(data: dict, user_session: UserSession):
    """
    Handles unassigning a worker from a shift.
    'data' should include: shift_id, user_id (employee_id), role_assigned (string value of EmployeeType)
    """
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": 231, "success": False, "error": "Unauthorized access."}

    try:
        shift_id = data.get("shift_id")
        user_id = data.get("user_id")
        role_assigned_str = data.get("role_assigned")

        if not all([shift_id, user_id, role_assigned_str]):
            return {"request_id": 231, "success": False, "error": "Missing required fields (shift_id, user_id, role_assigned)."}

        with get_db_session() as session:
            controller = ShiftWorkersController(session)
            # Uses the new delete_entity_by_composite_key method
            deleted_assignment = controller.delete_entity_by_composite_key(int(shift_id), int(user_id), role_assigned_str)

            if deleted_assignment:
                return {"request_id": 231, "success": True, "message": "Worker unassigned successfully."}
            else:
                return {"request_id": 231, "success": False, "error": "Assignment not found or invalid role."}
            
    except ValueError as ve: # For int conversion or invalid enum value
        return {"request_id": 231, "success": False, "error": f"Invalid data: {str(ve)}"}
    except Exception as e:
        print(f"Error in handle_unassign_worker_from_shift: {e}")
        return {"request_id": 231, "success": False, "error": "An unexpected error occurred."}


def handle_update_shift_requirements(data: dict, user_session: UserSession):
    """
    Update the worker requirements for an existing shift.
    Request ID: 232
    """
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": 232, "success": False, "error": "Manager access required."}

    shift_id = data.get("shift_id")
    required_employee_counts = data.get("required_employee_counts", {})

    if not shift_id:
        return {"request_id": 232, "success": False, "error": "shift_id is required."}

    try:
        with get_db_session() as session:
            shifts_controller = ShiftsController(session)

            # Get the existing shift
            shift = shifts_controller.get_entity(shift_id)
            if not shift:
                return {"request_id": 232, "success": False, "error": "Shift not found."}

            # Update the required employee counts
            update_data = {
                "required_employee_counts": required_employee_counts
            }

            updated_shift = shifts_controller.update_entity(shift_id, update_data)

            if updated_shift:
                # Get updated shift with workers for response
                shift_with_workers = shifts_controller.get_shift_by_id(shift_id)

                return {
                    "request_id": 232,
                    "success": True,
                    "message": "Shift requirements updated successfully.",
                    "data": {
                        "shift_id": shift_id,
                        "required_employee_counts": updated_shift.required_employee_counts,
                        "shift": shift_with_workers
                    }
                }
            else:
                return {"request_id": 232, "success": False, "error": "Failed to update shift requirements."}

    except Exception as e:
        print(f"Error in handle_update_shift_requirements: {e}")
        return {"request_id": 232, "success": False, "error": str(e)}
