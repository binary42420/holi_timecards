import React, { useState, useEffect } from 'react';
import ToggleSwitch from '../ToggleSwitch';

const SecuritySettings = ({ settings, onUpdate, onMarkUnsaved, isLoading }) => {
  const initialFormData = {
    // Access control
    require_two_factor_auth: false, // This is in UserManagementSettings in backend, but fits here thematically
    session_timeout_minutes: 480,   // This is in UserManagementSettings and WorkplaceSettings in backend
    password_expiry_days: 90,       // This is in UserManagementSettings and WorkplaceSettings
    // Data retention
    keep_timesheet_records_months: 24,
    keep_schedule_history_months: 12,
  };

  const [formData, setFormData] = useState(initialFormData);

  useEffect(() => {
    // SecuritySettings model fields
    const secSettings = settings?.security_settings;
    // Some fields might also be in user_management or workplace_settings
    const umSettings = settings?.user_management; 
    const wpSettings = settings?.workplace_settings;

    let combinedData = { ...initialFormData };

    if (secSettings) {
        combinedData = { ...combinedData, ...secSettings };
    }
    // Override with more specific settings if they exist elsewhere and are managed here for UI convenience
    if (umSettings) {
        if (umSettings.hasOwnProperty('require_two_factor_auth')) combinedData.require_two_factor_auth = umSettings.require_two_factor_auth;
        if (umSettings.hasOwnProperty('session_timeout_minutes')) combinedData.session_timeout_minutes = umSettings.session_timeout_minutes;
        if (umSettings.hasOwnProperty('password_expiry_days')) combinedData.password_expiry_days = umSettings.password_expiry_days;
    }
    // If workplace_settings also has some of these, decide on source of truth or ensure consistency
    if (wpSettings) {
         if (wpSettings.hasOwnProperty('session_timeout_minutes') && !umSettings?.hasOwnProperty('session_timeout_minutes')) {
            combinedData.session_timeout_minutes = wpSettings.session_timeout_minutes;
         }
         if (wpSettings.hasOwnProperty('password_expiry_days') && !umSettings?.hasOwnProperty('password_expiry_days')) {
            combinedData.password_expiry_days = wpSettings.password_expiry_days;
         }
    }


    setFormData(combinedData);

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

  const handleSubmit = (e) => {
    e.preventDefault();
    const dataToSave = {
        require_two_factor_auth: formData.require_two_factor_auth,
        session_timeout_minutes: formData.session_timeout_minutes,
        password_expiry_days: formData.password_expiry_days,
        keep_timesheet_records_months: formData.keep_timesheet_records_months,
        keep_schedule_history_months: formData.keep_schedule_history_months,
    };
    onUpdate('security', dataToSave);
  };
  
  if (!settings) {
    return <div>Loading security settings...</div>;
  }
  const currentData = formData; 

  return (
    <form onSubmit={handleSubmit} className="settings-form-category">
      <h3 className="category-title">Security & Access Control</h3>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Access Control & Authentication</h4>
        <div className="form-grid">
          <ToggleSwitch 
            label="Require Two-Factor Authentication (2FA)" 
            checked={currentData.require_two_factor_auth} 
            onChange={() => handleToggle('require_two_factor_auth')} 
            description="Enhance account security by requiring a second form of verification."
          />
          <div className="form-group">
            <label htmlFor="session_timeout_minutes">Session Timeout (minutes)</label>
            <input type="number" id="session_timeout_minutes" name="session_timeout_minutes" value={currentData.session_timeout_minutes} onChange={handleChange} min="5" className="form-input" />
            <small>Automatically log out users after inactivity.</small>
          </div>
          <div className="form-group">
            <label htmlFor="password_expiry_days">Password Expiry (days)</label>
            <input type="number" id="password_expiry_days" name="password_expiry_days" value={currentData.password_expiry_days} onChange={handleChange} min="0" className="form-input" />
            <small>Set to 0 to disable password expiration.</small>
          </div>
        </div>
      </section>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Data Retention</h4>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="keep_timesheet_records_months">Keep Timesheet Records (months)</label>
            <input type="number" id="keep_timesheet_records_months" name="keep_timesheet_records_months" value={currentData.keep_timesheet_records_months} onChange={handleChange} min="1" className="form-input" />
            <small>How long to retain detailed timesheet data.</small>
          </div>
          <div className="form-group">
            <label htmlFor="keep_schedule_history_months">Keep Schedule History (months)</label>
            <input type="number" id="keep_schedule_history_months" name="keep_schedule_history_months" value={currentData.keep_schedule_history_months} onChange={handleChange} min="1" className="form-input" />
            <small>How long to retain past schedule data.</small>
          </div>
        </div>
      </section>

      <div className="settings-actions">
        <button type="submit" className="btn btn-primary" disabled={isLoading}>
          {isLoading ? 'Saving...' : 'Save Security Settings'}
        </button>
      </div>
      <p style={{marginTop: '15px', color: '#777'}}>
        <i>Note: Password complexity and login attempt settings are managed under "User Management".</i>
      </p>
    </form>
  );
};

export default SecuritySettings;
