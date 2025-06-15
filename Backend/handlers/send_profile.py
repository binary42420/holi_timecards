import logging
from main import get_db_session
from db.controllers.shifts_controller import ShiftsController, convert_shifts_for_client
from db.controllers.users_controller import UsersController
from user_session import UserSession

logger = logging.getLogger(__name__)

def handle_send_profile(user_session: UserSession) -> dict:
    """
    Handles the request to send the user's profile data to the client.

    Returns:
        dict: A dictionary containing the user's profile data.
              The structure of the dictionary depends on the user's role (manager or worker).
    Raises:
        Exception: If the user session is not found.
    """
    try:
        logger.info("Processing send profile request")

        # Retrieve the user ID from the user session
        user_id = user_session.get_id

        with get_db_session() as session:
            # Initialize the controllers with the session
            users_controller = UsersController(session)
            shifts_controller = ShiftsController(session)

            # Create a dictionary to hold the returned data by key-value pairs
            returned_data = {
                "user_id": user_id,
                "username": users_controller.get_username_by_id(user_id)
            }

            # Retrieve the user's profile
            if user_session.can_access_manager_page():
                # Add manager-specific data to the dictionary
                returned_data["workplace_name"] = "Hands on Labor"  # Single company name
                future_shifts = shifts_controller.get_future_shifts_for_workplace(user_id)  # user_id of manager = workplace_id
                future_shifts_for_client = convert_shifts_for_client(future_shifts, session)
                returned_data["future_shifts"] = future_shifts_for_client
            else:
                # Add worker-specific data to the dictionary
                returned_data["name"] = users_controller.get_name_by_id(user_id)
                returned_data["workplace_name"] = "Hands on Labor"  # Single company name
                future_shifts = shifts_controller.get_future_shifts_for_user(user_id)
                future_shifts_for_client = convert_shifts_for_client(future_shifts, session, is_manager=False)
                returned_data["future_shifts"] = future_shifts_for_client

            # Return the dictionary
            logger.info(f"Profile data retrieved for user: {user_id}")
            return returned_data

    except Exception as e:
        logger.error(f"Error in handle_send_profile: {e}")
        return {
            "success": False,
            "error": f"Failed to get profile data: {str(e)}"
        }
