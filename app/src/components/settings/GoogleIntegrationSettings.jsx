import React, { useState, useEffect } from 'react';
import ToggleSwitch from '../ToggleSwitch';

const GoogleIntegrationSettings = ({ settings, onUpdate, onMarkUnsaved, isLoading, onAdminAction }) => {
  const initialFormData = {
    enable_google_sso: false,
    google_client_id: '',
    google_client_secret: '',
    google_calendar_sync_enabled: false,
    google_calendar_default_visibility: 'private',
    google_calendar_sync_frequency_minutes: 60,
    google_maps_api_key: '',
    enable_google_drive_integration: false,
  };

  const [formData, setFormData] = useState(initialFormData);
  const [testConnectionStatus, setTestConnectionStatus] = useState(''); 
  const [syncStatus, setSyncStatus] = useState('');


  useEffect(() => {
    if (settings && settings.google_integration_settings) {
      setFormData(prev => ({ ...initialFormData, ...settings.google_integration_settings }));
    } else if (settings && Object.keys(settings).length > 0 && !settings.google_integration_settings) {
      setFormData(initialFormData);
    }
  }, [settings]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const val = type === 'checkbox' ? checked : value;
    setFormData(prev => ({ ...prev, [name]: val }));
    onMarkUnsaved();
  };

  const handleToggle = (name) => {
    setFormData(prev => ({ ...prev, [name]: !prev[name] }));
    onMarkUnsaved();
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const dataToSave = { ...formData };
    if (dataToSave.google_client_secret && dataToSave.google_client_secret.startsWith('********') && dataToSave.google_client_secret.length === (settings?.google_integration_settings?.google_client_secret?.length || 8)) {
        delete dataToSave.google_client_secret;
    }
    if (dataToSave.google_maps_api_key && dataToSave.google_maps_api_key.startsWith('********') && dataToSave.google_maps_api_key.length === (settings?.google_integration_settings?.google_maps_api_key?.length || 8)) {
        delete dataToSave.google_maps_api_key;
    }
    onUpdate('google-integration', dataToSave);
  };

  const handleTestConnection = () => {
    setTestConnectionStatus('Testing...');
    if (onAdminAction) onAdminAction(1113, { client_id: formData.google_client_id, client_secret: formData.google_client_secret });
    else console.error("onAdminAction prop not provided to GoogleIntegrationSettings");
    setTimeout(() => setTestConnectionStatus(''), 5000); 
  };

  const handleManualSync = () => {
    setSyncStatus('Syncing...');
    if (onAdminAction) onAdminAction(1114, {});
    else console.error("onAdminAction prop not provided to GoogleIntegrationSettings");
    setTimeout(() => setSyncStatus(''), 5000); 
  };
  
  if (!settings) {
    return <div>Loading Google integration settings...</div>;
  }
  const currentData = (settings && settings.google_integration_settings) 
    ? { ...initialFormData, ...settings.google_integration_settings } 
    : formData;

  return (
    <form onSubmit={handleSubmit} className="settings-form-category">
      <h3 className="category-title">Google Integration Settings</h3>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Google Sign-In (SSO)</h4>
        <div className="form-grid">
          <ToggleSwitch 
            label="Enable Google Single Sign-On" 
            checked={currentData.enable_google_sso} 
            onChange={() => handleToggle('enable_google_sso')} 
            description="Allow users to sign in/up with their Google accounts."
          />
          <div className="form-group">
            <label htmlFor="google_client_id">Google Client ID</label>
            <input type="text" id="google_client_id" name="google_client_id" value={currentData.google_client_id || ''} onChange={handleChange} className="form-input" />
          </div>
          <div className="form-group">
            <label htmlFor="google_client_secret">Google Client Secret</label>
            <input 
                type="password" 
                id="google_client_secret" 
                name="google_client_secret" 
                placeholder={currentData.google_client_secret ? "********" : "Enter new secret"}
                onChange={handleChange} className="form-input" />
            <small>Leave blank to keep existing secret. Enter new value to update.</small>
          </div>
        </div>
      </section>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Google Calendar Integration</h4>
        <div className="form-grid">
          <ToggleSwitch 
            label="Enable Google Calendar Sync" 
            checked={currentData.google_calendar_sync_enabled} 
            onChange={() => handleToggle('google_calendar_sync_enabled')} 
            description="Sync employee schedules with their Google Calendars."
          />
          <div className="form-group">
            <label htmlFor="google_calendar_default_visibility">Default Calendar Event Visibility</label>
            <select id="google_calendar_default_visibility" name="google_calendar_default_visibility" value={currentData.google_calendar_default_visibility} onChange={handleChange} className="form-input">
              <option value="private">Private</option>
              <option value="public">Public</option>
              <option value="default">Calendar Default</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="google_calendar_sync_frequency_minutes">Calendar Sync Frequency (minutes)</label>
            <input type="number" id="google_calendar_sync_frequency_minutes" name="google_calendar_sync_frequency_minutes" value={currentData.google_calendar_sync_frequency_minutes} onChange={handleChange} min="5" className="form-input" />
          </div>
        </div>
      </section>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Google Maps Integration</h4>
        <div className="form-grid">
          <div className="form-group full-width">
            <label htmlFor="google_maps_api_key">Google Maps API Key</label>
            <input type="password" id="google_maps_api_key" name="google_maps_api_key" 
                   placeholder={currentData.google_maps_api_key ? "********" : "Enter API Key"}
                   onChange={handleChange} className="form-input" />
            <small>For location services and mapping features. Leave blank to keep existing key.</small>
          </div>
        </div>
      </section>

       <section className="settings-subsection">
        <h4 className="subcategory-title">Google Drive Integration</h4>
        <div className="form-grid">
            <ToggleSwitch 
                label="Enable Google Drive Integration" 
                checked={currentData.enable_google_drive_integration} 
                onChange={() => handleToggle('enable_google_drive_integration')} 
                description="Allow linking or storing documents in Google Drive (e.g., for certifications)."
            />
        </div>
      </section>
      
      <div className="settings-actions">
        <button type="submit" className="btn btn-primary" disabled={isLoading}>
          {isLoading ? 'Saving...' : 'Save Google Settings'}
        </button>
      </div>

      <div className="admin-actions-group" style={{marginTop: '20px', borderTop: '1px solid #eee', paddingTop: '20px'}}>
        <h4 className="subcategory-title">Connection & Sync</h4>
        <div className="settings-actions spaced">
            <button type="button" onClick={handleTestConnection} className="btn btn-secondary" disabled={isLoading || !currentData.enable_google_sso}>
            Test Google Connection
            </button>
            {testConnectionStatus && <span className="action-status">{testConnectionStatus}</span>}
        </div>
        <div className="settings-actions spaced" style={{marginTop: '10px'}}>
            <button type="button" onClick={handleManualSync} className="btn btn-secondary" disabled={isLoading || !currentData.google_calendar_sync_enabled}>
            Manual Calendar Sync
            </button>
            {syncStatus && <span className="action-status">{syncStatus}</span>}
        </div>
      </div>
    </form>
  );
};

export default GoogleIntegrationSettings;
