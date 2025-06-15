"""
Additional settings models for EasyShifts application.
These models support reporting, mobile, and system administration settings.
"""

from datetime import time
from sqlalchemy import Column, String, Boolean, Date, Enum, PrimaryKeyConstraint, ForeignKey, DateTime, JSON, func, \
    Integer, Float, Text, Time
from sqlalchemy.orm import relationship
from .models import Base


class ReportingSettings(Base):
    """
    Reporting and analytics configuration settings.
    """
    __tablename__ = 'reporting_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Report Generation
    auto_generate_reports = Column(Boolean, default=True, nullable=False)
    report_generation_frequency = Column(String(20), default='weekly', nullable=False)
    report_generation_day = Column(String(10), default='monday', nullable=False)
    report_generation_time = Column(Time, default=time(8, 0), nullable=False)

    # Data Retention
    keep_timesheet_records_months = Column(Integer, default=24, nullable=False)
    keep_schedule_history_months = Column(Integer, default=12, nullable=False)
    keep_employee_records_years = Column(Integer, default=7, nullable=False)
    keep_client_records_years = Column(Integer, default=7, nullable=False)
    keep_audit_logs_years = Column(Integer, default=10, nullable=False)

    # Export Formats
    default_export_format = Column(String(10), default='xlsx', nullable=False)
    allow_pdf_exports = Column(Boolean, default=True, nullable=False)
    allow_csv_exports = Column(Boolean, default=True, nullable=False)
    allow_json_exports = Column(Boolean, default=False, nullable=False)
    include_charts_in_exports = Column(Boolean, default=True, nullable=False)

    # Report Distribution
    auto_email_reports = Column(Boolean, default=False, nullable=False)
    email_recipients = Column(JSON, default=list, nullable=False)
    include_summary_dashboard = Column(Boolean, default=True, nullable=False)
    password_protect_reports = Column(Boolean, default=False, nullable=False)

    # Analytics & Metrics
    track_employee_performance = Column(Boolean, default=True, nullable=False)
    track_client_satisfaction = Column(Boolean, default=True, nullable=False)
    track_job_profitability = Column(Boolean, default=True, nullable=False)
    track_equipment_utilization = Column(Boolean, default=False, nullable=False)
    calculate_labor_efficiency = Column(Boolean, default=True, nullable=False)

    # Custom Reports
    enable_custom_reports = Column(Boolean, default=True, nullable=False)
    max_custom_reports_per_user = Column(Integer, default=10, nullable=False)
    allow_scheduled_custom_reports = Column(Boolean, default=True, nullable=False)
    custom_report_retention_days = Column(Integer, default=90, nullable=False)

    # Data Privacy
    anonymize_employee_data = Column(Boolean, default=False, nullable=False)
    exclude_sensitive_fields = Column(Boolean, default=True, nullable=False)
    require_approval_for_detailed_reports = Column(Boolean, default=False, nullable=False)
    audit_report_access = Column(Boolean, default=True, nullable=False)

    # Performance Settings
    report_cache_duration_hours = Column(Integer, default=4, nullable=False)
    max_report_rows = Column(Integer, default=10000, nullable=False)
    enable_report_pagination = Column(Boolean, default=True, nullable=False)
    async_report_generation = Column(Boolean, default=True, nullable=False)

    # Report Templates
    report_templates = Column(JSON, default=list, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'auto_generate_reports': self.auto_generate_reports,
            'report_generation_frequency': self.report_generation_frequency,
            'report_generation_day': self.report_generation_day,
            'report_generation_time': self.report_generation_time.isoformat() if self.report_generation_time else None,
            'keep_timesheet_records_months': self.keep_timesheet_records_months,
            'keep_schedule_history_months': self.keep_schedule_history_months,
            'keep_employee_records_years': self.keep_employee_records_years,
            'keep_client_records_years': self.keep_client_records_years,
            'keep_audit_logs_years': self.keep_audit_logs_years,
            'default_export_format': self.default_export_format,
            'allow_pdf_exports': self.allow_pdf_exports,
            'allow_csv_exports': self.allow_csv_exports,
            'allow_json_exports': self.allow_json_exports,
            'include_charts_in_exports': self.include_charts_in_exports,
            'auto_email_reports': self.auto_email_reports,
            'email_recipients': self.email_recipients,
            'include_summary_dashboard': self.include_summary_dashboard,
            'password_protect_reports': self.password_protect_reports,
            'track_employee_performance': self.track_employee_performance,
            'track_client_satisfaction': self.track_client_satisfaction,
            'track_job_profitability': self.track_job_profitability,
            'track_equipment_utilization': self.track_equipment_utilization,
            'calculate_labor_efficiency': self.calculate_labor_efficiency,
            'enable_custom_reports': self.enable_custom_reports,
            'max_custom_reports_per_user': self.max_custom_reports_per_user,
            'allow_scheduled_custom_reports': self.allow_scheduled_custom_reports,
            'custom_report_retention_days': self.custom_report_retention_days,
            'anonymize_employee_data': self.anonymize_employee_data,
            'exclude_sensitive_fields': self.exclude_sensitive_fields,
            'require_approval_for_detailed_reports': self.require_approval_for_detailed_reports,
            'audit_report_access': self.audit_report_access,
            'report_cache_duration_hours': self.report_cache_duration_hours,
            'max_report_rows': self.max_report_rows,
            'enable_report_pagination': self.enable_report_pagination,
            'async_report_generation': self.async_report_generation,
            'report_templates': self.report_templates,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class MobileAccessibilitySettings(Base):
    """
    Mobile app and accessibility configuration settings.
    """
    __tablename__ = 'mobile_accessibility_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Mobile App Settings
    mobile_app_enabled = Column(Boolean, default=True, nullable=False)
    force_mobile_app_updates = Column(Boolean, default=False, nullable=False)
    allow_mobile_web_access = Column(Boolean, default=True, nullable=False)
    mobile_session_timeout_minutes = Column(Integer, default=240, nullable=False)

    # Offline Capabilities
    enable_offline_mode = Column(Boolean, default=True, nullable=False)
    offline_data_sync_hours = Column(Integer, default=24, nullable=False)
    cache_shift_schedules = Column(Boolean, default=True, nullable=False)
    cache_employee_directory = Column(Boolean, default=False, nullable=False)
    cache_timesheet_data = Column(Boolean, default=True, nullable=False)

    # Push Notifications
    mobile_push_notifications = Column(Boolean, default=True, nullable=False)
    push_shift_reminders = Column(Boolean, default=True, nullable=False)
    push_schedule_changes = Column(Boolean, default=True, nullable=False)
    push_timesheet_deadlines = Column(Boolean, default=True, nullable=False)
    push_emergency_alerts = Column(Boolean, default=True, nullable=False)
    quiet_hours_start = Column(Time, default=time(22, 0), nullable=False)
    quiet_hours_end = Column(Time, default=time(6, 0), nullable=False)

    # Location Services
    gps_tracking_enabled = Column(Boolean, default=True, nullable=False)
    location_accuracy_meters = Column(Integer, default=50, nullable=False)
    background_location_tracking = Column(Boolean, default=False, nullable=False)
    geofencing_enabled = Column(Boolean, default=True, nullable=False)
    auto_clock_in_geofence = Column(Boolean, default=False, nullable=False)

    # Accessibility Features
    high_contrast_mode = Column(Boolean, default=False, nullable=False)
    large_text_support = Column(Boolean, default=True, nullable=False)
    voice_over_support = Column(Boolean, default=True, nullable=False)
    screen_reader_optimized = Column(Boolean, default=True, nullable=False)
    keyboard_navigation = Column(Boolean, default=True, nullable=False)

    # Visual Accessibility
    font_size_multiplier = Column(Float, default=1.0, nullable=False)
    color_blind_friendly_colors = Column(Boolean, default=False, nullable=False)
    reduce_motion_effects = Column(Boolean, default=False, nullable=False)
    increase_touch_targets = Column(Boolean, default=False, nullable=False)

    # Audio Accessibility
    audio_feedback_enabled = Column(Boolean, default=False, nullable=False)
    notification_sounds = Column(Boolean, default=True, nullable=False)
    haptic_feedback = Column(Boolean, default=True, nullable=False)
    voice_commands_enabled = Column(Boolean, default=False, nullable=False)

    # Language & Localization
    default_language = Column(String(5), default='en', nullable=False)
    auto_detect_language = Column(Boolean, default=True, nullable=False)
    right_to_left_support = Column(Boolean, default=False, nullable=False)
    currency_localization = Column(Boolean, default=True, nullable=False)
    date_format_localization = Column(Boolean, default=True, nullable=False)

    # Device Compatibility
    minimum_ios_version = Column(String(10), default='13.0', nullable=False)
    minimum_android_version = Column(String(10), default='8.0', nullable=False)
    tablet_optimized_layout = Column(Boolean, default=True, nullable=False)
    landscape_mode_support = Column(Boolean, default=True, nullable=False)

    # Security Features
    biometric_authentication = Column(Boolean, default=True, nullable=False)
    pin_code_backup = Column(Boolean, default=True, nullable=False)
    auto_lock_minutes = Column(Integer, default=5, nullable=False)
    screenshot_prevention = Column(Boolean, default=False, nullable=False)
    app_backgrounding_security = Column(Boolean, default=True, nullable=False)

    # Data Usage
    compress_images = Column(Boolean, default=True, nullable=False)
    limit_background_data = Column(Boolean, default=False, nullable=False)
    wifi_only_sync = Column(Boolean, default=False, nullable=False)
    data_usage_warnings = Column(Boolean, default=True, nullable=False)

    # Performance
    image_quality = Column(String(10), default='medium', nullable=False)
    animation_speed = Column(String(10), default='normal', nullable=False)
    preload_next_screens = Column(Boolean, default=True, nullable=False)
    cache_size_mb = Column(Integer, default=100, nullable=False)

    # Supported Languages
    supported_languages = Column(JSON, default=list, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'mobile_app_enabled': self.mobile_app_enabled,
            'force_mobile_app_updates': self.force_mobile_app_updates,
            'allow_mobile_web_access': self.allow_mobile_web_access,
            'mobile_session_timeout_minutes': self.mobile_session_timeout_minutes,
            'enable_offline_mode': self.enable_offline_mode,
            'offline_data_sync_hours': self.offline_data_sync_hours,
            'cache_shift_schedules': self.cache_shift_schedules,
            'cache_employee_directory': self.cache_employee_directory,
            'cache_timesheet_data': self.cache_timesheet_data,
            'mobile_push_notifications': self.mobile_push_notifications,
            'push_shift_reminders': self.push_shift_reminders,
            'push_schedule_changes': self.push_schedule_changes,
            'push_timesheet_deadlines': self.push_timesheet_deadlines,
            'push_emergency_alerts': self.push_emergency_alerts,
            'quiet_hours_start': self.quiet_hours_start.isoformat() if self.quiet_hours_start else None,
            'quiet_hours_end': self.quiet_hours_end.isoformat() if self.quiet_hours_end else None,
            'gps_tracking_enabled': self.gps_tracking_enabled,
            'location_accuracy_meters': self.location_accuracy_meters,
            'background_location_tracking': self.background_location_tracking,
            'geofencing_enabled': self.geofencing_enabled,
            'auto_clock_in_geofence': self.auto_clock_in_geofence,
            'high_contrast_mode': self.high_contrast_mode,
            'large_text_support': self.large_text_support,
            'voice_over_support': self.voice_over_support,
            'screen_reader_optimized': self.screen_reader_optimized,
            'keyboard_navigation': self.keyboard_navigation,
            'font_size_multiplier': self.font_size_multiplier,
            'color_blind_friendly_colors': self.color_blind_friendly_colors,
            'reduce_motion_effects': self.reduce_motion_effects,
            'increase_touch_targets': self.increase_touch_targets,
            'audio_feedback_enabled': self.audio_feedback_enabled,
            'notification_sounds': self.notification_sounds,
            'haptic_feedback': self.haptic_feedback,
            'voice_commands_enabled': self.voice_commands_enabled,
            'default_language': self.default_language,
            'auto_detect_language': self.auto_detect_language,
            'right_to_left_support': self.right_to_left_support,
            'currency_localization': self.currency_localization,
            'date_format_localization': self.date_format_localization,
            'minimum_ios_version': self.minimum_ios_version,
            'minimum_android_version': self.minimum_android_version,
            'tablet_optimized_layout': self.tablet_optimized_layout,
            'landscape_mode_support': self.landscape_mode_support,
            'biometric_authentication': self.biometric_authentication,
            'pin_code_backup': self.pin_code_backup,
            'auto_lock_minutes': self.auto_lock_minutes,
            'screenshot_prevention': self.screenshot_prevention,
            'app_backgrounding_security': self.app_backgrounding_security,
            'compress_images': self.compress_images,
            'limit_background_data': self.limit_background_data,
            'wifi_only_sync': self.wifi_only_sync,
            'data_usage_warnings': self.data_usage_warnings,
            'image_quality': self.image_quality,
            'animation_speed': self.animation_speed,
            'preload_next_screens': self.preload_next_screens,
            'cache_size_mb': self.cache_size_mb,
            'supported_languages': self.supported_languages,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class SystemAdminSettings(Base):
    """
    System administration and maintenance settings.
    """
    __tablename__ = 'system_admin_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Backup & Recovery
    auto_backup_enabled = Column(Boolean, default=True, nullable=False)
    backup_frequency = Column(String(20), default='daily', nullable=False)
    backup_time = Column(Time, default=time(2, 0), nullable=False)
    backup_retention_days = Column(Integer, default=30, nullable=False)
    cloud_backup_enabled = Column(Boolean, default=True, nullable=False)
    local_backup_enabled = Column(Boolean, default=False, nullable=False)

    # Database Maintenance
    auto_optimize_database = Column(Boolean, default=True, nullable=False)
    database_cleanup_frequency = Column(String(20), default='weekly', nullable=False)
    purge_old_logs_days = Column(Integer, default=90, nullable=False)
    compress_old_data = Column(Boolean, default=True, nullable=False)
    vacuum_database = Column(Boolean, default=True, nullable=False)

    # System Monitoring
    system_health_monitoring = Column(Boolean, default=True, nullable=False)
    performance_monitoring = Column(Boolean, default=True, nullable=False)
    error_tracking = Column(Boolean, default=True, nullable=False)
    uptime_monitoring = Column(Boolean, default=True, nullable=False)
    resource_usage_alerts = Column(Boolean, default=True, nullable=False)

    # Audit Logging
    audit_logging_enabled = Column(Boolean, default=True, nullable=False)
    log_user_actions = Column(Boolean, default=True, nullable=False)
    log_data_changes = Column(Boolean, default=True, nullable=False)
    log_system_events = Column(Boolean, default=True, nullable=False)
    log_security_events = Column(Boolean, default=True, nullable=False)
    audit_log_retention_years = Column(Integer, default=7, nullable=False)

    # Security Settings
    enable_rate_limiting = Column(Boolean, default=True, nullable=False)
    max_requests_per_minute = Column(Integer, default=100, nullable=False)
    enable_ip_whitelisting = Column(Boolean, default=False, nullable=False)
    blocked_ip_addresses = Column(JSON, default=list, nullable=False)
    security_scan_frequency = Column(String(20), default='weekly', nullable=False)

    # System Limits
    max_concurrent_users = Column(Integer, default=500, nullable=False)
    max_file_upload_size_mb = Column(Integer, default=10, nullable=False)
    session_timeout_minutes = Column(Integer, default=480, nullable=False)
    api_timeout_seconds = Column(Integer, default=30, nullable=False)
    max_database_connections = Column(Integer, default=100, nullable=False)

    # Maintenance Mode
    maintenance_mode_enabled = Column(Boolean, default=False, nullable=False)
    maintenance_message = Column(Text, default='System is currently under maintenance. Please try again later.', nullable=False)
    allow_admin_access_during_maintenance = Column(Boolean, default=True, nullable=False)
    scheduled_maintenance_notifications = Column(Boolean, default=True, nullable=False)

    # Email System
    email_service_provider = Column(String(20), default='smtp', nullable=False)
    smtp_server = Column(String(255), nullable=True)
    smtp_port = Column(Integer, default=587, nullable=False)
    smtp_username = Column(String(255), nullable=True)
    smtp_password = Column(String(255), nullable=True)
    email_rate_limit_per_hour = Column(Integer, default=1000, nullable=False)

    # API Configuration
    api_versioning_enabled = Column(Boolean, default=True, nullable=False)
    current_api_version = Column(String(10), default='v1', nullable=False)
    deprecated_api_support = Column(Boolean, default=True, nullable=False)
    api_documentation_enabled = Column(Boolean, default=True, nullable=False)
    cors_enabled = Column(Boolean, default=True, nullable=False)
    allowed_origins = Column(JSON, default=list, nullable=False)

    # Caching
    redis_caching_enabled = Column(Boolean, default=False, nullable=False)
    cache_ttl_minutes = Column(Integer, default=60, nullable=False)
    cache_user_sessions = Column(Boolean, default=True, nullable=False)
    cache_database_queries = Column(Boolean, default=True, nullable=False)
    cache_static_content = Column(Boolean, default=True, nullable=False)

    # Error Handling
    detailed_error_messages = Column(Boolean, default=False, nullable=False)
    error_notification_emails = Column(Boolean, default=True, nullable=False)
    error_notification_recipients = Column(JSON, default=list, nullable=False)
    automatic_error_reporting = Column(Boolean, default=True, nullable=False)

    # System Updates
    auto_update_enabled = Column(Boolean, default=False, nullable=False)
    update_check_frequency = Column(String(20), default='weekly', nullable=False)
    beta_updates_enabled = Column(Boolean, default=False, nullable=False)
    update_notification_emails = Column(Boolean, default=True, nullable=False)

    # Data Export/Import
    allow_data_export = Column(Boolean, default=True, nullable=False)
    export_rate_limit_per_day = Column(Integer, default=10, nullable=False)
    allow_bulk_import = Column(Boolean, default=True, nullable=False)
    import_validation_strict = Column(Boolean, default=True, nullable=False)

    # Compliance
    gdpr_compliance_mode = Column(Boolean, default=True, nullable=False)
    data_anonymization_enabled = Column(Boolean, default=False, nullable=False)
    right_to_be_forgotten_enabled = Column(Boolean, default=True, nullable=False)
    consent_tracking_enabled = Column(Boolean, default=True, nullable=False)

    # System Status
    system_status = Column(JSON, default=dict, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'auto_backup_enabled': self.auto_backup_enabled,
            'backup_frequency': self.backup_frequency,
            'backup_time': self.backup_time.isoformat() if self.backup_time else None,
            'backup_retention_days': self.backup_retention_days,
            'cloud_backup_enabled': self.cloud_backup_enabled,
            'local_backup_enabled': self.local_backup_enabled,
            'auto_optimize_database': self.auto_optimize_database,
            'database_cleanup_frequency': self.database_cleanup_frequency,
            'purge_old_logs_days': self.purge_old_logs_days,
            'compress_old_data': self.compress_old_data,
            'vacuum_database': self.vacuum_database,
            'system_health_monitoring': self.system_health_monitoring,
            'performance_monitoring': self.performance_monitoring,
            'error_tracking': self.error_tracking,
            'uptime_monitoring': self.uptime_monitoring,
            'resource_usage_alerts': self.resource_usage_alerts,
            'audit_logging_enabled': self.audit_logging_enabled,
            'log_user_actions': self.log_user_actions,
            'log_data_changes': self.log_data_changes,
            'log_system_events': self.log_system_events,
            'log_security_events': self.log_security_events,
            'audit_log_retention_years': self.audit_log_retention_years,
            'enable_rate_limiting': self.enable_rate_limiting,
            'max_requests_per_minute': self.max_requests_per_minute,
            'enable_ip_whitelisting': self.enable_ip_whitelisting,
            'blocked_ip_addresses': self.blocked_ip_addresses,
            'security_scan_frequency': self.security_scan_frequency,
            'max_concurrent_users': self.max_concurrent_users,
            'max_file_upload_size_mb': self.max_file_upload_size_mb,
            'session_timeout_minutes': self.session_timeout_minutes,
            'api_timeout_seconds': self.api_timeout_seconds,
            'max_database_connections': self.max_database_connections,
            'maintenance_mode_enabled': self.maintenance_mode_enabled,
            'maintenance_message': self.maintenance_message,
            'allow_admin_access_during_maintenance': self.allow_admin_access_during_maintenance,
            'scheduled_maintenance_notifications': self.scheduled_maintenance_notifications,
            'email_service_provider': self.email_service_provider,
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'smtp_username': self.smtp_username,
            'smtp_password': self.smtp_password,
            'email_rate_limit_per_hour': self.email_rate_limit_per_hour,
            'api_versioning_enabled': self.api_versioning_enabled,
            'current_api_version': self.current_api_version,
            'deprecated_api_support': self.deprecated_api_support,
            'api_documentation_enabled': self.api_documentation_enabled,
            'cors_enabled': self.cors_enabled,
            'allowed_origins': self.allowed_origins,
            'redis_caching_enabled': self.redis_caching_enabled,
            'cache_ttl_minutes': self.cache_ttl_minutes,
            'cache_user_sessions': self.cache_user_sessions,
            'cache_database_queries': self.cache_database_queries,
            'cache_static_content': self.cache_static_content,
            'detailed_error_messages': self.detailed_error_messages,
            'error_notification_emails': self.error_notification_emails,
            'error_notification_recipients': self.error_notification_recipients,
            'automatic_error_reporting': self.automatic_error_reporting,
            'auto_update_enabled': self.auto_update_enabled,
            'update_check_frequency': self.update_check_frequency,
            'beta_updates_enabled': self.beta_updates_enabled,
            'update_notification_emails': self.update_notification_emails,
            'allow_data_export': self.allow_data_export,
            'export_rate_limit_per_day': self.export_rate_limit_per_day,
            'allow_bulk_import': self.allow_bulk_import,
            'import_validation_strict': self.import_validation_strict,
            'gdpr_compliance_mode': self.gdpr_compliance_mode,
            'data_anonymization_enabled': self.data_anonymization_enabled,
            'right_to_be_forgotten_enabled': self.right_to_be_forgotten_enabled,
            'consent_tracking_enabled': self.consent_tracking_enabled,
            'system_status': self.system_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
