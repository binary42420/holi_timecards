from datetime import datetime, timedelta
from main import get_db_session
from db.controllers.shifts_controller import ShiftsController
from db.controllers.shiftWorkers_controller import ShiftWorkersController
from db.controllers.users_controller import UsersController
from db.controllers.jobs_controller import JobsController
from db.controllers.client_companies_controller import ClientCompaniesController
from db.controllers.workplace_settings_controller import WorkplaceSettingsController
from user_session import UserSession


def handle_get_schedule_data(data: dict, user_session: UserSession) -> dict:
    """
    Get comprehensive schedule data for the enhanced schedule view.
    """
    request_id = 2001
    if not user_session:
        return {"request_id": request_id, "success": False, "error": "User session not found."}
    
    try:
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        view_type = data.get('view_type', 'week')
        include_workers = data.get('include_workers', True)
        include_jobs = data.get('include_jobs', True)
        include_clients = data.get('include_clients', True)
        filters = data.get('filters', {})
        
        if not start_date_str or not end_date_str:
            return {"request_id": request_id, "success": False, "error": "start_date and end_date are required."}
        
        # Parse dates
        start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
        end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')).date()
        
        # Initialize controllers with proper session management
        with get_db_session() as session:
            shifts_controller = ShiftsController(session)
            shift_workers_controller = ShiftWorkersController(session)
            users_controller = UsersController(session)
            jobs_controller = JobsController(session)
            client_companies_controller = ClientCompaniesController(session)
            workplace_settings_controller = WorkplaceSettingsController(session)

            # Get user and determine access level
            user = users_controller.get_entity(user_session.get_id)

            # Get shifts in date range (no workplace_id needed for single company)
            shifts = shifts_controller.get_shifts_by_date_range(start_date, end_date, None)

            # Enhance shifts with worker assignments and requirements
            enhanced_shifts = []
            for shift in shifts:
                shift_dict = {
                    'id': shift.id,
                    'job_id': shift.job_id,
                    'shift_start_datetime': shift.shift_start_datetime.isoformat() if shift.shift_start_datetime else None,
                    'shift_end_datetime': shift.shift_end_datetime.isoformat() if shift.shift_end_datetime else None,
                    'client_po_number': shift.client_po_number,
                    'role_requirements': shift.required_employee_counts or {},
                    # Legacy fields for backward compatibility
                    'shiftDate': shift.shiftDate.isoformat() if shift.shiftDate else None,
                    'shiftPart': shift.shiftPart.value if shift.shiftPart else None,
                }

                # Get job information
                if shift.job_id:
                    job = jobs_controller.get_entity(shift.job_id)
                    if job:
                        shift_dict['job_name'] = job.jobName if hasattr(job, 'jobName') else getattr(job, 'name', 'Unknown Job')
                        shift_dict['job_location'] = f"{getattr(job, 'venue_name', '')}, {getattr(job, 'venue_address', '')}"
                        shift_dict['venue_name'] = getattr(job, 'venue_name', '')
                        shift_dict['venue_address'] = getattr(job, 'venue_address', '')
                        if hasattr(job, 'client_company_id') and job.client_company_id:
                            client = client_companies_controller.get_entity(job.client_company_id)
                            if client:
                                shift_dict['client_company_name'] = client.companyName if hasattr(client, 'companyName') else getattr(client, 'name', 'Unknown Client')

                # Get assigned workers
                assigned_workers = shift_workers_controller.get_shift_workers_by_shift_id(shift.id)
                shift_dict['assigned_workers'] = []

                for sw in assigned_workers:
                    worker = users_controller.get_entity(sw.userID)
                    if worker:
                        shift_dict['assigned_workers'].append({
                            'user_id': sw.userID,
                            'name': worker.name,
                            'role_assigned': sw.role_assigned.value if sw.role_assigned else 'stagehand',
                            'is_approved': sw.is_approved,
                            'times_submitted_at': sw.times_submitted_at.isoformat() if sw.times_submitted_at else None
                        })

                enhanced_shifts.append(shift_dict)

            # Prepare response data
            response_data = {
                'shifts': enhanced_shifts,
                'view_type': view_type,
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }

            # Include workers if requested
            if include_workers:
                # Get all workers (fallback to get_all_entities if get_all_approved_workers doesn't exist)
                try:
                    workers = users_controller.get_all_approved_workers()
                except AttributeError:
                    workers = users_controller.get_all_entities()
                    # Filter for active workers only
                    workers = [w for w in workers if getattr(w, 'isActive', True)]

                workers_data = []

                for worker in workers:
                    worker_dict = {
                        'id': worker.id,
                        'name': worker.name,
                        'employee_type': worker.employee_type.value if hasattr(worker, 'employee_type') and worker.employee_type else 'stagehand',
                        'is_active': getattr(worker, 'isActive', True),
                        'certifications': None
                    }

                    # Get certifications
                    if hasattr(worker, 'certifications') and worker.certifications:
                        try:
                            worker_dict['certifications'] = worker.certifications.to_dict()
                        except:
                            worker_dict['certifications'] = None

                    # Calculate availability score (could be enhanced with actual availability data)
                    worker_dict['availability_score'] = 100  # Placeholder
                    worker_dict['current_shifts_count'] = len([s for s in enhanced_shifts
                                                             if any(aw['user_id'] == worker.id for aw in s['assigned_workers'])])

                    workers_data.append(worker_dict)

                response_data['workers'] = workers_data

            # Include jobs if requested
            if include_jobs:
                jobs = jobs_controller.get_all_entities()
                jobs_data = []

                for job in jobs:
                    job_dict = {
                        'id': job.id,
                        'jobName': job.jobName if hasattr(job, 'jobName') else getattr(job, 'name', 'Unknown Job'),
                        'location': f"{getattr(job, 'venue_name', '')}, {getattr(job, 'venue_address', '')}",
                        'venue_name': getattr(job, 'venue_name', ''),
                        'venue_address': getattr(job, 'venue_address', ''),
                        'client_company_id': getattr(job, 'client_company_id', None),
                        'isActive': getattr(job, 'is_active', True)
                    }

                    if hasattr(job, 'client_company_id') and job.client_company_id:
                        client = client_companies_controller.get_entity(job.client_company_id)
                        if client:
                            job_dict['client_company_name'] = client.companyName if hasattr(client, 'companyName') else getattr(client, 'name', 'Unknown Client')

                    jobs_data.append(job_dict)

                response_data['jobs'] = jobs_data

            # Include clients if requested
            if include_clients:
                clients = client_companies_controller.get_all_entities()
                clients_data = []

                for client in clients:
                    clients_data.append({
                        'id': client.id,
                        'companyName': client.companyName if hasattr(client, 'companyName') else getattr(client, 'name', 'Unknown Client'),
                        'name': client.companyName if hasattr(client, 'companyName') else getattr(client, 'name', 'Unknown Client'),
                        'isActive': getattr(client, 'isActive', True)  # ClientCompany model might not have isActive field
                    })

                response_data['clients'] = clients_data

            # Include workplace settings for Hands on Labor
            try:
                workplace_settings = workplace_settings_controller.get_settings()
                if workplace_settings:
                    response_data['workplace_settings'] = workplace_settings.to_dict()
            except:
                response_data['workplace_settings'] = None

            return {"request_id": request_id, "success": True, "data": response_data}
        
    except Exception as e:
        print(f"Error getting schedule data: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to retrieve schedule data."}


def handle_assign_worker_to_shift_enhanced(data: dict, user_session: UserSession) -> dict:
    """
    Assign a worker to a shift with role specification.
    """
    request_id = 2002
    if not user_session:
        return {"request_id": request_id, "success": False, "error": "User session not found."}
    
    try:
        shift_id = data.get('shift_id')
        worker_id = data.get('worker_id')
        role_assigned = data.get('role_assigned', 'stagehand')
        
        if not all([shift_id, worker_id]):
            return {"request_id": request_id, "success": False, "error": "shift_id and worker_id are required."}
        
        # Verify permissions
        with get_db_session() as session:
            users_controller = UsersController(session)
            user = users_controller.get_entity(user_session.get_id)

            if not user.isManager:
                # Check if user is crew chief on this shift
                shift_workers_controller = ShiftWorkersController(session)
                shift_workers = shift_workers_controller.get_shift_workers_by_shift_id(shift_id)
                is_crew_chief = any(sw.userID == user_session.get_id and
                                  sw.role_assigned.value == 'crew_chief'
                                  for sw in shift_workers)

                if not is_crew_chief:
                    return {"request_id": request_id, "success": False, "error": "Insufficient permissions to assign workers."}

        # Assign worker to shift
        with get_db_session() as session:
            shift_workers_controller = ShiftWorkersController(session)
            assignment_data = {
                'shiftID': shift_id,
                'userID': worker_id,
                'role_assigned': role_assigned
            }

            shift_worker = shift_workers_controller.create_entity(assignment_data)
        
        if shift_worker:
            return {"request_id": request_id, "success": True, "message": "Worker assigned successfully."}
        else:
            return {"request_id": request_id, "success": False, "error": "Failed to assign worker."}
            
    except Exception as e:
        print(f"Error assigning worker to shift: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to assign worker to shift."}


def handle_unassign_worker_from_shift_enhanced(data: dict, user_session: UserSession) -> dict:
    """
    Unassign a worker from a shift.
    """
    request_id = 2003
    if not user_session:
        return {"request_id": request_id, "success": False, "error": "User session not found."}
    
    try:
        shift_id = data.get('shift_id')
        worker_id = data.get('worker_id')
        role_assigned = data.get('role_assigned', 'stagehand')
        
        if not all([shift_id, worker_id]):
            return {"request_id": request_id, "success": False, "error": "shift_id and worker_id are required."}
        
        # Verify permissions
        with get_db_session() as session:
            users_controller = UsersController(session)
            user = users_controller.get_entity(user_session.get_id)

            if not user.isManager:
                # Check if user is crew chief on this shift
                shift_workers_controller = ShiftWorkersController(session)
                shift_workers = shift_workers_controller.get_shift_workers_by_shift_id(shift_id)
                is_crew_chief = any(sw.userID == user_session.get_id and
                                  sw.role_assigned.value == 'crew_chief'
                                  for sw in shift_workers)

                if not is_crew_chief:
                    return {"request_id": request_id, "success": False, "error": "Insufficient permissions to unassign workers."}

        # Unassign worker from shift
        with get_db_session() as session:
            shift_workers_controller = ShiftWorkersController(session)
            success = shift_workers_controller.delete_entity_by_composite_key(shift_id, worker_id, role_assigned)
        
        if success:
            return {"request_id": request_id, "success": True, "message": "Worker unassigned successfully."}
        else:
            return {"request_id": request_id, "success": False, "error": "Failed to unassign worker."}
            
    except Exception as e:
        print(f"Error unassigning worker from shift: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to unassign worker from shift."}


def handle_create_shift_enhanced(data: dict, user_session: UserSession) -> dict:
    """
    Create a new shift with enhanced features.
    """
    request_id = 2004
    if not user_session:
        return {"request_id": request_id, "success": False, "error": "User session not found."}
    
    try:
        # Verify permissions
        with get_db_session() as session:
            users_controller = UsersController(session)
            user = users_controller.get_entity(user_session.get_id)

            if not user.isManager:
                return {"request_id": request_id, "success": False, "error": "Only managers can create shifts."}

            # Extract shift data
            shift_start_datetime = data.get('shift_start_datetime')
            shift_end_datetime = data.get('shift_end_datetime')
            job_id = data.get('job_id')
            role_requirements = data.get('role_requirements', {})
            client_po_number = data.get('client_po_number')
            auto_assign_worker = data.get('auto_assign_worker')

            if not shift_start_datetime:
                return {"request_id": request_id, "success": False, "error": "shift_start_datetime is required."}

            # Create shift
            shifts_controller = ShiftsController(session)
            shift_data = {
                'shift_start_datetime': datetime.fromisoformat(shift_start_datetime.replace('Z', '+00:00')),
                'job_id': job_id,
                'required_employee_counts': role_requirements,
                'client_po_number': client_po_number
            }

            if shift_end_datetime:
                shift_data['shift_end_datetime'] = datetime.fromisoformat(shift_end_datetime.replace('Z', '+00:00'))

            shift = shifts_controller.create_entity(shift_data)

            if not shift:
                return {"request_id": request_id, "success": False, "error": "Failed to create shift."}

            # Auto-assign worker if specified
            if auto_assign_worker and auto_assign_worker.get('worker_id'):
                shift_workers_controller = ShiftWorkersController(session)
                assignment_data = {
                    'shiftID': shift.id,
                    'userID': auto_assign_worker['worker_id'],
                    'role_assigned': auto_assign_worker.get('role', 'stagehand')
                }
                shift_workers_controller.create_entity(assignment_data)
        
        # Return created shift data
        shift_dict = {
            'id': shift.id,
            'job_id': shift.job_id,
            'shift_start_datetime': shift.shift_start_datetime.isoformat() if shift.shift_start_datetime else None,
            'shift_end_datetime': shift.shift_end_datetime.isoformat() if shift.shift_end_datetime else None,
            'client_po_number': shift.client_po_number,
            'role_requirements': shift.required_employee_counts or {},
            'assigned_workers': []
        }
        
        return {"request_id": request_id, "success": True, "data": shift_dict, "message": "Shift created successfully."}
        
    except Exception as e:
        print(f"Error creating shift: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to create shift."}


def handle_update_shift_enhanced(data: dict, user_session: UserSession) -> dict:
    """
    Update an existing shift.
    """
    request_id = 2005
    if not user_session:
        return {"request_id": request_id, "success": False, "error": "User session not found."}
    
    try:
        shift_id = data.get('shift_id')
        if not shift_id:
            return {"request_id": request_id, "success": False, "error": "shift_id is required."}
        
        # Verify permissions
        with get_db_session() as session:
            users_controller = UsersController(session)
            user = users_controller.get_entity(user_session.get_id)

            if not user.isManager:
                return {"request_id": request_id, "success": False, "error": "Only managers can update shifts."}

            # Update shift
            shifts_controller = ShiftsController(session)
            update_data = {}

            if 'shift_start_datetime' in data:
                update_data['shift_start_datetime'] = datetime.fromisoformat(data['shift_start_datetime'].replace('Z', '+00:00'))

            if 'shift_end_datetime' in data:
                update_data['shift_end_datetime'] = datetime.fromisoformat(data['shift_end_datetime'].replace('Z', '+00:00'))

            if 'job_id' in data:
                update_data['job_id'] = data['job_id']

            if 'role_requirements' in data:
                update_data['required_employee_counts'] = data['role_requirements']

            if 'client_po_number' in data:
                update_data['client_po_number'] = data['client_po_number']

            updated_shift = shifts_controller.update_entity(shift_id, update_data)
        
        if updated_shift:
            shift_dict = {
                'id': updated_shift.id,
                'job_id': updated_shift.job_id,
                'shift_start_datetime': updated_shift.shift_start_datetime.isoformat() if updated_shift.shift_start_datetime else None,
                'shift_end_datetime': updated_shift.shift_end_datetime.isoformat() if updated_shift.shift_end_datetime else None,
                'client_po_number': updated_shift.client_po_number,
                'role_requirements': updated_shift.required_employee_counts or {}
            }
            
            return {"request_id": request_id, "success": True, "data": shift_dict, "message": "Shift updated successfully."}
        else:
            return {"request_id": request_id, "success": False, "error": "Failed to update shift."}
            
    except Exception as e:
        print(f"Error updating shift: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update shift."}


def handle_delete_shift_enhanced(data: dict, user_session: UserSession) -> dict:
    """
    Delete a shift.
    """
    request_id = 2006
    if not user_session:
        return {"request_id": request_id, "success": False, "error": "User session not found."}
    
    try:
        shift_id = data.get('shift_id')
        if not shift_id:
            return {"request_id": request_id, "success": False, "error": "shift_id is required."}
        
        # Verify permissions
        with get_db_session() as session:
            users_controller = UsersController(session)
            user = users_controller.get_entity(user_session.get_id)

            if not user.isManager:
                return {"request_id": request_id, "success": False, "error": "Only managers can delete shifts."}

            # Delete shift (this should also cascade delete shift workers)
            shifts_controller = ShiftsController(session)
            success = shifts_controller.delete_entity(shift_id)
        
        if success:
            return {"request_id": request_id, "success": True, "message": "Shift deleted successfully."}
        else:
            return {"request_id": request_id, "success": False, "error": "Failed to delete shift."}
            
    except Exception as e:
        print(f"Error deleting shift: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to delete shift."}
