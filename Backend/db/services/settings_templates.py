"""
Settings Templates for EasyShifts Extended Settings
Provides pre-configured settings templates for different business scenarios.
"""

from typing import Dict, Any, List
from datetime import time


class SettingsTemplates:
    """
    Pre-configured settings templates for different business scenarios.
    """

    @staticmethod
    def get_hands_on_labor_default() -> Dict[str, Any]:
        """
        Default settings template for Hands on Labor.
        Optimized for event staffing and stage work in San Diego.
        """
        return {
            'company_profile': {
                'company_name': 'Hands on Labor',
                'company_tagline': 'Professional Event Staffing Solutions',
                'company_email': 'info@handsonlabor.com',
                'company_phone': '(619) 555-0123',
                'company_address': 'San Diego, CA',
                'website_url': 'https://handsonlabor.com',
                'default_hourly_rate': 28.50,
                'operating_hours_start': time(6, 0),
                'operating_hours_end': time(22, 0),
                'time_zone': 'America/Los_Angeles',
                'business_type': 'event_staffing',
                'primary_services': ['stage_setup', 'event_support', 'load_in_out'],
                'service_area': 'San Diego County'
            },
            'user_management': {
                'auto_approve_employees': False,
                'require_manager_approval': True,
                'password_min_length': 8,
                'session_timeout_minutes': 480,
                'crew_chief_premium_rate': 5.00,
                'forklift_operators_premium_rate': 3.00,
                'truck_drivers_premium_rate': 4.00,
                'allow_employee_self_registration': True,
                'require_email_verification': True,
                'enable_role_upgrades': True,
                'max_shifts_per_week': 6
            },
            'certifications': {
                'require_crew_chief_certification': True,
                'require_forklift_certification': True,
                'require_safety_training': True,
                'crew_chief_cert_validity_months': 24,
                'forklift_cert_validity_months': 36,
                'safety_training_validity_months': 12,
                'background_check_validity_months': 24,
                'auto_notify_expiring_certs': True,
                'cert_expiry_warning_days': 30,
                'custom_certifications': [
                    {
                        'name': 'Rigging Certification',
                        'validity_months': 12,
                        'required': True,
                        'premium_rate': 2.00
                    },
                    {
                        'name': 'Audio/Visual Setup',
                        'validity_months': 24,
                        'required': False,
                        'premium_rate': 1.50
                    }
                ]
            },
            'client_management': {
                'auto_create_client_invoices': True,
                'default_payment_terms_days': 30,
                'late_payment_fee_percentage': 1.5,
                'require_client_approval_for_timesheets': True,
                'allow_client_direct_booking': False,
                'client_portal_enabled': True,
                'show_worker_names_to_clients': True,
                'client_rating_system_enabled': True,
                'require_purchase_orders': True,
                'auto_send_completion_reports': True
            },
            'job_configuration': {
                'enable_job_templates': True,
                'default_job_duration_hours': 8,
                'allow_multi_day_jobs': True,
                'require_crew_chief_per_shift': True,
                'max_workers_per_crew_chief': 8,
                'require_job_location': True,
                'require_location_coordinates': True,
                'min_notice_hours_new_jobs': 24,
                'auto_assign_workers': False,
                'job_templates': [
                    {
                        'id': 1,
                        'name': 'Stage Setup - Small Venue',
                        'duration_hours': 6,
                        'required_roles': {
                            'crew_chief': 1,
                            'stagehand': 4,
                            'forklift_operator': 1
                        },
                        'equipment_needed': ['forklifts', 'hand_tools', 'safety_gear']
                    },
                    {
                        'id': 2,
                        'name': 'Stage Setup - Large Venue',
                        'duration_hours': 10,
                        'required_roles': {
                            'crew_chief': 2,
                            'stagehand': 12,
                            'forklift_operator': 2,
                            'truck_driver': 1
                        },
                        'equipment_needed': ['forklifts', 'trucks', 'rigging_equipment']
                    },
                    {
                        'id': 3,
                        'name': 'Load In/Out',
                        'duration_hours': 4,
                        'required_roles': {
                            'crew_chief': 1,
                            'stagehand': 6
                        },
                        'equipment_needed': ['hand_tools', 'dollies']
                    }
                ]
            },
            'timesheet_advanced': {
                'require_photo_clock_in': False,
                'require_location_verification': True,
                'location_verification_radius_feet': 100,
                'max_clock_pairs_per_shift': 3,
                'overtime_threshold_daily': 8,
                'overtime_threshold_weekly': 40,
                'overtime_rate_multiplier': 1.5,
                'double_time_threshold_daily': 12,
                'double_time_rate_multiplier': 2.0,
                'crew_chiefs_can_edit_team_times': True,
                'clients_can_view_timesheets': True,
                'clients_can_edit_timesheets': False,
                'round_time_to_nearest_minutes': 15,
                'auto_deduct_unpaid_breaks': True,
                'unpaid_break_threshold_minutes': 30
            },
            'google_integration': {
                'google_oauth_enabled': True,
                'google_calendar_sync_enabled': True,
                'calendar_sync_direction': 'both',
                'gmail_notifications_enabled': True,
                'google_maps_enabled': True,
                'google_drive_enabled': True,
                'sync_frequency_minutes': 15,
                'auto_backup_timesheets': True,
                'calculate_travel_distances': True
            },
            'reporting': {
                'auto_generate_reports': True,
                'report_generation_frequency': 'weekly',
                'report_generation_day': 'monday',
                'report_generation_time': time(8, 0),
                'keep_timesheet_records_months': 24,
                'keep_employee_records_years': 7,
                'default_export_format': 'xlsx',
                'track_employee_performance': True,
                'track_client_satisfaction': True,
                'enable_custom_reports': True
            },
            'mobile_accessibility': {
                'mobile_app_enabled': True,
                'enable_offline_mode': True,
                'mobile_push_notifications': True,
                'gps_tracking_enabled': True,
                'geofencing_enabled': True,
                'high_contrast_mode': False,
                'large_text_support': True,
                'voice_over_support': True,
                'default_language': 'en',
                'biometric_authentication': True
            },
            'system_admin': {
                'auto_backup_enabled': True,
                'backup_frequency': 'daily',
                'backup_time': time(2, 0),
                'system_health_monitoring': True,
                'audit_logging_enabled': True,
                'enable_rate_limiting': True,
                'gdpr_compliance_mode': True,
                'session_timeout_minutes': 480,
                'max_concurrent_users': 500
            }
        }

    @staticmethod
    def get_small_business_template() -> Dict[str, Any]:
        """
        Template for small staffing businesses (1-50 employees).
        """
        base_template = SettingsTemplates.get_hands_on_labor_default()
        
        # Modify for smaller operations
        base_template['user_management'].update({
            'auto_approve_employees': True,
            'max_shifts_per_week': 5,
            'crew_chief_premium_rate': 3.00
        })
        
        base_template['job_configuration'].update({
            'max_workers_per_crew_chief': 6,
            'min_notice_hours_new_jobs': 12
        })
        
        base_template['system_admin'].update({
            'max_concurrent_users': 50,
            'backup_frequency': 'weekly'
        })
        
        return base_template

    @staticmethod
    def get_enterprise_template() -> Dict[str, Any]:
        """
        Template for large enterprise operations (500+ employees).
        """
        base_template = SettingsTemplates.get_hands_on_labor_default()
        
        # Modify for enterprise operations
        base_template['user_management'].update({
            'require_manager_approval': True,
            'password_min_length': 12,
            'session_timeout_minutes': 240
        })
        
        base_template['certifications'].update({
            'require_background_checks': True,
            'cert_expiry_warning_days': 60
        })
        
        base_template['system_admin'].update({
            'max_concurrent_users': 2000,
            'enable_rate_limiting': True,
            'max_requests_per_minute': 1000,
            'detailed_error_messages': False
        })
        
        return base_template

    @staticmethod
    def get_high_security_template() -> Dict[str, Any]:
        """
        Template for high-security environments.
        """
        base_template = SettingsTemplates.get_hands_on_labor_default()
        
        # Enhanced security settings
        base_template['user_management'].update({
            'password_min_length': 14,
            'require_two_factor_auth': True,
            'session_timeout_minutes': 120,
            'require_email_verification': True
        })
        
        base_template['timesheet_advanced'].update({
            'require_photo_clock_in': True,
            'require_supervisor_witness': True,
            'track_gps_location': True
        })
        
        base_template['system_admin'].update({
            'audit_logging_enabled': True,
            'detailed_error_messages': False,
            'enable_ip_whitelisting': True,
            'security_scan_frequency': 'daily'
        })
        
        return base_template

    @staticmethod
    def get_available_templates() -> List[Dict[str, Any]]:
        """
        Get list of all available templates with metadata.
        """
        return [
            {
                'id': 'hands_on_labor_default',
                'name': 'Hands on Labor Default',
                'description': 'Optimized for event staffing and stage work',
                'category': 'event_staffing',
                'recommended_for': 'Event staffing companies, stage work, load in/out operations'
            },
            {
                'id': 'small_business',
                'name': 'Small Business',
                'description': 'Simplified settings for small operations',
                'category': 'small_business',
                'recommended_for': 'Companies with 1-50 employees'
            },
            {
                'id': 'enterprise',
                'name': 'Enterprise',
                'description': 'Advanced settings for large operations',
                'category': 'enterprise',
                'recommended_for': 'Companies with 500+ employees'
            },
            {
                'id': 'high_security',
                'name': 'High Security',
                'description': 'Enhanced security and compliance features',
                'category': 'security',
                'recommended_for': 'High-security environments, government contracts'
            }
        ]

    @staticmethod
    def apply_template(template_id: str) -> Dict[str, Any]:
        """
        Apply a specific template by ID.
        
        Args:
            template_id (str): The template identifier
            
        Returns:
            Dict containing the template settings
        """
        templates = {
            'hands_on_labor_default': SettingsTemplates.get_hands_on_labor_default,
            'small_business': SettingsTemplates.get_small_business_template,
            'enterprise': SettingsTemplates.get_enterprise_template,
            'high_security': SettingsTemplates.get_high_security_template
        }
        
        if template_id not in templates:
            raise ValueError(f"Unknown template ID: {template_id}")
        
        return templates[template_id]()
