import React, { useState, useEffect } from 'react';
import ToggleSwitch from '../ToggleSwitch';

const NotificationSettings = ({ settings, onUpdate, onMarkUnsaved, isLoading }) => {
  const initialFormData = {
    // Email notifications
    email_notifications_enabled: true,
    notify_on_shift_requests: true,
    notify_on_worker_assignments: true,
    notify_on_timesheet_submissions: true,
    notify_on_schedule_changes: true,
    // SMS notifications
    sms_notifications_enabled: false,
    sms_urgent_only: true,
    // In-app notifications
    push_notifications_enabled: true,
    notification_sound_enabled: true,
  };

  const [formData, setFormData] = useState(initialFormData);

  useEffect(() => {
    if (settings && settings.workplace_settings) { // Data comes from workplace_settings
      setFormData(prev => ({ ...initialFormData, ...settings.workplace_settings }));
    } else if (settings && Object.keys(settings).length > 0 && !settings.workplace_settings) {
      setFormData(initialFormData);
    }
  }, [settings]);

  const handleToggle = (name) => {
    setFormData(prev => ({ ...prev, [name]: !prev[name] }));
    onMarkUnsaved();
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onUpdate('workplace_settings', formData); // Updates WorkplaceSettings
  };

  if (!settings) {
    return <div>Loading notification settings...</div>;
  }
  // Use currentData to ensure form is responsive even if settings.workplace_settings is initially undefined
  const currentData = (settings && settings.workplace_settings) 
    ? { ...initialFormData, ...settings.workplace_settings } 
    : formData;

  return (
    <form onSubmit={handleSubmit} className="settings-form-category">
      <h3 className="category-title">Notification Preferences</h3>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Email Notifications</h4>
        <div className="form-grid">
          <ToggleSwitch label="Enable Email Notifications" checked={currentData.email_notifications_enabled} onChange={() => handleToggle('email_notifications_enabled')} description="Global switch for all email notifications."/>
          <ToggleSwitch label="Notify on New Shift Requests" checked={currentData.notify_on_shift_requests} onChange={() => handleToggle('notify_on_shift_requests')} description="When employees submit their availability or requests."/>
          <ToggleSwitch label="Notify on Worker Assignments" checked={currentData.notify_on_worker_assignments} onChange={() => handleToggle('notify_on_worker_assignments')} description="When workers are assigned to or unassigned from shifts."/>
          <ToggleSwitch label="Notify on Timesheet Submissions" checked={currentData.notify_on_timesheet_submissions} onChange={() => handleToggle('notify_on_timesheet_submissions')} description="When crew chiefs or workers submit timesheets."/>
          <ToggleSwitch label="Notify on Schedule Changes" checked={currentData.notify_on_schedule_changes} onChange={() => handleToggle('notify_on_schedule_changes')} description="When a published schedule is modified."/>
        </div>
      </section>

      <section className="settings-subsection">
        <h4 className="subcategory-title">SMS Notifications</h4>
        <div className="form-grid">
          <ToggleSwitch label="Enable SMS Notifications" checked={currentData.sms_notifications_enabled} onChange={() => handleToggle('sms_notifications_enabled')} description="Global switch for SMS alerts (carrier rates may apply)."/>
          <ToggleSwitch label="Send SMS for Urgent Matters Only" checked={currentData.sms_urgent_only} onChange={() => handleToggle('sms_urgent_only')} description="e.g., last-minute shift changes or cancellations."/>
        </div>
      </section>
      
      <section className="settings-subsection">
        <h4 className="subcategory-title">In-App / Push Notifications</h4>
        <div className="form-grid">
          <ToggleSwitch label="Enable Push Notifications (Mobile App)" checked={currentData.push_notifications_enabled} onChange={() => handleToggle('push_notifications_enabled')} description="For users of the mobile application."/>
          <ToggleSwitch label="Enable Notification Sounds (In-App)" checked={currentData.notification_sound_enabled} onChange={() => handleToggle('notification_sound_enabled')} description="Play a sound for new notifications in the web/mobile app."/>
        </div>
      </section>

      <div className="settings-actions">
        <button type="submit" className="btn btn-primary" disabled={isLoading}>
          {isLoading ? 'Saving...' : 'Save Notification Settings'}
        </button>
      </div>
    </form>
  );
};

export default NotificationSettings;
