from datetime import datetime
from main import create_session
from db.controllers.userRequests_controller import UserRequestsController
from db.controllers.shiftBoard_controller import ShiftBoardController
from user_session import UserSession


def handle_employee_shifts_request(data, user_session):
    user_id = user_session.get_id
    shifts_string = data['shiftsString']

    shifts_request_data = {"id": user_id, "modifyAt": datetime.now(), "requests": shifts_string}

    # Use proper database session management
    db_session = create_session()
    try:
        user_request_controller = UserRequestsController(db_session)
        user_request_controller.update_entity(user_id, shifts_request_data)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()


def handle_is_in_request_window(user_session: UserSession) -> bool:  # When the user opens the user request page
    """
    Checks if the current date is within the request window for the user.

    Args:
        user_session (UserSession): The user session containing user information.

    Returns:
        bool: True if the current date is within the request window, False otherwise.
    """
    # Use proper database session management
    db_session = create_session()
    try:
        # Create a controller for the shift board
        shift_board_controller = ShiftBoardController(db_session)

        # Get manager id by worker id
        workPlaces_controller = WorkPlacesController(db_session)
        workplace_id = workPlaces_controller.get_workplace_id_by_user_id(user_session.get_id)

        print("workplace_id: ", workplace_id)

        # Get the last shift board
        last_shift_board = shift_board_controller.get_last_shift_board(workplace_id)

        # Check if the current date is in the request window
        if last_shift_board and last_shift_board.requests_window_start <= datetime.now() <= last_shift_board.requests_window_end:
            return True

        return False
    except Exception as e:
        print(f"Error in handle_is_in_request_window: {e}")
        return False
    finally:
        db_session.close()

def handle_get_request_window_times(user_session: UserSession) -> dict:
    """
    Handles the request to get the start and end times of the request window.
    """
    request_id = 42
    if not user_session:
        return {"request_id": request_id, "success": False, "error": "User session not found."}

    # Use proper database session management
    db_session = create_session()
    try:
        shift_board_controller = ShiftBoardController(db_session)
        workPlaces_controller = WorkPlacesController(db_session)
        workplace_id = workPlaces_controller.get_workplace_id_by_user_id(user_session.get_id)

        if workplace_id is None:
            return {"request_id": request_id, "success": False, "error": "User not associated with a workplace."}

        last_shift_board = shift_board_controller.get_last_shift_board(workplace_id)

        return {
            "request_id": request_id,
            "success": True,
            "data": {
                "requests_window_start": last_shift_board.requests_window_start.isoformat() if last_shift_board and last_shift_board.requests_window_start else None,
                "requests_window_end": last_shift_board.requests_window_end.isoformat() if last_shift_board and last_shift_board.requests_window_end else None,
            }
        }
    except Exception as e:
        print(f"Error in handle_get_request_window_times: {e}")
        return {"request_id": request_id, "success": False, "error": f"An error occurred: {str(e)}"}
    finally:
        db_session.close()

