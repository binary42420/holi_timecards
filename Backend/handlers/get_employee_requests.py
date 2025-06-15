import logging
from main import get_db_session
from db.controllers.userRequests_controller import UserRequestsController
from db.controllers.users_controller import UsersController

logger = logging.getLogger(__name__)

def handle_get_employee_requests(data, user_session):
    """Handle get employee requests with comprehensive error handling"""
    try:
        logger.info("Processing get employee requests")

        if user_session.can_access_manager_page():
            with get_db_session() as session:
                users_controller = UsersController(session)
                user_requests_controller = UserRequestsController(session)

                # For Hands on Labor: Get all active employees (no workplace restrictions)
                all_users = users_controller.get_all_entities()
                active_workers = [user for user in all_users if not user.isManager and user.isActive and user.isApproval]

                employees_requests = {}
                for worker in active_workers:
                    employees_requests[worker.name] = user_requests_controller.get_request_by_userid(worker.id)

                logger.info(f"Retrieved requests for {len(active_workers)} employees")
                return {"success": True, "data": employees_requests}
        else:
            error_message = "User does not have access to manager-specific pages."
            logger.warning(f"Access denied for user: {user_session.user_id}")
            return {"success": False, "error": error_message}

    except Exception as e:
        logger.error(f"Error in handle_get_employee_requests: {e}")
        return {
            "success": False,
            "error": f"Failed to get employee requests: {str(e)}"
        }
