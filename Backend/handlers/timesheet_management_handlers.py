from datetime import datetime
from main import get_db_session
from db.controllers.shiftWorkers_controller import ShiftWorkersController
from db.controllers.shifts_controller import ShiftsController
from db.controllers.users_controller import UsersController
from db.controllers.jobs_controller import JobsController
from db.controllers.client_companies_controller import ClientCompaniesController
from user_session import UserSession


def handle_get_shift_timesheet_details(data: dict, user_session: UserSession) -> dict:
    """
    Get timesheet details for a specific shift with role-based access control.
    
    Access levels:
    - Managers: Can view all shifts for their workplace
    - Crew Chiefs: Can view shifts they're assigned to as crew chief
    - Clients: Can view shifts for their jobs (read-only)
    - Regular employees: Can view only their own timesheet data
    """
    request_id = 1010
    if not user_session:
        return {"request_id": request_id, "success": False, "error": "User session not found."}
    
    shift_id = data.get('shift_id')
    if not shift_id:
        return {"request_id": request_id, "success": False, "error": "shift_id is required."}
    
    try:
        with get_db_session() as session:

            shifts_controller = ShiftsController(session)
        with get_db_session() as session:

            shift_workers_controller = ShiftWorkersController(session)
        with get_db_session() as session:

            users_controller = UsersController(session)
        with get_db_session() as session:

            jobs_controller = JobsController(session)
        with get_db_session() as session:

            client_companies_controller = ClientCompaniesController(session)
        
        # Get shift details
        shift = shifts_controller.get_entity(shift_id)
        if not shift:
            return {"request_id": request_id, "success": False, "error": "Shift not found."}
        
        # Get job and client details
        job = jobs_controller.get_entity(shift.job_id)
        client_company = None
        if job and job.client_company_id:
            client_company = client_companies_controller.get_entity(job.client_company_id)
        
        # Get all workers for this shift
        shift_workers = shift_workers_controller.get_workers_for_shift(shift_id)
        
        # Determine user access level and filter data accordingly
        user = users_controller.get_entity(user_session.get_id)
        is_manager = user.isManager
        is_client = user.client_company_id is not None
        is_crew_chief_on_shift = any(sw.userID == user_session.get_id and 
                                   sw.role_assigned.value == 'crew_chief' 
                                   for sw in shift_workers)
        
        # Build timesheet data based on access level
        timesheet_data = []
        
        for sw in shift_workers:
            worker = users_controller.get_entity(sw.userID)
            if not worker:
                continue
            
            # Determine if this user can see this worker's data
            can_view = False
            can_edit = False
            
            if is_manager:
                # Managers can view and edit all workers
                can_view = True
                can_edit = True
            elif is_crew_chief_on_shift:
                # Crew chiefs can view and edit all workers on their shift
                can_view = True
                can_edit = True
            elif is_client and job and job.client_company_id == user.client_company_id:
                # Clients can view (but not edit) workers on their jobs
                can_view = True
                can_edit = False
            elif sw.userID == user_session.get_id:
                # Workers can view their own data (but not edit if already submitted)
                can_view = True
                can_edit = not sw.times_submitted_at  # Can't edit if already submitted
            
            if can_view:
                worker_data = {
                    'user_id': sw.userID,
                    'name': worker.name,
                    'role_assigned': sw.role_assigned.value,
                    'can_edit': can_edit,
                    'timesheet': sw.to_dict()
                }
                timesheet_data.append(worker_data)
        
        # Build shift details
        shift_details = {
            'shift_id': shift.id,
            'job_id': shift.job_id,
            'job_name': job.jobName if job else 'Unknown Job',
            'client_company_name': client_company.companyName if client_company else 'Unknown Client',
            'shift_start_datetime': shift.shift_start_datetime.isoformat() if shift.shift_start_datetime else None,
            'shift_end_datetime': shift.shift_end_datetime.isoformat() if shift.shift_end_datetime else None,
            # Legacy fields for backward compatibility
            'shift_date': shift.shiftDate.isoformat() if shift.shiftDate else None,
            'shift_part': shift.shiftPart.value if shift.shiftPart else None,
            'client_po_number': shift.client_po_number,
        }
        
        response_data = {
            'shift_details': shift_details,
            'timesheet_data': timesheet_data,
            'user_permissions': {
                'is_manager': is_manager,
                'is_crew_chief': is_crew_chief_on_shift,
                'is_client': is_client,
                'can_approve': is_manager,
                'can_edit_others': is_manager or is_crew_chief_on_shift
            }
        }
        
        return {"request_id": request_id, "success": True, "data": response_data}
        
    except Exception as e:
        print(f"Error getting shift timesheet details: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to retrieve timesheet details."}


def handle_update_worker_timesheet(data: dict, user_session: UserSession) -> dict:
    """
    Update timesheet data for a worker on a shift.
    Only managers and crew chiefs can edit others' timesheets.
    """
    request_id = 1011
    if not user_session:
        return {"request_id": request_id, "success": False, "error": "User session not found."}
    
    try:
        shift_id = data.get('shift_id')
        worker_user_id = data.get('worker_user_id')
        role_assigned = data.get('role_assigned')
        time_pairs = data.get('time_pairs', [])
        notes = data.get('notes', '')
        
        if not all([shift_id, worker_user_id, role_assigned]):
            return {"request_id": request_id, "success": False, "error": "shift_id, worker_user_id, and role_assigned are required."}
        
        # Verify permissions
        with get_db_session() as session:

            users_controller = UsersController(session)
        with get_db_session() as session:

            shift_workers_controller = ShiftWorkersController(session)
        
        user = users_controller.get_entity(user_session.get_id)
        is_manager = user.isManager
        
        # Check if user is crew chief on this shift
        shift_workers = shift_workers_controller.get_workers_for_shift(shift_id)
        is_crew_chief_on_shift = any(sw.userID == user_session.get_id and 
                                   sw.role_assigned.value == 'crew_chief' 
                                   for sw in shift_workers)
        
        # Check if user is editing their own timesheet
        is_own_timesheet = worker_user_id == user_session.get_id
        
        if not (is_manager or is_crew_chief_on_shift or is_own_timesheet):
            return {"request_id": request_id, "success": False, "error": "Insufficient permissions to edit this timesheet."}
        
        # Get the shift worker record
        shift_worker = shift_workers_controller.get_shift_worker(shift_id, worker_user_id, role_assigned)
        if not shift_worker:
            return {"request_id": request_id, "success": False, "error": "Shift worker record not found."}
        
        # If already submitted and user is not manager/crew chief, prevent editing
        if shift_worker.times_submitted_at and not (is_manager or is_crew_chief_on_shift):
            return {"request_id": request_id, "success": False, "error": "Cannot edit timesheet after submission."}
        
        # Update time pairs
        update_data = {'notes': notes}
        
        for pair in time_pairs:
            pair_num = pair.get('pair_number')
            clock_in = pair.get('clock_in')
            clock_out = pair.get('clock_out')
            
            if pair_num in [1, 2, 3]:
                if clock_in:
                    update_data[f'clock_in_time_{pair_num}'] = datetime.fromisoformat(clock_in.replace('Z', '+00:00'))
                if clock_out:
                    update_data[f'clock_out_time_{pair_num}'] = datetime.fromisoformat(clock_out.replace('Z', '+00:00'))
        
        # Update the record
        updated_shift_worker = shift_workers_controller.update_shift_worker_times(
            shift_id, worker_user_id, role_assigned, update_data
        )
        
        if updated_shift_worker:
            # Recalculate total hours
            updated_shift_worker.calculate_total_hours()
            db.commit()
            
            return {"request_id": request_id, "success": True, "data": updated_shift_worker.to_dict()}
        else:
            return {"request_id": request_id, "success": False, "error": "Failed to update timesheet."}
            
    except Exception as e:
        print(f"Error updating worker timesheet: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update timesheet."}


def handle_submit_shift_timesheet(data: dict, user_session: UserSession) -> dict:
    """
    Submit timesheet for a shift (mark as submitted).
    Only managers and crew chiefs can submit timesheets.
    """
    request_id = 1012
    if not user_session:
        return {"request_id": request_id, "success": False, "error": "User session not found."}
    
    try:
        shift_id = data.get('shift_id')
        worker_ids = data.get('worker_ids', [])  # List of worker IDs to submit
        
        if not shift_id:
            return {"request_id": request_id, "success": False, "error": "shift_id is required."}
        
        # Verify permissions
        with get_db_session() as session:

            users_controller = UsersController(session)
        with get_db_session() as session:

            shift_workers_controller = ShiftWorkersController(session)
        
        user = users_controller.get_entity(user_session.get_id)
        is_manager = user.isManager
        
        # Check if user is crew chief on this shift
        shift_workers = shift_workers_controller.get_workers_for_shift(shift_id)
        is_crew_chief_on_shift = any(sw.userID == user_session.get_id and 
                                   sw.role_assigned.value == 'crew_chief' 
                                   for sw in shift_workers)
        
        if not (is_manager or is_crew_chief_on_shift):
            return {"request_id": request_id, "success": False, "error": "Only managers and crew chiefs can submit timesheets."}
        
        # Submit timesheets for specified workers (or all if none specified)
        workers_to_submit = worker_ids if worker_ids else [sw.userID for sw in shift_workers]
        
        submitted_count = 0
        errors = []
        
        for worker_id in workers_to_submit:
            try:
                success = shift_workers_controller.submit_timesheet_for_worker(
                    shift_id, worker_id, user_session.get_id
                )
                if success:
                    submitted_count += 1
                else:
                    errors.append(f"Failed to submit timesheet for worker {worker_id}")
            except Exception as e:
                errors.append(f"Error submitting timesheet for worker {worker_id}: {str(e)}")
        
        if submitted_count > 0:
            message = f"Successfully submitted {submitted_count} timesheet(s)."
            if errors:
                message += f" {len(errors)} failed."
            return {"request_id": request_id, "success": True, "message": message, "errors": errors}
        else:
            return {"request_id": request_id, "success": False, "error": "No timesheets were submitted.", "errors": errors}
            
    except Exception as e:
        print(f"Error submitting shift timesheet: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to submit timesheet."}


def handle_approve_shift_timesheet(data: dict, user_session: UserSession) -> dict:
    """
    Approve timesheet for a shift.
    Only managers can approve timesheets.
    """
    request_id = 1013
    if not user_session:
        return {"request_id": request_id, "success": False, "error": "User session not found."}
    
    try:
        shift_id = data.get('shift_id')
        worker_ids = data.get('worker_ids', [])  # List of worker IDs to approve
        
        if not shift_id:
            return {"request_id": request_id, "success": False, "error": "shift_id is required."}
        
        # Verify permissions - only managers can approve
        with get_db_session() as session:

            users_controller = UsersController(session)
        user = users_controller.get_entity(user_session.get_id)
        
        if not user.isManager:
            return {"request_id": request_id, "success": False, "error": "Only managers can approve timesheets."}
        
        with get_db_session() as session:

        
            shift_workers_controller = ShiftWorkersController(session)
        shift_workers = shift_workers_controller.get_workers_for_shift(shift_id)
        
        # Approve timesheets for specified workers (or all if none specified)
        workers_to_approve = worker_ids if worker_ids else [sw.userID for sw in shift_workers]
        
        approved_count = 0
        errors = []
        
        for worker_id in workers_to_approve:
            try:
                success = shift_workers_controller.approve_timesheet_for_worker(
                    shift_id, worker_id, user_session.get_id
                )
                if success:
                    approved_count += 1
                else:
                    errors.append(f"Failed to approve timesheet for worker {worker_id}")
            except Exception as e:
                errors.append(f"Error approving timesheet for worker {worker_id}: {str(e)}")
        
        if approved_count > 0:
            message = f"Successfully approved {approved_count} timesheet(s)."
            if errors:
                message += f" {len(errors)} failed."
            return {"request_id": request_id, "success": True, "message": message, "errors": errors}
        else:
            return {"request_id": request_id, "success": False, "error": "No timesheets were approved.", "errors": errors}
            
    except Exception as e:
        print(f"Error approving shift timesheet: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to approve timesheet."}


def handle_get_employee_timesheet_history(data: dict, user_session: UserSession) -> dict:
    """
    Get timesheet history for an employee.
    Employees can view their own history, managers can view all.
    """
    request_id = 1014
    if not user_session:
        return {"request_id": request_id, "success": False, "error": "User session not found."}
    
    try:
        employee_id = data.get('employee_id', user_session.get_id)  # Default to current user
        start_date = data.get('start_date')  # Optional date filter
        end_date = data.get('end_date')    # Optional date filter
        
        # Verify permissions
        with get_db_session() as session:

            users_controller = UsersController(session)
        user = users_controller.get_entity(user_session.get_id)
        
        # Only managers can view other employees' timesheets
        if employee_id != user_session.get_id and not user.isManager:
            return {"request_id": request_id, "success": False, "error": "Insufficient permissions to view this employee's timesheet history."}
        
        with get_db_session() as session:

        
            shift_workers_controller = ShiftWorkersController(session)
        timesheet_history = shift_workers_controller.get_employee_timesheet_history(
            employee_id, start_date, end_date
        )
        
        return {"request_id": request_id, "success": True, "data": timesheet_history}

    except Exception as e:
        print(f"Error getting employee timesheet history: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to retrieve timesheet history."}


def handle_get_all_submitted_timesheets(user_session: UserSession) -> dict:
    """
    Get all submitted timesheets for manager review.
    Only managers can access this.
    """
    request_id = 103
    if not user_session:
        return {"request_id": request_id, "success": False, "error": "User session not found."}

    try:
        # Verify permissions - only managers can view all submitted timesheets
        with get_db_session() as session:

            users_controller = UsersController(session)
        user = users_controller.get_entity(user_session.get_id)

        if not user.isManager:
            return {"request_id": request_id, "success": False, "error": "Only managers can view all submitted timesheets."}

        with get_db_session() as session:


            shift_workers_controller = ShiftWorkersController(session)
        with get_db_session() as session:

            shifts_controller = ShiftsController(session)
        with get_db_session() as session:

            jobs_controller = JobsController(session)
        with get_db_session() as session:

            client_companies_controller = ClientCompaniesController(session)

        # Get all submitted timesheets for the manager's workplace
        submitted_timesheets = shift_workers_controller.get_submitted_timesheets_for_workplace(user.workplaceID)

        # Format the data for frontend
        timesheet_data = []
        for sw in submitted_timesheets:
            # Get shift details
            shift = shifts_controller.get_entity(sw.shiftID)
            if not shift:
                continue

            # Get job and client details
            job = jobs_controller.get_entity(shift.job_id)
            client_company = None
            if job and job.client_company_id:
                client_company = client_companies_controller.get_entity(job.client_company_id)

            # Get worker details
            worker = users_controller.get_entity(sw.userID)
            if not worker:
                continue

            timesheet_entry = {
                'shift_id': sw.shiftID,
                'worker_id': sw.userID,
                'worker_name': worker.name,
                'job_name': job.jobName if job else 'Unknown Job',
                'client_company_name': client_company.companyName if client_company else 'Unknown Client',
                'shift_date': shift.shiftDate.isoformat() if shift.shiftDate else None,
                'shift_part': shift.shiftPart.value if shift.shiftPart else None,
                'role_assigned': sw.role_assigned.value,
                'total_hours': sw.total_hours,
                'submitted_at': sw.times_submitted_at.isoformat() if sw.times_submitted_at else None,
                'approved_at': sw.times_approved_at.isoformat() if sw.times_approved_at else None,
                'approved_by': sw.times_approved_by,
                'status': 'approved' if sw.times_approved_at else 'submitted',
                'notes': sw.notes
            }
            timesheet_data.append(timesheet_entry)

        return {"request_id": request_id, "success": True, "data": timesheet_data}

    except Exception as e:
        print(f"Error getting all submitted timesheets: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to retrieve submitted timesheets."}


def handle_update_timesheet_status(data: dict, user_session: UserSession) -> dict:
    """
    Update timesheet status (approve/reject).
    Only managers can update timesheet status.
    """
    request_id = 104
    if not user_session:
        return {"request_id": request_id, "success": False, "error": "User session not found."}

    try:
        shift_id = data.get('shift_id')
        worker_id = data.get('worker_id')
        action = data.get('action')  # 'approve' or 'reject'

        if not all([shift_id, worker_id, action]):
            return {"request_id": request_id, "success": False, "error": "shift_id, worker_id, and action are required."}

        if action not in ['approve', 'reject']:
            return {"request_id": request_id, "success": False, "error": "Action must be 'approve' or 'reject'."}

        # Verify permissions - only managers can update timesheet status
        with get_db_session() as session:

            users_controller = UsersController(session)
        user = users_controller.get_entity(user_session.get_id)

        if not user.isManager:
            return {"request_id": request_id, "success": False, "error": "Only managers can update timesheet status."}

        with get_db_session() as session:


            shift_workers_controller = ShiftWorkersController(session)

        if action == 'approve':
            success = shift_workers_controller.approve_timesheet_for_worker(
                shift_id, worker_id, user_session.get_id
            )
            message = "Timesheet approved successfully." if success else "Failed to approve timesheet."
        else:  # reject
            success = shift_workers_controller.reject_timesheet_for_worker(
                shift_id, worker_id, user_session.get_id
            )
            message = "Timesheet rejected successfully." if success else "Failed to reject timesheet."

        if success:
            db.commit()
            return {"request_id": request_id, "success": True, "message": message}
        else:
            return {"request_id": request_id, "success": False, "error": message}

    except Exception as e:
        print(f"Error updating timesheet status: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update timesheet status."}
