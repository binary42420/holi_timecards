from typing import Dict, Any, List
from datetime import datetime, timedelta
from ..repositories.workplace_settings_repository import WorkplaceSettingsRepository


class WorkplaceSettingsService:
    """
    Service layer for workplace settings business logic.
    """

    def __init__(self, repository: WorkplaceSettingsRepository):
        self.repository = repository

    def validate_scheduling_settings(self, settings_data: Dict[str, Any]) -> List[str]:
        """
        Validate scheduling settings for logical consistency.
        
        Args:
            settings_data (dict): The settings data to validate
            
        Returns:
            List[str]: List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate shifts per day
        shifts_per_day = settings_data.get('shifts_per_day', 2)
        if not isinstance(shifts_per_day, int) or shifts_per_day < 1 or shifts_per_day > 5:
            errors.append("Shifts per day must be between 1 and 5")
        
        # Validate worker limits
        max_workers = settings_data.get('max_workers_per_shift', 10)
        min_workers = settings_data.get('min_workers_per_shift', 1)
        
        if not isinstance(max_workers, int) or max_workers < 1:
            errors.append("Maximum workers per shift must be at least 1")
        
        if not isinstance(min_workers, int) or min_workers < 1:
            errors.append("Minimum workers per shift must be at least 1")
        
        if max_workers < min_workers:
            errors.append("Maximum workers must be greater than or equal to minimum workers")
        
        # Validate business hours
        start_time = settings_data.get('business_start_time')
        end_time = settings_data.get('business_end_time')
        
        if start_time and end_time:
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time)
            
            if end_time <= start_time:
                errors.append("Business end time must be after start time")
        
        # Validate shift duration
        duration = settings_data.get('default_shift_duration_hours', 8)
        if not isinstance(duration, int) or duration < 1 or duration > 24:
            errors.append("Shift duration must be between 1 and 24 hours")
        
        # Validate break duration
        break_duration = settings_data.get('break_duration_minutes', 30)
        if not isinstance(break_duration, int) or break_duration < 0 or break_duration > 480:
            errors.append("Break duration must be between 0 and 480 minutes (8 hours)")
        
        # Validate days
        closed_days = settings_data.get('closed_days', [])
        operating_days = settings_data.get('operating_days', [])
        
        valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        if closed_days:
            invalid_closed = [day for day in closed_days if day not in valid_days]
            if invalid_closed:
                errors.append(f"Invalid closed days: {', '.join(invalid_closed)}")
        
        if operating_days:
            invalid_operating = [day for day in operating_days if day not in valid_days]
            if invalid_operating:
                errors.append(f"Invalid operating days: {', '.join(invalid_operating)}")
            
            # Check for conflicts
            conflicts = set(closed_days) & set(operating_days)
            if conflicts:
                errors.append(f"Days cannot be both closed and operating: {', '.join(conflicts)}")
        
        return errors

    def validate_worker_management_settings(self, settings_data: Dict[str, Any]) -> List[str]:
        """
        Validate worker management settings.
        
        Args:
            settings_data (dict): The settings data to validate
            
        Returns:
            List[str]: List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate consecutive days limit
        max_consecutive = settings_data.get('max_consecutive_days', 6)
        if not isinstance(max_consecutive, int) or max_consecutive < 1 or max_consecutive > 14:
            errors.append("Maximum consecutive days must be between 1 and 14")
        
        # Validate weekly hours limit
        max_hours_week = settings_data.get('max_hours_per_week', 40)
        if not isinstance(max_hours_week, int) or max_hours_week < 1 or max_hours_week > 168:
            errors.append("Maximum hours per week must be between 1 and 168")
        
        return errors

    def validate_timesheet_settings(self, settings_data: Dict[str, Any]) -> List[str]:
        """
        Validate timesheet settings.
        
        Args:
            settings_data (dict): The settings data to validate
            
        Returns:
            List[str]: List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate auto clock out hours
        auto_clock_out = settings_data.get('auto_clock_out_hours', 12)
        if not isinstance(auto_clock_out, int) or auto_clock_out < 1 or auto_clock_out > 24:
            errors.append("Auto clock out hours must be between 1 and 24")
        
        # Validate overtime thresholds
        daily_threshold = settings_data.get('overtime_threshold_daily', 8)
        weekly_threshold = settings_data.get('overtime_threshold_weekly', 40)
        
        if not isinstance(daily_threshold, int) or daily_threshold < 1 or daily_threshold > 24:
            errors.append("Daily overtime threshold must be between 1 and 24 hours")
        
        if not isinstance(weekly_threshold, int) or weekly_threshold < 1 or weekly_threshold > 168:
            errors.append("Weekly overtime threshold must be between 1 and 168 hours")
        
        # Validate overtime rate
        overtime_rate = settings_data.get('overtime_rate_multiplier', 1.5)
        if not isinstance(overtime_rate, (int, float)) or overtime_rate < 1.0 or overtime_rate > 5.0:
            errors.append("Overtime rate multiplier must be between 1.0 and 5.0")
        
        return errors

    def validate_request_window_settings(self, settings_data: Dict[str, Any]) -> List[str]:
        """
        Validate request window settings.
        
        Args:
            settings_data (dict): The settings data to validate
            
        Returns:
            List[str]: List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate days ahead
        days_ahead = settings_data.get('request_window_days_ahead', 7)
        if not isinstance(days_ahead, int) or days_ahead < 1 or days_ahead > 30:
            errors.append("Request window days ahead must be between 1 and 30")
        
        # Validate duration hours
        duration_hours = settings_data.get('request_window_duration_hours', 72)
        if not isinstance(duration_hours, int) or duration_hours < 1 or duration_hours > 720:
            errors.append("Request window duration must be between 1 and 720 hours (30 days)")
        
        # Validate manual window times
        start_time = settings_data.get('requests_window_start')
        end_time = settings_data.get('requests_window_end')
        
        if start_time and end_time:
            if isinstance(start_time, str):
                try:
                    start_time = datetime.fromisoformat(start_time)
                except ValueError:
                    errors.append("Invalid start time format")
                    return errors
            
            if isinstance(end_time, str):
                try:
                    end_time = datetime.fromisoformat(end_time)
                except ValueError:
                    errors.append("Invalid end time format")
                    return errors
            
            if end_time <= start_time:
                errors.append("Request window end time must be after start time")
        
        return errors

    def validate_display_settings(self, settings_data: Dict[str, Any]) -> List[str]:
        """
        Validate display settings.
        
        Args:
            settings_data (dict): The settings data to validate
            
        Returns:
            List[str]: List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate calendar view
        calendar_view = settings_data.get('default_calendar_view', 'week')
        valid_views = ['day', 'week', 'month']
        if calendar_view not in valid_views:
            errors.append(f"Calendar view must be one of: {', '.join(valid_views)}")
        
        # Validate timezone
        timezone = settings_data.get('timezone', 'America/New_York')
        # Basic timezone validation (could be more comprehensive)
        if not isinstance(timezone, str) or len(timezone) < 3:
            errors.append("Invalid timezone format")
        
        # Validate language
        language = settings_data.get('language', 'en')
        valid_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'zh', 'ja', 'ko']
        if language not in valid_languages:
            errors.append(f"Language must be one of: {', '.join(valid_languages)}")
        
        # Validate currency
        currency = settings_data.get('currency', 'USD')
        valid_currencies = ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CNY', 'MXN']
        if currency not in valid_currencies:
            errors.append(f"Currency must be one of: {', '.join(valid_currencies)}")
        
        # Validate date format
        date_format = settings_data.get('date_format', 'MM/DD/YYYY')
        valid_formats = ['MM/DD/YYYY', 'DD/MM/YYYY', 'YYYY-MM-DD', 'DD-MM-YYYY', 'MM-DD-YYYY']
        if date_format not in valid_formats:
            errors.append(f"Date format must be one of: {', '.join(valid_formats)}")
        
        return errors

    def validate_all_settings(self, settings_data: Dict[str, Any]) -> List[str]:
        """
        Validate all settings categories.
        
        Args:
            settings_data (dict): The settings data to validate
            
        Returns:
            List[str]: List of all validation errors
        """
        all_errors = []
        
        all_errors.extend(self.validate_scheduling_settings(settings_data))
        all_errors.extend(self.validate_worker_management_settings(settings_data))
        all_errors.extend(self.validate_timesheet_settings(settings_data))
        all_errors.extend(self.validate_request_window_settings(settings_data))
        all_errors.extend(self.validate_display_settings(settings_data))
        
        return all_errors

    def get_default_settings_template(self) -> Dict[str, Any]:
        """
        Get a template of default settings for new workplaces.
        
        Returns:
            dict: Default settings template
        """
        return {
            # Scheduling
            'shifts_per_day': 2,
            'max_workers_per_shift': 10,
            'min_workers_per_shift': 1,
            'default_shift_duration_hours': 8,
            'break_duration_minutes': 30,
            'closed_days': [],
            'operating_days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
            
            # Notifications
            'email_notifications_enabled': True,
            'notify_on_shift_requests': True,
            'notify_on_worker_assignments': True,
            'notify_on_timesheet_submissions': True,
            'notify_on_schedule_changes': True,
            'sms_notifications_enabled': False,
            'sms_urgent_only': True,
            'push_notifications_enabled': True,
            'notification_sound_enabled': True,
            
            # Request windows
            'auto_open_request_windows': True,
            'request_window_days_ahead': 7,
            'request_window_duration_hours': 72,
            
            # Worker management
            'auto_assign_workers': False,
            'auto_assign_by_seniority': True,
            'auto_assign_by_availability': True,
            'auto_assign_by_skills': True,
            'require_certification_verification': True,
            'allow_overtime_assignments': True,
            'max_consecutive_days': 6,
            'max_hours_per_week': 40,
            
            # Timesheet
            'require_photo_clock_in': False,
            'require_location_verification': False,
            'auto_clock_out_hours': 12,
            'overtime_threshold_daily': 8,
            'overtime_threshold_weekly': 40,
            'overtime_rate_multiplier': 1.5,
            'require_manager_approval': True,
            'auto_approve_regular_hours': False,
            'auto_approve_overtime': False,
            
            # Display
            'default_calendar_view': 'week',
            'show_worker_photos': True,
            'show_certification_badges': True,
            'color_code_by_role': True,
            'use_24_hour_format': False,
            'timezone': 'America/New_York',
            'language': 'en',
            'currency': 'USD',
            'date_format': 'MM/DD/YYYY',
            
            # Security
            'require_two_factor_auth': False,
            'session_timeout_minutes': 480,
            'password_expiry_days': 90,
            'keep_timesheet_records_months': 24,
            'keep_schedule_history_months': 12,
            
            # Integrations
            'payroll_system_integration': False,
            'hr_system_integration': False,
            'calendar_sync_enabled': False,
            'api_access_enabled': False,
            'webhook_notifications': False,
            
            # Custom fields
            'custom_shift_fields': [],
            'custom_worker_fields': [],
        }
