"""
Extended Settings Service Layer
Provides business logic and validation for extended settings operations.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, time
import json
import re
from sqlalchemy.orm import Session

from ..controllers.extended_settings_controller import ExtendedSettingsController
from ..models import User


class ExtendedSettingsService:
    """
    Service layer for extended settings operations.
    Handles business logic, validation, and complex operations.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.controller = ExtendedSettingsController(db_session)

    def get_settings_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all settings with key metrics and status for Hands on Labor.

        Returns:
            Dict containing settings summary
        """
        try:
            all_settings = self.controller.get_all_extended_settings()
            
            summary = {
                'total_categories': len(all_settings),
                'last_updated': None,
                'configuration_status': {},
                'integration_status': {},
                'compliance_status': {},
                'recommendations': []
            }
            
            # Analyze configuration completeness
            for category, settings in all_settings.items():
                if settings and 'updated_at' in settings:
                    if not summary['last_updated'] or settings['updated_at'] > summary['last_updated']:
                        summary['last_updated'] = settings['updated_at']
                
                summary['configuration_status'][category] = self._analyze_category_completeness(category, settings)
            
            # Check integration status
            if 'google_integration' in all_settings:
                google_settings = all_settings['google_integration']
                summary['integration_status']['google'] = {
                    'oauth_configured': bool(google_settings.get('google_client_id')),
                    'calendar_enabled': google_settings.get('google_calendar_sync_enabled', False),
                    'maps_enabled': google_settings.get('google_maps_enabled', False)
                }
            
            # Check compliance status
            if 'system_admin' in all_settings:
                admin_settings = all_settings['system_admin']
                summary['compliance_status'] = {
                    'gdpr_compliant': admin_settings.get('gdpr_compliance_mode', False),
                    'audit_logging': admin_settings.get('audit_logging_enabled', False),
                    'backup_enabled': admin_settings.get('auto_backup_enabled', False)
                }
            
            # Generate recommendations
            summary['recommendations'] = self._generate_recommendations(all_settings)
            
            return summary
            
        except Exception as e:
            raise Exception(f"Error generating settings summary: {str(e)}")

    def _analyze_category_completeness(self, category: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze completeness of a settings category."""
        if not settings:
            return {'status': 'not_configured', 'completeness': 0}
        
        # Define critical fields for each category
        critical_fields = {
            'company_profile': ['company_name', 'company_email', 'default_hourly_rate'],
            'user_management': ['password_min_length', 'session_timeout_minutes'],
            'certifications': ['crew_chief_cert_validity_months', 'forklift_cert_validity_months'],
            'client_management': ['default_payment_terms_days'],
            'job_configuration': ['default_job_duration_hours', 'max_workers_per_crew_chief'],
            'timesheet_advanced': ['overtime_threshold_daily', 'overtime_rate_multiplier'],
            'google_integration': ['google_oauth_enabled'],
            'reporting': ['auto_generate_reports', 'default_export_format'],
            'mobile_accessibility': ['mobile_app_enabled'],
            'system_admin': ['auto_backup_enabled', 'audit_logging_enabled']
        }
        
        if category not in critical_fields:
            return {'status': 'configured', 'completeness': 100}
        
        required_fields = critical_fields[category]
        configured_fields = sum(1 for field in required_fields if settings.get(field) is not None)
        completeness = (configured_fields / len(required_fields)) * 100
        
        if completeness == 100:
            status = 'fully_configured'
        elif completeness >= 50:
            status = 'partially_configured'
        else:
            status = 'minimally_configured'
        
        return {
            'status': status,
            'completeness': completeness,
            'missing_fields': [field for field in required_fields if settings.get(field) is None]
        }

    def _generate_recommendations(self, all_settings: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate configuration recommendations based on current settings."""
        recommendations = []
        
        # Check company profile
        company_profile = all_settings.get('company_profile', {})
        if not company_profile.get('company_logo_url'):
            recommendations.append({
                'category': 'company_profile',
                'type': 'branding',
                'priority': 'medium',
                'title': 'Add Company Logo',
                'description': 'Upload a company logo to improve branding across the application.'
            })
        
        # Check Google integration
        google_settings = all_settings.get('google_integration', {})
        if not google_settings.get('google_oauth_enabled'):
            recommendations.append({
                'category': 'google_integration',
                'type': 'integration',
                'priority': 'high',
                'title': 'Enable Google Integration',
                'description': 'Set up Google OAuth to enable calendar sync and enhanced authentication.'
            })
        
        # Check certifications
        cert_settings = all_settings.get('certifications', {})
        if not cert_settings.get('auto_notify_expiring_certs'):
            recommendations.append({
                'category': 'certifications',
                'type': 'automation',
                'priority': 'high',
                'title': 'Enable Certification Notifications',
                'description': 'Automatically notify workers about expiring certifications to maintain compliance.'
            })
        
        # Check backup settings
        admin_settings = all_settings.get('system_admin', {})
        if not admin_settings.get('auto_backup_enabled'):
            recommendations.append({
                'category': 'system_admin',
                'type': 'security',
                'priority': 'critical',
                'title': 'Enable Automatic Backups',
                'description': 'Set up automatic backups to protect against data loss.'
            })
        
        return recommendations

    def validate_settings_bulk(self, settings_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate multiple settings categories at once for Hands on Labor.

        Args:
            settings_data (Dict): Dictionary of category -> settings data

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        all_errors = []
        
        validation_methods = {
            'company_profile': self.controller.validate_company_profile_settings,
            'user_management': self.controller.validate_user_management_settings,
            'certifications': self.controller.validate_certifications_settings,
            'client_management': self.controller.validate_client_management_settings,
            'job_configuration': self.controller.validate_job_configuration_settings,
            'timesheet_advanced': self.controller.validate_timesheet_advanced_settings,
            'google_integration': self.controller.validate_google_integration_settings,
            'reporting': self.controller.validate_reporting_settings,
            'mobile_accessibility': self.controller.validate_mobile_accessibility_settings,
            'system_admin': self.controller.validate_system_admin_settings
        }
        
        for category, data in settings_data.items():
            if category in validation_methods:
                errors = validation_methods[category](data)
                if errors:
                    all_errors.extend([f"{category}: {error}" for error in errors])
        
        return len(all_errors) == 0, all_errors

    def update_settings_bulk(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update multiple settings categories in a single transaction for Hands on Labor.

        Args:
            settings_data (Dict): Dictionary of category -> settings data

        Returns:
            Dict containing updated settings
        """
        try:
            # Validate all settings first
            is_valid, errors = self.validate_settings_bulk(settings_data)
            if not is_valid:
                raise ValueError(f"Validation errors: {'; '.join(errors)}")

            updated_settings = {}

            update_methods = {
                'company_profile': self.controller.update_company_profile_settings,
                'user_management': self.controller.update_user_management_settings,
                'certifications': self.controller.update_certifications_settings,
                'client_management': self.controller.update_client_management_settings,
                'job_configuration': self.controller.update_job_configuration_settings,
                'timesheet_advanced': self.controller.update_timesheet_advanced_settings,
                'google_integration': self.controller.update_google_integration_settings,
                'reporting': self.controller.update_reporting_settings,
                'mobile_accessibility': self.controller.update_mobile_accessibility_settings,
                'system_admin': self.controller.update_system_admin_settings
            }

            # Update each category
            for category, data in settings_data.items():
                if category in update_methods:
                    result = update_methods[category](data)
                    updated_settings[category] = result.to_dict()

            return updated_settings

        except Exception as e:
            self.db_session.rollback()
            raise Exception(f"Error updating settings: {str(e)}")

    def export_settings_for_backup(self) -> Dict[str, Any]:
        """
        Export all settings in a format suitable for backup/restore for Hands on Labor.

        Returns:
            Dict containing exportable settings data
        """
        try:
            all_settings = self.controller.get_all_extended_settings()

            export_data = {
                'export_metadata': {
                    'exported_at': datetime.now().isoformat(),
                    'company_name': 'Hands on Labor',
                    'export_version': '1.0',
                    'application': 'EasyShifts Extended Settings'
                },
                'settings': all_settings,
                'schema_version': '1.0'
            }

            return export_data

        except Exception as e:
            raise Exception(f"Error exporting settings: {str(e)}")

    def import_settings_from_backup(self, import_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Import settings from backup data for Hands on Labor.

        Args:
            import_data (Dict): The backup data to import

        Returns:
            Dict containing import results
        """
        try:
            # Validate import data structure
            if 'settings' not in import_data:
                raise ValueError("Invalid import data: missing 'settings' key")

            settings_data = import_data['settings']

            # Validate and update settings
            updated_settings = self.update_settings_bulk(settings_data)

            return {
                'success': True,
                'imported_categories': list(updated_settings.keys()),
                'imported_at': datetime.now().isoformat(),
                'source_export_date': import_data.get('export_metadata', {}).get('exported_at'),
                'updated_settings': updated_settings
            }

        except Exception as e:
            raise Exception(f"Error importing settings: {str(e)}")

    def get_settings_diff(self, comparison_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare current settings with provided data and return differences for Hands on Labor.

        Args:
            comparison_data (Dict): Settings data to compare against

        Returns:
            Dict containing differences
        """
        try:
            current_settings = self.controller.get_all_extended_settings()
            differences = {}

            for category in current_settings.keys():
                if category in comparison_data:
                    category_diff = self._compare_category_settings(
                        current_settings[category],
                        comparison_data[category]
                    )
                    if category_diff:
                        differences[category] = category_diff

            return differences

        except Exception as e:
            raise Exception(f"Error comparing settings: {str(e)}")

    def _compare_category_settings(self, current: Dict[str, Any], comparison: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two category settings and return differences."""
        differences = {}
        
        # Check for changed values
        for key, value in comparison.items():
            if key in current and current[key] != value:
                differences[key] = {
                    'current': current[key],
                    'comparison': value,
                    'type': 'changed'
                }
            elif key not in current:
                differences[key] = {
                    'current': None,
                    'comparison': value,
                    'type': 'new'
                }
        
        # Check for removed values
        for key, value in current.items():
            if key not in comparison:
                differences[key] = {
                    'current': value,
                    'comparison': None,
                    'type': 'removed'
                }
        
        return differences
