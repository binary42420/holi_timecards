import os
import sys
import json
import asyncio
import logging
import websockets
from datetime import datetime, timezone
from aiohttp import web
import aiohttp_cors
from dotenv import load_dotenv
from handlers.google_auth import google_auth_instance

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv('.env')

print(f"🚀 Starting Holi Backend Server...")
print(f"🐍 Python version: {sys.version}")
print(f"📁 Working directory: {os.getcwd()}")
print(f"🌍 Environment variables:")
print(f"   HOST: {os.getenv('HOST', 'not set')}")
print(f"   PORT: {os.getenv('PORT', 'not set')}")

from user_session import UserSession
import websockets
import asyncio
import json
from handlers import login, employee_signin, manager_signin, employee_shifts_request, \
    get_employee_requests, manager_insert_shifts, employee_list, send_profile, manager_schedule, \
    send_shifts_to_employee, make_shifts, timesheet_management_handlers, enhanced_schedule_handlers, \
    enhanced_settings_handlers
from handlers import crew_chief_handlers, client_company_handlers, client_directory_handlers, job_handlers, shift_management_handlers, user_management_handlers, admin_data_access
from handlers.google_auth import google_auth_instance
from handlers.google_session_create import handle_google_session_create
from db.controllers.shiftBoard_controller import convert_shiftBoard_to_client
from migrate_soft_delete import migrate_soft_delete_columns
from migrate_jobs_soft_delete import migrate_jobs_soft_delete_columns
from migrate_all_soft_delete import migrate_all_soft_delete_columns

# Initialize the database engine and session factory
database_initialized = False
try:
    from main import initialize_database_and_session_factory
    initialize_database_and_session_factory()
    database_initialized = True
    print("✅ Database engine and session factory initialized successfully")
except ImportError as e:
    print(f"⚠️  Database module import failed: {e}")
    print("⚠️  Server will start but database operations will fail")
except Exception as e:
    print(f"⚠️  Database initialization failed: {e}")
    print("⚠️  Server will start but database operations may fail")
    print(f"⚠️  Error details: {type(e).__name__}: {str(e)}")

# Print environment info for debugging
print(f"🔍 Environment check:")
print(f"   DB_HOST: {os.getenv('DB_HOST', 'not set')}")
print(f"   DB_PORT: {os.getenv('DB_PORT', 'not set')}")
print(f"   DB_USER: {os.getenv('DB_USER', 'not set')}")
print(f"   DB_NAME: {os.getenv('DB_NAME', 'not set')}")
print(f"   DB_PASSWORD: {'set' if os.getenv('DB_PASSWORD') else 'not set'}")
print(f"   REDIS_HOST: {os.getenv('REDIS_HOST', 'not set')}")
print(f"   REDIS_PASSWORD: {'set' if os.getenv('REDIS_PASSWORD') else 'not set'}")
print(f"   SESSION_SECRET_KEY: {'set' if os.getenv('SESSION_SECRET_KEY') else 'not set'}")
print(f"   CSRF_SECRET_KEY: {'set' if os.getenv('CSRF_SECRET_KEY') else 'not set'}")
print(f"   Database initialized: {database_initialized}")

# Session management - per-client sessions only
user_sessions = {}  # Dictionary to store sessions by client_id


async def handle_request(request_id, data, client_id=None, session_id=None, csrf_token=None):
    global user_sessions
    from security.secure_session import secure_session_manager

    # Get session for this client
    current_session = user_sessions.get(client_id) if client_id else None

    # Check for session data in request for authenticated requests (fallback to data if not provided)
    if not session_id:
        session_id = data.get('session_id') if isinstance(data, dict) else None
    if not csrf_token:
        csrf_token = data.get('csrf_token') if isinstance(data, dict) else None

    # Validate session if provided (prioritize session_id over client_id lookup)
    if session_id and csrf_token:
        try:
            session_data = secure_session_manager.validate_session(session_id, client_ip="unknown")
            if session_data:
                # Create UserSession object from validated session (no workplace for single company)
                current_session = UserSession(
                    user_id=session_data.get('user_id'),
                    username=session_data.get('username'),
                    is_manager=session_data.get('is_manager', False),
                    email=session_data.get('email'),
                    is_admin=session_data.get('is_admin', False)
                )
                # Store in client sessions for this connection
                if client_id:
                    user_sessions[client_id] = current_session
                print(f"DEBUG: Session validated for client {client_id}: {current_session.username}")
            else:
                print(f"DEBUG: Session validation failed for session_id: {session_id}")
        except Exception as e:
            print(f"DEBUG: Session validation error: {e}")

    # If no session found via session_id but we have stored user data, try to find by user credentials
    elif not current_session and isinstance(data, dict):
        # Check if this is a Google user with stored credentials
        stored_user = data.get('user')
        if stored_user and stored_user.get('googleId'):
            # For Google users, try to find existing session by email/googleId
            google_id = stored_user.get('googleId')
            email = stored_user.get('email')
            username = stored_user.get('username')

            print(f"DEBUG: Looking for existing session for Google user: {email}, username: {username}")
            print(f"DEBUG: Current user_sessions keys: {list(user_sessions.keys())}")

            # Look for existing session with matching Google credentials
            session_found = False
            for existing_client_id, existing_session in user_sessions.items():
                print(f"DEBUG: Checking session {existing_client_id}: email={getattr(existing_session, '_email', 'None')}, username={getattr(existing_session, '_username', 'None')}")

                if (hasattr(existing_session, '_email') and existing_session._email == email) or \
                   (hasattr(existing_session, '_username') and existing_session._username == username):
                    current_session = existing_session
                    # Update the session mapping for this new client_id
                    if client_id and client_id != existing_client_id:
                        user_sessions[client_id] = current_session
                        print(f"DEBUG: Reused Google session for client {client_id}: {current_session._username}")
                    session_found = True
                    break

            if not session_found:
                print(f"DEBUG: No existing session found for Google user {email}. Creating new session.")
                # Create a new session for this Google user
                from user_session import UserSession
                current_session = UserSession(
                    user_id=stored_user.get('userId') or stored_user.get('id'),
                    username=username,
                    is_manager=stored_user.get('isManager', False),
                    email=email,
                    is_admin=stored_user.get('isAdmin', False)
                )
                if client_id:
                    user_sessions[client_id] = current_session
                    print(f"DEBUG: Created new session for Google user {client_id}: {username}")

    # Session validation complete - current_session is now set if valid session exists

    print(f"DEBUG: handle_request - client_id: {client_id}, current_session: {current_session}")
    print(f"DEBUG: Received request_id: {request_id}, type: {type(request_id)}")
    print(f"DEBUG: Request data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")

    if request_id == 10:
        # Login request handling
        print("Received Login request")
        print(f"DEBUG: Login request data: {data}")
        print(f"DEBUG: Request ID confirmed as: {request_id}")
        print(f"DEBUG: Client ID: {client_id}")

        # Get client IP for security logging
        client_ip = "unknown"
        if client_id in user_sessions:
            # Try to get IP from session if available
            client_ip = getattr(user_sessions[client_id], 'client_ip', 'unknown')

        response, session = login.handle_login(data, client_ip)

        # Store session for this client
        if client_id and session:
            user_sessions[client_id] = session
            print(f"DEBUG: Stored session for client {client_id}: {session}")
        current_session = session

        return {"request_id": request_id, "data": response}

    elif request_id == 20:
        # Employee Sign in request handling
        print("Received Employee Sign in request")
        session = employee_signin.handle_employee_signin(data)
        # Store session for this client
        if client_id and session:
            user_sessions[client_id] = session
            print(f"DEBUG: Stored employee session for client {client_id}: {session}")
        # Assuming employee_signin returns current_session or raises error
        # For consistency, let's ensure a response structure
        if session: # Simplified check, actual logic might be more complex
            return {"request_id": request_id, "success": True, "message": "Employee sign-in successful."}
        else: # This path might not be hit if handle_employee_signin raises errors for failure
            return {"request_id": request_id, "success": False, "message": "Employee sign-in failed."}


    elif request_id == 30:
        # Manager Sign in request handling
        print("Received Manager Sign in request")
        # handle_manager_signin in manager_signin.py returns a dict {'success': True/False, 'message': ...}
        response_data = manager_signin.handle_manager_signin(data)
        if response_data.get("success"):
            # If sign-in is successful, we might need to establish a session.
            # For now, assuming handle_login is called separately or this handler also sets current_session.
            # The original code assigned user_session = manager_signin.handle_manager_signin(data)
            # but the handler returns a dict, not a session object directly.
            # This part might need further review based on how session is truly established for managers.
            # For now, let's assume a successful sign-in implies a session is managed internally or by a subsequent login.
            pass # Placeholder for potential session establishment logic if needed here
        return {"request_id": request_id, "data": response_data}


    elif request_id == 40:
        # Employee's Shifts Request handling (Submit availability)
        print("Received Employee's Shifts Request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        employee_shifts_request.handle_employee_shifts_request(data, current_session)
        return {"request_id": request_id, "success": True, "message": "Shift request submitted."}

    elif request_id == 41:
        # Check if employee is in shift request window
        print("Received Is In Request Window check")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        is_in_window = employee_shifts_request.handle_is_in_request_window(current_session)
        return {"request_id": request_id, "success": True, "data": {"is_in_window": is_in_window}}

    elif request_id == 42:
        # Get request window times
        print("Received Get Request Window Times")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        window_times = employee_shifts_request.handle_get_request_window_times(current_session)
        return {"request_id": request_id, "success": True, "data": window_times}

    elif request_id == 50:
        # Manager Get Employees Requests Request
        print("Received Manager Get Employees Requests Request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        # This handler returns data directly
        return get_employee_requests.handle_get_employee_requests(data, current_session)

    elif request_id == 55:
        # Manager Shifts inserting Request handling
        print("Received Manager Shifts inserting Request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        manager_insert_shifts.handle_manager_insert_shifts(data, current_session)
        return {"request_id": request_id, "success": True, "message": "Shifts inserted."}


    elif request_id == 60:
        # Employees list request handling
        print("Received Employees list request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        # This handler returns data directly
        return employee_list.handle_employee_list(current_session)

    elif request_id == 62:
        # Employee approval request handling
        print("Received Employee Approval request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        success = employee_list.handle_employee_approval(data, current_session)
        return {"request_id": request_id, "success": success}

    elif request_id == 64:
        # Employee rejection request handling
        print("Received Employee Rejection request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        success = employee_list.handle_employee_rejection(data, current_session)
        return {"request_id": request_id, "success": success}

    elif request_id == 65: # CREATE_EMPLOYEE_BY_MANAGER
        print("Received Create Employee by Manager request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return employee_list.handle_create_employee_by_manager(data, current_session)

    elif request_id == 70:
        # Send user profile handling
        print("Send user profile")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        profile_data = send_profile.handle_send_profile(current_session)
        return {"request_id": request_id, "success": True, "data": profile_data}

    elif request_id == 80:
        # Make new week shifts (original ID 80)
        print("Make new week shifts")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        make_shifts.make_shifts(current_session) # This function doesn't return a client response
        return {"request_id": request_id, "success": True, "message": "Attempted to make new week shifts."}

    elif request_id == 81:
        # Manager creates new shift board
        print("Received Create New Shift Board request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        board = manager_schedule.handle_create_new_board(current_session)
        converted_board = convert_shiftBoard_to_client(board)
        return {"request_id": request_id, "success": True, "data": converted_board}

    elif request_id == 82:
        # Manager saves shift board content
        print("Received Save Shift Board Content request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        # data here is request_data from handle_client
        board = manager_schedule.handle_save_board(data, current_session)
        converted_board = convert_shiftBoard_to_client(board)
        return {"request_id": request_id, "success": True, "data": converted_board}

    elif request_id == 83:
        # Manager resets shift board content
        print("Received Reset Shift Board Content request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        board = manager_schedule.handle_reset_board(current_session)
        converted_board = convert_shiftBoard_to_client(board)
        return {"request_id": request_id, "success": True, "data": converted_board}

    elif request_id == 84:
        # Manager publishes shift board
        print("Received Publish Shift Board request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        is_published = manager_schedule.handle_publish_board(current_session)
        return {"request_id": request_id, "success": True, "data": {"is_published": is_published}}

    elif request_id == 85:
        # Manager unpublishes shift board
        print("Received Unpublish Shift Board request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        # handle_unpublish_board returns True if successfully unpublished (board.is_published is False)
        # So, if result is True, it means is_published is False.
        result_is_unpublished_successfully = manager_schedule.handle_unpublish_board(current_session)
        return {"request_id": request_id, "success": result_is_unpublished_successfully, "data": {"is_published": not result_is_unpublished_successfully}}


    elif request_id == 90:
        # Get Employee's shifts handling
        print("Send employees shifts")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        employees_shifts = send_shifts_to_employee.handle_send_shifts(current_session)
        print(employees_shifts)
        return {"request_id": request_id, "success": True, "data": employees_shifts}

    elif request_id == 91:
        # Get Employees Requests Data for Manager Schedule
        print("Get Employees Requests Data for Manager Schedule")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        res = manager_schedule.watch_workers_requests(current_session)
        print(res)
        return {"request_id": request_id, "success": True, "data": res}

    elif request_id == 93:
        # Get all workers for Manager Schedule
        print("Get all workers for Manager Schedule")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        res = manager_schedule.get_all_workers_names_by_workplace_id(current_session)
        print(res)
        return {"request_id": request_id, "success": True, "data": res}

    elif request_id == 94: # Get All Approved Worker Details
        print("Received Get All Approved Worker Details request")
        print(f"DEBUG: request_id 94 - current_session: {current_session}")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return employee_list.handle_get_all_approved_worker_details(current_session)

    elif request_id == 410: # Update Employee Certifications
        print("Received Update Employee Certifications request")
        print(f"DEBUG: request_id 410 - current_session: {current_session}")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return employee_list.handle_manager_update_employee_certifications(data, current_session)

    elif request_id == 95:
        # Get preferences for Manager Schedule
        print("Get preferences for Manager Schedule")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        res = manager_schedule.handle_get_preferences(current_session)
        print(res)
        return {"request_id": request_id, "success": True, "data": res}

    elif request_id == 97:
        # Get start date for Manager Schedule
        print("Get start date for Manager Schedule")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        res = manager_schedule.handle_get_start_date(current_session).isoformat()  # Convert to ISO format
        print(res)
        return {"request_id": request_id, "success": True, "data": res}

    elif request_id == 98:
        # Get assigned shifts for Manager Schedule
        print("Get assigned shifts for Manager Schedule")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        res = manager_schedule.handle_get_assigned_shifts(current_session, data)
        print(res)
        return {"request_id": request_id, "success": True, "data": res}

    elif request_id == 99:
        # Change schedule (assign/unassign worker to/from shift)
        print("Received Change Schedule request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        manager_schedule.handle_schedules(current_session, data)
        return {"request_id": request_id, "success": True, "message": "Schedule change processed."}


    elif request_id == 100: # New request ID for Crew Chief to get their shifts
        print("Received Get Crew Chief Shifts request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        # This handler returns data directly in the desired format
        return crew_chief_handlers.handle_get_crew_chief_shifts(current_session)

    elif request_id == 101: # Get Crew Members for Shift (Crew Chief)
        print("Received Get Crew Members for Shift request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return crew_chief_handlers.handle_get_crew_members_for_shift(data, current_session)

    elif request_id == 102: # Submit Shift Times (Crew Chief)
        print("Received Submit Shift Times request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return crew_chief_handlers.handle_submit_shift_times(data, current_session)

    elif request_id == 103: # Get all submitted timesheets for manager
        print("Received Get All Submitted Timesheets request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return timesheet_management_handlers.handle_get_all_submitted_timesheets(current_session)

    elif request_id == 104: # Update timesheet status (approve/reject)
        print("Received Update Timesheet Status request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return timesheet_management_handlers.handle_update_timesheet_status(data, current_session)

    elif request_id == 200: # Get All Client Companies
        print("Received Get All Client Companies request")
        print(f"DEBUG: request_id 200 - current_session: {current_session}")
        return client_company_handlers.handle_get_all_client_companies(current_session)

    elif request_id == 201: # Create Client Company
        print("Received Create Client Company request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return client_company_handlers.handle_create_client_company(data, current_session)

    elif request_id == 202: # Update Client Company
        print("Received Update Client Company request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return client_company_handlers.handle_update_client_company(data, current_session)

    elif request_id == 203: # Delete Client Company
        print("Received Delete Client Company request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return client_company_handlers.handle_delete_client_company(data, current_session)

    # === JOB MANAGEMENT HANDLERS ===
    elif request_id == 210: # Create Job
        print("Received Create Job request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return job_handlers.handle_create_job(data, current_session)

    elif request_id == 211: # Get Jobs by Manager
        print("Received Get Jobs by Manager request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return job_handlers.handle_get_jobs_by_manager(current_session)

    elif request_id == 213: # Update Job
        print("Received Update Job request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return job_handlers.handle_update_job(data, current_session)

    # === CLIENT DIRECTORY HANDLERS ===
    elif request_id == 212: # Get Client Directory
        print("Received Get Client Directory request")
        print(f"DEBUG: Client Directory - client_id: {client_id}, current_session: {current_session}")
        print(f"DEBUG: Client Directory - session details: {getattr(current_session, '_username', 'No username') if current_session else 'No session'}")
        print(f"DEBUG: Client Directory - is_manager: {getattr(current_session, '_is_manager', 'Unknown') if current_session else 'No session'}")

        # SESSION MANAGEMENT FIX: Enhanced session validation for Client Directory
        if not current_session:
            print(f"DEBUG: Client Directory - No session found. Available sessions: {list(user_sessions.keys())}")
            print(f"DEBUG: Client Directory - Attempting session recovery...")
            
            # Try to recover session from stored sessions
            if client_id in user_sessions:
                current_session = user_sessions[client_id]
                print(f"DEBUG: Client Directory - Recovered session for client {client_id}")
            else:
                # Try to find any valid manager session as fallback
                for cid, session in user_sessions.items():
                    if hasattr(session, '_is_manager') and session._is_manager:
                        current_session = session
                        user_sessions[client_id] = session  # Store for this client
                        print(f"DEBUG: Client Directory - Using fallback manager session from client {cid}")
                        break
                        
            if not current_session:
                return {"request_id": request_id, "success": False, "error": "User session not found."}
                
        return client_directory_handlers.handle_get_client_directory(current_session)

    elif request_id == 216: # Get Client Company Details (changed from 213 to avoid conflict)
        print("Received Get Client Company Details request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return client_directory_handlers.handle_get_client_company_details(data, current_session)

    elif request_id == 214: # Update Client User Status
        print("Received Update Client User Status request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return client_directory_handlers.handle_update_client_user_status(data, current_session)

    elif request_id == 215: # Get Client Analytics
        print("Received Get Client Analytics request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return client_directory_handlers.handle_get_client_analytics(current_session)

    elif request_id == 220: # Create Shift
        print("Received Create Shift request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return shift_management_handlers.handle_create_shift(data, current_session)

    elif request_id == 221: # Get Shifts by Job ID
        print("Received Get Shifts by Job ID request")
        print(f"DEBUG: Current current_session: {current_session}")
        print(f"DEBUG: current_session type: {type(current_session)}")
        if current_session:
            print(f"DEBUG: current_session.get_id: {current_session.get_id}")
            print(f"DEBUG: current_session._is_manager: {current_session._is_manager}")
        return shift_management_handlers.handle_get_shifts_by_job(data, current_session)

    elif request_id == 230: # Assign Worker to Shift
        print("Received Assign Worker to Shift request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return shift_management_handlers.handle_assign_worker_to_shift(data, current_session)

    elif request_id == 231: # Unassign Worker from Shift
        print("Received Unassign Worker from Shift request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return shift_management_handlers.handle_unassign_worker_from_shift(data, current_session)

    elif request_id == 232: # Update Shift Requirements
        print("Received Update Shift Requirements request")
        print(f"DEBUG: request_id 232 - current_session: {current_session}")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return shift_management_handlers.handle_update_shift_requirements(data, current_session)

    # === TIMECARD MANAGEMENT HANDLERS ===
    elif request_id == 240: # Get Shift Timecard
        print("Received Get Shift Timecard request")
        from handlers.timecard_handlers import handle_get_shift_timecard
        return handle_get_shift_timecard(data, current_session)

    elif request_id == 241: # Clock In/Out Worker
        print("Received Clock In/Out Worker request")
        from handlers.timecard_handlers import handle_clock_in_out_worker
        return handle_clock_in_out_worker(data, current_session)

    elif request_id == 242: # Mark Worker Absent
        print("Received Mark Worker Absent request")
        from handlers.timecard_handlers import handle_mark_worker_absent
        return handle_mark_worker_absent(data, current_session)

    elif request_id == 243: # Update Worker Notes
        print("Received Update Worker Notes request")
        from handlers.timecard_handlers import handle_update_worker_notes
        return handle_update_worker_notes(data, current_session)

    elif request_id == 244: # End Shift - Clock Out All
        print("Received End Shift - Clock Out All request")
        from handlers.timecard_handlers import handle_end_shift_clock_out_all
        return handle_end_shift_clock_out_all(data, current_session)

    elif request_id == 991:
        # Set preferences
        print("Set preferences")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        manager_schedule.handle_save_preferences(current_session.get_id, data)
        return {"request_id": request_id, "success": True, "message": "Preferences saved."}


    elif request_id == 992:
        # Set schedule window time
        print("Set schedule window time")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        manager_schedule.open_requests_windows(current_session.get_id, data)
        # manager_schedule.get_last_shift_board_window_times(current_session.get_id) # This seems like a debug/logging line
        return {"request_id": request_id, "success": True, "message": "Schedule window time set."}

    # === TIMESHEET MANAGEMENT HANDLERS ===
    elif request_id == 1010: # Get shift timesheet details
        print("Received Get Shift Timesheet Details request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return timesheet_management_handlers.handle_get_shift_timesheet_details(data, current_session)

    elif request_id == 1011: # Update worker timesheet
        print("Received Update Worker Timesheet request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return timesheet_management_handlers.handle_update_worker_timesheet(data, current_session)

    elif request_id == 1012: # Submit shift timesheet
        print("Received Submit Shift Timesheet request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return timesheet_management_handlers.handle_submit_shift_timesheet(data, current_session)

    elif request_id == 1013: # Approve shift timesheet
        print("Received Approve Shift Timesheet request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return timesheet_management_handlers.handle_approve_shift_timesheet(data, current_session)

    elif request_id == 1014: # Get employee timesheet history
        print("Received Get Employee Timesheet History request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return timesheet_management_handlers.handle_get_employee_timesheet_history(data, current_session)

    elif request_id == 1020: # Get user shifts
        print("Received Get User Shifts request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        from handlers.user_shifts_handlers import handle_get_user_shifts
        return handle_get_user_shifts(data, current_session)

    elif request_id == 1021: # Get crew chief shifts
        print("Received Get Crew Chief Shifts request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        from handlers.user_shifts_handlers import handle_get_crew_chief_shifts
        return handle_get_crew_chief_shifts(data, current_session)

    # === ENHANCED SCHEDULE HANDLERS ===
    elif request_id == 2001: # Get schedule data
        print("Received Get Schedule Data request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_schedule_handlers.handle_get_schedule_data(data, current_session)

    elif request_id == 2002: # Assign worker to shift (enhanced)
        print("Received Assign Worker to Shift (Enhanced) request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_schedule_handlers.handle_assign_worker_to_shift_enhanced(data, current_session)

    elif request_id == 2003: # Unassign worker from shift (enhanced)
        print("Received Unassign Worker from Shift (Enhanced) request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_schedule_handlers.handle_unassign_worker_from_shift_enhanced(data, current_session)

    elif request_id == 2004: # Create shift (enhanced)
        print("Received Create Shift (Enhanced) request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_schedule_handlers.handle_create_shift_enhanced(data, current_session)

    elif request_id == 2005: # Update shift (enhanced)
        print("Received Update Shift (Enhanced) request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_schedule_handlers.handle_update_shift_enhanced(data, current_session)

    elif request_id == 2006: # Delete shift (enhanced)
        print("Received Delete Shift (Enhanced) request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_schedule_handlers.handle_delete_shift_enhanced(data, current_session)

    # Google OAuth Authentication handlers
    elif request_id == 66: # GOOGLE_AUTH_LOGIN
        print("Received Google Auth Login request")
        response = google_auth_instance.handle_google_auth_login(data)

        # If login successful and user exists, store session for this client
        if response.get('success') and response.get('data', {}).get('user_exists'):
            session = response['data'].get('user_session')
            # Store session for this client
            if client_id and session:
                user_sessions[client_id] = session
                print(f"DEBUG: Stored Google auth session for client {client_id}: manager={session._is_manager}")
            # Remove user_session from response data as it's not JSON serializable
            response['data'].pop('user_session', None)

        return {"request_id": request_id, **response}

    elif request_id == 67: # LINK_GOOGLE_ACCOUNT
        print("Received Link Google Account request")
        response = google_auth_instance.handle_link_google_account(data)

        # If linking successful, store session for this client
        if response.get('success'):
            session = response['data'].get('user_session')
            # Store session for this client
            if client_id and session:
                user_sessions[client_id] = session
                print(f"DEBUG: Stored Google link session for client {client_id}: manager={session._is_manager}")
            # Remove user_session from response data as it's not JSON serializable
            response['data'].pop('user_session', None)

        return {"request_id": request_id, **response}

    elif request_id == 68: # CREATE_ACCOUNT_WITH_GOOGLE
        print("Received Create Account with Google request")
        response = google_auth_instance.handle_create_account_with_google(data)

        # If account creation successful, store session for this client
        if response.get('success'):
            session = response['data'].get('user_session')
            # Store session for this client
            if client_id and session:
                user_sessions[client_id] = session
                print(f"DEBUG: Stored Google create session for client {client_id}: manager={session._is_manager}")
            # Remove user_session from response data as it's not JSON serializable
            response['data'].pop('user_session', None)

        return {"request_id": request_id, **response}

    elif request_id == 69: # GOOGLE_SESSION_CREATE
        print("Received Google Session Create request")
        print(f"DEBUG: Google session create data: {data}")

        # Get client IP for security logging
        client_ip = "unknown"
        if client_id in user_sessions:
            client_ip = getattr(user_sessions[client_id], 'client_ip', 'unknown')

        # Create session for Google user
        response, session = handle_google_session_create(data, client_ip)

        # Store session for this client
        if client_id and session:
            user_sessions[client_id] = session
            print(f"DEBUG: Stored Google session for client {client_id}: {session}")
        current_session = session

        return {"request_id": request_id, "data": response}

    elif request_id == 72: # GOOGLE_SIGNUP_EMPLOYEE (changed from 69 to avoid conflict)
        print("Received Google Signup Employee request")
        response = google_auth_instance.handle_google_signup_employee(data)

        # If signup successful, store session for this client
        if response.get('success'):
            session = response['data'].get('user_session')
            # Store session for this client
            if client_id and session:
                user_sessions[client_id] = session
                print(f"DEBUG: Stored Google employee signup session for client {client_id}: manager={session._is_manager}")
            # Remove user_session from response data as it's not JSON serializable
            response['data'].pop('user_session', None)

        return {"request_id": request_id, **response}

    elif request_id == 73: # GOOGLE_SIGNUP_MANAGER (changed from 70 to avoid conflict)
        print("Received Google Signup Manager request")
        response = google_auth_instance.handle_google_signup_manager(data)

        # If signup successful, store session for this client
        if response.get('success'):
            session = response['data'].get('user_session')
            # Store session for this client
            if client_id and session:
                user_sessions[client_id] = session
                print(f"DEBUG: Stored Google manager signup session for client {client_id}: manager={session._is_manager}")
            # Remove user_session from response data as it's not JSON serializable
            response['data'].pop('user_session', None)

        return {"request_id": request_id, **response}

    elif request_id == 74: # GOOGLE_SIGNUP_CLIENT (changed from 71 to avoid conflict)
        print("Received Google Signup Client request")
        response = google_auth_instance.handle_google_signup_client(data)

        # If signup successful, store session for this client
        if response.get('success'):
            session = response['data'].get('user_session')
            # Store session for this client
            if client_id and session:
                user_sessions[client_id] = session
                print(f"DEBUG: Stored Google client signup session for client {client_id}: manager={session._is_manager}")
            # Remove user_session from response data as it's not JSON serializable
            response['data'].pop('user_session', None)

        return {"request_id": request_id, **response}

    # === USER MANAGEMENT HANDLERS ===
    elif request_id == 300: # Create Manager
        print("Received Create Manager request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return user_management_handlers.handle_create_manager(data, current_session)

    elif request_id == 301: # Create Admin
        print("Received Create Admin request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return user_management_handlers.handle_create_admin(data, current_session)

    elif request_id == 302: # Get All Users
        print("Received Get All Users request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return user_management_handlers.handle_get_all_users(current_session)

    elif request_id == 950: # Admin Get All Data
        print("Received Admin Get All Data request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return admin_data_access.handle_admin_get_all_data(current_session)

    elif request_id == 951: # Admin User Management
        print("Received Admin User Management request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return admin_data_access.handle_admin_user_management(data, current_session)

    elif request_id == 303: # Update User Role
        print("Received Update User Role request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return user_management_handlers.handle_update_user_role(data, current_session)

    # === EXTENDED SETTINGS HANDLERS ===
    elif request_id == 1100: # Update Company Profile Settings
        print("Received Update Company Profile Settings request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_update_company_profile_settings(data, current_session)

    elif request_id == 1101: # Update User Management Settings
        print("Received Update User Management Settings request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_update_user_management_settings(data, current_session)

    elif request_id == 1102: # Update Certifications Settings
        print("Received Update Certifications Settings request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_update_certifications_settings(data, current_session)

    elif request_id == 1103: # Update Client Management Settings
        print("Received Update Client Management Settings request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_update_client_management_settings(data, current_session)

    elif request_id == 1104: # Update Job Configuration Settings
        print("Received Update Job Configuration Settings request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_update_job_configuration_settings(data, current_session)

    elif request_id == 1105: # Update Advanced Timesheet Settings
        print("Received Update Advanced Timesheet Settings request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_update_timesheet_advanced_settings(data, current_session)

    elif request_id == 1106: # Update Google Integration Settings
        print("Received Update Google Integration Settings request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_update_google_integration_settings(data, current_session)

    elif request_id == 1107: # Update Reporting Settings
        print("Received Update Reporting Settings request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_update_reporting_settings(data, current_session)

    elif request_id == 1108: # Update Security Settings
        print("Received Update Security Settings request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_update_security_settings(data, current_session)

    elif request_id == 1109: # Update Mobile Accessibility Settings
        print("Received Update Mobile Accessibility Settings request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_update_mobile_accessibility_settings(data, current_session)

    elif request_id == 1110: # Update System Admin Settings
        print("Received Update System Admin Settings request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_update_system_admin_settings(data, current_session)

    elif request_id == 1111: # Get All Extended Settings
        print("Received Get All Extended Settings request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_get_extended_settings(current_session)

    elif request_id == 1112: # Reset Extended Settings to Defaults
        print("Received Reset Extended Settings to Defaults request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_reset_extended_settings_to_defaults(current_session)

    elif request_id == 1113: # Test Google Connection
        print("Received Test Google Connection request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_test_google_connection(data, current_session)

    elif request_id == 1114: # Manual Google Sync
        print("Received Manual Google Sync request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_manual_google_sync(current_session)

    elif request_id == 1115: # System Health Check
        print("Received System Health Check request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_system_health_check(current_session)

    elif request_id == 1116: # Manual Backup
        print("Received Manual Backup request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_manual_backup(current_session)

    # === ADVANCED SETTINGS MANAGEMENT ===
    elif request_id == 1117: # Get Settings Summary
        print("Received Get Settings Summary request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_get_settings_summary(current_session)

    elif request_id == 1118: # Bulk Update Settings
        print("Received Bulk Update Settings request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_bulk_update_settings(data, current_session)

    elif request_id == 1119: # Export Settings Backup
        print("Received Export Settings Backup request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_export_settings_backup(current_session)

    elif request_id == 1120: # Import Settings Backup
        print("Received Import Settings Backup request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_import_settings_backup(data, current_session)

    elif request_id == 1121: # Get Settings Templates
        print("Received Get Settings Templates request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_get_settings_templates(current_session)

    elif request_id == 1122: # Apply Settings Template
        print("Received Apply Settings Template request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_apply_settings_template(data, current_session)

    elif request_id == 1123: # Compare Settings
        print("Received Compare Settings request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_compare_settings(data, current_session)

    elif request_id == 1124: # Validate Settings Bulk
        print("Received Validate Settings Bulk request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        return enhanced_settings_handlers.handle_validate_settings_bulk(data, current_session)

    # === MISSING HANDLERS (NEWLY ADDED) ===
    elif request_id == 1: # Test Connection
        print("Received Test Connection request")
        from handlers.missing_handlers import handle_test_connection
        return handle_test_connection(data, current_session)

    elif request_id == 10: # Logout
        print("Received Logout request")
        from handlers.missing_handlers import handle_logout
        return handle_logout(data, current_session)

    elif request_id == 72: # Enhanced Schedule Data
        print("Received Enhanced Schedule Data request")
        from handlers.missing_handlers import handle_get_enhanced_schedule_data
        return handle_get_enhanced_schedule_data(data, current_session)

    elif request_id == 73: # Bulk Shift Operation
        print("Received Bulk Shift Operation request")
        from handlers.missing_handlers import handle_bulk_shift_operation
        return handle_bulk_shift_operation(data, current_session)

    elif request_id == 86: # Get Board Status
        print("Received Get Board Status request")
        if not current_session:
            return {"request_id": request_id, "success": False, "error": "User session not found."}
        res = manager_schedule.handle_get_board(current_session)
        return {"request_id": request_id, "success": True, "data": res}

    elif request_id == 600: # Get Client Companies
        print("Received Get Client Companies request")
        from handlers.missing_handlers import handle_get_client_companies
        return handle_get_client_companies(data, current_session)

    elif request_id == 601: # Create Client Company
        print("Received Create Client Company request")
        from handlers.missing_handlers import handle_create_client_company
        return handle_create_client_company(data, current_session)

    elif request_id == 602: # Update Client Company
        print("Received Update Client Company request")
        from handlers.missing_handlers import handle_update_client_company
        return handle_update_client_company(data, current_session)

    elif request_id == 603: # Delete Client Company
        print("Received Delete Client Company request")
        from handlers.missing_handlers import handle_delete_client_company
        return handle_delete_client_company(data, current_session)

    elif request_id == 700: # Get Employee List
        print("Received Get Employee List request")
        from handlers.missing_handlers import handle_get_employee_list
        return handle_get_employee_list(data, current_session)

    elif request_id == 701: # Create Employee Account
        print("Received Create Employee Account request")
        from handlers.missing_handlers import handle_create_employee_account
        return handle_create_employee_account(data, current_session)

    elif request_id == 702: # Update Employee Certifications
        print("Received Update Employee Certifications request")
        from handlers.missing_handlers import handle_update_employee_certifications
        return handle_update_employee_certifications(data, current_session)

    elif request_id == 800: # Get Timesheet Summary
        print("Received Get Timesheet Summary request")
        from handlers.missing_handlers import handle_get_timesheet_summary
        return handle_get_timesheet_summary(data, current_session)

    elif request_id == 800: # Get Timesheet Summary
        print("Received Get Timesheet Summary request")
        from handlers.missing_handlers import handle_get_timesheet_summary
        return handle_get_timesheet_summary(data, current_session)

    elif request_id == 900: # Get Notifications
        print("Received Get Notifications request")
        from handlers.missing_handlers import handle_get_notifications
        return handle_get_notifications(data, current_session)

    elif request_id == 901: # Mark Notification Read
        print("Received Mark Notification Read request")
        from handlers.missing_handlers import handle_mark_notification_read
        return handle_mark_notification_read(data, current_session)

    elif request_id == 902: # Send Notification
        print("Received Send Notification request")
        from handlers.missing_handlers import handle_send_notification
        return handle_send_notification(data, current_session)

    elif request_id == 903: # Get Notification Settings
        print("Received Get Notification Settings request")
        from handlers.missing_handlers import handle_get_notification_settings
        return handle_get_notification_settings(data, current_session)

    elif request_id == 904: # Update Notification Settings
        print("Received Update Notification Settings request")
        from handlers.missing_handlers import handle_update_notification_settings
        return handle_update_notification_settings(data, current_session)

    elif request_id == 400: # Generate Report
        print("Received Generate Report request")
        from handlers.missing_handlers import handle_generate_report
        return handle_generate_report(data, current_session)

    elif request_id == 998: # Debug Info
        print("Received Debug Info request")
        from handlers.missing_handlers import handle_debug_info
        return handle_debug_info(data, current_session)

    elif request_id == 999: # System Status
        print("Received System Status request")
        from handlers.missing_handlers import handle_system_status
        return handle_system_status(data, current_session)

    elif request_id == 1000: # Health Check
        print("Received Health Check request")
        from handlers.missing_handlers import handle_health_check
        return handle_health_check(data, current_session)

    elif request_id == 1002: # Ping
        print("Received Ping request")
        from handlers.missing_handlers import handle_ping
        return handle_ping(data, current_session)

    elif request_id == 500: # Get User Settings
        print("Received Get User Settings request")
        from handlers.missing_handlers import handle_get_user_settings
        return handle_get_user_settings(data, current_session)

    elif request_id == 501: # Update User Settings
        print("Received Update User Settings request")
        from handlers.missing_handlers import handle_update_user_settings
        return handle_update_user_settings(data, current_session)

    elif request_id == 502: # Reset User Settings
        print("Received Reset User Settings request")
        from handlers.missing_handlers import handle_reset_user_settings
        return handle_reset_user_settings(data, current_session)

    # === TRASH BIN HANDLERS ===
    elif request_id == 701: # Get Deleted Items
        print("Received Get Deleted Items request")
        from handlers.trash_handlers import handle_get_deleted_items
        return handle_get_deleted_items(data, current_session)

    elif request_id == 702: # Restore Item
        print("Received Restore Item request")
        from handlers.trash_handlers import handle_restore_item
        return handle_restore_item(data, current_session)

    elif request_id == 703: # Bulk Restore Items
        print("Received Bulk Restore Items request")
        from handlers.trash_handlers import handle_bulk_restore_items
        return handle_bulk_restore_items(data, current_session)

    elif request_id == 704: # Permanent Delete Item
        print("Received Permanent Delete Item request")
        from handlers.trash_handlers import handle_permanent_delete_item
        return handle_permanent_delete_item(data, current_session)

    elif request_id == 705: # Soft Delete Job
        print("Received Soft Delete Job request")
        from handlers.trash_handlers import handle_soft_delete_job
        return handle_soft_delete_job(data, current_session)

    else:
        print("Unknown request ID:", request_id)
        return {"request_id": request_id, "success": False, "error": f"Unknown request ID: {request_id}"}


# Removed old websockets handler - using aiohttp WebSocket handler instead


async def handle_http_request(request):
    """Handle HTTP requests (health checks)"""
    if request.path in ['/', '/health']:
        return web.Response(
            text=json.dumps({
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": "holi-timesheets-backend"
            }),
            content_type='application/json'
        )
    else:
        return web.Response(text="Not Found", status=404)


async def handle_migration_request(request):
    """Handle database migration requests"""
    try:
        print("🔧 Running soft delete migration...")
        success = migrate_soft_delete_columns()

        if success:
            return web.Response(
                text=json.dumps({
                    "status": "success",
                    "message": "Soft delete columns migration completed successfully",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                content_type='application/json'
            )
        else:
            return web.Response(
                text=json.dumps({
                    "status": "error",
                    "message": "Migration failed",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                content_type='application/json',
                status=500
            )

    except Exception as e:
        print(f"❌ Migration error: {e}")
        return web.Response(
            text=json.dumps({
                "status": "error",
                "message": f"Migration failed: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }),
            content_type='application/json',
            status=500
        )


async def handle_jobs_migration_request(request):
    """Handle jobs table migration requests"""
    try:
        print("🔧 Running jobs soft delete migration...")
        success = migrate_jobs_soft_delete_columns()

        if success:
            return web.Response(
                text=json.dumps({
                    "status": "success",
                    "message": "Jobs soft delete columns migration completed successfully",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                content_type='application/json'
            )
        else:
            return web.Response(
                text=json.dumps({
                    "status": "error",
                    "message": "Jobs migration failed",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                content_type='application/json',
                status=500
            )

    except Exception as e:
        print(f"❌ Jobs migration error: {e}")
        return web.Response(
            text=json.dumps({
                "status": "error",
                "message": f"Jobs migration failed: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }),
            content_type='application/json',
            status=500
        )


async def handle_all_migration_request(request):
    """Handle comprehensive migration requests for all tables"""
    try:
        print("🔧 Running comprehensive soft delete migration...")
        success = migrate_all_soft_delete_columns()

        if success:
            return web.Response(
                text=json.dumps({
                    "status": "success",
                    "message": "Comprehensive soft delete columns migration completed successfully",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                content_type='application/json'
            )
        else:
            return web.Response(
                text=json.dumps({
                    "status": "error",
                    "message": "Comprehensive migration failed",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                content_type='application/json',
                status=500
            )

    except Exception as e:
        print(f"❌ Comprehensive migration error: {e}")
        return web.Response(
            text=json.dumps({
                "status": "error",
                "message": f"Comprehensive migration failed: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }),
            content_type='application/json',
            status=500
        )


async def handle_workplace_migration_request(request):
    """Handle workplace_id to manager_id migration for shiftBoards table"""
    try:
        print("🔧 Running workplace_id to manager_id migration...")

        from sqlalchemy import text
        from main import get_db_session

        with get_db_session() as session:
            # Check if manager_id column already exists
            def check_column_exists(table_name, column_name):
                try:
                    result = session.execute(text(f"""
                        SELECT COUNT(*)
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = DATABASE()
                        AND TABLE_NAME = '{table_name}'
                        AND COLUMN_NAME = '{column_name}'
                    """))
                    return result.fetchone()[0] > 0
                except Exception as e:
                    print(f"Error checking column {column_name} in {table_name}: {e}")
                    return False

            rows_updated = 0

            # Add manager_id column if it doesn't exist
            if not check_column_exists('shiftBoards', 'manager_id'):
                session.execute(text("ALTER TABLE shiftBoards ADD COLUMN manager_id INT NULL"))
                session.commit()
                print("✓ manager_id column added to shiftBoards")

            # Migrate data from workplaceID to manager_id
            result = session.execute(text("""
                UPDATE shiftBoards
                SET manager_id = workplaceID
                WHERE manager_id IS NULL AND workplaceID IS NOT NULL
            """))
            session.commit()
            rows_updated = result.rowcount
            print(f"✓ Migrated {rows_updated} records from workplaceID to manager_id")

            # Add foreign key constraint for manager_id
            try:
                session.execute(text("""
                    ALTER TABLE shiftBoards
                    ADD CONSTRAINT fk_shiftboards_manager_id
                    FOREIGN KEY (manager_id) REFERENCES users(id)
                """))
                session.commit()
                print("✓ Foreign key constraint added for manager_id")
            except Exception as e:
                if "Duplicate key name" in str(e) or "already exists" in str(e):
                    print("✓ Foreign key constraint already exists")
                else:
                    print(f"⚠️  Could not add foreign key constraint: {e}")

        return web.Response(
            text=json.dumps({
                "status": "success",
                "message": "Workplace ID migration completed successfully",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "rows_migrated": rows_updated
            }),
            content_type='application/json'
        )
    except Exception as e:
        print(f"❌ Workplace migration error: {e}")
        return web.Response(
            text=json.dumps({
                "status": "error",
                "message": f"Workplace migration failed: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }),
            content_type='application/json',
            status=500
        )


async def handle_websocket_request(request):
    """Handle WebSocket upgrade requests with improved async error handling"""
    from websocket.redis_websocket_manager import redis_websocket_manager

    # Create WebSocket response with heartbeat for connection health
    ws = web.WebSocketResponse(heartbeat=30, timeout=60)
    await ws.prepare(request)

    client_id = str(id(ws))  # Convert to string for consistency
    client_ip = request.remote if request.remote else "unknown"
    logger.info(f"New WebSocket client connected: {client_id} from {client_ip}")

    # Register connection with Redis manager
    try:
        await redis_websocket_manager.register_connection_async(ws, client_id, {
            'client_ip': client_ip,
            'connected_at': datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        logger.warning(f"Failed to register WebSocket connection in Redis: {e}")

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                try:
                    logger.debug(f"Received message from client {client_id}: {msg.data[:100]}...")
                    request_data = json.loads(msg.data)

                    # Heartbeat message handling
                    if request_data.get('type') == 'heartbeat':
                        try:
                            await redis_websocket_manager.update_heartbeat_async(client_id)
                            await ws.send_str(json.dumps({
                                'type': 'heartbeat_ack',
                                'timestamp': datetime.now(timezone.utc).isoformat()
                            }))
                            logger.debug(f"Processed heartbeat for WebSocket {client_id}")
                        except Exception as e:
                            logger.warning(f"Heartbeat processing failed for {client_id}: {e}")
                        continue

                    request_id = request_data.get('request_id')
                    data = request_data.get('data', {})

                    # Extract session authentication data from top level
                    session_id = request_data.get('session_id')
                    csrf_token = request_data.get('csrf_token')

                    logger.info(f"Processing request {request_id} from client {client_id}")
                    if session_id:
                        logger.debug(f"Session authentication provided for client {client_id}")

                    # Use the async handle_request function
                    try:
                        response = await handle_request(request_id, data, client_id, session_id, csrf_token)
                    except Exception as e:
                        logger.exception(f"Error in handle_request for client {client_id}: {str(e)}")
                        response = {
                            "request_id": request_id,
                            "success": False,
                            "error": f"Request processing error: {str(e)}"
                        }

                    # Ensure response has request_id for client matching
                    if 'request_id' not in response:
                        response['request_id'] = request_id

                    # Send response back to client with error handling
                    try:
                        response_json = json.dumps(response, default=str)
                        await ws.send_str(response_json)
                        logger.debug(f"Sent response to client {client_id} for request {request_id}: {response.get('success', 'unknown')}")
                    except Exception as e:
                        logger.error(f"Failed to send response to client {client_id}: {e}")

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON from client {client_id}: {e}")
                    try:
                        await ws.send_str(json.dumps({
                            "success": False,
                            "error": "Invalid JSON format"
                        }))
                    except Exception as send_error:
                        logger.error(f"Failed to send error response to client {client_id}: {send_error}")

                except Exception as e:
                    logger.exception(f"Error processing message from client {client_id}: {str(e)}")
                    try:
                        error_response = {
                            "request_id": request_data.get('request_id') if 'request_data' in locals() else None,
                            "success": False,
                            "error": f"Server error: {str(e)}"
                        }
                        await ws.send_str(json.dumps(error_response))
                    except Exception as send_error:
                        logger.error(f"Failed to send error response to client {client_id}: {send_error}")

            elif msg.type == web.WSMsgType.ERROR:
                logger.error(f"WebSocket error from client {client_id}: {ws.exception()}")
                break
            elif msg.type == web.WSMsgType.CLOSE:
                logger.info(f"WebSocket close message from client {client_id}")
                break

    except Exception as e:
        logger.exception(f"Unexpected error with WebSocket client {client_id}: {str(e)}")
    finally:
        # Clean up session and Redis connection
        try:
            if client_id in user_sessions:
                session = user_sessions[client_id]
                del user_sessions[client_id]
                logger.info(f"Cleaned up session for client {client_id}")

            # Unregister from Redis manager
            await redis_websocket_manager.unregister_connection_async(client_id)
            logger.info(f"WebSocket client {client_id} connection closed and cleaned up")
        except Exception as cleanup_error:
            logger.error(f"Error during cleanup for client {client_id}: {cleanup_error}")

    return ws


async def create_combined_app():
    """Create the combined HTTP/WebSocket application"""
    app = web.Application()

    # Configure CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })

    # Add HTTP routes
    app.router.add_get('/', handle_http_request)
    app.router.add_get('/health', handle_http_request)
    app.router.add_get('/migrate-soft-delete', handle_migration_request)
    app.router.add_get('/migrate-jobs-soft-delete', handle_jobs_migration_request)
    app.router.add_get('/migrate-all-soft-delete', handle_all_migration_request)
    app.router.add_get('/migrate-workplace-id', handle_workplace_migration_request)

    # Add WebSocket route
    app.router.add_get('/ws', handle_websocket_request)

    # Add CORS to all routes
    for route in list(app.router.routes()):
        cors.add(route)

    return app


async def start_combined_server():
    """Start the combined HTTP/WebSocket server"""
    port = int(os.getenv('PORT', 8080))  # Cloud Run default port
    host = os.getenv('HOST', '0.0.0.0')

    logger.info(f"🚀 Starting Holi backend server...")
    logger.info(f"📍 Host: {host}")
    logger.info(f"🔌 Port: {port}")
    logger.info(f"🗄️  Database initialized: {database_initialized}")

    try:
        app = await create_combined_app()
        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, host, port)
        await site.start()

        logger.info(f"✅ Combined HTTP/WebSocket server started on {host}:{port}")
        logger.info(f"🔍 Health check available at: http://{host}:{port}/health")
        logger.info(f"🔌 WebSocket endpoint available at: ws://{host}:{port}/ws")
        logger.info(f"🎯 Server is ready to accept connections!")

        # Keep the server running
        await asyncio.Future()  # Run forever

    except Exception as e:
        logger.exception(f"❌ Failed to start combined server: {str(e)}")
        logger.error(f"💥 Server startup failed with error: {type(e).__name__}")
        raise


if __name__ == "__main__":
    try:
        logger.info("🎬 Starting Holi backend application...")
        # Start Redis WebSocket heartbeat monitor in the background
        from websocket.redis_websocket_manager import redis_websocket_manager
        import asyncio
        loop = asyncio.get_event_loop()
        loop.create_task(redis_websocket_manager.start_heartbeat_monitor())
        asyncio.run(start_combined_server())
    except KeyboardInterrupt:
        logger.info("⏹️  Server stopped by user")
    except Exception as e:
        logger.exception(f"💥 Server crashed: {str(e)}")
        logger.error(f"🔥 Fatal error: {type(e).__name__}: {str(e)}")
        import sys
        sys.exit(1)
