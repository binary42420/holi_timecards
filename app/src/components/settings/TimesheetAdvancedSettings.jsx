import React, { useState, useEffect } from 'react';
import ToggleSwitch from '../ToggleSwitch';

const TimesheetAdvancedSettings = ({ settings, onUpdate, onMarkUnsaved, isLoading }) => {
  const initialFormData = {
    // Time tracking
    require_photo_clock_in: false,
    require_location_verification: false,
    auto_clock_out_hours: 12,
    location_verification_radius_feet: 100, // Added from model
    allow_early_clock_in_minutes: 15,    // Added from model
    allow_late_clock_out_minutes: 15,     // Added from model
    max_clock_pairs_per_shift: 3,         // Added from model
    require_break_documentation: true,    // Added from model
    auto_deduct_unpaid_breaks: true,      // Added from model
    // Overtime rules
    overtime_threshold_daily: 8,
    overtime_threshold_weekly: 40,
    overtime_rate_multiplier: 1.5,
    // Approval workflow
    require_manager_approval: true, // This is for timesheets
    auto_approve_regular_hours: false,
    auto_approve_overtime: false,
  };

  const [formData, setFormData] = useState(initialFormData);

  useEffect(() => {
    if (settings && settings.workplace_settings) { // Data comes from workplace_settings
      setFormData(prev => ({ ...initialFormData, ...settings.workplace_settings }));
    } else if (settings && Object.keys(settings).length > 0 && !settings.workplace_settings) {
      setFormData(initialFormData);
    }
  }, [settings]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    let val = type === 'checkbox' ? checked : value;
    if (type === 'number') {
      val = parseFloat(value); // Use parseFloat for rates/multipliers
      if (isNaN(val)) val = name.includes('rate') || name.includes('multiplier') ? 0.0 : 0;
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
    // Updates a part of WorkplaceSettings, so use the same category key
    onUpdate('workplace_settings', formData); 
  };

  if (!settings) {
    return <div>Loading advanced timesheet settings...</div>;
  }
  const currentData = (settings && settings.workplace_settings) 
    ? { ...initialFormData, ...settings.workplace_settings } 
    : formData;

  return (
    <form onSubmit={handleSubmit} className="settings-form-category">
      <h3 className="category-title">Advanced Timesheet & Payroll Settings</h3>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Time Tracking Rules</h4>
        <div className="form-grid">
          <ToggleSwitch label="Require Photo at Clock-In" checked={currentData.require_photo_clock_in} onChange={() => handleToggle('require_photo_clock_in')} />
          <ToggleSwitch label="Require Location Verification for Clock-In/Out" checked={currentData.require_location_verification} onChange={() => handleToggle('require_location_verification')} />
          <div className="form-group">
            <label htmlFor="location_verification_radius_feet">Location Verification Radius (feet)</label>
            <input type="number" id="location_verification_radius_feet" name="location_verification_radius_feet" value={currentData.location_verification_radius_feet} onChange={handleChange} min="0" className="form-input" />
          </div>
          <div className="form-group">
            <label htmlFor="allow_early_clock_in_minutes">Allow Early Clock-In (minutes before shift)</label>
            <input type="number" id="allow_early_clock_in_minutes" name="allow_early_clock_in_minutes" value={currentData.allow_early_clock_in_minutes} onChange={handleChange} min="0" className="form-input" />
          </div>
          <div className="form-group">
            <label htmlFor="allow_late_clock_out_minutes">Allow Late Clock-Out (minutes after shift)</label>
            <input type="number" id="allow_late_clock_out_minutes" name="allow_late_clock_out_minutes" value={currentData.allow_late_clock_out_minutes} onChange={handleChange} min="0" className="form-input" />
          </div>
          <div className="form-group">
            <label htmlFor="auto_clock_out_hours">Auto Clock-Out After (hours on shift)</label>
            <input type="number" id="auto_clock_out_hours" name="auto_clock_out_hours" value={currentData.auto_clock_out_hours} onChange={handleChange} min="1" className="form-input" />
          </div>
           <div className="form-group">
            <label htmlFor="max_clock_pairs_per_shift">Max Clock In/Out Pairs Per Shift (for breaks)</label>
            <input type="number" id="max_clock_pairs_per_shift" name="max_clock_pairs_per_shift" value={currentData.max_clock_pairs_per_shift} onChange={handleChange} min="1" max="5" className="form-input" />
          </div>
          <ToggleSwitch label="Require Break Documentation" checked={currentData.require_break_documentation} onChange={() => handleToggle('require_break_documentation')} />
          <ToggleSwitch label="Auto-deduct Unpaid Breaks" checked={currentData.auto_deduct_unpaid_breaks} onChange={() => handleToggle('auto_deduct_unpaid_breaks')} />
        </div>
      </section>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Overtime Rules</h4>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="overtime_threshold_daily">Daily Overtime Threshold (hours)</label>
            <input type="number" id="overtime_threshold_daily" name="overtime_threshold_daily" value={currentData.overtime_threshold_daily} onChange={handleChange} step="0.1" min="0" className="form-input" />
          </div>
          <div className="form-group">
            <label htmlFor="overtime_threshold_weekly">Weekly Overtime Threshold (hours)</label>
            <input type="number" id="overtime_threshold_weekly" name="overtime_threshold_weekly" value={currentData.overtime_threshold_weekly} onChange={handleChange} step="0.1" min="0" className="form-input" />
          </div>
          <div className="form-group">
            <label htmlFor="overtime_rate_multiplier">Overtime Rate Multiplier</label>
            <input type="number" id="overtime_rate_multiplier" name="overtime_rate_multiplier" value={currentData.overtime_rate_multiplier} onChange={handleChange} step="0.01" min="1" className="form-input" />
          </div>
        </div>
      </section>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Timesheet Approval Workflow</h4>
        <div className="form-grid">
          <ToggleSwitch label="Require Manager Approval for Timesheets" checked={currentData.require_manager_approval} onChange={() => handleToggle('require_manager_approval')} />
          <ToggleSwitch label="Auto-approve Regular Hours" checked={currentData.auto_approve_regular_hours} onChange={() => handleToggle('auto_approve_regular_hours')} />
          <ToggleSwitch label="Auto-approve Overtime Hours" checked={currentData.auto_approve_overtime} onChange={() => handleToggle('auto_approve_overtime')} />
        </div>
      </section>

      <div className="settings-actions">
        <button type="submit" className="btn btn-primary" disabled={isLoading}>
          {isLoading ? 'Saving...' : 'Save Timesheet Settings'}
        </button>
      </div>
    </form>
  );
};

export default TimesheetAdvancedSettings;
