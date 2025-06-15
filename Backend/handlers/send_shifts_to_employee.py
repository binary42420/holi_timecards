import logging
from config.constants import db
from main import get_db_session
from db.controllers.shifts_controller import ShiftsController, convert_shifts_for_client

logger = logging.getLogger(__name__)

def handle_send_shifts(user_session):
    """Handle send shifts to employee with comprehensive error handling"""
    try:
        logger.info("Processing send shifts request")

        if user_session is None:
            raise Exception("User session not found.")

        user_id = user_session.get_id
        with get_db_session() as session:
            shifts_controller = ShiftsController(session)

        future_shifts = shifts_controller.get_future_shifts_for_user(user_id)
        future_shifts_for_client = convert_shifts_for_client(future_shifts, db, is_manager=False)

        logger.info(f"Retrieved {len(future_shifts_for_client)} shifts for user: {user_id}")
        return future_shifts_for_client

    except Exception as e:
        logger.error(f"Error in handle_send_shifts: {e}")
        return {
            "success": False,
            "error": f"Failed to get shifts: {str(e)}"
        }
