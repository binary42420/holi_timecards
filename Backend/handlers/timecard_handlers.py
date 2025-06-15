"""
Handlers for shift timecard management functionality.
Includes clock in/out, absence marking, notes, and timesheet generation.
"""

from datetime import datetime
from main import get_db_session
from user_session import UserSession
from db.controllers.shiftWorkers_controller import ShiftWorkersController
from db.controllers.shifts_controller import ShiftsController
from db.controllers.users_controller import UsersController

def handle_get_shift_timecard(data: dict, user_session: UserSession):
    """
    Get the timecard for a specific shift with all assigned workers.
    Request ID: 240
    """
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": 240, "success": False, "error": "Manager access required."}

    shift_id = data.get("shift_id")
    if not shift_id:
        return {"request_id": 240, "success": False, "error": "shift_id is required."}

    try:
        with get_db_session() as session:
            shift_workers_controller = ShiftWorkersController(session)
            shifts_controller = ShiftsController(session)
            users_controller = UsersController(session)

            # Get shift details
            shift = shifts_controller.get_shift_by_id(shift_id)
            if not shift:
                return {"request_id": 240, "success": False, "error": "Shift not found."}

            # Get all workers assigned to this shift
            shift_workers = shift_workers_controller.get_workers_by_shift_id(shift_id)

            # Format timecard data
            timecard_data = []
            for sw in shift_workers:
                # Get user details
                user = users_controller.get_entity(sw.userID)

                timecard_entry = {
                    "user_id": sw.userID,
                    "user_name": user.name if user else "Unknown",
                    "role_assigned": sw.role_assigned.value if sw.role_assigned else None,
                    "current_status": getattr(sw, 'current_status', 'not_started'),
                    "last_action_time": getattr(sw, 'last_action_time').isoformat() if getattr(sw, 'last_action_time', None) else None,
                    "is_absent": getattr(sw, 'is_absent', False),
                    "shift_notes": getattr(sw, 'shift_notes', ''),
                    "time_pairs": sw.get_time_pairs(),
                    "total_hours_worked": sw.total_hours_worked,
                    "is_approved": sw.is_approved
                }
                timecard_data.append(timecard_entry)

            return {
                "request_id": 240,
                "success": True,
                "data": {
                    "shift_id": shift_id,
                    "shift_info": {
                        "shift_start_datetime": shift.shift_start_datetime.isoformat() if shift.shift_start_datetime else None,
                        "shift_end_datetime": shift.shift_end_datetime.isoformat() if shift.shift_end_datetime else None,
                        "shift_description": getattr(shift, 'shift_description', ''),
                    },
                    "workers": timecard_data
                }
            }
        
    except Exception as e:
        print(f"Error in handle_get_shift_timecard: {e}")
        return {"request_id": 240, "success": False, "error": str(e)}

def handle_clock_in_out_worker(data: dict, user_session: UserSession):
    """
    Clock a worker in or out of a shift.
    Request ID: 241
    """
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": 241, "success": False, "error": "Manager access required."}

    shift_id = data.get("shift_id")
    user_id = data.get("user_id")
    action = data.get("action")  # "clock_in" or "clock_out"

    if not all([shift_id, user_id, action]):
        return {"request_id": 241, "success": False, "error": "shift_id, user_id, and action are required."}

    if action not in ["clock_in", "clock_out"]:
        return {"request_id": 241, "success": False, "error": "action must be 'clock_in' or 'clock_out'."}

    try:
        with get_db_session() as db:
            shift_workers_controller = ShiftWorkersController(db)
            current_time = datetime.now()

            # Get the shift worker record
            shift_worker = shift_workers_controller.get_shift_worker_for_timecard(shift_id, user_id)
            if not shift_worker:
                return {"request_id": 241, "success": False, "error": "Worker not assigned to this shift."}

            # Update clock times and status
            result = shift_workers_controller.update_clock_time(
                shift_id, user_id, action, current_time, user_session.get_id
            )

            if result:
                return {"request_id": 241, "success": True, "data": {"action": action, "time": current_time.isoformat()}}
            else:
                return {"request_id": 241, "success": False, "error": "Failed to update clock time."}
        
    except Exception as e:
        print(f"Error in handle_clock_in_out_worker: {e}")
        return {"request_id": 241, "success": False, "error": str(e)}

def handle_mark_worker_absent(data: dict, user_session: UserSession):
    """
    Mark a worker as absent for a shift.
    Request ID: 242
    """
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": 242, "success": False, "error": "Manager access required."}

    shift_id = data.get("shift_id")
    user_id = data.get("user_id")

    if not all([shift_id, user_id]):
        return {"request_id": 242, "success": False, "error": "shift_id and user_id are required."}

    try:
        with get_db_session() as db:
            shift_workers_controller = ShiftWorkersController(db)

            result = shift_workers_controller.mark_worker_absent(
                shift_id, user_id, user_session.get_id
            )

            if result:
                return {"request_id": 242, "success": True, "data": {"marked_absent": True}}
            else:
                return {"request_id": 242, "success": False, "error": "Failed to mark worker absent."}
        
    except Exception as e:
        print(f"Error in handle_mark_worker_absent: {e}")
        return {"request_id": 242, "success": False, "error": str(e)}

def handle_update_worker_notes(data: dict, user_session: UserSession):
    """
    Update notes for a worker on a specific shift.
    Request ID: 243
    """
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": 243, "success": False, "error": "Manager access required."}

    shift_id = data.get("shift_id")
    user_id = data.get("user_id")
    notes = data.get("notes", "")

    if not all([shift_id, user_id]):
        return {"request_id": 243, "success": False, "error": "shift_id and user_id are required."}

    try:
        with get_db_session() as db:
            shift_workers_controller = ShiftWorkersController(db)

            result = shift_workers_controller.update_worker_notes(
                shift_id, user_id, notes
            )

            if result:
                return {"request_id": 243, "success": True, "data": {"notes_updated": True}}
            else:
                return {"request_id": 243, "success": False, "error": "Failed to update worker notes."}
        
    except Exception as e:
        print(f"Error in handle_update_worker_notes: {e}")
        return {"request_id": 243, "success": False, "error": str(e)}

def handle_end_shift_clock_out_all(data: dict, user_session: UserSession):
    """
    End shift by clocking out all workers and generating draft timesheet.
    Request ID: 244
    """
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": 244, "success": False, "error": "Manager access required."}

    shift_id = data.get("shift_id")
    if not shift_id:
        return {"request_id": 244, "success": False, "error": "shift_id is required."}

    try:
        with get_db_session() as db:
            shift_workers_controller = ShiftWorkersController(db)
            current_time = datetime.now()

            # Clock out all workers still clocked in
            clocked_out_workers = shift_workers_controller.clock_out_all_workers(
                shift_id, current_time, user_session.get_id
            )

            # Generate draft timesheet
            timesheet = shift_workers_controller.generate_shift_timesheet(shift_id)

            return {
                "request_id": 244,
                "success": True,
                "data": {
                    "shift_ended": True,
                    "clocked_out_workers": clocked_out_workers,
                    "draft_timesheet": timesheet
                }
            }
        
    except Exception as e:
        print(f"Error in handle_end_shift_clock_out_all: {e}")
        return {"request_id": 244, "success": False, "error": str(e)}
