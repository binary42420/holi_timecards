import React, { useState, useEffect } from 'react';
import ToggleSwitch from '../ToggleSwitch';
import Select from 'react-select'; // For multi-select like closed_days

const SchedulingSettings = ({ settings, onUpdate, onMarkUnsaved, isLoading }) => {
  const dayOptions = [
    { value: 'sunday', label: 'Sunday' },
    { value: 'monday', label: 'Monday' },
    { value: 'tuesday', label: 'Tuesday' },
    { value: 'wednesday', label: 'Wednesday' },
    { value: 'thursday', label: 'Thursday' },
    { value: 'friday', label: 'Friday' },
    { value: 'saturday', label: 'Saturday' }
  ];

  const initialFormData = {
    // Basic scheduling
    shifts_per_day: 2,
    max_workers_per_shift: 10,
    min_workers_per_shift: 1,
    // Operating hours (simplified for now, full DateTime might be complex for this form)
    // business_start_time: '', // Example: "09:00"
    // business_end_time: '',   // Example: "17:00"
    default_shift_duration_hours: 8,
    break_duration_minutes: 30,
    // Days and scheduling
    closed_days: [], // Array of strings e.g., ["sunday", "saturday"]
    // operating_days: [], // This is also a JSON field
    // Request Windows (Automation part)
    auto_open_request_windows: true,
    request_window_days_ahead: 7,
    request_window_duration_hours: 72,
    // Manual window times (requests_window_start, requests_window_end) are handled in ManagerSettings.jsx
  };

  const [formData, setFormData] = useState(initialFormData);

  useEffect(() => {
    if (settings && settings.workplace_settings) {
      const ws = settings.workplace_settings;
      setFormData(prev => ({
        ...initialFormData,
        ...ws,
        // Ensure multi-select fields are initialized correctly for react-select
        closed_days: Array.isArray(ws.closed_days) 
          ? ws.closed_days.map(dayValue => dayOptions.find(opt => opt.value === dayValue)).filter(Boolean) 
          : [],
      }));
    } else if (settings && Object.keys(settings).length > 0 && !settings.workplace_settings) {
      setFormData(initialFormData);
    }
  }, [settings]);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    const val = type === 'number' ? parseInt(value, 10) : value;
    setFormData(prev => ({ ...prev, [name]: val }));
    onMarkUnsaved();
  };

  const handleToggle = (name) => {
    setFormData(prev => ({ ...prev, [name]: !prev[name] }));
    onMarkUnsaved();
  };

  const handleMultiSelectChange = (name, selectedOptions) => {
    setFormData(prev => ({ ...prev, [name]: selectedOptions || [] }));
    onMarkUnsaved();
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const dataToSave = {
      ...formData,
      closed_days: formData.closed_days.map(opt => opt.value), // Convert back to array of strings
    };
    onUpdate('workplace_settings', dataToSave); // Key for WorkplaceSettings
  };
  
  if (!settings) {
    return <div>Loading scheduling settings...</div>;
  }
  // Use currentData to ensure form is responsive even if settings.workplace_settings is initially undefined
  const currentData = (settings && settings.workplace_settings) 
    ? { ...initialFormData, ...settings.workplace_settings, closed_days: formData.closed_days } 
    : formData;


  return (
    <form onSubmit={handleSubmit} className="settings-form-category">
      <h3 className="category-title">Scheduling Preferences</h3>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Basic Scheduling</h4>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="shifts_per_day">Default Shifts Per Day</label>
            <input type="number" id="shifts_per_day" name="shifts_per_day" value={currentData.shifts_per_day} onChange={handleChange} min="1" max="5" className="form-input" />
          </div>
          <div className="form-group">
            <label htmlFor="max_workers_per_shift">Max Workers Per Shift</label>
            <input type="number" id="max_workers_per_shift" name="max_workers_per_shift" value={currentData.max_workers_per_shift} onChange={handleChange} min="1" className="form-input" />
          </div>
          <div className="form-group">
            <label htmlFor="min_workers_per_shift">Min Workers Per Shift</label>
            <input type="number" id="min_workers_per_shift" name="min_workers_per_shift" value={currentData.min_workers_per_shift} onChange={handleChange} min="0" className="form-input" />
          </div>
          <div className="form-group">
            <label htmlFor="default_shift_duration_hours">Default Shift Duration (hours)</label>
            <input type="number" id="default_shift_duration_hours" name="default_shift_duration_hours" value={currentData.default_shift_duration_hours} onChange={handleChange} min="1" max="24" className="form-input" />
          </div>
          <div className="form-group">
            <label htmlFor="break_duration_minutes">Default Break Duration (minutes)</label>
            <input type="number" id="break_duration_minutes" name="break_duration_minutes" value={currentData.break_duration_minutes} onChange={handleChange} min="0" step="5" className="form-input" />
          </div>
        </div>
      </section>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Operating Days</h4>
        <div className="form-group">
          <label htmlFor="closed_days">Closed Days</label>
          <Select
            inputId="closed_days"
            isMulti
            name="closed_days"
            options={dayOptions}
            className="basic-multi-select"
            classNamePrefix="select"
            value={currentData.closed_days}
            onChange={(selected) => handleMultiSelectChange('closed_days', selected)}
          />
          <small>Select days when the business is typically closed.</small>
        </div>
        {/* Operating days could be another multi-select if needed */}
      </section>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Request Window Automation</h4>
        <ToggleSwitch 
          label="Auto-open Request Windows" 
          checked={currentData.auto_open_request_windows} 
          onChange={() => handleToggle('auto_open_request_windows')} 
          description="Automatically open shift request windows based on the settings below."
        />
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="request_window_days_ahead">Open Window X Days Before Shift Week</label>
            <input type="number" id="request_window_days_ahead" name="request_window_days_ahead" value={currentData.request_window_days_ahead} onChange={handleChange} min="1" className="form-input" disabled={!currentData.auto_open_request_windows}/>
          </div>
          <div className="form-group">
            <label htmlFor="request_window_duration_hours">Request Window Duration (hours)</label>
            <input type="number" id="request_window_duration_hours" name="request_window_duration_hours" value={currentData.request_window_duration_hours} onChange={handleChange} min="1" className="form-input" disabled={!currentData.auto_open_request_windows}/>
          </div>
        </div>
        <small>Manual request window start/end times are set in the 'Schedule Window' tab under Basic Settings.</small>
      </section>

      <div className="settings-actions">
        <button type="submit" className="btn btn-primary" disabled={isLoading}>
          {isLoading ? 'Saving...' : 'Save Scheduling Settings'}
        </button>
      </div>
    </form>
  );
};

export default SchedulingSettings;
