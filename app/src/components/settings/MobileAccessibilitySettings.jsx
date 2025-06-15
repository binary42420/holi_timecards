import React, { useState, useEffect } from 'react';
import ToggleSwitch from '../ToggleSwitch';
import Select from 'react-select';

const MobileAccessibilitySettings = ({ settings, onUpdate, onMarkUnsaved, isLoading }) => {
  const initialFormData = {
    // Mobile App Features
    enable_offline_mode: true,
    offline_data_sync_interval_minutes: 60,
    enable_push_notifications_mobile: true,
    allow_mobile_clock_in_out: true,
    require_gps_for_mobile_clock_in: true,
    // Accessibility
    enable_high_contrast_mode: false,
    font_size_adjustment_percent: 100,
    enable_screen_reader_support: true,
    keyboard_navigation_enhanced: true,
    reduce_motion_effects: false,
    // App Customization
    mobile_theme: 'system', // system, light, dark
    allow_custom_notifications_sounds_mobile: true,
    // Data Usage
    limit_background_data_usage_mobile: false,
    image_quality_mobile: 'medium', // low, medium, high
  };

  const [formData, setFormData] = useState(initialFormData);

  useEffect(() => {
    if (settings && settings.mobile_accessibility_settings) {
      setFormData(prev => ({ ...initialFormData, ...settings.mobile_accessibility_settings }));
    } else if (settings && Object.keys(settings).length > 0 && !settings.mobile_accessibility_settings) {
      setFormData(initialFormData);
    }
  }, [settings]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    let val = type === 'checkbox' ? checked : value;
    if (type === 'number') {
      val = parseInt(value, 10);
      if (isNaN(val)) val = 0;
    }
    setFormData(prev => ({ ...prev, [name]: val }));
    onMarkUnsaved();
  };

  const handleToggle = (name) => {
    setFormData(prev => ({ ...prev, [name]: !prev[name] }));
    onMarkUnsaved();
  };
  
  const handleSelectChange = (name, selectedOption) => {
    setFormData(prev => ({ ...prev, [name]: selectedOption.value }));
    onMarkUnsaved();
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onUpdate('mobile-accessibility', formData);
  };

  if (!settings) {
    return <div>Loading mobile & accessibility settings...</div>;
  }
  const currentData = (settings && settings.mobile_accessibility_settings) 
    ? { ...initialFormData, ...settings.mobile_accessibility_settings } 
    : formData;

  const mobileThemeOptions = [
    { value: 'system', label: 'System Default' },
    { value: 'light', label: 'Light Mode' },
    { value: 'dark', label: 'Dark Mode' },
  ];

  const imageQualityOptions = [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
  ];

  return (
    <form onSubmit={handleSubmit} className="settings-form-category">
      <h3 className="category-title">Mobile App & Accessibility</h3>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Mobile App Features</h4>
        <div className="form-grid">
          <ToggleSwitch label="Enable Offline Mode" checked={currentData.enable_offline_mode} onChange={() => handleToggle('enable_offline_mode')} description="Allow app usage with limited functionality when offline."/>
          <div className="form-group">
            <label htmlFor="offline_data_sync_interval_minutes">Offline Data Sync Interval (minutes)</label>
            <input type="number" id="offline_data_sync_interval_minutes" name="offline_data_sync_interval_minutes" value={currentData.offline_data_sync_interval_minutes} onChange={handleChange} min="5" className="form-input" disabled={!currentData.enable_offline_mode}/>
          </div>
          <ToggleSwitch label="Enable Push Notifications on Mobile" checked={currentData.enable_push_notifications_mobile} onChange={() => handleToggle('enable_push_notifications_mobile')} />
          <ToggleSwitch label="Allow Mobile Clock In/Out" checked={currentData.allow_mobile_clock_in_out} onChange={() => handleToggle('allow_mobile_clock_in_out')} />
          <ToggleSwitch label="Require GPS for Mobile Clock In/Out" checked={currentData.require_gps_for_mobile_clock_in} onChange={() => handleToggle('require_gps_for_mobile_clock_in')} disabled={!currentData.allow_mobile_clock_in_out}/>
        </div>
      </section>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Accessibility Options</h4>
        <div className="form-grid">
          <ToggleSwitch label="Enable High Contrast Mode" checked={currentData.enable_high_contrast_mode} onChange={() => handleToggle('enable_high_contrast_mode')} />
          <div className="form-group">
            <label htmlFor="font_size_adjustment_percent">Font Size Adjustment (%)</label>
            <input type="number" id="font_size_adjustment_percent" name="font_size_adjustment_percent" value={currentData.font_size_adjustment_percent} onChange={handleChange} min="50" max="200" step="10" className="form-input" />
          </div>
          <ToggleSwitch label="Enable Screen Reader Support Enhancements" checked={currentData.enable_screen_reader_support} onChange={() => handleToggle('enable_screen_reader_support')} />
          <ToggleSwitch label="Enhance Keyboard Navigation" checked={currentData.keyboard_navigation_enhanced} onChange={() => handleToggle('keyboard_navigation_enhanced')} />
          <ToggleSwitch label="Reduce Motion Effects" checked={currentData.reduce_motion_effects} onChange={() => handleToggle('reduce_motion_effects')} description="Minimize animations and transitions."/>
        </div>
      </section>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Mobile App Customization</h4>
        <div className="form-grid">
            <div className="form-group">
                <label htmlFor="mobile_theme">Mobile App Theme</label>
                <Select
                    inputId="mobile_theme"
                    options={mobileThemeOptions}
                    value={mobileThemeOptions.find(opt => opt.value === currentData.mobile_theme)}
                    onChange={selectedOption => handleSelectChange('mobile_theme', selectedOption)}
                    classNamePrefix="select"
                />
            </div>
            <ToggleSwitch label="Allow Custom Notification Sounds (Mobile)" checked={currentData.allow_custom_notifications_sounds_mobile} onChange={() => handleToggle('allow_custom_notifications_sounds_mobile')} />
        </div>
      </section>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Mobile Data Usage</h4>
        <div className="form-grid">
            <ToggleSwitch label="Limit Background Data Usage (Mobile)" checked={currentData.limit_background_data_usage_mobile} onChange={() => handleToggle('limit_background_data_usage_mobile')} />
            <div className="form-group">
                <label htmlFor="image_quality_mobile">Image Quality (Mobile App)</label>
                <Select
                    inputId="image_quality_mobile"
                    options={imageQualityOptions}
                    value={imageQualityOptions.find(opt => opt.value === currentData.image_quality_mobile)}
                    onChange={selectedOption => handleSelectChange('image_quality_mobile', selectedOption)}
                    classNamePrefix="select"
                />
                <small>Affects images like profile pictures or job site photos.</small>
            </div>
        </div>
      </section>

      <div className="settings-actions">
        <button type="submit" className="btn btn-primary" disabled={isLoading}>
          {isLoading ? 'Saving...' : 'Save Mobile & Accessibility Settings'}
        </button>
      </div>
    </form>
  );
};

export default MobileAccessibilitySettings;
