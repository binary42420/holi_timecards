import datetime
from datetime import time
from sqlalchemy import Column, String, Boolean, Date, Enum, PrimaryKeyConstraint, ForeignKey, DateTime, JSON, func, \
    Integer, Float, Text, Time
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4
import enum

Base = declarative_base()

NAMES_LEN = 20
PASS_LEN = 50
ID_LEN = 500
REQUEST_LEN = 255


class EmployeeType(enum.Enum):
    """Represents different types/roles of employees within the agency."""
    CREW_CHIEF = 'crew_chief'
    STAGEHAND = 'stagehand'
    FORK_OPERATOR = 'fork_operator'
    PICKUP_TRUCK_DRIVER = 'pickup_truck_driver'
    # Add other employee types as needed
    GENERAL_EMPLOYEE = 'general_employee'


class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id (str): Unique identifier for the user.
        username (str): User's unique username.
        password (str): User's password.
        isManager (bool): Indicates if the user is a manager within the agency.
        isAdmin (bool): Indicates if the user is an admin within the agency.
        client_company_id (int): Foreign key to client_companies. If set, user is a client representative.
        isActive (bool): Indicates if the user account is active. Default is True.
        isApproval (bool): Indicates if the user is approved. Default is False.
        name (str): User's name or display name.
        employee_type (EmployeeType): The type or role of the agency employee. Null for clients or some admins.
        google_id (str): Google OAuth unique identifier. Null if not linked to Google account.
        email (str): User's email address. Required for Google OAuth users.
        google_picture (str): URL to user's Google profile picture.
        last_login (DateTime): Timestamp of user's last login.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, nullable=False)  # userID
    username = Column(String(NAMES_LEN), unique=True, nullable=False)
    password = Column(String(PASS_LEN), nullable=True)  # Made nullable for Google OAuth users
    isManager = Column(Boolean, nullable=False, default=False)
    isAdmin = Column(Boolean, nullable=False, default=False)
    client_company_id = Column(Integer, ForeignKey('client_companies.id'), nullable=True)
    isActive = Column(Boolean, nullable=False, default=True)
    isApproval = Column(Boolean, nullable=False, default=False)
    name = Column(String(NAMES_LEN), nullable=False)
    employee_type = Column(Enum(EmployeeType), nullable=True)

    # Google OAuth fields
    google_id = Column(String(100), unique=True, nullable=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    google_picture = Column(String(500), nullable=True)
    last_login = Column(DateTime, nullable=True)

    # Soft delete fields
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    certifications = relationship("EmployeeCertification", back_populates="user", uselist=False)


class ClientCompany(Base):
    """
    Represents a client company.

    Attributes:
        id (int): Unique identifier for the client company.
        name (str): Name of the client company.
    """
    __tablename__ = "client_companies"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String(NAMES_LEN * 2), unique=True, nullable=False)
    # Add other client company details here, e.g., address, contact_person

    # Soft delete fields
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)


class Job(Base):
    """
    Represents a specific project at a specific venue for Hands on Labor staffing agency.
    Each job is tied to one location - if location changes, create a new job.

    Attributes:
        id (int): Unique identifier for the job.
        name (str): Name of the job/project.
        client_company_id (int): Foreign key to the client company.
        description (str): Optional description of the job.

        # Location information (job-level, inherited by all shifts)
        venue_name (str): Name of the venue where ALL shifts for this job take place.
        venue_address (str): Address of the venue.
        venue_contact_info (str): Contact information for the venue.

        # Job metadata
        created_by (int): ID of the manager who created this job (for tracking).
        created_at (DateTime): When the job was created.
        is_active (bool): Whether the job is currently active.
        estimated_start_date (Date): Expected start date of the job.
        estimated_end_date (Date): Expected end date of the job.
    """
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String(NAMES_LEN * 2), nullable=False)
    client_company_id = Column(Integer, ForeignKey('client_companies.id'), nullable=False)
    description = Column(String(500), nullable=True)

    # Location information - ALL shifts inherit this location
    venue_name = Column(String(200), nullable=False)
    venue_address = Column(String(500), nullable=False)
    venue_contact_info = Column(String(300), nullable=True)

    # Job metadata
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    estimated_start_date = Column(Date, nullable=True)
    estimated_end_date = Column(Date, nullable=True)

    # Soft delete fields
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)


# WorkPlace model removed - not needed for Hands on Labor single company system


class UserRequest(Base):
    """
    Represents user request for shifts (typically from agency employees).

    Attributes:
        id (str): Unique identifier for the user that send the request.
        modifyAt (DateTime): Date and time of the modification.
        requests (str): User's request details.
    """
    __tablename__ = "userRequests"

    id = Column(Integer, ForeignKey('users.id'), primary_key=True, index=True)  # userID
    modifyAt = Column(DateTime)
    requests = Column(String(REQUEST_LEN))


class ShiftPart(enum.Enum):
    """Represents possible shift parts."""
    Morning = 'morning'
    Noon = 'noon'
    Evening = 'evening'


class Shift(Base):
    """
    Represents shifts in the system for Hands on Labor.
    Each shift belongs to a job and inherits the job's location.

    Attributes:
        id (int): Unique identifier for the shift.
        job_id (int): Identifier for the associated job (location inherited from job).
        shift_start_datetime (DateTime): Start date and time of the shift.
        shift_end_datetime (DateTime): End date and time of the shift (optional).
        required_employee_counts (JSON): Stores the number of each employee type required for the shift.
                                         Example: {"stagehand": 5, "crew_chief": 1}
        client_po_number (str): Client's Purchase Order number related to this shift.
        shift_description (str): Description of what this specific shift involves (e.g., "Setup Day", "Event Day", "Teardown").
        special_instructions (str): Any special instructions specific to this shift.

        # Legacy fields for backward compatibility
        shiftDate (Date): DEPRECATED - Use shift_start_datetime instead.
        shiftPart (str): DEPRECATED - Use shift_start_datetime instead.

        # Note: Location fields removed - inherited from job
    """
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True, nullable=False)  # shiftID
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)

    # Datetime fields
    shift_start_datetime = Column(DateTime, nullable=True)  # Will become required after migration
    shift_end_datetime = Column(DateTime, nullable=True)

    # Legacy fields for backward compatibility
    shiftDate = Column(Date, nullable=True)  # Made nullable for migration
    shiftPart = Column(Enum(ShiftPart), nullable=True)  # Made nullable for migration

    # Shift-specific information
    required_employee_counts = Column(JSON, nullable=True)
    client_po_number = Column(String(50), nullable=True)
    shift_description = Column(String(200), nullable=True)  # e.g., "Setup Day", "Event Day", "Teardown"
    special_instructions = Column(String(1000), nullable=True)  # Shift-specific instructions

    # Soft delete fields
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)

    # Note: venue_name and venue_address removed - inherited from job


class ShiftWorker(Base):
    """
    Represents agency employees assigned to shifts with enhanced time tracking.

    Attributes:
        shiftID (int): ID of the associated shift.
        userID (int): ID of the associated user (agency employee).
        role_assigned (EmployeeType): The role the user is fulfilling for this shift.

        # Multiple clock in/out pairs for breaks
        clock_in_time_1 (DateTime): First clock-in time (start of shift).
        clock_out_time_1 (DateTime): First clock-out time (first break/lunch).
        clock_in_time_2 (DateTime): Second clock-in time (return from first break).
        clock_out_time_2 (DateTime): Second clock-out time (second break/lunch).
        clock_in_time_3 (DateTime): Third clock-in time (return from second break).
        clock_out_time_3 (DateTime): Third clock-out time (end of shift).

        # Legacy fields for backward compatibility
        clock_in_time (DateTime): DEPRECATED - Use clock_in_time_1 instead.
        clock_out_time (DateTime): DEPRECATED - Use clock_out_time_3 instead.

        # Metadata
        times_submitted_at (DateTime): Timestamp when the times were submitted.
        times_submitted_by (int): ID of user who submitted the times (crew chief or manager).
        is_approved (Boolean): Indicates if the timesheet has been approved by a manager.
        approved_at (DateTime): Timestamp when timesheet was approved.
        approved_by (int): ID of manager who approved the timesheet.

        # Additional tracking
        total_hours_worked (Float): Calculated total hours worked (excluding breaks).
        overtime_hours (Float): Calculated overtime hours based on workplace settings.
        notes (String): Optional notes about the timesheet entry.
    """
    __tablename__ = "shiftWorkers"

    shiftID = Column(Integer, ForeignKey('shifts.id'), nullable=False)
    userID = Column(Integer, ForeignKey('users.id'), nullable=False) # Agency Employee's ID
    role_assigned = Column(Enum(EmployeeType), nullable=False)

    # Multiple clock in/out pairs for breaks and lunches
    clock_in_time_1 = Column(DateTime, nullable=True)   # Start of shift
    clock_out_time_1 = Column(DateTime, nullable=True)  # First break/lunch start
    clock_in_time_2 = Column(DateTime, nullable=True)   # Return from first break
    clock_out_time_2 = Column(DateTime, nullable=True)  # Second break/lunch start
    clock_in_time_3 = Column(DateTime, nullable=True)   # Return from second break
    clock_out_time_3 = Column(DateTime, nullable=True)  # End of shift

    # Legacy fields for backward compatibility
    clock_in_time = Column(DateTime, nullable=True)     # DEPRECATED
    clock_out_time = Column(DateTime, nullable=True)    # DEPRECATED

    # Submission and approval tracking
    times_submitted_at = Column(DateTime, nullable=True)
    times_submitted_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    is_approved = Column(Boolean, nullable=False, default=False)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Calculated fields
    total_hours_worked = Column(Float, nullable=True)
    overtime_hours = Column(Float, nullable=True)
    notes = Column(String(500), nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint('shiftID', 'userID', 'role_assigned'),
    )

    def get_time_pairs(self):
        """Get all clock in/out time pairs as a list."""
        pairs = []

        # Pair 1
        if self.clock_in_time_1 or self.clock_out_time_1:
            pairs.append({
                'pair_number': 1,
                'clock_in': self.clock_in_time_1.isoformat() if self.clock_in_time_1 else None,
                'clock_out': self.clock_out_time_1.isoformat() if self.clock_out_time_1 else None,
                'description': 'Start of shift to first break'
            })

        # Pair 2
        if self.clock_in_time_2 or self.clock_out_time_2:
            pairs.append({
                'pair_number': 2,
                'clock_in': self.clock_in_time_2.isoformat() if self.clock_in_time_2 else None,
                'clock_out': self.clock_out_time_2.isoformat() if self.clock_out_time_2 else None,
                'description': 'Return from first break to second break'
            })

        # Pair 3
        if self.clock_in_time_3 or self.clock_out_time_3:
            pairs.append({
                'pair_number': 3,
                'clock_in': self.clock_in_time_3.isoformat() if self.clock_in_time_3 else None,
                'clock_out': self.clock_out_time_3.isoformat() if self.clock_out_time_3 else None,
                'description': 'Return from second break to end of shift'
            })

        return pairs

    def calculate_total_hours(self):
        """Calculate total hours worked across all time pairs."""
        from datetime import timedelta

        total_time = timedelta()

        # Calculate time for each pair
        pairs = [
            (self.clock_in_time_1, self.clock_out_time_1),
            (self.clock_in_time_2, self.clock_out_time_2),
            (self.clock_in_time_3, self.clock_out_time_3)
        ]

        for clock_in, clock_out in pairs:
            if clock_in and clock_out and clock_out > clock_in:
                total_time += (clock_out - clock_in)

        # Convert to hours
        total_hours = total_time.total_seconds() / 3600
        self.total_hours_worked = round(total_hours, 2)
        return self.total_hours_worked

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'shift_id': self.shiftID,
            'user_id': self.userID,
            'role_assigned': self.role_assigned.value if self.role_assigned else None,
            'time_pairs': self.get_time_pairs(),
            'total_hours_worked': self.total_hours_worked,
            'overtime_hours': self.overtime_hours,
            'times_submitted_at': self.times_submitted_at.isoformat() if self.times_submitted_at else None,
            'times_submitted_by': self.times_submitted_by,
            'is_approved': self.is_approved,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'approved_by': self.approved_by,
            'notes': self.notes,
            # Legacy fields for backward compatibility
            'clock_in_time': self.clock_in_time.isoformat() if self.clock_in_time else None,
            'clock_out_time': self.clock_out_time.isoformat() if self.clock_out_time else None,
        }


class ShiftBoard(Base):
    """
    DEPRECATED: This model is deprecated for Hands on Labor single company system.
    Use the new job-based shift system instead.

    Represents the agency's shift-board for a manager.

    Attributes:
        weekStartDate (Date): Start date of the week.
        manager_id (int): ID of the manager (formerly workplaceID).
        isPublished (bool): Indicates if the shift is published and visible to workers.
        content (JSON): Stores the shift-board content.
        preferences (JSON): Stores company preferences/settings.
            - number_of_shifts_per_day
            - max_workers_per_shift
            - closed_days
            - etc.
        requests_window_start (DateTime): Start date and time of the requests window for employees.
        requests_window_end (DateTime): End date and time of the requests window for employees.
    """
    __tablename__ = "shiftBoards"

    weekStartDate = Column(Date, nullable=False, default=lambda: next_sunday())
    # Renamed from workplaceID to manager_id for clarity
    manager_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Manager's ID
    # Keep old column for backward compatibility
    workplaceID = Column(Integer, ForeignKey('users.id'), nullable=True)  # DEPRECATED
    isPublished = Column(Boolean, nullable=False, default=False)
    content = Column(JSON, default=dict)
    preferences = Column(JSON, default={"closed_days": [], "number_of_shifts_per_day": 3})
    requests_window_start = Column(DateTime)
    requests_window_end = Column(DateTime)

    __table_args__ = (
        PrimaryKeyConstraint('weekStartDate', 'manager_id'),
    )


# Define the next_sunday function to be used as the default value
def next_sunday():
    today = datetime.date.today()
    days_until_sunday = (6 - today.weekday() + 7) % 7
    return today + datetime.timedelta(days=days_until_sunday)


class EmployeeCertification(Base):
    """
    Model for tracking employee certifications/perks.
    All employees are stagehands by default, with optional additional certifications.
    """
    __tablename__ = 'employee_certifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Certification flags
    can_crew_chief = Column(Boolean, default=False, nullable=False)
    can_forklift = Column(Boolean, default=False, nullable=False)
    can_truck = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="certifications")

    def to_dict(self):
        """Convert certification to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'can_crew_chief': self.can_crew_chief,
            'can_forklift': self.can_forklift,
            'can_truck': self.can_truck,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_role_list(self):
        """Get list of roles this employee is certified for."""
        roles = ['Stagehand']  # Everyone is a stagehand

        if self.can_crew_chief:
            roles.append('Crew Chief')
        if self.can_forklift:
            roles.append('Forklift Operator')
        if self.can_truck:
            roles.append('Truck Driver')

        return roles

    def can_fill_role(self, role):
        """Check if employee can fill a specific role."""
        role_lower = role.lower()

        if role_lower in ['stagehand', 'sh']:
            return True  # Everyone can be a stagehand
        elif role_lower in ['crew chief', 'cc', 'crew_chief']:
            return self.can_crew_chief
        elif role_lower in ['forklift operator', 'forklift', 'fo', 'fork_operator']:
            return self.can_forklift
        elif role_lower in ['truck driver', 'truck', 'trk', 'pickup_truck_driver']:
            return self.can_truck

        return False


class WorkplaceSettings(Base):
    """
    Comprehensive settings model for workplace/manager preferences.
    Replaces the JSON preferences field in ShiftBoard with a proper relational model.
    """
    __tablename__ = 'workplace_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # === SCHEDULING PREFERENCES ===
    # Basic scheduling
    shifts_per_day = Column(Integer, default=2, nullable=False)
    max_workers_per_shift = Column(Integer, default=10, nullable=False)
    min_workers_per_shift = Column(Integer, default=1, nullable=False)

    # Operating hours
    business_start_time = Column(DateTime, nullable=True)  # Default start time for shifts
    business_end_time = Column(DateTime, nullable=True)    # Default end time for shifts
    default_shift_duration_hours = Column(Integer, default=8, nullable=False)
    break_duration_minutes = Column(Integer, default=30, nullable=False)

    # Days and scheduling
    closed_days = Column(JSON, default=list, nullable=False)  # ["monday", "sunday"]
    operating_days = Column(JSON, default=["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], nullable=False)

    # === NOTIFICATION PREFERENCES ===
    # Email notifications
    email_notifications_enabled = Column(Boolean, default=True, nullable=False)
    notify_on_shift_requests = Column(Boolean, default=True, nullable=False)
    notify_on_worker_assignments = Column(Boolean, default=True, nullable=False)
    notify_on_timesheet_submissions = Column(Boolean, default=True, nullable=False)
    notify_on_schedule_changes = Column(Boolean, default=True, nullable=False)

    # SMS notifications
    sms_notifications_enabled = Column(Boolean, default=False, nullable=False)
    sms_urgent_only = Column(Boolean, default=True, nullable=False)

    # In-app notifications
    push_notifications_enabled = Column(Boolean, default=True, nullable=False)
    notification_sound_enabled = Column(Boolean, default=True, nullable=False)

    # === REQUEST WINDOW SETTINGS ===
    # Automatic request windows
    auto_open_request_windows = Column(Boolean, default=True, nullable=False)
    request_window_days_ahead = Column(Integer, default=7, nullable=False)  # Open requests X days before shift week
    request_window_duration_hours = Column(Integer, default=72, nullable=False)  # Keep open for X hours

    # Manual request windows
    requests_window_start = Column(DateTime, nullable=True)
    requests_window_end = Column(DateTime, nullable=True)

    # === WORKER MANAGEMENT ===
    # Auto-assignment
    auto_assign_workers = Column(Boolean, default=False, nullable=False)
    auto_assign_by_seniority = Column(Boolean, default=True, nullable=False)
    auto_assign_by_availability = Column(Boolean, default=True, nullable=False)
    auto_assign_by_skills = Column(Boolean, default=True, nullable=False)

    # Worker requirements
    require_certification_verification = Column(Boolean, default=True, nullable=False)
    allow_overtime_assignments = Column(Boolean, default=True, nullable=False)
    max_consecutive_days = Column(Integer, default=6, nullable=False)
    max_hours_per_week = Column(Integer, default=40, nullable=False)

    # === TIMESHEET & PAYROLL ===
    # Time tracking
    require_photo_clock_in = Column(Boolean, default=False, nullable=False)
    require_location_verification = Column(Boolean, default=False, nullable=False)
    auto_clock_out_hours = Column(Integer, default=12, nullable=False)  # Auto clock out after X hours

    # Overtime rules
    overtime_threshold_daily = Column(Integer, default=8, nullable=False)  # Hours per day
    overtime_threshold_weekly = Column(Integer, default=40, nullable=False)  # Hours per week
    overtime_rate_multiplier = Column(Float, default=1.5, nullable=False)

    # Approval workflow
    require_manager_approval = Column(Boolean, default=True, nullable=False)
    auto_approve_regular_hours = Column(Boolean, default=False, nullable=False)
    auto_approve_overtime = Column(Boolean, default=False, nullable=False)

    # === DISPLAY & UI PREFERENCES ===
    # Calendar view
    default_calendar_view = Column(String(20), default='week', nullable=False)  # 'day', 'week', 'month'
    show_worker_photos = Column(Boolean, default=True, nullable=False)
    show_certification_badges = Column(Boolean, default=True, nullable=False)
    color_code_by_role = Column(Boolean, default=True, nullable=False)

    # Time format
    use_24_hour_format = Column(Boolean, default=False, nullable=False)
    timezone = Column(String(50), default='America/New_York', nullable=False)

    # Language and locale
    language = Column(String(10), default='en', nullable=False)
    currency = Column(String(3), default='USD', nullable=False)
    date_format = Column(String(20), default='MM/DD/YYYY', nullable=False)

    # === SECURITY & COMPLIANCE ===
    # Access control
    require_two_factor_auth = Column(Boolean, default=False, nullable=False)
    session_timeout_minutes = Column(Integer, default=480, nullable=False)  # 8 hours
    password_expiry_days = Column(Integer, default=90, nullable=False)

    # Data retention
    keep_timesheet_records_months = Column(Integer, default=24, nullable=False)
    keep_schedule_history_months = Column(Integer, default=12, nullable=False)

    # === INTEGRATION SETTINGS ===
    # External systems
    payroll_system_integration = Column(Boolean, default=False, nullable=False)
    hr_system_integration = Column(Boolean, default=False, nullable=False)
    calendar_sync_enabled = Column(Boolean, default=False, nullable=False)

    # API settings
    api_access_enabled = Column(Boolean, default=False, nullable=False)
    webhook_notifications = Column(Boolean, default=False, nullable=False)

    # === CUSTOM FIELDS ===
    # Custom shift fields
    custom_shift_fields = Column(JSON, default=list, nullable=False)  # [{"name": "Equipment", "type": "text", "required": false}]
    custom_worker_fields = Column(JSON, default=list, nullable=False)  # [{"name": "Emergency Contact", "type": "phone", "required": true}]

    # === METADATA ===
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        """Convert settings to dictionary for API responses."""
        return {
            'id': self.id,

            # Scheduling
            'scheduling': {
                'shifts_per_day': self.shifts_per_day,
                'max_workers_per_shift': self.max_workers_per_shift,
                'min_workers_per_shift': self.min_workers_per_shift,
                'business_start_time': self.business_start_time.isoformat() if self.business_start_time else None,
                'business_end_time': self.business_end_time.isoformat() if self.business_end_time else None,
                'default_shift_duration_hours': self.default_shift_duration_hours,
                'break_duration_minutes': self.break_duration_minutes,
                'closed_days': self.closed_days,
                'operating_days': self.operating_days,
            },

            # Notifications
            'notifications': {
                'email_enabled': self.email_notifications_enabled,
                'notify_shift_requests': self.notify_on_shift_requests,
                'notify_worker_assignments': self.notify_on_worker_assignments,
                'notify_timesheet_submissions': self.notify_on_timesheet_submissions,
                'notify_schedule_changes': self.notify_on_schedule_changes,
                'sms_enabled': self.sms_notifications_enabled,
                'sms_urgent_only': self.sms_urgent_only,
                'push_enabled': self.push_notifications_enabled,
                'notification_sound': self.notification_sound_enabled,
            },

            # Request windows
            'request_windows': {
                'auto_open': self.auto_open_request_windows,
                'days_ahead': self.request_window_days_ahead,
                'duration_hours': self.request_window_duration_hours,
                'manual_start': self.requests_window_start.isoformat() if self.requests_window_start else None,
                'manual_end': self.requests_window_end.isoformat() if self.requests_window_end else None,
            },

            # Worker management
            'worker_management': {
                'auto_assign': self.auto_assign_workers,
                'auto_assign_by_seniority': self.auto_assign_by_seniority,
                'auto_assign_by_availability': self.auto_assign_by_availability,
                'auto_assign_by_skills': self.auto_assign_by_skills,
                'require_certification_verification': self.require_certification_verification,
                'allow_overtime': self.allow_overtime_assignments,
                'max_consecutive_days': self.max_consecutive_days,
                'max_hours_per_week': self.max_hours_per_week,
            },

            # Timesheet & payroll
            'timesheet': {
                'require_photo_clock_in': self.require_photo_clock_in,
                'require_location_verification': self.require_location_verification,
                'auto_clock_out_hours': self.auto_clock_out_hours,
                'overtime_daily_threshold': self.overtime_threshold_daily,
                'overtime_weekly_threshold': self.overtime_threshold_weekly,
                'overtime_rate': self.overtime_rate_multiplier,
                'require_manager_approval': self.require_manager_approval,
                'auto_approve_regular': self.auto_approve_regular_hours,
                'auto_approve_overtime': self.auto_approve_overtime,
            },

            # Display preferences
            'display': {
                'default_calendar_view': self.default_calendar_view,
                'show_worker_photos': self.show_worker_photos,
                'show_certification_badges': self.show_certification_badges,
                'color_code_by_role': self.color_code_by_role,
                'use_24_hour_format': self.use_24_hour_format,
                'timezone': self.timezone,
                'language': self.language,
                'currency': self.currency,
                'date_format': self.date_format,
            },

            # Security
            'security': {
                'require_two_factor': self.require_two_factor_auth,
                'session_timeout_minutes': self.session_timeout_minutes,
                'password_expiry_days': self.password_expiry_days,
                'keep_timesheet_records_months': self.keep_timesheet_records_months,
                'keep_schedule_history_months': self.keep_schedule_history_months,
            },

            # Integrations
            'integrations': {
                'payroll_system': self.payroll_system_integration,
                'hr_system': self.hr_system_integration,
                'calendar_sync': self.calendar_sync_enabled,
                'api_access': self.api_access_enabled,
                'webhook_notifications': self.webhook_notifications,
            },

            # Custom fields
            'custom_fields': {
                'shift_fields': self.custom_shift_fields,
                'worker_fields': self.custom_worker_fields,
            },

            # Metadata
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_notification_preferences(self):
        """Get notification preferences for this workplace."""
        return {
            'email': self.email_notifications_enabled,
            'sms': self.sms_notifications_enabled,
            'push': self.push_notifications_enabled,
            'types': {
                'shift_requests': self.notify_on_shift_requests,
                'worker_assignments': self.notify_on_worker_assignments,
                'timesheet_submissions': self.notify_on_timesheet_submissions,
                'schedule_changes': self.notify_on_schedule_changes,
            }
        }

    def get_scheduling_rules(self):
        """Get scheduling rules for validation."""
        return {
            'max_workers_per_shift': self.max_workers_per_shift,
            'min_workers_per_shift': self.min_workers_per_shift,
            'max_consecutive_days': self.max_consecutive_days,
            'max_hours_per_week': self.max_hours_per_week,
            'closed_days': self.closed_days,
            'operating_days': self.operating_days,
        }


class CompanyProfile(Base):
    """
    Company profile and branding settings for Hands on Labor.
    """
    __tablename__ = 'company_profile'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Company Information
    company_name = Column(String(255), default='Hands on Labor', nullable=False)
    company_tagline = Column(String(500), default='Professional Labor Staffing Solutions', nullable=True)
    company_description = Column(Text, nullable=True)
    company_website = Column(String(255), nullable=True)
    company_email = Column(String(255), nullable=True)
    company_phone = Column(String(50), nullable=True)
    company_address = Column(Text, nullable=True)

    # Branding
    company_logo_url = Column(String(500), nullable=True)
    company_primary_color = Column(String(7), default='#2563eb', nullable=False)
    company_secondary_color = Column(String(7), default='#1e40af', nullable=False)
    show_company_branding = Column(Boolean, default=True, nullable=False)

    # Business Details
    business_license = Column(String(100), nullable=True)
    tax_id = Column(String(50), nullable=True)
    workers_comp_policy = Column(String(100), nullable=True)
    liability_insurance_policy = Column(String(100), nullable=True)

    # Emergency Contact
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(50), nullable=True)
    emergency_contact_email = Column(String(255), nullable=True)

    # Operating Hours & Rates
    operating_hours_start = Column(Time, default=time(6, 0), nullable=False)
    operating_hours_end = Column(Time, default=time(22, 0), nullable=False)
    time_zone = Column(String(50), default='America/Los_Angeles', nullable=False)
    default_hourly_rate = Column(Float, default=25.00, nullable=False)
    overtime_rate_multiplier = Column(Float, default=1.5, nullable=False)

    # Settings
    allow_public_job_postings = Column(Boolean, default=False, nullable=False)
    require_background_checks = Column(Boolean, default=True, nullable=False)
    drug_testing_required = Column(Boolean, default=False, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'company_tagline': self.company_tagline,
            'company_description': self.company_description,
            'company_website': self.company_website,
            'company_email': self.company_email,
            'company_phone': self.company_phone,
            'company_address': self.company_address,
            'company_logo_url': self.company_logo_url,
            'company_primary_color': self.company_primary_color,
            'company_secondary_color': self.company_secondary_color,
            'show_company_branding': self.show_company_branding,
            'business_license': self.business_license,
            'tax_id': self.tax_id,
            'workers_comp_policy': self.workers_comp_policy,
            'liability_insurance_policy': self.liability_insurance_policy,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'emergency_contact_email': self.emergency_contact_email,
            'operating_hours_start': self.operating_hours_start.isoformat() if self.operating_hours_start else None,
            'operating_hours_end': self.operating_hours_end.isoformat() if self.operating_hours_end else None,
            'time_zone': self.time_zone,
            'default_hourly_rate': self.default_hourly_rate,
            'overtime_rate_multiplier': self.overtime_rate_multiplier,
            'allow_public_job_postings': self.allow_public_job_postings,
            'require_background_checks': self.require_background_checks,
            'drug_testing_required': self.drug_testing_required,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class UserManagementSettings(Base):
    """
    User management and role-based permissions settings.
    """
    __tablename__ = 'user_management_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Employee Management
    auto_approve_employees = Column(Boolean, default=False, nullable=False)
    require_manager_approval = Column(Boolean, default=True, nullable=False)
    allow_employee_self_registration = Column(Boolean, default=True, nullable=False)
    require_email_verification = Column(Boolean, default=True, nullable=False)
    employee_probation_period_days = Column(Integer, default=90, nullable=False)

    # Manager Permissions
    managers_can_create_employees = Column(Boolean, default=True, nullable=False)
    managers_can_edit_all_timesheets = Column(Boolean, default=True, nullable=False)
    managers_can_approve_overtime = Column(Boolean, default=True, nullable=False)
    managers_can_modify_rates = Column(Boolean, default=False, nullable=False)
    managers_can_access_reports = Column(Boolean, default=True, nullable=False)

    # Client Permissions
    clients_can_view_timesheets = Column(Boolean, default=True, nullable=False)
    clients_can_edit_timesheets = Column(Boolean, default=False, nullable=False)
    clients_can_request_workers = Column(Boolean, default=True, nullable=False)
    clients_can_modify_jobs = Column(Boolean, default=True, nullable=False)
    clients_can_cancel_shifts = Column(Boolean, default=False, nullable=False)

    # Role-Based Access & Premiums
    crew_chiefs_can_edit_team_times = Column(Boolean, default=True, nullable=False)
    crew_chiefs_can_mark_absent = Column(Boolean, default=True, nullable=False)
    crew_chiefs_can_add_notes = Column(Boolean, default=True, nullable=False)
    forklift_operators_premium_rate = Column(Float, default=2.00, nullable=False)
    truck_drivers_premium_rate = Column(Float, default=3.00, nullable=False)
    crew_chief_premium_rate = Column(Float, default=5.00, nullable=False)

    # Account Security
    password_min_length = Column(Integer, default=8, nullable=False)
    require_password_complexity = Column(Boolean, default=True, nullable=False)
    password_expiry_days = Column(Integer, default=90, nullable=False)
    max_login_attempts = Column(Integer, default=5, nullable=False)
    account_lockout_duration_minutes = Column(Integer, default=30, nullable=False)
    require_two_factor_auth = Column(Boolean, default=False, nullable=False)

    # Session Management
    session_timeout_minutes = Column(Integer, default=480, nullable=False)  # 8 hours
    remember_me_duration_days = Column(Integer, default=30, nullable=False)
    force_logout_inactive_users = Column(Boolean, default=True, nullable=False)
    concurrent_sessions_allowed = Column(Integer, default=3, nullable=False)

    # User Directory
    show_employee_contact_info = Column(Boolean, default=True, nullable=False)
    show_employee_certifications = Column(Boolean, default=True, nullable=False)
    allow_employee_profile_editing = Column(Boolean, default=True, nullable=False)
    require_profile_photos = Column(Boolean, default=False, nullable=False)

    # Approval Workflows
    require_shift_assignment_approval = Column(Boolean, default=False, nullable=False)
    require_schedule_change_approval = Column(Boolean, default=True, nullable=False)
    require_overtime_pre_approval = Column(Boolean, default=True, nullable=False)
    auto_notify_approvers = Column(Boolean, default=True, nullable=False)
    approval_timeout_hours = Column(Integer, default=24, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'auto_approve_employees': self.auto_approve_employees,
            'require_manager_approval': self.require_manager_approval,
            'allow_employee_self_registration': self.allow_employee_self_registration,
            'require_email_verification': self.require_email_verification,
            'employee_probation_period_days': self.employee_probation_period_days,
            'managers_can_create_employees': self.managers_can_create_employees,
            'managers_can_edit_all_timesheets': self.managers_can_edit_all_timesheets,
            'managers_can_approve_overtime': self.managers_can_approve_overtime,
            'managers_can_modify_rates': self.managers_can_modify_rates,
            'managers_can_access_reports': self.managers_can_access_reports,
            'clients_can_view_timesheets': self.clients_can_view_timesheets,
            'clients_can_edit_timesheets': self.clients_can_edit_timesheets,
            'clients_can_request_workers': self.clients_can_request_workers,
            'clients_can_modify_jobs': self.clients_can_modify_jobs,
            'clients_can_cancel_shifts': self.clients_can_cancel_shifts,
            'crew_chiefs_can_edit_team_times': self.crew_chiefs_can_edit_team_times,
            'crew_chiefs_can_mark_absent': self.crew_chiefs_can_mark_absent,
            'crew_chiefs_can_add_notes': self.crew_chiefs_can_add_notes,
            'forklift_operators_premium_rate': self.forklift_operators_premium_rate,
            'truck_drivers_premium_rate': self.truck_drivers_premium_rate,
            'crew_chief_premium_rate': self.crew_chief_premium_rate,
            'password_min_length': self.password_min_length,
            'require_password_complexity': self.require_password_complexity,
            'password_expiry_days': self.password_expiry_days,
            'max_login_attempts': self.max_login_attempts,
            'account_lockout_duration_minutes': self.account_lockout_duration_minutes,
            'require_two_factor_auth': self.require_two_factor_auth,
            'session_timeout_minutes': self.session_timeout_minutes,
            'remember_me_duration_days': self.remember_me_duration_days,
            'force_logout_inactive_users': self.force_logout_inactive_users,
            'concurrent_sessions_allowed': self.concurrent_sessions_allowed,
            'show_employee_contact_info': self.show_employee_contact_info,
            'show_employee_certifications': self.show_employee_certifications,
            'allow_employee_profile_editing': self.allow_employee_profile_editing,
            'require_profile_photos': self.require_profile_photos,
            'require_shift_assignment_approval': self.require_shift_assignment_approval,
            'require_schedule_change_approval': self.require_schedule_change_approval,
            'require_overtime_pre_approval': self.require_overtime_pre_approval,
            'auto_notify_approvers': self.auto_notify_approvers,
            'approval_timeout_hours': self.approval_timeout_hours,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class CertificationsSettings(Base):
    """
    Employee certification requirements and role definitions.
    """
    __tablename__ = 'certifications_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Certification Requirements
    require_crew_chief_certification = Column(Boolean, default=True, nullable=False)
    require_forklift_certification = Column(Boolean, default=True, nullable=False)
    require_truck_driver_license = Column(Boolean, default=True, nullable=False)
    require_safety_training = Column(Boolean, default=True, nullable=False)
    require_background_check = Column(Boolean, default=True, nullable=False)

    # Certification Validity
    crew_chief_cert_validity_months = Column(Integer, default=24, nullable=False)
    forklift_cert_validity_months = Column(Integer, default=36, nullable=False)
    safety_training_validity_months = Column(Integer, default=12, nullable=False)
    background_check_validity_months = Column(Integer, default=12, nullable=False)

    # Training Requirements
    mandatory_safety_orientation = Column(Boolean, default=True, nullable=False)
    safety_orientation_duration_hours = Column(Integer, default=4, nullable=False)
    require_annual_safety_refresher = Column(Boolean, default=True, nullable=False)
    require_equipment_specific_training = Column(Boolean, default=True, nullable=False)

    # Role Experience Requirements
    stagehand_min_experience_months = Column(Integer, default=0, nullable=False)
    crew_chief_min_experience_months = Column(Integer, default=12, nullable=False)
    forklift_operator_min_experience_months = Column(Integer, default=6, nullable=False)
    truck_driver_min_experience_months = Column(Integer, default=3, nullable=False)

    # Certification Tracking
    auto_notify_expiring_certs = Column(Boolean, default=True, nullable=False)
    cert_expiry_warning_days = Column(Integer, default=30, nullable=False)
    suspend_expired_cert_workers = Column(Boolean, default=True, nullable=False)
    require_cert_photo_upload = Column(Boolean, default=True, nullable=False)

    # Training Providers
    approved_training_providers = Column(JSON, default=list, nullable=False)

    # Verification Settings
    require_manager_cert_verification = Column(Boolean, default=True, nullable=False)
    allow_self_reported_experience = Column(Boolean, default=False, nullable=False)
    require_reference_verification = Column(Boolean, default=True, nullable=False)
    background_check_provider = Column(String(255), default='Sterling Talent Solutions', nullable=True)

    # Skill Assessments
    require_practical_skill_test = Column(Boolean, default=True, nullable=False)
    skill_test_validity_months = Column(Integer, default=12, nullable=False)
    allow_skill_test_retakes = Column(Boolean, default=True, nullable=False)
    max_skill_test_attempts = Column(Integer, default=3, nullable=False)

    # Documentation
    require_cert_documentation = Column(Boolean, default=True, nullable=False)
    accept_digital_certificates = Column(Boolean, default=True, nullable=False)
    require_original_documents = Column(Boolean, default=False, nullable=False)
    document_retention_years = Column(Integer, default=7, nullable=False)

    # Custom Certifications
    custom_certifications = Column(JSON, default=list, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'require_crew_chief_certification': self.require_crew_chief_certification,
            'require_forklift_certification': self.require_forklift_certification,
            'require_truck_driver_license': self.require_truck_driver_license,
            'require_safety_training': self.require_safety_training,
            'require_background_check': self.require_background_check,
            'crew_chief_cert_validity_months': self.crew_chief_cert_validity_months,
            'forklift_cert_validity_months': self.forklift_cert_validity_months,
            'safety_training_validity_months': self.safety_training_validity_months,
            'background_check_validity_months': self.background_check_validity_months,
            'mandatory_safety_orientation': self.mandatory_safety_orientation,
            'safety_orientation_duration_hours': self.safety_orientation_duration_hours,
            'require_annual_safety_refresher': self.require_annual_safety_refresher,
            'require_equipment_specific_training': self.require_equipment_specific_training,
            'stagehand_min_experience_months': self.stagehand_min_experience_months,
            'crew_chief_min_experience_months': self.crew_chief_min_experience_months,
            'forklift_operator_min_experience_months': self.forklift_operator_min_experience_months,
            'truck_driver_min_experience_months': self.truck_driver_min_experience_months,
            'auto_notify_expiring_certs': self.auto_notify_expiring_certs,
            'cert_expiry_warning_days': self.cert_expiry_warning_days,
            'suspend_expired_cert_workers': self.suspend_expired_cert_workers,
            'require_cert_photo_upload': self.require_cert_photo_upload,
            'approved_training_providers': self.approved_training_providers,
            'require_manager_cert_verification': self.require_manager_cert_verification,
            'allow_self_reported_experience': self.allow_self_reported_experience,
            'require_reference_verification': self.require_reference_verification,
            'background_check_provider': self.background_check_provider,
            'require_practical_skill_test': self.require_practical_skill_test,
            'skill_test_validity_months': self.skill_test_validity_months,
            'allow_skill_test_retakes': self.allow_skill_test_retakes,
            'max_skill_test_attempts': self.max_skill_test_attempts,
            'require_cert_documentation': self.require_cert_documentation,
            'accept_digital_certificates': self.accept_digital_certificates,
            'require_original_documents': self.require_original_documents,
            'document_retention_years': self.document_retention_years,
            'custom_certifications': self.custom_certifications,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class ClientManagementSettings(Base):
    """
    Client management, onboarding, and service settings.
    """
    __tablename__ = 'client_management_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Client Onboarding
    auto_approve_client_registrations = Column(Boolean, default=False, nullable=False)
    require_client_verification = Column(Boolean, default=True, nullable=False)
    require_business_license_verification = Column(Boolean, default=True, nullable=False)
    require_insurance_verification = Column(Boolean, default=True, nullable=False)
    client_onboarding_checklist_enabled = Column(Boolean, default=True, nullable=False)

    # Communication Preferences
    default_communication_method = Column(String(20), default='email', nullable=False)
    allow_sms_notifications = Column(Boolean, default=True, nullable=False)
    require_job_confirmation = Column(Boolean, default=True, nullable=False)
    send_shift_reminders = Column(Boolean, default=True, nullable=False)
    shift_reminder_hours_before = Column(Integer, default=24, nullable=False)

    # Billing & Invoicing
    auto_generate_invoices = Column(Boolean, default=True, nullable=False)
    invoice_generation_frequency = Column(String(20), default='weekly', nullable=False)
    default_payment_terms_days = Column(Integer, default=30, nullable=False)
    late_payment_fee_percentage = Column(Float, default=2.5, nullable=False)
    require_po_numbers = Column(Boolean, default=True, nullable=False)
    allow_credit_applications = Column(Boolean, default=True, nullable=False)

    # Job Management
    clients_can_create_jobs = Column(Boolean, default=True, nullable=False)
    clients_can_modify_active_jobs = Column(Boolean, default=False, nullable=False)
    clients_can_cancel_jobs = Column(Boolean, default=True, nullable=False)
    job_cancellation_notice_hours = Column(Integer, default=24, nullable=False)
    allow_rush_job_requests = Column(Boolean, default=True, nullable=False)
    rush_job_premium_percentage = Column(Float, default=25, nullable=False)

    # Worker Requests
    clients_can_request_specific_workers = Column(Boolean, default=True, nullable=False)
    clients_can_exclude_workers = Column(Boolean, default=False, nullable=False)
    allow_worker_rating_system = Column(Boolean, default=True, nullable=False)
    require_worker_feedback = Column(Boolean, default=False, nullable=False)

    # Timesheet & Approval
    clients_receive_daily_timesheets = Column(Boolean, default=True, nullable=False)
    require_client_timesheet_approval = Column(Boolean, default=False, nullable=False)
    timesheet_approval_deadline_hours = Column(Integer, default=48, nullable=False)
    auto_approve_if_no_response = Column(Boolean, default=True, nullable=False)

    # Pricing & Rates
    show_rates_to_clients = Column(Boolean, default=False, nullable=False)
    allow_client_rate_negotiation = Column(Boolean, default=False, nullable=False)
    use_tiered_pricing = Column(Boolean, default=True, nullable=False)
    volume_discount_threshold_hours = Column(Integer, default=100, nullable=False)
    volume_discount_percentage = Column(Float, default=5, nullable=False)

    # Service Areas
    default_service_radius_miles = Column(Integer, default=50, nullable=False)
    charge_travel_time = Column(Boolean, default=True, nullable=False)
    travel_time_rate_percentage = Column(Float, default=100, nullable=False)
    minimum_job_duration_hours = Column(Integer, default=4, nullable=False)

    # Quality Control
    require_job_completion_photos = Column(Boolean, default=True, nullable=False)
    send_client_satisfaction_surveys = Column(Boolean, default=True, nullable=False)
    survey_frequency = Column(String(20), default='after_each_job', nullable=False)
    track_client_complaints = Column(Boolean, default=True, nullable=False)

    # Contract Management
    require_signed_contracts = Column(Boolean, default=True, nullable=False)
    use_digital_signatures = Column(Boolean, default=True, nullable=False)
    contract_auto_renewal = Column(Boolean, default=False, nullable=False)
    contract_renewal_notice_days = Column(Integer, default=30, nullable=False)

    # Emergency Procedures
    emergency_contact_required = Column(Boolean, default=True, nullable=False)
    after_hours_support_available = Column(Boolean, default=True, nullable=False)
    emergency_response_time_minutes = Column(Integer, default=30, nullable=False)

    # Data & Privacy
    share_worker_names_with_clients = Column(Boolean, default=True, nullable=False)
    share_worker_photos_with_clients = Column(Boolean, default=False, nullable=False)
    allow_client_worker_direct_contact = Column(Boolean, default=False, nullable=False)
    client_data_retention_years = Column(Integer, default=7, nullable=False)

    # Custom Fields
    custom_fields = Column(JSON, default=list, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'auto_approve_client_registrations': self.auto_approve_client_registrations,
            'require_client_verification': self.require_client_verification,
            'require_business_license_verification': self.require_business_license_verification,
            'require_insurance_verification': self.require_insurance_verification,
            'client_onboarding_checklist_enabled': self.client_onboarding_checklist_enabled,
            'default_communication_method': self.default_communication_method,
            'allow_sms_notifications': self.allow_sms_notifications,
            'require_job_confirmation': self.require_job_confirmation,
            'send_shift_reminders': self.send_shift_reminders,
            'shift_reminder_hours_before': self.shift_reminder_hours_before,
            'auto_generate_invoices': self.auto_generate_invoices,
            'invoice_generation_frequency': self.invoice_generation_frequency,
            'default_payment_terms_days': self.default_payment_terms_days,
            'late_payment_fee_percentage': self.late_payment_fee_percentage,
            'require_po_numbers': self.require_po_numbers,
            'allow_credit_applications': self.allow_credit_applications,
            'clients_can_create_jobs': self.clients_can_create_jobs,
            'clients_can_modify_active_jobs': self.clients_can_modify_active_jobs,
            'clients_can_cancel_jobs': self.clients_can_cancel_jobs,
            'job_cancellation_notice_hours': self.job_cancellation_notice_hours,
            'allow_rush_job_requests': self.allow_rush_job_requests,
            'rush_job_premium_percentage': self.rush_job_premium_percentage,
            'clients_can_request_specific_workers': self.clients_can_request_specific_workers,
            'clients_can_exclude_workers': self.clients_can_exclude_workers,
            'allow_worker_rating_system': self.allow_worker_rating_system,
            'require_worker_feedback': self.require_worker_feedback,
            'clients_receive_daily_timesheets': self.clients_receive_daily_timesheets,
            'require_client_timesheet_approval': self.require_client_timesheet_approval,
            'timesheet_approval_deadline_hours': self.timesheet_approval_deadline_hours,
            'auto_approve_if_no_response': self.auto_approve_if_no_response,
            'show_rates_to_clients': self.show_rates_to_clients,
            'allow_client_rate_negotiation': self.allow_client_rate_negotiation,
            'use_tiered_pricing': self.use_tiered_pricing,
            'volume_discount_threshold_hours': self.volume_discount_threshold_hours,
            'volume_discount_percentage': self.volume_discount_percentage,
            'default_service_radius_miles': self.default_service_radius_miles,
            'charge_travel_time': self.charge_travel_time,
            'travel_time_rate_percentage': self.travel_time_rate_percentage,
            'minimum_job_duration_hours': self.minimum_job_duration_hours,
            'require_job_completion_photos': self.require_job_completion_photos,
            'send_client_satisfaction_surveys': self.send_client_satisfaction_surveys,
            'survey_frequency': self.survey_frequency,
            'track_client_complaints': self.track_client_complaints,
            'require_signed_contracts': self.require_signed_contracts,
            'use_digital_signatures': self.use_digital_signatures,
            'contract_auto_renewal': self.contract_auto_renewal,
            'contract_renewal_notice_days': self.contract_renewal_notice_days,
            'emergency_contact_required': self.emergency_contact_required,
            'after_hours_support_available': self.after_hours_support_available,
            'emergency_response_time_minutes': self.emergency_response_time_minutes,
            'share_worker_names_with_clients': self.share_worker_names_with_clients,
            'share_worker_photos_with_clients': self.share_worker_photos_with_clients,
            'allow_client_worker_direct_contact': self.allow_client_worker_direct_contact,
            'client_data_retention_years': self.client_data_retention_years,
            'custom_fields': self.custom_fields,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
