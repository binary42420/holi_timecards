"""
Extended settings models for EasyShifts application.
These models support the expanded settings functionality.
"""

from datetime import time
from sqlalchemy import Column, String, Boolean, Date, Enum, PrimaryKeyConstraint, ForeignKey, DateTime, JSON, func, \
    Integer, Float, Text, Time
from sqlalchemy.orm import relationship
from .models import Base


class JobConfigurationSettings(Base):
    """
    Job and shift configuration settings.
    """
    __tablename__ = 'job_configuration_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Job Templates
    enable_job_templates = Column(Boolean, default=True, nullable=False)
    default_job_duration_hours = Column(Integer, default=8, nullable=False)
    allow_multi_day_jobs = Column(Boolean, default=True, nullable=False)
    max_job_duration_days = Column(Integer, default=30, nullable=False)

    # Shift Configuration
    default_shift_duration_hours = Column(Integer, default=8, nullable=False)
    min_shift_duration_hours = Column(Integer, default=2, nullable=False)
    max_shift_duration_hours = Column(Integer, default=16, nullable=False)
    allow_split_shifts = Column(Boolean, default=True, nullable=False)
    break_duration_minutes = Column(Integer, default=30, nullable=False)
    lunch_break_duration_minutes = Column(Integer, default=60, nullable=False)
    max_breaks_per_shift = Column(Integer, default=3, nullable=False)

    # Role Requirements
    require_crew_chief_per_shift = Column(Boolean, default=True, nullable=False)
    max_workers_per_crew_chief = Column(Integer, default=8, nullable=False)
    allow_role_upgrades_during_shift = Column(Boolean, default=True, nullable=False)
    require_role_certification_verification = Column(Boolean, default=True, nullable=False)

    # Location Management
    require_job_location = Column(Boolean, default=True, nullable=False)
    allow_multiple_locations_per_job = Column(Boolean, default=False, nullable=False)
    require_location_coordinates = Column(Boolean, default=True, nullable=False)
    default_setup_time_minutes = Column(Integer, default=30, nullable=False)
    default_teardown_time_minutes = Column(Integer, default=30, nullable=False)

    # Equipment & Resources
    track_equipment_usage = Column(Boolean, default=True, nullable=False)
    require_equipment_checkout = Column(Boolean, default=False, nullable=False)
    allow_equipment_requests = Column(Boolean, default=True, nullable=False)
    require_safety_equipment = Column(Boolean, default=True, nullable=False)

    # Scheduling Rules
    min_notice_hours_new_jobs = Column(Integer, default=24, nullable=False)
    max_advance_scheduling_days = Column(Integer, default=90, nullable=False)
    allow_overlapping_shifts = Column(Boolean, default=False, nullable=False)
    require_rest_period_between_shifts = Column(Boolean, default=True, nullable=False)
    min_rest_period_hours = Column(Integer, default=8, nullable=False)

    # Worker Assignment
    auto_assign_workers = Column(Boolean, default=False, nullable=False)
    assignment_priority = Column(String(20), default='seniority', nullable=False)
    allow_worker_preferences = Column(Boolean, default=True, nullable=False)
    respect_worker_availability = Column(Boolean, default=True, nullable=False)

    # Job Status Management
    auto_activate_jobs = Column(Boolean, default=False, nullable=False)
    require_manager_approval = Column(Boolean, default=True, nullable=False)
    allow_job_modifications_after_approval = Column(Boolean, default=False, nullable=False)
    auto_close_completed_jobs = Column(Boolean, default=True, nullable=False)

    # Quality Control
    require_job_photos = Column(Boolean, default=True, nullable=False)
    require_completion_checklist = Column(Boolean, default=False, nullable=False)
    require_client_sign_off = Column(Boolean, default=False, nullable=False)
    track_job_performance_metrics = Column(Boolean, default=True, nullable=False)

    # Emergency Procedures
    require_emergency_contact_info = Column(Boolean, default=True, nullable=False)
    require_safety_briefing = Column(Boolean, default=True, nullable=False)
    emergency_evacuation_procedures = Column(Boolean, default=True, nullable=False)
    incident_reporting_required = Column(Boolean, default=True, nullable=False)

    # Job Templates and Equipment Categories
    job_templates = Column(JSON, default=list, nullable=False)
    equipment_categories = Column(JSON, default=list, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'enable_job_templates': self.enable_job_templates,
            'default_job_duration_hours': self.default_job_duration_hours,
            'allow_multi_day_jobs': self.allow_multi_day_jobs,
            'max_job_duration_days': self.max_job_duration_days,
            'default_shift_duration_hours': self.default_shift_duration_hours,
            'min_shift_duration_hours': self.min_shift_duration_hours,
            'max_shift_duration_hours': self.max_shift_duration_hours,
            'allow_split_shifts': self.allow_split_shifts,
            'break_duration_minutes': self.break_duration_minutes,
            'lunch_break_duration_minutes': self.lunch_break_duration_minutes,
            'max_breaks_per_shift': self.max_breaks_per_shift,
            'require_crew_chief_per_shift': self.require_crew_chief_per_shift,
            'max_workers_per_crew_chief': self.max_workers_per_crew_chief,
            'allow_role_upgrades_during_shift': self.allow_role_upgrades_during_shift,
            'require_role_certification_verification': self.require_role_certification_verification,
            'require_job_location': self.require_job_location,
            'allow_multiple_locations_per_job': self.allow_multiple_locations_per_job,
            'require_location_coordinates': self.require_location_coordinates,
            'default_setup_time_minutes': self.default_setup_time_minutes,
            'default_teardown_time_minutes': self.default_teardown_time_minutes,
            'track_equipment_usage': self.track_equipment_usage,
            'require_equipment_checkout': self.require_equipment_checkout,
            'allow_equipment_requests': self.allow_equipment_requests,
            'require_safety_equipment': self.require_safety_equipment,
            'min_notice_hours_new_jobs': self.min_notice_hours_new_jobs,
            'max_advance_scheduling_days': self.max_advance_scheduling_days,
            'allow_overlapping_shifts': self.allow_overlapping_shifts,
            'require_rest_period_between_shifts': self.require_rest_period_between_shifts,
            'min_rest_period_hours': self.min_rest_period_hours,
            'auto_assign_workers': self.auto_assign_workers,
            'assignment_priority': self.assignment_priority,
            'allow_worker_preferences': self.allow_worker_preferences,
            'respect_worker_availability': self.respect_worker_availability,
            'auto_activate_jobs': self.auto_activate_jobs,
            'require_manager_approval': self.require_manager_approval,
            'allow_job_modifications_after_approval': self.allow_job_modifications_after_approval,
            'auto_close_completed_jobs': self.auto_close_completed_jobs,
            'require_job_photos': self.require_job_photos,
            'require_completion_checklist': self.require_completion_checklist,
            'require_client_sign_off': self.require_client_sign_off,
            'track_job_performance_metrics': self.track_job_performance_metrics,
            'require_emergency_contact_info': self.require_emergency_contact_info,
            'require_safety_briefing': self.require_safety_briefing,
            'emergency_evacuation_procedures': self.emergency_evacuation_procedures,
            'incident_reporting_required': self.incident_reporting_required,
            'job_templates': self.job_templates,
            'equipment_categories': self.equipment_categories,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class TimesheetAdvancedSettings(Base):
    """
    Advanced timesheet management settings.
    """
    __tablename__ = 'timesheet_advanced_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Clock In/Out Rules
    require_photo_clock_in = Column(Boolean, default=False, nullable=False)
    require_location_verification = Column(Boolean, default=True, nullable=False)
    location_verification_radius_feet = Column(Integer, default=100, nullable=False)
    allow_early_clock_in_minutes = Column(Integer, default=15, nullable=False)
    allow_late_clock_out_minutes = Column(Integer, default=15, nullable=False)
    auto_clock_out_hours = Column(Integer, default=12, nullable=False)

    # Multiple Clock In/Out Support
    max_clock_pairs_per_shift = Column(Integer, default=3, nullable=False)
    require_break_documentation = Column(Boolean, default=True, nullable=False)
    auto_deduct_unpaid_breaks = Column(Boolean, default=True, nullable=False)
    unpaid_break_threshold_minutes = Column(Integer, default=30, nullable=False)

    # Overtime Policies
    overtime_threshold_daily = Column(Integer, default=8, nullable=False)
    overtime_threshold_weekly = Column(Integer, default=40, nullable=False)
    overtime_rate_multiplier = Column(Float, default=1.5, nullable=False)
    double_time_threshold_daily = Column(Integer, default=12, nullable=False)
    double_time_rate_multiplier = Column(Float, default=2.0, nullable=False)
    weekend_overtime_enabled = Column(Boolean, default=False, nullable=False)
    holiday_overtime_enabled = Column(Boolean, default=True, nullable=False)

    # Approval Workflows
    require_manager_approval = Column(Boolean, default=True, nullable=False)
    require_client_approval = Column(Boolean, default=False, nullable=False)
    auto_approve_regular_hours = Column(Boolean, default=False, nullable=False)
    auto_approve_overtime = Column(Boolean, default=False, nullable=False)
    approval_timeout_hours = Column(Integer, default=48, nullable=False)
    escalate_unapproved_timesheets = Column(Boolean, default=True, nullable=False)

    # Time Tracking Accuracy
    round_time_to_nearest_minutes = Column(Integer, default=15, nullable=False)
    allow_manual_time_adjustments = Column(Boolean, default=True, nullable=False)
    require_adjustment_justification = Column(Boolean, default=True, nullable=False)
    track_gps_location = Column(Boolean, default=True, nullable=False)
    require_supervisor_witness = Column(Boolean, default=False, nullable=False)

    # Crew Chief Permissions
    crew_chiefs_can_edit_team_times = Column(Boolean, default=True, nullable=False)
    crew_chiefs_can_mark_absent = Column(Boolean, default=True, nullable=False)
    crew_chiefs_can_add_notes = Column(Boolean, default=True, nullable=False)
    crew_chiefs_can_approve_breaks = Column(Boolean, default=True, nullable=False)
    crew_chiefs_can_end_shift_for_all = Column(Boolean, default=True, nullable=False)

    # Client Access
    clients_can_view_timesheets = Column(Boolean, default=True, nullable=False)
    clients_can_edit_timesheets = Column(Boolean, default=False, nullable=False)
    clients_can_dispute_hours = Column(Boolean, default=True, nullable=False)
    clients_can_add_timesheet_notes = Column(Boolean, default=True, nullable=False)
    show_worker_names_to_clients = Column(Boolean, default=True, nullable=False)

    # Payroll Integration
    export_format = Column(String(10), default='csv', nullable=False)
    include_break_details = Column(Boolean, default=True, nullable=False)
    include_location_data = Column(Boolean, default=False, nullable=False)
    include_photo_timestamps = Column(Boolean, default=False, nullable=False)
    auto_calculate_taxes = Column(Boolean, default=False, nullable=False)

    # Compliance & Auditing
    retain_timesheet_data_years = Column(Integer, default=7, nullable=False)
    require_digital_signatures = Column(Boolean, default=False, nullable=False)
    track_all_timesheet_changes = Column(Boolean, default=True, nullable=False)
    require_change_justification = Column(Boolean, default=True, nullable=False)
    audit_log_retention_years = Column(Integer, default=10, nullable=False)

    # Notifications
    notify_late_clock_in = Column(Boolean, default=True, nullable=False)
    notify_missed_clock_out = Column(Boolean, default=True, nullable=False)
    notify_overtime_threshold = Column(Boolean, default=True, nullable=False)
    notify_approval_required = Column(Boolean, default=True, nullable=False)
    send_daily_timesheet_summary = Column(Boolean, default=False, nullable=False)

    # Mobile & Offline
    allow_offline_time_entry = Column(Boolean, default=True, nullable=False)
    sync_when_online = Column(Boolean, default=True, nullable=False)
    offline_data_retention_days = Column(Integer, default=7, nullable=False)
    require_network_for_clock_in = Column(Boolean, default=False, nullable=False)

    # Payroll Export Fields
    payroll_export_fields = Column(JSON, default=list, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'require_photo_clock_in': self.require_photo_clock_in,
            'require_location_verification': self.require_location_verification,
            'location_verification_radius_feet': self.location_verification_radius_feet,
            'allow_early_clock_in_minutes': self.allow_early_clock_in_minutes,
            'allow_late_clock_out_minutes': self.allow_late_clock_out_minutes,
            'auto_clock_out_hours': self.auto_clock_out_hours,
            'max_clock_pairs_per_shift': self.max_clock_pairs_per_shift,
            'require_break_documentation': self.require_break_documentation,
            'auto_deduct_unpaid_breaks': self.auto_deduct_unpaid_breaks,
            'unpaid_break_threshold_minutes': self.unpaid_break_threshold_minutes,
            'overtime_threshold_daily': self.overtime_threshold_daily,
            'overtime_threshold_weekly': self.overtime_threshold_weekly,
            'overtime_rate_multiplier': self.overtime_rate_multiplier,
            'double_time_threshold_daily': self.double_time_threshold_daily,
            'double_time_rate_multiplier': self.double_time_rate_multiplier,
            'weekend_overtime_enabled': self.weekend_overtime_enabled,
            'holiday_overtime_enabled': self.holiday_overtime_enabled,
            'require_manager_approval': self.require_manager_approval,
            'require_client_approval': self.require_client_approval,
            'auto_approve_regular_hours': self.auto_approve_regular_hours,
            'auto_approve_overtime': self.auto_approve_overtime,
            'approval_timeout_hours': self.approval_timeout_hours,
            'escalate_unapproved_timesheets': self.escalate_unapproved_timesheets,
            'round_time_to_nearest_minutes': self.round_time_to_nearest_minutes,
            'allow_manual_time_adjustments': self.allow_manual_time_adjustments,
            'require_adjustment_justification': self.require_adjustment_justification,
            'track_gps_location': self.track_gps_location,
            'require_supervisor_witness': self.require_supervisor_witness,
            'crew_chiefs_can_edit_team_times': self.crew_chiefs_can_edit_team_times,
            'crew_chiefs_can_mark_absent': self.crew_chiefs_can_mark_absent,
            'crew_chiefs_can_add_notes': self.crew_chiefs_can_add_notes,
            'crew_chiefs_can_approve_breaks': self.crew_chiefs_can_approve_breaks,
            'crew_chiefs_can_end_shift_for_all': self.crew_chiefs_can_end_shift_for_all,
            'clients_can_view_timesheets': self.clients_can_view_timesheets,
            'clients_can_edit_timesheets': self.clients_can_edit_timesheets,
            'clients_can_dispute_hours': self.clients_can_dispute_hours,
            'clients_can_add_timesheet_notes': self.clients_can_add_timesheet_notes,
            'show_worker_names_to_clients': self.show_worker_names_to_clients,
            'export_format': self.export_format,
            'include_break_details': self.include_break_details,
            'include_location_data': self.include_location_data,
            'include_photo_timestamps': self.include_photo_timestamps,
            'auto_calculate_taxes': self.auto_calculate_taxes,
            'retain_timesheet_data_years': self.retain_timesheet_data_years,
            'require_digital_signatures': self.require_digital_signatures,
            'track_all_timesheet_changes': self.track_all_timesheet_changes,
            'require_change_justification': self.require_change_justification,
            'audit_log_retention_years': self.audit_log_retention_years,
            'notify_late_clock_in': self.notify_late_clock_in,
            'notify_missed_clock_out': self.notify_missed_clock_out,
            'notify_overtime_threshold': self.notify_overtime_threshold,
            'notify_approval_required': self.notify_approval_required,
            'send_daily_timesheet_summary': self.send_daily_timesheet_summary,
            'allow_offline_time_entry': self.allow_offline_time_entry,
            'sync_when_online': self.sync_when_online,
            'offline_data_retention_days': self.offline_data_retention_days,
            'require_network_for_clock_in': self.require_network_for_clock_in,
            'payroll_export_fields': self.payroll_export_fields,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class GoogleIntegrationSettings(Base):
    """
    Google services integration settings.
    """
    __tablename__ = 'google_integration_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # OAuth Configuration
    google_oauth_enabled = Column(Boolean, default=True, nullable=False)
    google_client_id = Column(String(255), nullable=True)
    google_client_secret = Column(String(255), nullable=True)
    oauth_redirect_uri = Column(String(500), default='https://easyshifts.app/auth/google/callback', nullable=False)

    # Calendar Integration
    google_calendar_sync_enabled = Column(Boolean, default=False, nullable=False)
    calendar_sync_direction = Column(String(20), default='both', nullable=False)
    default_calendar_name = Column(String(255), default='EasyShifts Work Schedule', nullable=False)
    sync_shift_assignments = Column(Boolean, default=True, nullable=False)
    sync_shift_requests = Column(Boolean, default=False, nullable=False)
    sync_timesheet_deadlines = Column(Boolean, default=True, nullable=False)

    # Gmail Integration
    gmail_notifications_enabled = Column(Boolean, default=False, nullable=False)
    gmail_send_from_address = Column(String(255), default='noreply@handsonlabor.com', nullable=False)
    gmail_template_style = Column(String(20), default='professional', nullable=False)
    include_company_branding = Column(Boolean, default=True, nullable=False)

    # Google Drive Integration
    google_drive_enabled = Column(Boolean, default=False, nullable=False)
    drive_folder_structure = Column(String(20), default='by_date', nullable=False)
    auto_backup_timesheets = Column(Boolean, default=False, nullable=False)
    auto_backup_schedules = Column(Boolean, default=False, nullable=False)
    backup_frequency = Column(String(20), default='weekly', nullable=False)

    # Google Maps Integration
    google_maps_enabled = Column(Boolean, default=True, nullable=False)
    maps_api_key = Column(String(255), nullable=True)
    show_job_locations_on_map = Column(Boolean, default=True, nullable=False)
    calculate_travel_distances = Column(Boolean, default=True, nullable=False)
    optimize_route_planning = Column(Boolean, default=False, nullable=False)

    # Google Workspace Integration
    workspace_domain = Column(String(255), nullable=True)
    restrict_to_workspace_domain = Column(Boolean, default=False, nullable=False)
    auto_create_workspace_users = Column(Boolean, default=False, nullable=False)
    sync_workspace_contacts = Column(Boolean, default=False, nullable=False)

    # Authentication Settings
    allow_google_signup = Column(Boolean, default=True, nullable=False)
    require_email_verification = Column(Boolean, default=True, nullable=False)
    auto_link_existing_accounts = Column(Boolean, default=True, nullable=False)
    google_profile_photo_sync = Column(Boolean, default=True, nullable=False)

    # Data Sync Settings
    sync_frequency_minutes = Column(Integer, default=15, nullable=False)
    sync_during_business_hours_only = Column(Boolean, default=False, nullable=False)
    business_hours_start = Column(Time, default=time(6, 0), nullable=False)
    business_hours_end = Column(Time, default=time(22, 0), nullable=False)

    # Privacy & Security
    store_google_tokens_encrypted = Column(Boolean, default=True, nullable=False)
    token_refresh_threshold_days = Column(Integer, default=7, nullable=False)
    revoke_tokens_on_deactivation = Column(Boolean, default=True, nullable=False)
    audit_google_api_calls = Column(Boolean, default=True, nullable=False)

    # Error Handling
    retry_failed_syncs = Column(Boolean, default=True, nullable=False)
    max_retry_attempts = Column(Integer, default=3, nullable=False)
    sync_error_notifications = Column(Boolean, default=True, nullable=False)
    fallback_to_manual_entry = Column(Boolean, default=True, nullable=False)

    # Sync Status
    sync_status = Column(JSON, default=dict, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'google_oauth_enabled': self.google_oauth_enabled,
            'google_client_id': self.google_client_id,
            'google_client_secret': self.google_client_secret,
            'oauth_redirect_uri': self.oauth_redirect_uri,
            'google_calendar_sync_enabled': self.google_calendar_sync_enabled,
            'calendar_sync_direction': self.calendar_sync_direction,
            'default_calendar_name': self.default_calendar_name,
            'sync_shift_assignments': self.sync_shift_assignments,
            'sync_shift_requests': self.sync_shift_requests,
            'sync_timesheet_deadlines': self.sync_timesheet_deadlines,
            'gmail_notifications_enabled': self.gmail_notifications_enabled,
            'gmail_send_from_address': self.gmail_send_from_address,
            'gmail_template_style': self.gmail_template_style,
            'include_company_branding': self.include_company_branding,
            'google_drive_enabled': self.google_drive_enabled,
            'drive_folder_structure': self.drive_folder_structure,
            'auto_backup_timesheets': self.auto_backup_timesheets,
            'auto_backup_schedules': self.auto_backup_schedules,
            'backup_frequency': self.backup_frequency,
            'google_maps_enabled': self.google_maps_enabled,
            'maps_api_key': self.maps_api_key,
            'show_job_locations_on_map': self.show_job_locations_on_map,
            'calculate_travel_distances': self.calculate_travel_distances,
            'optimize_route_planning': self.optimize_route_planning,
            'workspace_domain': self.workspace_domain,
            'restrict_to_workspace_domain': self.restrict_to_workspace_domain,
            'auto_create_workspace_users': self.auto_create_workspace_users,
            'sync_workspace_contacts': self.sync_workspace_contacts,
            'allow_google_signup': self.allow_google_signup,
            'require_email_verification': self.require_email_verification,
            'auto_link_existing_accounts': self.auto_link_existing_accounts,
            'google_profile_photo_sync': self.google_profile_photo_sync,
            'sync_frequency_minutes': self.sync_frequency_minutes,
            'sync_during_business_hours_only': self.sync_during_business_hours_only,
            'business_hours_start': self.business_hours_start.isoformat() if self.business_hours_start else None,
            'business_hours_end': self.business_hours_end.isoformat() if self.business_hours_end else None,
            'store_google_tokens_encrypted': self.store_google_tokens_encrypted,
            'token_refresh_threshold_days': self.token_refresh_threshold_days,
            'revoke_tokens_on_deactivation': self.revoke_tokens_on_deactivation,
            'audit_google_api_calls': self.audit_google_api_calls,
            'retry_failed_syncs': self.retry_failed_syncs,
            'max_retry_attempts': self.max_retry_attempts,
            'sync_error_notifications': self.sync_error_notifications,
            'fallback_to_manual_entry': self.fallback_to_manual_entry,
            'sync_status': self.sync_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
