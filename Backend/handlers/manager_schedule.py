from datetime import timedelta, datetime
from main import get_db_session
from db.controllers.shiftWorkers_controller import ShiftWorkersController
from db.controllers.jobs_controller import JobsController
from db.controllers.client_companies_controller import ClientCompaniesController
from db.models import ShiftBoard
from user_session import UserSession
from db.controllers.shiftBoard_controller import ShiftBoardController
from db.controllers.userRequests_controller import UserRequestsController
from db.controllers.users_controller import UsersController
from db.controllers.shifts_controller import ShiftsController, convert_shifts_for_client
from config.constants import next_sunday


def get_or_create_default_job(user_session):
    """
    Gets or creates a default job for legacy shift creation.
    For Hands on Labor, we need a default job to link shifts to.
    """
    try:
        with get_db_session() as session:
            jobs_controller = JobsController(session)
            client_companies_controller = ClientCompaniesController(session)

            # Try to get existing default job
            all_jobs = jobs_controller.get_all_active_jobs()
            if all_jobs:
                # Return the first active job as default
                return all_jobs[0]['id']

            # If no jobs exist, create a default one
            # First, get or create a default client company
            all_companies = client_companies_controller.get_all_entities()
            if not all_companies:
                # Create a default client company for Hands on Labor
                default_company_data = {
                    "name": "Default Client",
                    "contact_email": "default@handsonlabor.com",
                    "contact_phone": "555-0000",
                    "address": "San Diego, CA",
                    "is_active": True
                }
                default_company = client_companies_controller.create_entity(default_company_data)
                client_company_id = default_company.id
            else:
                client_company_id = all_companies[0].id

            # Create default job
            default_job_data = {
                "name": "General Labor - Default",
                "client_company_id": client_company_id,
                "venue_name": "Various Locations",
                "venue_address": "San Diego, CA",
                "venue_contact_info": "Contact Hands on Labor for details",
                "description": "Default job for general labor assignments",
                "created_by": user_session.get_id,
                "is_active": True
            }

            created_job = jobs_controller.create_job(default_job_data)
            return created_job['id']

    except Exception as e:
        print(f"Error creating default job: {e}")
        # If we can't create a default job, we can't create shifts
        raise Exception("Cannot create shifts without a valid job_id. Please create a job first.")


def handle_create_new_board(user_session: UserSession):
    """Create a new shift board with proper database session management."""
    with get_db_session() as session:
        # Create a controller for the shift board
        shift_board_controller = ShiftBoardController(session)

        # In case the manager wants to create his first board
        try:
            shift_board_controller.get_last_shift_board(user_session.get_id)
        except IndexError:
            # Create a new shift board
            board = shift_board_controller.create_shift_board(
                {"weekStartDate": next_sunday, "workplaceID": user_session.get_id})
            return board

        # Get the last shift board
        last_board = shift_board_controller.get_last_shift_board(user_session.get_id)

        # Create a new shift board
        new_week_start_date = last_board.weekStartDate + timedelta(days=7)  # A week after the last shift board
        new_board = shift_board_controller.create_shift_board(
            {"weekStartDate": new_week_start_date, "workplaceID": user_session.get_id})

        # Return the new shift board
        return new_board


def handle_get_board(user_session: UserSession) -> dict:
    """
    Get board status for the manager schedule.
    For Hands on Labor, return a simple board status.
    """
    try:
        if not user_session or not user_session.can_access_manager_page():
            return {"request_id": 86, "success": False, "error": "Unauthorized access."}

        # Return default board status for Hands on Labor
        board_status = {
            "is_published": False,
            "content": {},
            "week_start_date": next_sunday.isoformat()
        }
        return board_status
    except Exception as e:
        print(f"Error in handle_get_board: {e}")
        return {"request_id": 86, "success": False, "error": "Internal server error."}


def handle_get_start_date(user_session: UserSession):
    """
    Get the start date for the schedule (next Sunday).
    For Hands on Labor, return the next Sunday as the start of the week.
    """
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": 97, "success": False, "error": "Unauthorized access."}

    # Return next Sunday as the start date
    return next_sunday


def handle_save_board(data, user_session: UserSession) -> ShiftBoard:
    # Get the week_start_date from the data
    week_start_date = data["week_start_date"]  # TODO: Depending on the client!

    # Extract the content from the data
    content = data["content"]  # TODO: Depending on the client!

    # Update the shift board


    with get_db_session() as session:


        shift_board_controller = ShiftBoardController(session)
    updated_shift_board = shift_board_controller.update_shift_board(week_start_date, user_session.get_id, content)

    # Return the updated shift board
    return updated_shift_board


def handle_reset_board(user_session: UserSession) -> ShiftBoard:
    # Get the last shift board (Assuming it is the last shift board, the others are published)
    with get_db_session() as session:
        shift_board_controller = ShiftBoardController(session)
    last_board = shift_board_controller.get_last_shift_board(user_session.get_id)

    # Update the shift board with the default content
    updated_board = shift_board_controller.update_shift_board(last_board.weekStartDate, user_session.get_id,
                                                              {"content": {}})

    # Return the updated shift board
    return updated_board


def handle_publish_board(user_session: UserSession) -> bool:
    # Publish the shift board (Assuming it is the last shift board, the others are published)
    with get_db_session() as session:
        shift_board_controller = ShiftBoardController(session)
    shift_board_controller.publish_shift_board(next_sunday, user_session.get_id)

    # Return True if the shift board is published
    return shift_board_controller.get_last_shift_board(user_session.get_id).is_published


def handle_unpublish_board(user_session: UserSession) -> bool:
    # Unpublish the shift board (Assuming it is the last shift board, the others are published)
    with get_db_session() as session:
        shift_board_controller = ShiftBoardController(session)
    shift_board_controller.unpublish_shift_board(next_sunday, user_session.get_id)

    # Return True if the shift board is unpublished
    return not shift_board_controller.get_last_shift_board(user_session.get_id).is_published


def handle_get_board_content(user_session: UserSession) -> dict:
    # Get the last shift board (Assuming it is the last shift board, the others are published)
    with get_db_session() as session:
        shift_board_controller = ShiftBoardController(session)
    last_board = shift_board_controller.get_last_shift_board(user_session.get_id)

    # Return the content of the shift board
    return last_board.content


def schedule_worker_to_shift(shift_id, worker_id) -> bool:
    # Assume the data is a dictionary containing the worker's ID and the shift's ID
    shift_workers_data = {
        "shiftID": shift_id,
        "userID": worker_id
    }

    # Schedule the worker to the shift
    with get_db_session() as session:

        shift_workers_controller = ShiftWorkersController(session)
    shift_workers_controller.create_entity(shift_workers_data)

    # Return True if the worker is scheduled to the shift
    return True


def unschedule_worker_from_shift(shift_id, worker_id) -> bool:
    # Unschedule the worker from the shift
    with get_db_session() as session:

        shift_workers_controller = ShiftWorkersController(session)
    shift_workers_controller.delete_entity_shift_worker(shift_id, worker_id)

    # Return True if the worker is unscheduled from the shift
    return True


def handle_schedules(user_session, data: dict) -> bool:
    print("user_session: ", user_session.get_id if user_session else "None")
    print("data: ", data)
    # Been called from the client every time a worker is scheduled or unscheduled from a shift

    # The data is a dictionary of worker's name and shift's day and part
    worker_name = data["worker_name"]["name"]
    shift_day = data["day"]
    shift_part = data["part"]

    print("worker_name: ", worker_name)
    print("shift_day: ", shift_day)
    print("shift_part: ", shift_part)

    # Get the worker's ID - For Hands on Labor, search all active employees
    with get_db_session() as session:

        users_controller = UsersController(session)
    all_users = users_controller.get_all_entities()
    worker = None
    for user in all_users:
        if user.name == worker_name and not user.isManager and user.isActive and user.isApproval:
            worker = user
            break

    if not worker:
        print(f"Worker '{worker_name}' not found")
        return False

    # Create shift_date based on next_sunday and shift_day (sunday, monday, etc.)
    shift_date = next_sunday + timedelta(days=convert_day_name_to_number(shift_day))

    # Get the shift's ID - For Hands on Labor, look for shifts by date and part only
    with get_db_session() as session:

        shift_controller = ShiftsController(session)
    # Since we don't have workplace concept, we need to find shifts by date and part
    # This will require updating the shifts controller method or using a different approach
    shift = shift_controller.get_shift_by_date_and_part(shift_date, shift_part)

    if shift is None:
        # If the shift does not exist, create it with proper job_id
        try:
            # Get or create default job using the provided user_session
            default_job_id = get_or_create_default_job(user_session)

            # Define shift times based on shift_part
            shift_times = {
                "morning": (8, 0, 12, 0),    # 8:00 AM - 12:00 PM
                "noon": (12, 0, 17, 0),      # 12:00 PM - 5:00 PM
                "evening": (17, 0, 22, 0)    # 5:00 PM - 10:00 PM
            }

            start_hour, start_min, end_hour, end_min = shift_times.get(shift_part.lower(), (8, 0, 17, 0))

            # Create datetime objects for shift start and end
            shift_start = datetime.combine(shift_date.date(), datetime.min.time().replace(hour=start_hour, minute=start_min))
            shift_end = datetime.combine(shift_date.date(), datetime.min.time().replace(hour=end_hour, minute=end_min))

            # Create shift with new schema
            shift_data = {
                "job_id": default_job_id,
                "shift_start_datetime": shift_start,
                "shift_end_datetime": shift_end,
                "required_employee_counts": {"stagehand": 1, "crew_chief": 0, "forklift_operator": 0, "truck_driver": 0},
                "shift_description": f"{shift_part} shift",
                # Legacy fields for backward compatibility
                "shiftDate": shift_date.date(),
                "shiftPart": shift_part
            }

            shift = shift_controller.create_entity(shift_data)
            print(f"Created new shift: {shift_part} on {shift_date.date()}")

        except Exception as e:
            print(f"Error creating shift: {e}")
            return False

    print("To schedule worker to shift:", shift.id, worker.id, data["type"])

    if data["type"] == "addShift":
        # Schedule the worker to the shift
        return schedule_worker_to_shift(shift.id, worker.id)

    elif data["type"] == "removeShift":
        # Unschedule the worker from the shift
        return unschedule_worker_from_shift(shift.id, worker.id)

    else:
        raise ValueError("Unknown type")


def convert_day_name_to_number(day_name: str) -> int:
    # Convert the day name to a number
    day_name_to_number = {
        "sunday": 0,
        "monday": 1,
        "tuesday": 2,
        "wednesday": 3,
        "thursday": 4,
        "friday": 5,
        "saturday": 6
    }
    return day_name_to_number[day_name]


def watch_workers_requests(user_session: UserSession):
    # For Hands on Labor: Get all active employees (no workplace restrictions)
    with get_db_session() as session:

        users_controller = UsersController(session)
    all_users = users_controller.get_all_entities()

    # Get only workers where worker.isApproval is True and not managers
    workers = [user for user in all_users if not user.isManager and user.isActive and user.isApproval]

    # Extract the IDs and names of the workers
    workers_info = [(worker.id, worker.name) for worker in workers]

    # Get all requests from the workers
    with get_db_session() as session:

        user_requests_controller = UserRequestsController(session)

    # Get the start and end datetimes for the requests window
    with get_db_session() as session:

        shift_board_controller = ShiftBoardController(session)
    relevant_shift_board = shift_board_controller.get_last_shift_board(user_session.get_id)
    requests_window_start = relevant_shift_board.requests_window_start
    requests_window_end = relevant_shift_board.requests_window_end

    combined_list = [None] * len(workers_info)
    with get_db_session() as session:

        user_controller = UsersController(session)

    for i, (worker_id, name) in enumerate(workers_info):
            combined_list[i] = {"name": name,
                                "request_content": user_requests_controller.get_request_by_userid(worker_id)}

    # Return the combined list
    return combined_list


def open_requests_windows(workplace_id, data: dict) -> bool:
    # Extract the start and end datetimes for the requests window
    requests_window_start = data["requests_window_start"]
    requests_window_end = data["requests_window_end"]

    # Convert the datetimes to datetime objects
    requests_window_start = datetime.strptime(requests_window_start, "%Y-%m-%dT%H:%M:%S.%fZ")
    requests_window_end = datetime.strptime(requests_window_end, "%Y-%m-%dT%H:%M:%S.%fZ")

    updated_data = {"requests_window_start": requests_window_start, "requests_window_end": requests_window_end}

    # Update the shift board with the new requests window
    with get_db_session() as session:

        shift_board_controller = ShiftBoardController(session)
    shift_board_controller.update_shift_board(next_sunday, workplace_id, updated_data)

    # Return True if the requests window is open
    return True


def get_last_shift_board_window_times(workplace_id):
    with get_db_session() as session:

        shift_board_controller = ShiftBoardController(session)
    last_board = shift_board_controller.get_last_shift_board(workplace_id)
    print("Open requests window times: ", last_board.requests_window_start, last_board.requests_window_end)
    return last_board.requests_window_start, last_board.requests_window_end


def handle_get_preferences(user_session: UserSession) -> dict:
    """
    Get schedule preferences for the manager.
    For Hands on Labor, return default preferences since there's only one company.
    """
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": 95, "success": False, "error": "Unauthorized access."}

    # Return default preferences for Hands on Labor
    default_preferences = {
        "number_of_shifts_per_day": 3,  # morning, afternoon, evening
        "closed_days": []  # No closed days by default
    }
    return default_preferences


def handle_save_preferences(workplace_id, data: dict) -> bool:
    # Extract the preferences from the data
    number_of_shifts_per_day = data["number_of_shifts_per_day"]
    closed_days = data["closed_days"]

    # Create a dictionary with the preferences
    new_preferences = {
        "number_of_shifts_per_day": number_of_shifts_per_day,
        "closed_days": closed_days
    }

    print("new_preferences: ", new_preferences)

    # Update the shift board with the new preferences
    with get_db_session() as session:

        shift_board_controller = ShiftBoardController(session)
    shift_board_controller.update_shift_board(next_sunday, workplace_id, {"preferences": new_preferences})

    # Return True if the preferences are saved
    return True


def get_all_workers_names_by_workplace_id(user_session):
    # For Hands on Labor: Get all active employees (no workplace restrictions)
    with get_db_session() as session:

        users_controller = UsersController(session)
    all_users = users_controller.get_all_entities()

    # Get only workers where worker.isApproval is True and not managers
    workers = [user for user in all_users if not user.isManager and user.isActive and user.isApproval]

    # Extract the names of the workers
    workers_names = [worker.name for worker in workers]

    # Return the names of the workers
    return workers_names


def handle_get_assigned_shifts(user_session, data):
    print("data: ", data)
    # data represents start and end dates
    start_date_str = data["start_date"]

    print("start_date_str: ", start_date_str)

    # Convert the start date to a datetime object
    start_date = datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Get the end date, a week after the start date
    end_date = start_date + timedelta(days=7)

    # Create an array where each element is a dictionary with the worker's name and the shifts he is assigned to
    assigned_shifts = []

    # For Hands on Labor: Get all active employees (no workplace restrictions)
    with get_db_session() as session:

        users_controller = UsersController(session)
    all_users = users_controller.get_all_entities()
    workers = [user for user in all_users if not user.isManager and user.isActive and user.isApproval]

    # Iterate over the workers
    for worker in workers:
        # Get all shifts assigned to the worker
        with get_db_session() as session:

            shifts_controller = ShiftsController(session)
        shifts = shifts_controller.get_all_shifts_between_dates_for_given_worker(worker.id, start_date, end_date)

        # Convert the shifts to a format that the client can understand
        converted_shifts = convert_shifts_for_client(shifts, db)

        # Add the worker's name and the shifts he is assigned to the array
        assigned_shifts.append({"name": worker.name, "shifts": converted_shifts})

    # Return the array
    print("assigned_shifts: ", assigned_shifts)
    return assigned_shifts


def get_all_approved_workers_details(user_session: UserSession):
    """
    Retrieves details (id, name, employee_type) of all active and approved workers
    for Hands on Labor.
    """
    if not user_session or not user_session.can_access_manager_page():
        print("Unauthorized access attempt in get_all_approved_workers_details")
        return []

    with get_db_session() as session:
        users_controller = UsersController(session)
        all_users = users_controller.get_all_entities()

    # For Hands on Labor: Get all active employees
    approved_workers_details = []
    for user in all_users:
        if not user.isManager and user.isActive and user.isApproval:
            approved_workers_details.append({
                "id": user.id,
                "name": user.name,
                "employee_type": user.employee_type.value if user.employee_type else None
            })
    return approved_workers_details

def handle_get_all_approved_worker_details(user_session: UserSession):
    """
    Handler for request ID 94.
    """
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": 94, "success": False, "error": "Unauthorized access."}
    
    details = get_all_approved_workers_details(user_session)
    return {"request_id": 94, "success": True, "data": details}
