# Export functions from other handler files to make them accessible
from .login import handle_login
from .employee_signin import handle_employee_signin
from .manager_signin import handle_manager_signin
from .employee_shifts_request import handle_employee_shifts_request, handle_is_in_request_window, handle_get_request_window_times
from .get_employee_requests import handle_get_employee_requests
from .manager_insert_shifts import handle_manager_insert_shifts
from .employee_list import handle_employee_list, handle_employee_approval, handle_employee_rejection, handle_get_all_approved_worker_details, handle_create_employee_by_manager
from .send_profile import handle_send_profile
from . import admin_data_access
from .manager_schedule import (
    handle_create_new_board,
    handle_get_board,
    handle_get_start_date,
    handle_save_board,
    handle_reset_board,
    handle_publish_board,
    handle_unpublish_board,
    handle_get_board_content,
    handle_schedules,
    watch_workers_requests,
    open_requests_windows,
    get_last_shift_board_window_times,
    handle_get_preferences,
    handle_save_preferences,
    get_all_workers_names_by_workplace_id,
    handle_get_assigned_shifts,
    handle_get_all_approved_worker_details
)
from .send_shifts_to_employee import handle_send_shifts
from .make_shifts import make_shifts
from .shift_management_handlers import handle_create_shift, handle_get_shifts_by_job, handle_assign_worker_to_shift, handle_unassign_worker_from_shift


# You can also define an __all__ list if you want to control what `from handlers import *` imports
# For example:
__all__ = [
    'handle_login', 'handle_employee_signin', 'handle_manager_signin', 
    'handle_employee_shifts_request', 'handle_get_employee_requests', 
    'handle_manager_insert_shifts', 'handle_employee_list', 
    'handle_send_profile', 'handle_create_new_board', 
    'handle_get_board', 'handle_get_start_date', 
    'handle_save_board', 'handle_reset_board', 
    'handle_publish_board', 'handle_unpublish_board', 
    'handle_get_board_content', 'handle_schedules', 
    'watch_workers_requests', 'open_requests_windows', 
    'get_last_shift_board_window_times', 'handle_get_preferences', 
    'handle_save_preferences', 'get_all_workers_names_by_workplace_id', 
    'handle_get_assigned_shifts', 'handle_get_all_approved_worker_details', 
    'handle_get_all_client_companies', 'handle_create_client_company', 
    'handle_update_client_company', 'handle_delete_client_company', 
    'handle_get_client_directory', 'handle_get_client_company_details', 
    'handle_update_client_user_status', 'handle_get_client_analytics',
    'handle_create_shift', 'handle_get_shifts_by_job', 
    'handle_assign_worker_to_shift', 'handle_unassign_worker_from_shift'
]
