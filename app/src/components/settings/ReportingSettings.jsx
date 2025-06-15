import React, { useState, useEffect } from 'react';
import ToggleSwitch from '../ToggleSwitch';
import Select from 'react-select';

const ReportingSettings = ({ settings, onUpdate, onMarkUnsaved, isLoading }) => {
  const initialFormData = {
    default_report_format: 'pdf',
    include_charts_in_reports: true,
    send_scheduled_reports_email: '',
    report_data_retention_months: 12,
    enable_realtime_analytics: true,
    analytics_dashboard_refresh_interval_seconds: 60,
    custom_report_fields: [], // JSON field, needs special handling
    anonymize_data_in_reports: false,
    default_reporting_period: 'last_month',
    timesheet_export_format: 'csv',
    payroll_export_format: 'csv',
    include_employee_photos_in_reports: false,
    include_job_details_in_reports: true,
    report_access_permissions: 'managers_only', // Example: 'managers_only', 'admins_only', 'managers_and_clients'
  };

  const [formData, setFormData] = useState(initialFormData);

  useEffect(() => {
    if (settings && settings.reporting_settings) {
      const rs = settings.reporting_settings;
      setFormData(prev => ({ 
        ...initialFormData, 
        ...rs,
        // Ensure multi-select or complex fields are handled if they exist
        // custom_report_fields: Array.isArray(rs.custom_report_fields) ? rs.custom_report_fields : [], 
      }));
    } else if (settings && Object.keys(settings).length > 0 && !settings.reporting_settings) {
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
  
  // Example for a multi-select if custom_report_fields were simple strings
  // const handleCustomFieldsChange = (selectedOptions) => {
  //   setFormData(prev => ({ ...prev, custom_report_fields: selectedOptions ? selectedOptions.map(opt => opt.value) : [] }));
  //   onMarkUnsaved();
  // };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Prepare data for saving, especially for JSON fields if they were editable
    const dataToSave = {
      ...formData,
      // custom_report_fields: formData.custom_report_fields, // Already an array of strings if using the example above
    };
    onUpdate('reporting', dataToSave);
  };

  if (!settings) {
    return <div>Loading reporting settings...</div>;
  }
  const currentData = (settings && settings.reporting_settings) 
    ? { ...initialFormData, ...settings.reporting_settings } 
    : formData;

  const reportFormatOptions = [
    { value: 'pdf', label: 'PDF' },
    { value: 'csv', label: 'CSV' },
    { value: 'excel', label: 'Excel (XLSX)' },
  ];
  
  const reportingPeriodOptions = [
      { value: 'last_week', label: 'Last Week'},
      { value: 'last_month', label: 'Last Month'},
      { value: 'last_quarter', label: 'Last Quarter'},
      { value: 'custom_range', label: 'Custom Range (Requires UI)'}
  ];
  
  const accessPermissionOptions = [
      { value: 'managers_only', label: 'Managers Only'},
      { value: 'admins_only', label: 'Admins Only'},
      { value: 'managers_and_clients', label: 'Managers & Clients'}
  ];

  return (
    <form onSubmit={handleSubmit} className="settings-form-category">
      <h3 className="category-title">Reporting & Analytics</h3>

      <section className="settings-subsection">
        <h4 className="subcategory-title">General Report Settings</h4>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="default_report_format">Default Report Format</label>
            <Select
                inputId="default_report_format"
                options={reportFormatOptions}
                value={reportFormatOptions.find(opt => opt.value === currentData.default_report_format)}
                onChange={selectedOption => {
                    setFormData(prev => ({ ...prev, default_report_format: selectedOption.value }));
                    onMarkUnsaved();
                }}
                classNamePrefix="select"
            />
          </div>
          <ToggleSwitch label="Include Charts in Reports" checked={currentData.include_charts_in_reports} onChange={() => handleToggle('include_charts_in_reports')} />
          <div className="form-group">
            <label htmlFor="send_scheduled_reports_email">Send Scheduled Reports To (Email)</label>
            <input type="email" id="send_scheduled_reports_email" name="send_scheduled_reports_email" value={currentData.send_scheduled_reports_email || ''} onChange={handleChange} className="form-input" placeholder="e.g., reports@example.com"/>
          </div>
          <div className="form-group">
            <label htmlFor="report_data_retention_months">Report Data Retention (months)</label>
            <input type="number" id="report_data_retention_months" name="report_data_retention_months" value={currentData.report_data_retention_months} onChange={handleChange} min="1" className="form-input" />
          </div>
        </div>
      </section>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Analytics</h4>
        <div className="form-grid">
          <ToggleSwitch label="Enable Real-time Analytics Dashboard" checked={currentData.enable_realtime_analytics} onChange={() => handleToggle('enable_realtime_analytics')} />
          <div className="form-group">
            <label htmlFor="analytics_dashboard_refresh_interval_seconds">Analytics Refresh Interval (seconds)</label>
            <input type="number" id="analytics_dashboard_refresh_interval_seconds" name="analytics_dashboard_refresh_interval_seconds" value={currentData.analytics_dashboard_refresh_interval_seconds} onChange={handleChange} min="10" className="form-input" disabled={!currentData.enable_realtime_analytics} />
          </div>
        </div>
      </section>
      
      <section className="settings-subsection">
        <h4 className="subcategory-title">Data Export & Display</h4>
        <div className="form-grid">
            <div className="form-group">
                <label htmlFor="default_reporting_period">Default Reporting Period</label>
                <Select
                    inputId="default_reporting_period"
                    options={reportingPeriodOptions}
                    value={reportingPeriodOptions.find(opt => opt.value === currentData.default_reporting_period)}
                    onChange={selectedOption => {
                        setFormData(prev => ({ ...prev, default_reporting_period: selectedOption.value }));
                        onMarkUnsaved();
                    }}
                    classNamePrefix="select"
                />
            </div>
            <div className="form-group">
                <label htmlFor="timesheet_export_format">Timesheet Export Format</label>
                 <Select
                    inputId="timesheet_export_format"
                    options={reportFormatOptions.filter(opt => ['csv', 'excel'].includes(opt.value))}
                    value={reportFormatOptions.find(opt => opt.value === currentData.timesheet_export_format)}
                    onChange={selectedOption => {
                        setFormData(prev => ({ ...prev, timesheet_export_format: selectedOption.value }));
                        onMarkUnsaved();
                    }}
                    classNamePrefix="select"
                />
            </div>
            <div className="form-group">
                <label htmlFor="payroll_export_format">Payroll Export Format</label>
                 <Select
                    inputId="payroll_export_format"
                    options={reportFormatOptions.filter(opt => ['csv', 'excel'].includes(opt.value))} // Assuming similar formats
                    value={reportFormatOptions.find(opt => opt.value === currentData.payroll_export_format)}
                    onChange={selectedOption => {
                        setFormData(prev => ({ ...prev, payroll_export_format: selectedOption.value }));
                        onMarkUnsaved();
                    }}
                    classNamePrefix="select"
                />
            </div>
            <ToggleSwitch label="Include Employee Photos in Reports" checked={currentData.include_employee_photos_in_reports} onChange={() => handleToggle('include_employee_photos_in_reports')} />
            <ToggleSwitch label="Include Full Job Details in Reports" checked={currentData.include_job_details_in_reports} onChange={() => handleToggle('include_job_details_in_reports')} />
             <div className="form-group">
                <label htmlFor="report_access_permissions">Report Access Permissions</label>
                <Select
                    inputId="report_access_permissions"
                    options={accessPermissionOptions}
                    value={accessPermissionOptions.find(opt => opt.value === currentData.report_access_permissions)}
                    onChange={selectedOption => {
                        setFormData(prev => ({ ...prev, report_access_permissions: selectedOption.value }));
                        onMarkUnsaved();
                    }}
                    classNamePrefix="select"
                />
            </div>
            <ToggleSwitch label="Anonymize Data in Aggregated Reports" checked={currentData.anonymize_data_in_reports} onChange={() => handleToggle('anonymize_data_in_reports')} />
        </div>
      </section>
      
      {/* Custom Report Fields would require a more complex UI (e.g., dynamic list of fields) */}
      {/* <section className="settings-subsection">
        <h4 className="subcategory-title">Custom Report Fields</h4>
        <p>Define custom fields to include in reports.</p>
        // UI for managing JSON array of {name, type, source_table, source_field}
      </section> */}

      <div className="settings-actions">
        <button type="submit" className="btn btn-primary" disabled={isLoading}>
          {isLoading ? 'Saving...' : 'Save Reporting Settings'}
        </button>
      </div>
    </form>
  );
};

export default ReportingSettings;
