from sqlalchemy.exc import NoResultFound
from main import get_db_session
from db.services.shiftWorkers_service import ShiftWorkersService
from db.repositories.shiftWorkers_repository import ShiftWorkersRepository
from user_session import UserSession
from db.models import EmployeeType, User, ShiftWorker
from db.controllers.users_controller import UsersController
from db.controllers.shiftWorkers_controller import ShiftWorkersController


def handle_get_crew_chief_shifts(user_session: UserSession):
    """
    Handles the request for a Crew Chief to view their supervised shifts.
    """
    if not user_session:
        return {"success": False, "error": "User session not found."}

    user_id = user_session.get_id

    # Verify user is a crew chief in general (optional, could rely on role_assigned in ShiftWorker)
    # with get_db_session() as session:
    #     user_controller = UsersController(session)
    #     user = user_controller.get_entity(user_id)
    #     if not user or user.employee_type != EmployeeType.CREW_CHIEF:
    #         return {"success": False, "error": "User is not authorized as a Crew Chief."}
    # The above check might be too restrictive if a user can be a crew chief for some shifts
    # and a regular employee for others. The primary check is role_assigned in ShiftWorker.

    with get_db_session() as session:
        shift_workers_repository = ShiftWorkersRepository(session)
        shift_workers_service = ShiftWorkersService(repository=shift_workers_repository)
    
    try:
        shifts_details = shift_workers_service.get_supervised_shifts_details(user_id)
        return {"request_id": 100, "success": True, "data": shifts_details}
    except Exception as e:
        print(f"Error in handle_get_crew_chief_shifts: {e}")
        return {"request_id": 100, "success": False, "error": str(e)}


def handle_get_crew_members_for_shift(request_data: dict, user_session: UserSession) -> dict:
    """
    Handles the request for a Crew Chief to get details of crew members assigned to a specific shift.
    """
    if not user_session:
        return {"request_id": 101, "success": False, "error": "User session not found."}

    shift_id = request_data.get('shift_id')
    if shift_id is None:
        return {"request_id": 101, "success": False, "error": "shift_id is required."}

    try:
        with get_db_session() as session:
            shift_workers_controller = ShiftWorkersController(session)
            users_controller = UsersController(session)

        shift_worker_entities = shift_workers_controller.get_shift_workers_by_shift_id(str(shift_id))
        crew_members_details = []

        for sw_entity in shift_worker_entities:
            try:
                user = users_controller.get_entity(str(sw_entity.userID))
                clock_in_time = sw_entity.clock_in_time.isoformat() if sw_entity.clock_in_time else None
                clock_out_time = sw_entity.clock_out_time.isoformat() if sw_entity.clock_out_time else None
                times_submitted_at = sw_entity.times_submitted_at.isoformat() if sw_entity.times_submitted_at else None

                crew_members_details.append({
                    "user_id": sw_entity.userID,
                    "name": user.name,
                    "role_assigned": sw_entity.role_assigned.value,
                    "clock_in_time": clock_in_time,
                    "clock_out_time": clock_out_time,
                    "times_submitted_at": times_submitted_at
                })
            except NoResultFound:
                # Handle case where user might have been deleted but shiftWorker entry remains
                print(f"Warning: User with ID {sw_entity.userID} not found for shift {shift_id}.")
                continue # Skip this entry and continue with others

        return {"request_id": 101, "success": True, "data": crew_members_details}
    except Exception as e:
        print(f"Error in handle_get_crew_members_for_shift: {e}")
        return {"request_id": 101, "success": False, "error": str(e)}


def handle_submit_shift_times(request_data: dict, user_session: UserSession) -> dict:
    """
    Handles the request for a Crew Chief to submit clock-in/out times for crew members on a shift.
    """
    if not user_session:
        return {"request_id": 102, "success": False, "error": "User session not found."}

    shift_id = request_data.get('shift_id')
    worker_times = request_data.get('worker_times')

    if shift_id is None or not isinstance(worker_times, list):
        return {"request_id": 102, "success": False, "error": "shift_id and worker_times list are required."}

    try:
        with get_db_session() as session:
            shift_workers_controller = ShiftWorkersController(session)

            all_successful = True
            errors = []

            for item in worker_times:
                user_id = item.get('user_id')
                role_assigned = item.get('role_assigned')
                clock_in_time = item.get('clock_in_time')
                clock_out_time = item.get('clock_out_time')

                if user_id is None or role_assigned is None:
                    all_successful = False
                    errors.append(f"Missing user_id or role_assigned for an item in worker_times.")
                    continue

                try:
                    updated_sw = shift_workers_controller.submit_times_for_worker_on_shift(
                        shift_id=int(shift_id),
                        user_id=int(user_id),
                        role_assigned_str=role_assigned,
                        clock_in_time_str=clock_in_time,
                        clock_out_time_str=clock_out_time
                    )
                    if updated_sw is None:
                        all_successful = False
                        errors.append(f"Failed to update times for user {user_id} on shift {shift_id}.")
                except Exception as update_e:
                    all_successful = False
                    errors.append(f"Error updating times for user {user_id} on shift {shift_id}: {str(update_e)}")

            if all_successful:
                return {"request_id": 102, "success": True, "message": "All worker times submitted successfully."}
            else:
                return {"request_id": 102, "success": False, "error": "Some worker times failed to submit.", "details": errors}

    except Exception as e:
        print(f"Error in handle_submit_shift_times: {e}")
        return {"request_id": 102, "success": False, "error": str(e)}
