import React, { useState, useEffect } from 'react';
import ToggleSwitch from '../ToggleSwitch'; // Assuming ToggleSwitch is in ../components

const UserManagementSettings = ({ settings, onUpdate, onMarkUnsaved, isLoading }) => {
  const initialFormData = {
    // Employee Management
    auto_approve_employees: false,
    require_manager_approval: true,
    allow_employee_self_registration: true,
    require_email_verification: true,
    employee_probation_period_days: 90,
    // Manager Permissions
    managers_can_create_employees: true,
    managers_can_edit_all_timesheets: true,
    managers_can_approve_overtime: true,
    managers_can_modify_rates: false,
    managers_can_access_reports: true,
    // Client Permissions
    clients_can_view_timesheets: true,
    clients_can_edit_timesheets: false,
    clients_can_request_workers: true,
    clients_can_modify_jobs: true,
    clients_can_cancel_shifts: false,
    // Role-Based Access & Premiums
    crew_chiefs_can_edit_team_times: true,
    crew_chiefs_can_mark_absent: true,
    crew_chiefs_can_add_notes: true,
    forklift_operators_premium_rate: 2.00,
    truck_drivers_premium_rate: 3.00,
    crew_chief_premium_rate: 5.00,
    // Account Security
    password_min_length: 8,
    require_password_complexity: true,
    password_expiry_days: 90,
    max_login_attempts: 5,
    account_lockout_duration_minutes: 30,
    require_two_factor_auth: false,
    // Session Management
    session_timeout_minutes: 480,
    remember_me_duration_days: 30,
    force_logout_inactive_users: true,
    concurrent_sessions_allowed: 3,
    // User Directory
    show_employee_contact_info: true,
    show_employee_certifications: true,
    allow_employee_profile_editing: true,
    require_profile_photos: false,
    // Approval Workflows
    require_shift_assignment_approval: false,
    require_schedule_change_approval: true,
    require_overtime_pre_approval: true,
    auto_notify_approvers: true,
    approval_timeout_hours: 24,
  };

  const [formData, setFormData] = useState(initialFormData);

  useEffect(() => {
    if (settings && settings.user_management) {
      // Merge fetched settings with initialFormData to ensure all keys are present
      setFormData(prev => ({ ...initialFormData, ...settings.user_management }));
    } else if (settings && Object.keys(settings).length > 0 && !settings.user_management) {
      // If settings object exists but user_management is missing, initialize with defaults
      // This can happen if the backend returns an empty object for a category
      setFormData(initialFormData);
    }
  }, [settings]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const val = type === 'checkbox' ? checked : (type === 'number' ? parseInt(value, 10) : value);
    setFormData(prev => ({ ...prev, [name]: val }));
    onMarkUnsaved();
  };

  const handleToggle = (name) => {
    setFormData(prev => ({ ...prev, [name]: !prev[name] }));
    onMarkUnsaved();
  };
  
  const handleRateChange = (name, value) => {
    const rate = parseFloat(value);
    setFormData(prev => ({ ...prev, [name]: isNaN(rate) ? 0 : rate }));
    onMarkUnsaved();
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onUpdate('user-management', formData);
  };

  if (!settings) {
    return <div>Loading user management settings...</div>;
  }
  
  // Fallback if settings.user_management is not yet populated but settings object exists
  const currentData = (settings && settings.user_management) ? { ...initialFormData, ...settings.user_management } : formData;


  return (
    <form onSubmit={handleSubmit} className="settings-form-category">
      <h3 className="category-title">User Management & Permissions</h3>

      {/* Employee Management Section */}
      <section className="settings-subsection">
        <h4 className="subcategory-title">Employee Onboarding & Management</h4>
        <div className="form-grid">
          <ToggleSwitch label="Auto-approve New Employees" checked={currentData.auto_approve_employees} onChange={() => handleToggle('auto_approve_employees')} description="Automatically approve new employee registrations." />
          <ToggleSwitch label="Require Manager Approval for Actions" checked={currentData.require_manager_approval} onChange={() => handleToggle('require_manager_approval')} description="Certain employee actions require manager sign-off." />
          <ToggleSwitch label="Allow Employee Self-Registration" checked={currentData.allow_employee_self_registration} onChange={() => handleToggle('allow_employee_self_registration')} description="Enable employees to create their own accounts." />
          <ToggleSwitch label="Require Email Verification" checked={currentData.require_email_verification} onChange={() => handleToggle('require_email_verification')} description="New users must verify their email address." />
          <div className="form-group">
            <label htmlFor="employee_probation_period_days">Employee Probation Period (days)</label>
            <input type="number" id="employee_probation_period_days" name="employee_probation_period_days" value={currentData.employee_probation_period_days} onChange={handleChange} min="0" className="form-input" />
          </div>
        </div>
      </section>

      {/* Manager Permissions Section */}
      <section className="settings-subsection">
        <h4 className="subcategory-title">Manager Permissions</h4>
        <div className="form-grid">
          <ToggleSwitch label="Managers Can Create Employees" checked={currentData.managers_can_create_employees} onChange={() => handleToggle('managers_can_create_employees')} />
          <ToggleSwitch label="Managers Can Edit All Timesheets" checked={currentData.managers_can_edit_all_timesheets} onChange={() => handleToggle('managers_can_edit_all_timesheets')} />
          <ToggleSwitch label="Managers Can Approve Overtime" checked={currentData.managers_can_approve_overtime} onChange={() => handleToggle('managers_can_approve_overtime')} />
          <ToggleSwitch label="Managers Can Modify Pay Rates" checked={currentData.managers_can_modify_rates} onChange={() => handleToggle('managers_can_modify_rates')} />
          <ToggleSwitch label="Managers Can Access Reports" checked={currentData.managers_can_access_reports} onChange={() => handleToggle('managers_can_access_reports')} />
        </div>
      </section>

      {/* Client Permissions Section */}
      <section className="settings-subsection">
        <h4 className="subcategory-title">Client Permissions</h4>
        <div className="form-grid">
          <ToggleSwitch label="Clients Can View Timesheets" checked={currentData.clients_can_view_timesheets} onChange={() => handleToggle('clients_can_view_timesheets')} />
          <ToggleSwitch label="Clients Can Edit Timesheets" checked={currentData.clients_can_edit_timesheets} onChange={() => handleToggle('clients_can_edit_timesheets')} />
          <ToggleSwitch label="Clients Can Request Workers" checked={currentData.clients_can_request_workers} onChange={() => handleToggle('clients_can_request_workers')} />
          <ToggleSwitch label="Clients Can Modify Jobs" checked={currentData.clients_can_modify_jobs} onChange={() => handleToggle('clients_can_modify_jobs')} />
          <ToggleSwitch label="Clients Can Cancel Shifts" checked={currentData.clients_can_cancel_shifts} onChange={() => handleToggle('clients_can_cancel_shifts')} />
        </div>
      </section>

      {/* Role-Based Access & Premiums Section */}
      <section className="settings-subsection">
        <h4 className="subcategory-title">Role-Based Access & Premiums</h4>
        <div className="form-grid">
          <ToggleSwitch label="Crew Chiefs Can Edit Team Times" checked={currentData.crew_chiefs_can_edit_team_times} onChange={() => handleToggle('crew_chiefs_can_edit_team_times')} />
          <ToggleSwitch label="Crew Chiefs Can Mark Absent" checked={currentData.crew_chiefs_can_mark_absent} onChange={() => handleToggle('crew_chiefs_can_mark_absent')} />
          <ToggleSwitch label="Crew Chiefs Can Add Notes" checked={currentData.crew_chiefs_can_add_notes} onChange={() => handleToggle('crew_chiefs_can_add_notes')} />
          <div className="form-group">
            <label htmlFor="crew_chief_premium_rate">Crew Chief Premium Rate ($/hr)</label>
            <input type="number" id="crew_chief_premium_rate" name="crew_chief_premium_rate" value={currentData.crew_chief_premium_rate} onChange={(e) => handleRateChange('crew_chief_premium_rate', e.target.value)} step="0.01" min="0" className="form-input" />
          </div>
          <div className="form-group">
            <label htmlFor="forklift_operators_premium_rate">Forklift Operator Premium ($/hr)</label>
            <input type="number" id="forklift_operators_premium_rate" name="forklift_operators_premium_rate" value={currentData.forklift_operators_premium_rate} onChange={(e) => handleRateChange('forklift_operators_premium_rate', e.target.value)} step="0.01" min="0" className="form-input" />
          </div>
          <div className="form-group">
            <label htmlFor="truck_drivers_premium_rate">Truck Driver Premium ($/hr)</label>
            <input type="number" id="truck_drivers_premium_rate" name="truck_drivers_premium_rate" value={currentData.truck_drivers_premium_rate} onChange={(e) => handleRateChange('truck_drivers_premium_rate', e.target.value)} step="0.01" min="0" className="form-input" />
          </div>
        </div>
      </section>
      
      {/* Account Security Section */}
      <section className="settings-subsection">
        <h4 className="subcategory-title">Account Security</h4>
        <div className="form-grid">
            <div className="form-group">
                <label htmlFor="password_min_length">Min Password Length</label>
                <input type="number" id="password_min_length" name="password_min_length" value={currentData.password_min_length} onChange={handleChange} min="6" className="form-input" />
            </div>
            <ToggleSwitch label="Require Password Complexity" checked={currentData.require_password_complexity} onChange={() => handleToggle('require_password_complexity')} description="Uppercase, lowercase, number, symbol" />
            <div className="form-group">
                <label htmlFor="password_expiry_days">Password Expiry (days)</label>
                <input type="number" id="password_expiry_days" name="password_expiry_days" value={currentData.password_expiry_days} onChange={handleChange} min="0" className="form-input" />
                 <small>Set to 0 to disable expiry.</small>
            </div>
            <div className="form-group">
                <label htmlFor="max_login_attempts">Max Login Attempts</label>
                <input type="number" id="max_login_attempts" name="max_login_attempts" value={currentData.max_login_attempts} onChange={handleChange} min="3" className="form-input" />
            </div>
             <div className="form-group">
                <label htmlFor="account_lockout_duration_minutes">Account Lockout Duration (minutes)</label>
                <input type="number" id="account_lockout_duration_minutes" name="account_lockout_duration_minutes" value={currentData.account_lockout_duration_minutes} onChange={handleChange} min="1" className="form-input" />
            </div>
            <ToggleSwitch label="Require Two-Factor Auth" checked={currentData.require_two_factor_auth} onChange={() => handleToggle('require_two_factor_auth')} />
        </div>
      </section>

      {/* Session Management Section */}
      <section className="settings-subsection">
        <h4 className="subcategory-title">Session Management</h4>
        <div className="form-grid">
            <div className="form-group">
                <label htmlFor="session_timeout_minutes">Session Timeout (minutes)</label>
                <input type="number" id="session_timeout_minutes" name="session_timeout_minutes" value={currentData.session_timeout_minutes} onChange={handleChange} min="5" className="form-input" />
            </div>
            <div className="form-group">
                <label htmlFor="remember_me_duration_days">"Remember Me" Duration (days)</label>
                <input type="number" id="remember_me_duration_days" name="remember_me_duration_days" value={currentData.remember_me_duration_days} onChange={handleChange} min="1" className="form-input" />
            </div>
            <ToggleSwitch label="Force Logout Inactive Users" checked={currentData.force_logout_inactive_users} onChange={() => handleToggle('force_logout_inactive_users')} />
            <div className="form-group">
                <label htmlFor="concurrent_sessions_allowed">Concurrent Sessions Allowed</label>
                <input type="number" id="concurrent_sessions_allowed" name="concurrent_sessions_allowed" value={currentData.concurrent_sessions_allowed} onChange={handleChange} min="1" className="form-input" />
            </div>
        </div>
      </section>

      {/* User Directory Section */}
      <section className="settings-subsection">
        <h4 className="subcategory-title">User Directory Display</h4>
         <div className="form-grid">
            <ToggleSwitch label="Show Employee Contact Info" checked={currentData.show_employee_contact_info} onChange={() => handleToggle('show_employee_contact_info')} />
            <ToggleSwitch label="Show Employee Certifications" checked={currentData.show_employee_certifications} onChange={() => handleToggle('show_employee_certifications')} />
            <ToggleSwitch label="Allow Employee Profile Editing" checked={currentData.allow_employee_profile_editing} onChange={() => handleToggle('allow_employee_profile_editing')} />
            <ToggleSwitch label="Require Profile Photos" checked={currentData.require_profile_photos} onChange={() => handleToggle('require_profile_photos')} />
        </div>
      </section>

      {/* Approval Workflows Section */}
      <section className="settings-subsection">
        <h4 className="subcategory-title">Approval Workflows</h4>
        <div className="form-grid">
            <ToggleSwitch label="Require Shift Assignment Approval" checked={currentData.require_shift_assignment_approval} onChange={() => handleToggle('require_shift_assignment_approval')} />
            <ToggleSwitch label="Require Schedule Change Approval" checked={currentData.require_schedule_change_approval} onChange={() => handleToggle('require_schedule_change_approval')} />
            <ToggleSwitch label="Require Overtime Pre-Approval" checked={currentData.require_overtime_pre_approval} onChange={() => handleToggle('require_overtime_pre_approval')} />
            <ToggleSwitch label="Auto-Notify Approvers" checked={currentData.auto_notify_approvers} onChange={() => handleToggle('auto_notify_approvers')} />
            <div className="form-group">
                <label htmlFor="approval_timeout_hours">Approval Timeout (hours)</label>
                <input type="number" id="approval_timeout_hours" name="approval_timeout_hours" value={currentData.approval_timeout_hours} onChange={handleChange} min="1" className="form-input" />
            </div>
        </div>
      </section>

      <div className="settings-actions">
        <button type="submit" className="btn btn-primary" disabled={isLoading}>
          {isLoading ? 'Saving...' : 'Save User Management Settings'}
        </button>
      </div>
    </form>
  );
};

export default UserManagementSettings;
