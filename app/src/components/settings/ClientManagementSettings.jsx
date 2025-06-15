import React, { useState, useEffect } from 'react';
import ToggleSwitch from '../ToggleSwitch';

const ClientManagementSettings = ({ settings, onUpdate, onMarkUnsaved, isLoading }) => {
  const initialFormData = {
    // Client Onboarding
    auto_approve_client_registrations: false,
    require_client_verification: true,
    require_business_license_verification: true,
    require_insurance_verification: true,
    client_onboarding_checklist_enabled: true,
    // Communication Preferences
    default_communication_method: 'email',
    allow_sms_notifications: true,
    require_job_confirmation: true,
    send_shift_reminders: true,
    shift_reminder_hours_before: 24,
    // Billing & Invoicing
    auto_generate_invoices: true,
    invoice_generation_frequency: 'weekly',
    default_payment_terms_days: 30,
    late_payment_fee_percentage: 2.5,
    require_po_numbers: true,
    allow_credit_applications: true,
    // Job Management by Clients
    clients_can_create_jobs: true,
    clients_can_modify_active_jobs: false,
    clients_can_cancel_jobs: true,
    job_cancellation_notice_hours: 24,
    allow_rush_job_requests: true,
    rush_job_premium_percentage: 25,
    // Worker Requests by Clients
    clients_can_request_specific_workers: true,
    clients_can_exclude_workers: false,
    allow_worker_rating_system: true,
    require_worker_feedback: false,
    // Timesheet & Approval by Clients
    clients_receive_daily_timesheets: true,
    require_client_timesheet_approval: false,
    timesheet_approval_deadline_hours: 48,
    auto_approve_if_no_response: true,
    // Pricing & Rates for Clients
    show_rates_to_clients: false,
    allow_client_rate_negotiation: false,
    use_tiered_pricing: true,
    volume_discount_threshold_hours: 100,
    volume_discount_percentage: 5,
    // Service Areas
    default_service_radius_miles: 50,
    charge_travel_time: true,
    travel_time_rate_percentage: 100,
    minimum_job_duration_hours: 4,
    // Quality Control
    require_job_completion_photos: true,
    send_client_satisfaction_surveys: true,
    survey_frequency: 'after_each_job',
    track_client_complaints: true,
    // Contract Management
    require_signed_contracts: true,
    use_digital_signatures: true,
    contract_auto_renewal: false,
    contract_renewal_notice_days: 30,
    // Emergency Procedures
    emergency_contact_required: true,
    after_hours_support_available: true,
    emergency_response_time_minutes: 30,
    // Data & Privacy
    share_worker_names_with_clients: true,
    share_worker_photos_with_clients: false,
    allow_client_worker_direct_contact: false,
    client_data_retention_years: 7,
    // custom_fields is JSON, needs special handling if editable
  };

  const [formData, setFormData] = useState(initialFormData);

  useEffect(() => {
    if (settings && settings.client_management_settings) {
      setFormData(prev => ({ ...initialFormData, ...settings.client_management_settings }));
    } else if (settings && Object.keys(settings).length > 0 && !settings.client_management_settings) {
      setFormData(initialFormData);
    }
  }, [settings]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    let val = type === 'checkbox' ? checked : value;
    if (type === 'number') {
      val = parseFloat(value);
      if (isNaN(val)) val = 0; // Default to 0 if parsing fails for number
    }
    setFormData(prev => ({ ...prev, [name]: val }));
    onMarkUnsaved();
  };

  const handleToggle = (name) => {
    setFormData(prev => ({ ...prev, [name]: !prev[name] }));
    onMarkUnsaved();
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onUpdate('client-management', formData);
  };

  if (!settings) {
    return <div>Loading client management settings...</div>;
  }
  const currentData = (settings && settings.client_management_settings) ? { ...initialFormData, ...settings.client_management_settings } : formData;

  const communicationMethodOptions = [
    { value: 'email', label: 'Email' },
    { value: 'phone', label: 'Phone' },
    { value: 'portal', label: 'Client Portal' },
  ];

  const invoiceFrequencyOptions = [
    { value: 'daily', label: 'Daily' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'bi-weekly', label: 'Bi-Weekly' },
    { value: 'monthly', label: 'Monthly' },
  ];
  
  const surveyFrequencyOptions = [
      { value: 'after_each_job', label: 'After Each Job' },
      { value: 'weekly', label: 'Weekly' },
      { value: 'monthly', label: 'Monthly' },
      { value: 'quarterly', label: 'Quarterly' },
  ];


  return (
    <form onSubmit={handleSubmit} className="settings-form-category">
      <h3 className="category-title">Client Management</h3>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Client Onboarding</h4>
        <div className="form-grid">
          <ToggleSwitch label="Auto-approve Client Registrations" checked={currentData.auto_approve_client_registrations} onChange={() => handleToggle('auto_approve_client_registrations')} />
          <ToggleSwitch label="Require Client Verification" checked={currentData.require_client_verification} onChange={() => handleToggle('require_client_verification')} />
          <ToggleSwitch label="Require Business License Verification" checked={currentData.require_business_license_verification} onChange={() => handleToggle('require_business_license_verification')} />
          <ToggleSwitch label="Require Insurance Verification" checked={currentData.require_insurance_verification} onChange={() => handleToggle('require_insurance_verification')} />
          <ToggleSwitch label="Enable Client Onboarding Checklist" checked={currentData.client_onboarding_checklist_enabled} onChange={() => handleToggle('client_onboarding_checklist_enabled')} />
        </div>
      </section>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Communication Preferences</h4>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="default_communication_method">Default Communication Method</label>
            <select id="default_communication_method" name="default_communication_method" value={currentData.default_communication_method} onChange={handleChange} className="form-input">
              {communicationMethodOptions.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
            </select>
          </div>
          <ToggleSwitch label="Allow SMS Notifications to Clients" checked={currentData.allow_sms_notifications} onChange={() => handleToggle('allow_sms_notifications')} />
          <ToggleSwitch label="Require Job Confirmation from Client" checked={currentData.require_job_confirmation} onChange={() => handleToggle('require_job_confirmation')} />
          <ToggleSwitch label="Send Shift Reminders to Client Contacts" checked={currentData.send_shift_reminders} onChange={() => handleToggle('send_shift_reminders')} />
          <div className="form-group">
            <label htmlFor="shift_reminder_hours_before">Shift Reminder Lead Time (hours)</label>
            <input type="number" id="shift_reminder_hours_before" name="shift_reminder_hours_before" value={currentData.shift_reminder_hours_before} onChange={handleChange} min="1" className="form-input" />
          </div>
        </div>
      </section>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Billing & Invoicing</h4>
        <div className="form-grid">
          <ToggleSwitch label="Auto-generate Invoices" checked={currentData.auto_generate_invoices} onChange={() => handleToggle('auto_generate_invoices')} />
          <div className="form-group">
            <label htmlFor="invoice_generation_frequency">Invoice Generation Frequency</label>
            <select id="invoice_generation_frequency" name="invoice_generation_frequency" value={currentData.invoice_generation_frequency} onChange={handleChange} className="form-input">
              {invoiceFrequencyOptions.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="default_payment_terms_days">Default Payment Terms (days)</label>
            <input type="number" id="default_payment_terms_days" name="default_payment_terms_days" value={currentData.default_payment_terms_days} onChange={handleChange} min="0" className="form-input" />
          </div>
          <div className="form-group">
            <label htmlFor="late_payment_fee_percentage">Late Payment Fee (%)</label>
            <input type="number" id="late_payment_fee_percentage" name="late_payment_fee_percentage" value={currentData.late_payment_fee_percentage} onChange={handleChange} step="0.1" min="0" className="form-input" />
          </div>
          <ToggleSwitch label="Require PO Numbers for Billing" checked={currentData.require_po_numbers} onChange={() => handleToggle('require_po_numbers')} />
          <ToggleSwitch label="Allow Credit Applications" checked={currentData.allow_credit_applications} onChange={() => handleToggle('allow_credit_applications')} />
        </div>
      </section>
      
      {/* Add more sections for Job Management, Worker Requests, Timesheet & Approval, Pricing, Service Areas, etc. */}

      <div className="settings-actions">
        <button type="submit" className="btn btn-primary" disabled={isLoading}>
          {isLoading ? 'Saving...' : 'Save Client Management Settings'}
        </button>
      </div>
    </form>
  );
};

export default ClientManagementSettings;
