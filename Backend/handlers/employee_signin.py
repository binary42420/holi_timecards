import logging
from datetime import datetime
from main import get_db_session
from db.controllers.userRequests_controller import UserRequestsController
from db.controllers.users_controller import UsersController
from handlers.login import handle_login

logger = logging.getLogger(__name__)

def handle_employee_signin(data):
    """Handle employee signin for Hands on Labor single company system"""
    try:
        logger.info("Processing employee signin request")

        # Get the relevant data from the packet
        username = data['username']
        password = data['password']
        name = data['employeeName']
        # Note: businessName is ignored since all employees work for Hands on Labor

        # Access the relevant db controllers
        with get_db_session() as session:
            user_controller = UsersController(session)
            user_requests_controller = UserRequestsController(session)

            # Insert data into Users table for Hands on Labor employee
            user_data = {
                'username': username,
                'password': password,
                'name': name,
                'isManager': False,
                'isActive': True,
                'isApproval': False,  # Requires manager approval
                'client_company_id': None,  # Agency employee, not client
                'employee_type': None,  # Will be set later by manager
                'google_id': None
            }
            new_user = user_controller.create_entity(user_data)

            if not new_user:
                logger.error(f"Failed to create user: {username}")
                return {"success": False, "message": "Failed to create user account"}

            # Insert data into userRequests table
            user_request_data = {
                'id': new_user.id,
                'modifyAt': datetime.now(),
                'requests': '...'
            }
            user_requests_controller.create_entity(user_request_data)

            login_data = {"username": data["username"], "password": data["password"]}

            # Send the username and password to the login function to create a user session
            _, user_session = handle_login(login_data)

            logger.info(f"Employee signin successful for Hands on Labor employee: {username}")
            return user_session

    except Exception as e:
        logger.error(f"Error in handle_employee_signin: {e}")
        return {
            "success": False,
            "error": f"Employee signin failed: {str(e)}"
        }

