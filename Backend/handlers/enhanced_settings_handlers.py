from datetime import datetime
from main import get_db_session
from db.controllers.workplace_settings_controller import WorkplaceSettingsController
from user_session import UserSession


def handle_get_all_settings(user_session: UserSession) -> dict:
    """
    Get all settings for the current workplace.
    """
    request_id = 995
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}
    
    try:
        with get_db_session() as session:

            controller = WorkplaceSettingsController(session)
        settings_dict = controller.get_settings_dict()
        return {"request_id": request_id, "success": True, "data": settings_dict}
    except Exception as e:
        print(f"Error getting settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to retrieve settings."}


def handle_update_scheduling_settings(data: dict, user_session: UserSession) -> dict:
    """
    Update scheduling-related settings.
    """
    request_id = 996
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}
    
    try:
        with get_db_session() as session:

            controller = WorkplaceSettingsController(session)
        
        # Validate the data
        service = controller.service
        errors = service.validate_scheduling_settings(data)
        if errors:
            return {"request_id": request_id, "success": False, "error": "; ".join(errors)}
        
        # Update settings
        updated_settings = controller.update_scheduling_settings(data)
        return {"request_id": request_id, "success": True, "data": updated_settings.to_dict()}
    except Exception as e:
        print(f"Error updating scheduling settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update scheduling settings."}


def handle_update_notification_settings(data: dict, user_session: UserSession) -> dict:
    """
    Update notification-related settings.
    """
    request_id = 997
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}
    
    try:
        with get_db_session() as session:

            controller = WorkplaceSettingsController(session)
        updated_settings = controller.update_notification_settings(data)
        return {"request_id": request_id, "success": True, "data": updated_settings.to_dict()}
    except Exception as e:
        print(f"Error updating notification settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update notification settings."}


def handle_update_request_window_settings(data: dict, user_session: UserSession) -> dict:
    """
    Update request window settings.
    """
    request_id = 998
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}
    
    try:
        with get_db_session() as session:

            controller = WorkplaceSettingsController(session)
        
        # Validate the data
        service = controller.service
        errors = service.validate_request_window_settings(data)
        if errors:
            return {"request_id": request_id, "success": False, "error": "; ".join(errors)}
        
        # Convert datetime strings to datetime objects if needed
        if 'requests_window_start' in data and isinstance(data['requests_window_start'], str):
            data['requests_window_start'] = datetime.fromisoformat(data['requests_window_start'].replace('Z', '+00:00'))
        if 'requests_window_end' in data and isinstance(data['requests_window_end'], str):
            data['requests_window_end'] = datetime.fromisoformat(data['requests_window_end'].replace('Z', '+00:00'))
        
        updated_settings = controller.update_request_window_settings(data)
        return {"request_id": request_id, "success": True, "data": updated_settings.to_dict()}
    except Exception as e:
        print(f"Error updating request window settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update request window settings."}


def handle_update_worker_management_settings(data: dict, user_session: UserSession) -> dict:
    """
    Update worker management settings.
    """
    request_id = 999
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}
    
    try:
        with get_db_session() as session:

            controller = WorkplaceSettingsController(session)
        
        # Validate the data
        service = controller.service
        errors = service.validate_worker_management_settings(data)
        if errors:
            return {"request_id": request_id, "success": False, "error": "; ".join(errors)}
        
        updated_settings = controller.update_worker_management_settings(data)
        return {"request_id": request_id, "success": True, "data": updated_settings.to_dict()}
    except Exception as e:
        print(f"Error updating worker management settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update worker management settings."}


def handle_update_timesheet_settings(data: dict, user_session: UserSession) -> dict:
    """
    Update timesheet and payroll settings.
    """
    request_id = 1000
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}
    
    try:
        with get_db_session() as session:

            controller = WorkplaceSettingsController(session)
        
        # Validate the data
        service = controller.service
        errors = service.validate_timesheet_settings(data)
        if errors:
            return {"request_id": request_id, "success": False, "error": "; ".join(errors)}
        
        updated_settings = controller.update_timesheet_settings(data)
        return {"request_id": request_id, "success": True, "data": updated_settings.to_dict()}
    except Exception as e:
        print(f"Error updating timesheet settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update timesheet settings."}


def handle_update_display_settings(data: dict, user_session: UserSession) -> dict:
    """
    Update display and UI settings.
    """
    request_id = 1001
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}
    
    try:
        with get_db_session() as session:

            controller = WorkplaceSettingsController(session)
        
        # Validate the data
        service = controller.service
        errors = service.validate_display_settings(data)
        if errors:
            return {"request_id": request_id, "success": False, "error": "; ".join(errors)}
        
        updated_settings = controller.update_display_settings(data)
        return {"request_id": request_id, "success": True, "data": updated_settings.to_dict()}
    except Exception as e:
        print(f"Error updating display settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update display settings."}


def handle_reset_settings_to_defaults(user_session: UserSession) -> dict:
    """
    Reset all settings to defaults.
    """
    request_id = 1002
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}
    
    try:
        with get_db_session() as session:

            controller = WorkplaceSettingsController(session)
        reset_settings = controller.reset_to_defaults()
        return {"request_id": request_id, "success": True, "data": reset_settings.to_dict()}
    except Exception as e:
        print(f"Error resetting settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to reset settings."}


def handle_get_settings_template(user_session: UserSession) -> dict:
    """
    Get a template of default settings for reference.
    """
    request_id = 1003
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}
    
    try:
        with get_db_session() as session:

            controller = WorkplaceSettingsController(session)
        template = controller.service.get_default_settings_template()
        return {"request_id": request_id, "success": True, "data": template}
    except Exception as e:
        print(f"Error getting settings template: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to get settings template."}


def handle_export_settings(user_session: UserSession) -> dict:
    """
    Export current settings as JSON for backup/import.
    """
    request_id = 1004
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}
    
    try:
        with get_db_session() as session:

            controller = WorkplaceSettingsController(session)
        settings_dict = controller.get_settings_dict()

        # Add export metadata
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "company_name": "Hands on Labor",
            "version": "1.0",
            "settings": settings_dict
        }
        
        return {"request_id": request_id, "success": True, "data": export_data}
    except Exception as e:
        print(f"Error exporting settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to export settings."}


def handle_import_settings(data: dict, user_session: UserSession) -> dict:
    """
    Import settings from exported JSON.
    """
    request_id = 1005
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}
    
    try:
        with get_db_session() as session:

            controller = WorkplaceSettingsController(session)
        
        # Validate import data structure
        if "settings" not in data:
            return {"request_id": request_id, "success": False, "error": "Invalid import data: missing settings."}
        
        settings_data = data["settings"]
        
        # Validate all settings
        service = controller.service
        errors = service.validate_all_settings(settings_data)
        if errors:
            return {"request_id": request_id, "success": False, "error": f"Invalid settings: {'; '.join(errors)}"}
        
        # Import settings
        updated_settings = controller.update_settings(settings_data)
        return {"request_id": request_id, "success": True, "data": updated_settings.to_dict()}
    except Exception as e:
        print(f"Error importing settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to import settings."}


# New Extended Settings Handlers

def handle_update_company_profile_settings(data: dict, user_session: UserSession) -> dict:
    """
    Update company profile settings.
    """
    request_id = 1100
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.controllers.extended_settings_controller import ExtendedSettingsController
        with get_db_session() as session:

            controller = ExtendedSettingsController(session)

        # Validate the data
        errors = controller.validate_company_profile_settings(data)
        if errors:
            return {"request_id": request_id, "success": False, "error": "; ".join(errors)}

        updated_settings = controller.update_company_profile_settings(data)
        return {"request_id": request_id, "success": True, "data": updated_settings.to_dict()}
    except Exception as e:
        print(f"Error updating company profile settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update company profile settings."}


def handle_update_user_management_settings(data: dict, user_session: UserSession) -> dict:
    """
    Update user management settings.
    """
    request_id = 1101
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.controllers.extended_settings_controller import ExtendedSettingsController
        with get_db_session() as session:

            controller = ExtendedSettingsController(session)

        # Validate the data
        errors = controller.validate_user_management_settings(data)
        if errors:
            return {"request_id": request_id, "success": False, "error": "; ".join(errors)}

        updated_settings = controller.update_user_management_settings(data)
        return {"request_id": request_id, "success": True, "data": updated_settings.to_dict()}
    except Exception as e:
        print(f"Error updating user management settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update user management settings."}


def handle_update_certifications_settings(data: dict, user_session: UserSession) -> dict:
    """
    Update certifications settings.
    """
    request_id = 1102
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.controllers.extended_settings_controller import ExtendedSettingsController
        with get_db_session() as session:

            controller = ExtendedSettingsController(session)

        # Validate the data
        errors = controller.validate_certifications_settings(data)
        if errors:
            return {"request_id": request_id, "success": False, "error": "; ".join(errors)}

        updated_settings = controller.update_certifications_settings(data)
        return {"request_id": request_id, "success": True, "data": updated_settings.to_dict()}
    except Exception as e:
        print(f"Error updating certifications settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update certifications settings."}


def handle_update_client_management_settings(data: dict, user_session: UserSession) -> dict:
    """
    Update client management settings.
    """
    request_id = 1103
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.controllers.extended_settings_controller import ExtendedSettingsController
        with get_db_session() as session:

            controller = ExtendedSettingsController(session)

        # Validate the data
        errors = controller.validate_client_management_settings(data)
        if errors:
            return {"request_id": request_id, "success": False, "error": "; ".join(errors)}

        updated_settings = controller.update_client_management_settings(data)
        return {"request_id": request_id, "success": True, "data": updated_settings.to_dict()}
    except Exception as e:
        print(f"Error updating client management settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update client management settings."}


def handle_update_job_configuration_settings(data: dict, user_session: UserSession) -> dict:
    """
    Update job configuration settings.
    """
    request_id = 1104
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.controllers.extended_settings_controller import ExtendedSettingsController
        with get_db_session() as session:

            controller = ExtendedSettingsController(session)

        # Validate the data
        errors = controller.validate_job_configuration_settings(data)
        if errors:
            return {"request_id": request_id, "success": False, "error": "; ".join(errors)}

        updated_settings = controller.update_job_configuration_settings(data)
        return {"request_id": request_id, "success": True, "data": updated_settings.to_dict()}
    except Exception as e:
        print(f"Error updating job configuration settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update job configuration settings."}


def handle_update_timesheet_advanced_settings(data: dict, user_session: UserSession) -> dict:
    """
    Update advanced timesheet settings.
    """
    request_id = 1105
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.controllers.extended_settings_controller import ExtendedSettingsController
        with get_db_session() as session:

            controller = ExtendedSettingsController(session)

        # Validate the data
        errors = controller.validate_timesheet_advanced_settings(data)
        if errors:
            return {"request_id": request_id, "success": False, "error": "; ".join(errors)}

        updated_settings = controller.update_timesheet_advanced_settings(data)
        return {"request_id": request_id, "success": True, "data": updated_settings.to_dict()}
    except Exception as e:
        print(f"Error updating advanced timesheet settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update advanced timesheet settings."}


def handle_update_google_integration_settings(data: dict, user_session: UserSession) -> dict:
    """
    Update Google integration settings.
    """
    request_id = 1106
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.controllers.extended_settings_controller import ExtendedSettingsController
        with get_db_session() as session:

            controller = ExtendedSettingsController(session)

        # Validate the data
        errors = controller.validate_google_integration_settings(data)
        if errors:
            return {"request_id": request_id, "success": False, "error": "; ".join(errors)}

        updated_settings = controller.update_google_integration_settings(data)
        return {"request_id": request_id, "success": True, "data": updated_settings.to_dict()}
    except Exception as e:
        print(f"Error updating Google integration settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update Google integration settings."}


def handle_update_reporting_settings(data: dict, user_session: UserSession) -> dict:
    """
    Update reporting settings.
    """
    request_id = 1107
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.controllers.extended_settings_controller import ExtendedSettingsController
        with get_db_session() as session:

            controller = ExtendedSettingsController(session)

        # Validate the data
        errors = controller.validate_reporting_settings(data)
        if errors:
            return {"request_id": request_id, "success": False, "error": "; ".join(errors)}

        updated_settings = controller.update_reporting_settings(data)
        return {"request_id": request_id, "success": True, "data": updated_settings.to_dict()}
    except Exception as e:
        print(f"Error updating reporting settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update reporting settings."}


def handle_update_security_settings(data: dict, user_session: UserSession) -> dict:
    """
    Update security settings.
    """
    request_id = 1108
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.controllers.extended_settings_controller import ExtendedSettingsController
        with get_db_session() as session:

            controller = ExtendedSettingsController(session)

        # Validate the data
        errors = controller.validate_security_settings(data)
        if errors:
            return {"request_id": request_id, "success": False, "error": "; ".join(errors)}

        updated_settings = controller.update_security_settings(data)
        return {"request_id": request_id, "success": True, "data": updated_settings.to_dict()}
    except Exception as e:
        print(f"Error updating security settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update security settings."}


def handle_update_mobile_accessibility_settings(data: dict, user_session: UserSession) -> dict:
    """
    Update mobile and accessibility settings.
    """
    request_id = 1109
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.controllers.extended_settings_controller import ExtendedSettingsController
        with get_db_session() as session:

            controller = ExtendedSettingsController(session)

        # Validate the data
        errors = controller.validate_mobile_accessibility_settings(data)
        if errors:
            return {"request_id": request_id, "success": False, "error": "; ".join(errors)}

        updated_settings = controller.update_mobile_accessibility_settings(data)
        return {"request_id": request_id, "success": True, "data": updated_settings.to_dict()}
    except Exception as e:
        print(f"Error updating mobile accessibility settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update mobile accessibility settings."}


def handle_update_system_admin_settings(data: dict, user_session: UserSession) -> dict:
    """
    Update system administration settings.
    """
    request_id = 1110
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.controllers.extended_settings_controller import ExtendedSettingsController
        with get_db_session() as session:

            controller = ExtendedSettingsController(session)

        # Validate the data
        errors = controller.validate_system_admin_settings(data)
        if errors:
            return {"request_id": request_id, "success": False, "error": "; ".join(errors)}

        updated_settings = controller.update_system_admin_settings(data)
        return {"request_id": request_id, "success": True, "data": updated_settings.to_dict()}
    except Exception as e:
        print(f"Error updating system admin settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to update system admin settings."}


def handle_get_extended_settings(user_session: UserSession) -> dict:
    """
    Get all extended settings for the current workplace.
    """
    request_id = 1111
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.controllers.extended_settings_controller import ExtendedSettingsController
        with get_db_session() as session:

            controller = ExtendedSettingsController(session)
        settings_dict = controller.get_all_extended_settings()
        return {"request_id": request_id, "success": True, "data": settings_dict}
    except Exception as e:
        print(f"Error getting extended settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to retrieve extended settings."}


def handle_reset_extended_settings_to_defaults(user_session: UserSession) -> dict:
    """
    Reset all extended settings to defaults.
    """
    request_id = 1112
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.controllers.extended_settings_controller import ExtendedSettingsController
        with get_db_session() as session:

            controller = ExtendedSettingsController(session)
        reset_settings = controller.reset_all_to_defaults(user_session.get_id)
        return {"request_id": request_id, "success": True, "data": reset_settings}
    except Exception as e:
        print(f"Error resetting extended settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to reset extended settings."}


def handle_test_google_connection(data: dict, user_session: UserSession) -> dict:
    """
    Test Google API connection.
    """
    request_id = 1113
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.controllers.extended_settings_controller import ExtendedSettingsController
        with get_db_session() as session:

            controller = ExtendedSettingsController(session)
        test_result = controller.test_google_connection(user_session.get_id, data)
        return {"request_id": request_id, "success": True, "data": test_result}
    except Exception as e:
        print(f"Error testing Google connection: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to test Google connection."}


def handle_manual_google_sync(user_session: UserSession) -> dict:
    """
    Trigger manual Google sync.
    """
    request_id = 1114
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.controllers.extended_settings_controller import ExtendedSettingsController
        with get_db_session() as session:

            controller = ExtendedSettingsController(session)
        sync_result = controller.trigger_manual_google_sync(user_session.get_id)
        return {"request_id": request_id, "success": True, "data": sync_result}
    except Exception as e:
        print(f"Error triggering manual Google sync: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to trigger manual Google sync."}


def handle_system_health_check(user_session: UserSession) -> dict:
    """
    Run system health check.
    """
    request_id = 1115
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.controllers.extended_settings_controller import ExtendedSettingsController
        with get_db_session() as session:

            controller = ExtendedSettingsController(session)
        health_result = controller.run_system_health_check(user_session.get_id)
        return {"request_id": request_id, "success": True, "data": health_result}
    except Exception as e:
        print(f"Error running system health check: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to run system health check."}


def handle_manual_backup(user_session: UserSession) -> dict:
    """
    Trigger manual backup.
    """
    request_id = 1116
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.controllers.extended_settings_controller import ExtendedSettingsController
        with get_db_session() as session:

            controller = ExtendedSettingsController(session)
        backup_result = controller.trigger_manual_backup(user_session.get_id)
        return {"request_id": request_id, "success": True, "data": backup_result}
    except Exception as e:
        print(f"Error triggering manual backup: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to trigger manual backup."}


# Advanced Settings Management Handlers

def handle_get_settings_summary(user_session: UserSession) -> dict:
    """
    Get settings summary with analysis and recommendations.
    """
    request_id = 1117
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.services.extended_settings_service import ExtendedSettingsService
        service = ExtendedSettingsService(db)
        summary = service.get_settings_summary()
        return {"request_id": request_id, "success": True, "data": summary}
    except Exception as e:
        print(f"Error getting settings summary: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to get settings summary."}


def handle_bulk_update_settings(data: dict, user_session: UserSession) -> dict:
    """
    Update multiple settings categories in one operation.
    """
    request_id = 1118
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.services.extended_settings_service import ExtendedSettingsService
        service = ExtendedSettingsService(db)

        settings_data = data.get('settings', {})
        updated_settings = service.update_settings_bulk(settings_data)

        return {"request_id": request_id, "success": True, "data": updated_settings}
    except Exception as e:
        print(f"Error bulk updating settings: {e}")
        return {"request_id": request_id, "success": False, "error": f"Failed to update settings: {str(e)}"}


def handle_export_settings_backup(user_session: UserSession) -> dict:
    """
    Export all settings for backup purposes.
    """
    request_id = 1119
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.services.extended_settings_service import ExtendedSettingsService
        service = ExtendedSettingsService(db)
        export_data = service.export_settings_for_backup(user_session.get_id)
        return {"request_id": request_id, "success": True, "data": export_data}
    except Exception as e:
        print(f"Error exporting settings backup: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to export settings backup."}


def handle_import_settings_backup(data: dict, user_session: UserSession) -> dict:
    """
    Import settings from backup data.
    """
    request_id = 1120
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.services.extended_settings_service import ExtendedSettingsService
        service = ExtendedSettingsService(db)

        import_data = data.get('backup_data', {})
        result = service.import_settings_from_backup(user_session.get_id, import_data)

        return {"request_id": request_id, "success": True, "data": result}
    except Exception as e:
        print(f"Error importing settings backup: {e}")
        return {"request_id": request_id, "success": False, "error": f"Failed to import settings: {str(e)}"}


def handle_get_settings_templates(user_session: UserSession) -> dict:
    """
    Get available settings templates.
    """
    request_id = 1121
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.services.settings_templates import SettingsTemplates
        templates = SettingsTemplates.get_available_templates()
        return {"request_id": request_id, "success": True, "data": {"templates": templates}}
    except Exception as e:
        print(f"Error getting settings templates: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to get settings templates."}


def handle_apply_settings_template(data: dict, user_session: UserSession) -> dict:
    """
    Apply a settings template.
    """
    request_id = 1122
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.services.settings_templates import SettingsTemplates
        from db.services.extended_settings_service import ExtendedSettingsService

        template_id = data.get('template_id')
        if not template_id:
            return {"request_id": request_id, "success": False, "error": "Template ID is required."}

        # Get template settings
        template_settings = SettingsTemplates.apply_template(template_id)

        # Apply template using bulk update
        service = ExtendedSettingsService(db)
        updated_settings = service.update_settings_bulk(user_session.get_id, template_settings)

        return {"request_id": request_id, "success": True, "data": {
            "applied_template": template_id,
            "updated_settings": updated_settings
        }}
    except Exception as e:
        print(f"Error applying settings template: {e}")
        return {"request_id": request_id, "success": False, "error": f"Failed to apply template: {str(e)}"}


def handle_compare_settings(data: dict, user_session: UserSession) -> dict:
    """
    Compare current settings with provided data.
    """
    request_id = 1123
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.services.extended_settings_service import ExtendedSettingsService
        service = ExtendedSettingsService(db)

        comparison_data = data.get('comparison_settings', {})
        differences = service.get_settings_diff(user_session.get_id, comparison_data)

        return {"request_id": request_id, "success": True, "data": {"differences": differences}}
    except Exception as e:
        print(f"Error comparing settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to compare settings."}


def handle_validate_settings_bulk(data: dict, user_session: UserSession) -> dict:
    """
    Validate multiple settings categories without saving.
    """
    request_id = 1124
    if not user_session or not user_session.can_access_manager_page():
        return {"request_id": request_id, "success": False, "error": "Unauthorized access."}

    try:
        from db.services.extended_settings_service import ExtendedSettingsService
        service = ExtendedSettingsService(db)

        settings_data = data.get('settings', {})
        is_valid, errors = service.validate_settings_bulk(user_session.get_id, settings_data)

        return {"request_id": request_id, "success": True, "data": {
            "is_valid": is_valid,
            "errors": errors,
            "validated_categories": list(settings_data.keys())
        }}
    except Exception as e:
        print(f"Error validating settings: {e}")
        return {"request_id": request_id, "success": False, "error": "Failed to validate settings."}
