from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from ..repositories.workplace_settings_repository import WorkplaceSettingsRepository
from ..services.workplace_settings_service import WorkplaceSettingsService
from .base_controller import BaseController


class WorkplaceSettingsController(BaseController):
    """
    Controller for managing workplace settings.
    """

    def __init__(self, db: Session):
        self.repository = WorkplaceSettingsRepository(db)
        self.service = WorkplaceSettingsService(self.repository)
        super().__init__(self.repository, self.service)

    def get_settings(self):
        """
        Get settings for Hands on Labor.
        Creates default settings if none exist.

        Returns:
            WorkplaceSettings: The settings object
        """
        settings = self.repository.get_first()
        if not settings:
            # Create default settings
            settings = self.create_default_settings()
        return settings

    def create_default_settings(self):
        """
        Create default settings for Hands on Labor.

        Returns:
            WorkplaceSettings: The created settings object
        """
        default_data = {
            # All fields will use their model defaults
        }
        return self.repository.create_entity(default_data)

    def update_settings(self, settings_data: Dict[str, Any]):
        """
        Update settings for Hands on Labor.

        Args:
            settings_data (dict): The settings data to update

        Returns:
            WorkplaceSettings: The updated settings object
        """
        settings = self.get_settings()
        return self.repository.update_entity(settings.id, settings_data)

    def update_scheduling_settings(self, scheduling_data: Dict[str, Any]):
        """
        Update only scheduling-related settings for Hands on Labor.

        Args:
            scheduling_data (dict): The scheduling settings to update

        Returns:
            WorkplaceSettings: The updated settings object
        """
        valid_fields = [
            'shifts_per_day', 'max_workers_per_shift', 'min_workers_per_shift',
            'business_start_time', 'business_end_time', 'default_shift_duration_hours',
            'break_duration_minutes', 'closed_days', 'operating_days'
        ]

        filtered_data = {k: v for k, v in scheduling_data.items() if k in valid_fields}
        return self.update_settings(filtered_data)

    def update_notification_settings(self, notification_data: Dict[str, Any]):
        """
        Update only notification-related settings for Hands on Labor.

        Args:
            notification_data (dict): The notification settings to update

        Returns:
            WorkplaceSettings: The updated settings object
        """
        valid_fields = [
            'email_notifications_enabled', 'notify_on_shift_requests',
            'notify_on_worker_assignments', 'notify_on_timesheet_submissions',
            'notify_on_schedule_changes', 'sms_notifications_enabled',
            'sms_urgent_only', 'push_notifications_enabled', 'notification_sound_enabled'
        ]

        filtered_data = {k: v for k, v in notification_data.items() if k in valid_fields}
        return self.update_settings(filtered_data)

    def update_request_window_settings(self, window_data: Dict[str, Any]):
        """
        Update only request window-related settings for Hands on Labor.

        Args:
            window_data (dict): The request window settings to update

        Returns:
            WorkplaceSettings: The updated settings object
        """
        valid_fields = [
            'auto_open_request_windows', 'request_window_days_ahead',
            'request_window_duration_hours', 'requests_window_start', 'requests_window_end'
        ]

        filtered_data = {k: v for k, v in window_data.items() if k in valid_fields}
        return self.update_settings(filtered_data)

    def update_worker_management_settings(self, worker_data: Dict[str, Any]):
        """
        Update only worker management-related settings for Hands on Labor.

        Args:
            worker_data (dict): The worker management settings to update

        Returns:
            WorkplaceSettings: The updated settings object
        """
        valid_fields = [
            'auto_assign_workers', 'auto_assign_by_seniority', 'auto_assign_by_availability',
            'auto_assign_by_skills', 'require_certification_verification',
            'allow_overtime_assignments', 'max_consecutive_days', 'max_hours_per_week'
        ]

        filtered_data = {k: v for k, v in worker_data.items() if k in valid_fields}
        return self.update_settings(filtered_data)

    def update_timesheet_settings(self, timesheet_data: Dict[str, Any]):
        """
        Update only timesheet-related settings for Hands on Labor.

        Args:
            timesheet_data (dict): The timesheet settings to update

        Returns:
            WorkplaceSettings: The updated settings object
        """
        valid_fields = [
            'require_photo_clock_in', 'require_location_verification', 'auto_clock_out_hours',
            'overtime_threshold_daily', 'overtime_threshold_weekly', 'overtime_rate_multiplier',
            'require_manager_approval', 'auto_approve_regular_hours', 'auto_approve_overtime'
        ]

        filtered_data = {k: v for k, v in timesheet_data.items() if k in valid_fields}
        return self.update_settings(filtered_data)

    def update_display_settings(self, display_data: Dict[str, Any]):
        """
        Update only display-related settings for Hands on Labor.

        Args:
            display_data (dict): The display settings to update

        Returns:
            WorkplaceSettings: The updated settings object
        """
        valid_fields = [
            'default_calendar_view', 'show_worker_photos', 'show_certification_badges',
            'color_code_by_role', 'use_24_hour_format', 'timezone', 'language',
            'currency', 'date_format'
        ]

        filtered_data = {k: v for k, v in display_data.items() if k in valid_fields}
        return self.update_settings(filtered_data)

    def get_settings_dict(self) -> Dict[str, Any]:
        """
        Get settings as a dictionary for API responses for Hands on Labor.

        Returns:
            dict: The settings as a dictionary
        """
        settings = self.get_settings()
        return settings.to_dict()

    def reset_to_defaults(self):
        """
        Reset all settings to defaults for Hands on Labor.

        Returns:
            WorkplaceSettings: The reset settings object
        """
        settings = self.get_settings()
        self.repository.delete_entity(settings.id)
        return self.create_default_settings()
