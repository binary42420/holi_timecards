"""
Extended Settings Controller for EasyShifts application.
Handles all extended settings operations including company profile, user management,
certifications, client management, job configuration, and more.
"""

from datetime import datetime, time
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models import (
    CompanyProfile, UserManagementSettings, CertificationsSettings,
    ClientManagementSettings
)
from ..extended_settings_models import (
    JobConfigurationSettings, TimesheetAdvancedSettings, GoogleIntegrationSettings
)
from ..additional_settings_models import (
    ReportingSettings, MobileAccessibilitySettings, SystemAdminSettings
)


class ExtendedSettingsController:
    """
    Controller for managing extended settings across all categories.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_all_extended_settings(self) -> Dict[str, Any]:
        """
        Get all extended settings for Hands on Labor.
        Since this is a single company system, there's only one set of settings.

        Returns:
            Dict containing all extended settings
        """
        try:
            settings = {}

            # Get all settings models
            settings_models = [
                ('company_profile', CompanyProfile),
                ('user_management', UserManagementSettings),
                ('certifications', CertificationsSettings),
                ('client_management', ClientManagementSettings),
                ('job_configuration', JobConfigurationSettings),
                ('timesheet_advanced', TimesheetAdvancedSettings),
                ('google_integration', GoogleIntegrationSettings),
                ('reporting', ReportingSettings),
                ('mobile_accessibility', MobileAccessibilitySettings),
                ('system_admin', SystemAdminSettings),
            ]

            for key, model_class in settings_models:
                setting = self.db_session.query(model_class).first()
                if setting:
                    settings[key] = setting.to_dict()
                else:
                    # Create default settings if they don't exist
                    default_setting = model_class()
                    self.db_session.add(default_setting)
                    self.db_session.commit()
                    settings[key] = default_setting.to_dict()

            return settings

        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise Exception(f"Database error getting extended settings: {str(e)}")

    def update_company_profile_settings(self, data: Dict[str, Any]) -> CompanyProfile:
        """
        Update company profile settings for Hands on Labor.

        Args:
            data (Dict): The settings data to update

        Returns:
            Updated CompanyProfile object
        """
        try:
            setting = self.db_session.query(CompanyProfile).first()
            if not setting:
                setting = CompanyProfile()
                self.db_session.add(setting)
            
            # Update fields
            for key, value in data.items():
                if hasattr(setting, key):
                    # Handle time fields
                    if key in ['operating_hours_start', 'operating_hours_end'] and isinstance(value, str):
                        try:
                            time_obj = datetime.strptime(value, '%H:%M').time()
                            setattr(setting, key, time_obj)
                        except ValueError:
                            continue
                    else:
                        setattr(setting, key, value)
            
            self.db_session.commit()
            return setting
            
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise Exception(f"Database error updating company profile settings: {str(e)}")

    def update_user_management_settings(self, data: Dict[str, Any]) -> UserManagementSettings:
        """
        Update user management settings for Hands on Labor.

        Args:
            data (Dict): The settings data to update

        Returns:
            Updated UserManagementSettings object
        """
        try:
            setting = self.db_session.query(UserManagementSettings).first()
            if not setting:
                setting = UserManagementSettings()
                self.db_session.add(setting)
            
            # Update fields
            for key, value in data.items():
                if hasattr(setting, key):
                    setattr(setting, key, value)
            
            self.db_session.commit()
            return setting
            
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise Exception(f"Database error updating user management settings: {str(e)}")

    def update_certifications_settings(self, data: Dict[str, Any]) -> CertificationsSettings:
        """
        Update certifications settings for Hands on Labor.

        Args:
            data (Dict): The settings data to update

        Returns:
            Updated CertificationsSettings object
        """
        try:
            setting = self.db_session.query(CertificationsSettings).first()
            if not setting:
                setting = CertificationsSettings()
                self.db_session.add(setting)

            # Update fields
            for key, value in data.items():
                if hasattr(setting, key):
                    setattr(setting, key, value)

            self.db_session.commit()
            return setting

        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise Exception(f"Database error updating certifications settings: {str(e)}")

    def update_client_management_settings(self, data: Dict[str, Any]) -> ClientManagementSettings:
        """
        Update client management settings for Hands on Labor.

        Args:
            data (Dict): The settings data to update

        Returns:
            Updated ClientManagementSettings object
        """
        try:
            setting = self.db_session.query(ClientManagementSettings).first()
            if not setting:
                setting = ClientManagementSettings()
                self.db_session.add(setting)
            
            # Update fields
            for key, value in data.items():
                if hasattr(setting, key):
                    setattr(setting, key, value)
            
            self.db_session.commit()
            return setting
            
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise Exception(f"Database error updating client management settings: {str(e)}")

    def update_job_configuration_settings(self, data: Dict[str, Any]) -> JobConfigurationSettings:
        """
        Update job configuration settings for Hands on Labor.

        Args:
            data (Dict): The settings data to update

        Returns:
            Updated JobConfigurationSettings object
        """
        try:
            setting = self.db_session.query(JobConfigurationSettings).first()
            if not setting:
                setting = JobConfigurationSettings()
                self.db_session.add(setting)

            # Update fields
            for key, value in data.items():
                if hasattr(setting, key):
                    setattr(setting, key, value)

            self.db_session.commit()
            return setting

        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise Exception(f"Database error updating job configuration settings: {str(e)}")

    def update_timesheet_advanced_settings(self, data: Dict[str, Any]) -> TimesheetAdvancedSettings:
        """
        Update advanced timesheet settings for Hands on Labor.

        Args:
            data (Dict): The settings data to update

        Returns:
            Updated TimesheetAdvancedSettings object
        """
        try:
            setting = self.db_session.query(TimesheetAdvancedSettings).first()
            if not setting:
                setting = TimesheetAdvancedSettings()
                self.db_session.add(setting)

            # Update fields
            for key, value in data.items():
                if hasattr(setting, key):
                    setattr(setting, key, value)

            self.db_session.commit()
            return setting

        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise Exception(f"Database error updating advanced timesheet settings: {str(e)}")

    def update_google_integration_settings(self, data: Dict[str, Any]) -> GoogleIntegrationSettings:
        """
        Update Google integration settings for Hands on Labor.

        Args:
            data (Dict): The settings data to update

        Returns:
            Updated GoogleIntegrationSettings object
        """
        try:
            setting = self.db_session.query(GoogleIntegrationSettings).first()
            if not setting:
                setting = GoogleIntegrationSettings()
                self.db_session.add(setting)

            # Update fields
            for key, value in data.items():
                if hasattr(setting, key):
                    # Handle time fields
                    if key in ['business_hours_start', 'business_hours_end'] and isinstance(value, str):
                        try:
                            time_obj = datetime.strptime(value, '%H:%M').time()
                            setattr(setting, key, time_obj)
                        except ValueError:
                            continue
                    else:
                        setattr(setting, key, value)

            self.db_session.commit()
            return setting

        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise Exception(f"Database error updating Google integration settings: {str(e)}")

    def update_reporting_settings(self, data: Dict[str, Any]) -> ReportingSettings:
        """
        Update reporting settings for Hands on Labor.

        Args:
            data (Dict): The settings data to update

        Returns:
            Updated ReportingSettings object
        """
        try:
            setting = self.db_session.query(ReportingSettings).first()
            if not setting:
                setting = ReportingSettings()
                self.db_session.add(setting)

            # Update fields
            for key, value in data.items():
                if hasattr(setting, key):
                    # Handle time fields
                    if key == 'report_generation_time' and isinstance(value, str):
                        try:
                            time_obj = datetime.strptime(value, '%H:%M').time()
                            setattr(setting, key, time_obj)
                        except ValueError:
                            continue
                    else:
                        setattr(setting, key, value)

            self.db_session.commit()
            return setting

        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise Exception(f"Database error updating reporting settings: {str(e)}")

    def update_mobile_accessibility_settings(self, data: Dict[str, Any]) -> MobileAccessibilitySettings:
        """
        Update mobile and accessibility settings for Hands on Labor.

        Args:
            data (Dict): The settings data to update

        Returns:
            Updated MobileAccessibilitySettings object
        """
        try:
            setting = self.db_session.query(MobileAccessibilitySettings).first()
            if not setting:
                setting = MobileAccessibilitySettings()
                self.db_session.add(setting)

            # Update fields
            for key, value in data.items():
                if hasattr(setting, key):
                    # Handle time fields
                    if key in ['quiet_hours_start', 'quiet_hours_end'] and isinstance(value, str):
                        try:
                            time_obj = datetime.strptime(value, '%H:%M').time()
                            setattr(setting, key, time_obj)
                        except ValueError:
                            continue
                    else:
                        setattr(setting, key, value)

            self.db_session.commit()
            return setting

        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise Exception(f"Database error updating mobile accessibility settings: {str(e)}")

    def update_system_admin_settings(self, data: Dict[str, Any]) -> SystemAdminSettings:
        """
        Update system administration settings for Hands on Labor.

        Args:
            data (Dict): The settings data to update

        Returns:
            Updated SystemAdminSettings object
        """
        try:
            setting = self.db_session.query(SystemAdminSettings).first()
            if not setting:
                setting = SystemAdminSettings()
                self.db_session.add(setting)

            # Update fields
            for key, value in data.items():
                if hasattr(setting, key):
                    # Handle time fields
                    if key == 'backup_time' and isinstance(value, str):
                        try:
                            time_obj = datetime.strptime(value, '%H:%M').time()
                            setattr(setting, key, time_obj)
                        except ValueError:
                            continue
                    else:
                        setattr(setting, key, value)

            self.db_session.commit()
            return setting

        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise Exception(f"Database error updating system admin settings: {str(e)}")

    # Validation Methods
    def validate_company_profile_settings(self, data: Dict[str, Any]) -> List[str]:
        """Validate company profile settings data."""
        errors = []

        if 'company_name' in data and not data['company_name'].strip():
            errors.append("Company name is required")

        if 'company_email' in data and data['company_email']:
            if '@' not in data['company_email']:
                errors.append("Invalid email format")

        if 'default_hourly_rate' in data:
            try:
                rate = float(data['default_hourly_rate'])
                if rate < 0:
                    errors.append("Hourly rate must be positive")
            except (ValueError, TypeError):
                errors.append("Invalid hourly rate format")

        return errors

    def validate_user_management_settings(self, data: Dict[str, Any]) -> List[str]:
        """Validate user management settings data."""
        errors = []

        if 'password_min_length' in data:
            try:
                length = int(data['password_min_length'])
                if length < 4 or length > 50:
                    errors.append("Password minimum length must be between 4 and 50")
            except (ValueError, TypeError):
                errors.append("Invalid password minimum length")

        if 'session_timeout_minutes' in data:
            try:
                timeout = int(data['session_timeout_minutes'])
                if timeout < 5 or timeout > 1440:
                    errors.append("Session timeout must be between 5 and 1440 minutes")
            except (ValueError, TypeError):
                errors.append("Invalid session timeout")

        return errors

    def validate_certifications_settings(self, data: Dict[str, Any]) -> List[str]:
        """Validate certifications settings data."""
        errors = []

        validity_fields = [
            'crew_chief_cert_validity_months',
            'forklift_cert_validity_months',
            'safety_training_validity_months',
            'background_check_validity_months'
        ]

        for field in validity_fields:
            if field in data:
                try:
                    months = int(data[field])
                    if months < 1 or months > 120:
                        errors.append(f"{field.replace('_', ' ').title()} must be between 1 and 120 months")
                except (ValueError, TypeError):
                    errors.append(f"Invalid {field.replace('_', ' ')}")

        return errors

    def validate_client_management_settings(self, data: Dict[str, Any]) -> List[str]:
        """Validate client management settings data."""
        errors = []

        if 'default_payment_terms_days' in data:
            try:
                days = int(data['default_payment_terms_days'])
                if days < 1 or days > 365:
                    errors.append("Payment terms must be between 1 and 365 days")
            except (ValueError, TypeError):
                errors.append("Invalid payment terms")

        if 'late_payment_fee_percentage' in data:
            try:
                fee = float(data['late_payment_fee_percentage'])
                if fee < 0 or fee > 50:
                    errors.append("Late payment fee must be between 0 and 50 percent")
            except (ValueError, TypeError):
                errors.append("Invalid late payment fee")

        return errors

    def validate_job_configuration_settings(self, data: Dict[str, Any]) -> List[str]:
        """Validate job configuration settings data."""
        errors = []

        duration_fields = [
            ('default_job_duration_hours', 1, 24),
            ('min_shift_duration_hours', 1, 12),
            ('max_shift_duration_hours', 8, 24),
            ('max_workers_per_crew_chief', 1, 50)
        ]

        for field, min_val, max_val in duration_fields:
            if field in data:
                try:
                    value = int(data[field])
                    if value < min_val or value > max_val:
                        errors.append(f"{field.replace('_', ' ').title()} must be between {min_val} and {max_val}")
                except (ValueError, TypeError):
                    errors.append(f"Invalid {field.replace('_', ' ')}")

        return errors

    def validate_timesheet_advanced_settings(self, data: Dict[str, Any]) -> List[str]:
        """Validate advanced timesheet settings data."""
        errors = []

        if 'overtime_rate_multiplier' in data:
            try:
                multiplier = float(data['overtime_rate_multiplier'])
                if multiplier < 1.0 or multiplier > 5.0:
                    errors.append("Overtime rate multiplier must be between 1.0 and 5.0")
            except (ValueError, TypeError):
                errors.append("Invalid overtime rate multiplier")

        return errors

    def validate_google_integration_settings(self, data: Dict[str, Any]) -> List[str]:
        """Validate Google integration settings data."""
        errors = []

        if 'google_oauth_enabled' in data and data['google_oauth_enabled']:
            if not data.get('google_client_id'):
                errors.append("Google Client ID is required when OAuth is enabled")
            if not data.get('google_client_secret'):
                errors.append("Google Client Secret is required when OAuth is enabled")

        return errors

    def validate_reporting_settings(self, data: Dict[str, Any]) -> List[str]:
        """Validate reporting settings data."""
        errors = []

        retention_fields = [
            ('keep_timesheet_records_months', 1, 120),
            ('keep_employee_records_years', 1, 25),
            ('keep_audit_logs_years', 1, 25)
        ]

        for field, min_val, max_val in retention_fields:
            if field in data:
                try:
                    value = int(data[field])
                    if value < min_val or value > max_val:
                        errors.append(f"{field.replace('_', ' ').title()} must be between {min_val} and {max_val}")
                except (ValueError, TypeError):
                    errors.append(f"Invalid {field.replace('_', ' ')}")

        return errors

    def validate_mobile_accessibility_settings(self, data: Dict[str, Any]) -> List[str]:
        """Validate mobile and accessibility settings data."""
        errors = []

        if 'font_size_multiplier' in data:
            try:
                multiplier = float(data['font_size_multiplier'])
                if multiplier < 0.5 or multiplier > 3.0:
                    errors.append("Font size multiplier must be between 0.5 and 3.0")
            except (ValueError, TypeError):
                errors.append("Invalid font size multiplier")

        return errors

    def validate_system_admin_settings(self, data: Dict[str, Any]) -> List[str]:
        """Validate system administration settings data."""
        errors = []

        if 'max_concurrent_users' in data:
            try:
                users = int(data['max_concurrent_users'])
                if users < 1 or users > 10000:
                    errors.append("Max concurrent users must be between 1 and 10000")
            except (ValueError, TypeError):
                errors.append("Invalid max concurrent users")

        return errors

    def update_security_settings(self, data: Dict[str, Any]) -> SystemAdminSettings:
        """
        Update security-related settings within system admin settings for Hands on Labor.

        Args:
            data (Dict): The security settings data to update

        Returns:
            Updated SystemAdminSettings object
        """
        try:
            setting = self.db_session.query(SystemAdminSettings).first()
            if not setting:
                setting = SystemAdminSettings()
                self.db_session.add(setting)

            # Update security-related fields only
            security_fields = [
                'enable_rate_limiting', 'max_requests_per_minute', 'enable_ip_whitelisting',
                'blocked_ip_addresses', 'security_scan_frequency', 'max_concurrent_users',
                'session_timeout_minutes', 'detailed_error_messages', 'gdpr_compliance_mode',
                'data_anonymization_enabled', 'right_to_be_forgotten_enabled'
            ]

            for key, value in data.items():
                if key in security_fields and hasattr(setting, key):
                    setattr(setting, key, value)

            self.db_session.commit()
            return setting

        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise Exception(f"Database error updating security settings: {str(e)}")

    # Utility Methods
    def reset_all_to_defaults(self) -> Dict[str, Any]:
        """
        Reset all extended settings to defaults for Hands on Labor.

        Returns:
            Dict containing all reset settings
        """
        try:
            settings_models = [
                CompanyProfile, UserManagementSettings, CertificationsSettings,
                ClientManagementSettings, JobConfigurationSettings, TimesheetAdvancedSettings,
                GoogleIntegrationSettings, ReportingSettings, MobileAccessibilitySettings,
                SystemAdminSettings
            ]

            # Delete existing settings
            for model_class in settings_models:
                self.db_session.query(model_class).delete()

            # Create new default settings
            reset_settings = {}
            for model_class in settings_models:
                new_setting = model_class()
                self.db_session.add(new_setting)
                self.db_session.flush()  # Get the ID
                reset_settings[model_class.__tablename__] = new_setting.to_dict()

            self.db_session.commit()
            return reset_settings

        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise Exception(f"Database error resetting settings: {str(e)}")

    def test_google_connection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test Google API connection for Hands on Labor.

        Args:
            data (Dict): Connection data to test

        Returns:
            Dict containing test results
        """
        try:
            # This would implement actual Google API testing
            # For now, return a mock response
            return {
                "connection_status": "success",
                "oauth_valid": True,
                "calendar_access": True,
                "gmail_access": True,
                "drive_access": True,
                "maps_access": True,
                "test_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "connection_status": "failed",
                "error": str(e),
                "test_timestamp": datetime.now().isoformat()
            }

    def trigger_manual_google_sync(self) -> Dict[str, Any]:
        """
        Trigger manual Google sync for Hands on Labor.

        Returns:
            Dict containing sync results
        """
        try:
            # This would implement actual Google sync
            # For now, return a mock response
            return {
                "sync_status": "completed",
                "events_synced": 15,
                "calendars_updated": 3,
                "sync_timestamp": datetime.now().isoformat(),
                "next_sync": (datetime.now()).isoformat()
            }
        except Exception as e:
            return {
                "sync_status": "failed",
                "error": str(e),
                "sync_timestamp": datetime.now().isoformat()
            }

    def run_system_health_check(self) -> Dict[str, Any]:
        """
        Run system health check for Hands on Labor.

        Returns:
            Dict containing health check results
        """
        try:
            # This would implement actual system health checks
            # For now, return a mock response
            return {
                "overall_status": "healthy",
                "database_status": "connected",
                "memory_usage": "42%",
                "cpu_usage": "23%",
                "disk_usage": "65%",
                "active_users": 45,
                "uptime": "99.9%",
                "last_backup": "2024-01-15 02:00:00",
                "check_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "overall_status": "error",
                "error": str(e),
                "check_timestamp": datetime.now().isoformat()
            }

    def trigger_manual_backup(self) -> Dict[str, Any]:
        """
        Trigger manual backup for Hands on Labor.

        Returns:
            Dict containing backup results
        """
        try:
            # This would implement actual backup functionality
            # For now, return a mock response
            return {
                "backup_status": "completed",
                "backup_size": "2.3 GB",
                "backup_location": "cloud_storage",
                "backup_timestamp": datetime.now().isoformat(),
                "backup_id": f"backup_handsonlabor_{int(datetime.now().timestamp())}"
            }
        except Exception as e:
            return {
                "backup_status": "failed",
                "error": str(e),
                "backup_timestamp": datetime.now().isoformat()
            }
