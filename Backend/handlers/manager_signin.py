from main import get_db_session
from db.controllers.shiftBoard_controller import ShiftBoardController
from db.controllers.users_controller import UsersController
from handlers.login import handle_login
from config.constants import next_sunday
from handlers.auth.authentication import BackendAuthenticationUser


def handle_manager_signin(data):
    """
    Handles the manager sign-up process by creating a new user using the UsersController.

    Parameters:
        data (dict): A dictionary containing user data for sign-up.
            Example: {'username': 'manager1', 'password': 'password123', 'name': 'Place Name'}

    Returns:
        dict: A dictionary containing the response to be sent back to the client.
            Example: {'success': True, 'message': 'Manager sign-up successful'}
    """
    try:
        print("IN")
        # Initialize the users controller
        with get_db_session() as session:

            user_controller = UsersController(session)

        # Insert the new manager into the database
        print(data)
        user_controller.create_entity(data)

        # Optionally, you can send a success response back to the client
        return {'success': True, 'message': 'Manager sign-up successful'}
    except Exception as e:
        # Handle any errors that occur during the sign-up process
        error_message = 'Error during manager sign-up: ' + str(e)
        print(error_message)
        return {'success': False, 'message': error_message}
