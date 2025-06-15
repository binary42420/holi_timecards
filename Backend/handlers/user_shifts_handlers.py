"""
Handlers for user shift management functionality.
Allows users to view their assigned shifts with role-based permissions.
"""

from datetime import datetime, timedelta
from main import get_db_session
from user_session import UserSession
from db.controllers.shiftWorkers_controller import ShiftWorkersController
from db.controllers.shifts_controller import ShiftsController
from db.controllers.users_controller import UsersController
from db.controllers.jobs_controller import JobsController
from db.controllers.client_companies_controller import ClientCompaniesController
from db.models import EmployeeType


def handle_get_user_shifts(data: dict, user_session: UserSession) -> dict:
    """
    Get all shifts assigned to the current user.
    Request ID: 1020
    
    Returns shifts where the user is assigned as any role (crew chief, stagehand, etc.)
    with proper role-based permissions for timesheet editing.
    """
    request_id = 1020
    if not user_session:
        return {"request_id": request_id, "success": False, "error": "User session not found."}

    try:
        user_id = user_session.get_id
        start_date = data.get('start_date')  # Optional filter
        end_date = data.get('end_date')      # Optional filter
        
        with get_db_session() as session:
            shift_workers_controller = ShiftWorkersController(session)
            shifts_controller = ShiftsController(session)
            users_controller = UsersController(session)
            jobs_controller = JobsController(session)
            client_companies_controller = ClientCompaniesController(session)
            
            # Get current user details
            current_user = users_controller.get_entity(user_id)
            if not current_user:
                return {"request_id": request_id, "success": False, "error": "User not found."}
            
            # Get all shift assignments for this user
            user_shift_assignments = shift_workers_controller.get_shifts_for_user(user_id)
            
            # Build response data
            user_shifts = []
            
            for assignment in user_shift_assignments:
                # Get shift details
                shift = shifts_controller.get_entity(assignment.shiftID)
                if not shift:
                    continue
                
                # Apply date filters if provided
                if start_date:
                    filter_start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    if shift.shiftDate < filter_start.date():
                        continue
                        
                if end_date:
                    filter_end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    if shift.shiftDate > filter_end.date():
                        continue
                
                # Get job and client details
                job = jobs_controller.get_entity(shift.job_id) if shift.job_id else None
                client_company = None
                if job and job.client_company_id:
                    client_company = client_companies_controller.get_entity(job.client_company_id)
                
                # Determine user's permissions for this shift
                can_edit_timesheet = _can_user_edit_shift_timesheet(
                    current_user, assignment, shift_workers_controller
                )
                
                # Get all workers on this shift for crew chief context
                all_shift_workers = shift_workers_controller.get_workers_for_shift(assignment.shiftID)
                worker_count = len(all_shift_workers)
                
                # Build shift data
                shift_data = {
                    'shift_id': shift.id,
                    'shift_date': shift.shiftDate.isoformat() if shift.shiftDate else None,
                    'shift_part': shift.shiftPart.value if shift.shiftPart else None,
                    'shift_start_datetime': shift.shift_start_datetime.isoformat() if shift.shift_start_datetime else None,
                    'shift_end_datetime': shift.shift_end_datetime.isoformat() if shift.shift_end_datetime else None,
                    'job_id': shift.job_id,
                    'job_name': job.jobName if job else 'Unknown Job',
                    'client_company_name': client_company.companyName if client_company else 'Unknown Client',
                    'client_po_number': shift.client_po_number,
                    
                    # User's role and assignment details
                    'user_role_assigned': assignment.role_assigned.value,
                    'is_crew_chief': assignment.role_assigned == EmployeeType.CREW_CHIEF,
                    'worker_count': worker_count,
                    
                    # Timesheet information
                    'timesheet_status': _get_timesheet_status(assignment),
                    'total_hours_worked': assignment.total_hours_worked,
                    'times_submitted_at': assignment.times_submitted_at.isoformat() if assignment.times_submitted_at else None,
                    'is_approved': assignment.is_approved,
                    'approved_at': assignment.approved_at.isoformat() if assignment.approved_at else None,
                    
                    # Permissions
                    'can_edit_timesheet': can_edit_timesheet,
                    'can_view_all_workers': current_user.isManager or assignment.role_assigned == EmployeeType.CREW_CHIEF,
                    'can_submit_timesheets': current_user.isManager or assignment.role_assigned == EmployeeType.CREW_CHIEF,
                }
                
                user_shifts.append(shift_data)
            
            # Sort shifts by date (most recent first)
            user_shifts.sort(key=lambda x: x['shift_date'] or '', reverse=True)
            
            return {
                "request_id": request_id,
                "success": True,
                "data": {
                    "user_info": {
                        "user_id": current_user.id,
                        "name": current_user.name,
                        "email": current_user.email,
                        "employee_type": current_user.employee_type.value if current_user.employee_type else None,
                        "is_manager": current_user.isManager,
                        "is_admin": current_user.isAdmin
                    },
                    "shifts": user_shifts,
                    "total_shifts": len(user_shifts)
                }
            }
        
    except Exception as e:
        print(f"Error getting user shifts: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to retrieve user shifts."}


def handle_get_crew_chief_shifts(data: dict, user_session: UserSession) -> dict:
    """
    Get shifts where the current user is assigned as crew chief.
    Request ID: 1021
    
    This is a specialized version for crew chiefs to see only their supervised shifts.
    """
    request_id = 1021
    if not user_session:
        return {"request_id": request_id, "success": False, "error": "User session not found."}

    try:
        user_id = user_session.get_id
        
        with get_db_session() as session:
            shift_workers_controller = ShiftWorkersController(session)
            shifts_controller = ShiftsController(session)
            users_controller = UsersController(session)
            jobs_controller = JobsController(session)
            client_companies_controller = ClientCompaniesController(session)
            
            # Get current user details
            current_user = users_controller.get_entity(user_id)
            if not current_user:
                return {"request_id": request_id, "success": False, "error": "User not found."}
            
            # Get only crew chief assignments for this user
            crew_chief_assignments = shift_workers_controller.get_crew_chief_shifts_for_user(user_id)
            
            # Build response data
            crew_chief_shifts = []
            
            for assignment in crew_chief_assignments:
                # Get shift details
                shift = shifts_controller.get_entity(assignment.shiftID)
                if not shift:
                    continue
                
                # Get job and client details
                job = jobs_controller.get_entity(shift.job_id) if shift.job_id else None
                client_company = None
                if job and job.client_company_id:
                    client_company = client_companies_controller.get_entity(job.client_company_id)
                
                # Get all workers on this shift
                all_shift_workers = shift_workers_controller.get_workers_for_shift(assignment.shiftID)
                worker_count = len(all_shift_workers)
                
                # Build shift data
                shift_data = {
                    'shift_id': shift.id,
                    'shift_date': shift.shiftDate.isoformat() if shift.shiftDate else None,
                    'shift_part': shift.shiftPart.value if shift.shiftPart else None,
                    'shift_start_datetime': shift.shift_start_datetime.isoformat() if shift.shift_start_datetime else None,
                    'shift_end_datetime': shift.shift_end_datetime.isoformat() if shift.shift_end_datetime else None,
                    'job_name': job.jobName if job else 'Unknown Job',
                    'client_company_name': client_company.companyName if client_company else 'Unknown Client',
                    'worker_count': worker_count,
                    'timesheet_status': _get_timesheet_status(assignment),
                    'can_edit_timesheet': True,  # Crew chiefs can always edit
                    'can_view_all_workers': True,
                    'can_submit_timesheets': True,
                }
                
                crew_chief_shifts.append(shift_data)
            
            # Sort shifts by date (most recent first)
            crew_chief_shifts.sort(key=lambda x: x['shift_date'] or '', reverse=True)
            
            return {
                "request_id": request_id,
                "success": True,
                "data": {
                    "user_info": {
                        "user_id": current_user.id,
                        "name": current_user.name,
                        "email": current_user.email,
                        "is_crew_chief": True
                    },
                    "supervised_shifts": crew_chief_shifts,
                    "total_shifts": len(crew_chief_shifts)
                }
            }
        
    except Exception as e:
        print(f"Error getting crew chief shifts: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to retrieve crew chief shifts."}


def _can_user_edit_shift_timesheet(user, assignment, shift_workers_controller) -> bool:
    """
    Determine if a user can edit timesheet for a specific shift.
    
    Rules:
    - Managers can edit all timesheets
    - Crew chiefs can edit timesheets for their shifts
    - Regular employees cannot edit timesheets (only view)
    - No one can edit approved timesheets
    """
    # Managers can edit all timesheets
    if user.isManager or user.isAdmin:
        return True
    
    # Crew chiefs can edit timesheets for shifts they supervise
    if assignment.role_assigned == EmployeeType.CREW_CHIEF:
        return True
    
    # Regular employees cannot edit timesheets
    return False


def _get_timesheet_status(assignment) -> str:
    """Get the timesheet status for a shift assignment."""
    if assignment.is_approved:
        return 'approved'
    elif assignment.times_submitted_at:
        return 'submitted'
    else:
        return 'draft'
