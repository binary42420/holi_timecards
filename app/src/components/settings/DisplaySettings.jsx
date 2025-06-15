import React, { useState, useEffect } from 'react';
import './SettingsStyles.css';

const DisplaySettings = ({ 
  settings, 
  onSettingChange, 
  onSave, 
  hasUnsavedChanges, 
  isSaving 
}) => {
  const [localSettings, setLocalSettings] = useState({
    theme: 'light',
    fontSize: 'medium',
    colorScheme: 'default',
    compactMode: false,
    showAvatars: true,
    animationsEnabled: true,
    highContrast: false,
    reducedMotion: false,
    customColors: {
      primary: '#007bff',
      secondary: '#6c757d',
      success: '#28a745',
      warning: '#ffc107',
      danger: '#dc3545'
    }
  });

  useEffect(() => {
    if (settings) {
      setLocalSettings(prev => ({
        ...prev,
        ...settings
      }));
    }
  }, [settings]);

  const handleChange = (key, value) => {
    const newSettings = { ...localSettings, [key]: value };
    setLocalSettings(newSettings);
    onSettingChange(key, value);
  };

  const handleColorChange = (colorKey, value) => {
    const newCustomColors = { ...localSettings.customColors, [colorKey]: value };
    const newSettings = { ...localSettings, customColors: newCustomColors };
    setLocalSettings(newSettings);
    onSettingChange('customColors', newCustomColors);
  };

  return (
    <div className="settings-section">
      <div className="settings-header">
        <h2>Display Settings</h2>
        <p>Customize the appearance and visual preferences of the application</p>
      </div>

      <div className="settings-grid">
        {/* Theme Settings */}
        <div className="setting-group">
          <h3>Theme & Appearance</h3>
          
          <div className="setting-item">
            <label htmlFor="theme">Theme</label>
            <select
              id="theme"
              value={localSettings.theme}
              onChange={(e) => handleChange('theme', e.target.value)}
              disabled={isSaving}
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="auto">Auto (System)</option>
            </select>
            <small>Choose your preferred color theme</small>
          </div>

          <div className="setting-item">
            <label htmlFor="colorScheme">Color Scheme</label>
            <select
              id="colorScheme"
              value={localSettings.colorScheme}
              onChange={(e) => handleChange('colorScheme', e.target.value)}
              disabled={isSaving}
            >
              <option value="default">Default</option>
              <option value="blue">Blue</option>
              <option value="green">Green</option>
              <option value="purple">Purple</option>
              <option value="custom">Custom</option>
            </select>
            <small>Select a color scheme for the interface</small>
          </div>

          <div className="setting-item">
            <label htmlFor="fontSize">Font Size</label>
            <select
              id="fontSize"
              value={localSettings.fontSize}
              onChange={(e) => handleChange('fontSize', e.target.value)}
              disabled={isSaving}
            >
              <option value="small">Small</option>
              <option value="medium">Medium</option>
              <option value="large">Large</option>
              <option value="extra-large">Extra Large</option>
            </select>
            <small>Adjust text size for better readability</small>
          </div>
        </div>

        {/* Layout Settings */}
        <div className="setting-group">
          <h3>Layout & Interface</h3>
          
          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={localSettings.compactMode}
                onChange={(e) => handleChange('compactMode', e.target.checked)}
                disabled={isSaving}
              />
              Compact Mode
            </label>
            <small>Reduce spacing and padding for more content on screen</small>
          </div>

          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={localSettings.showAvatars}
                onChange={(e) => handleChange('showAvatars', e.target.checked)}
                disabled={isSaving}
              />
              Show User Avatars
            </label>
            <small>Display profile pictures throughout the interface</small>
          </div>

          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={localSettings.animationsEnabled}
                onChange={(e) => handleChange('animationsEnabled', e.target.checked)}
                disabled={isSaving}
              />
              Enable Animations
            </label>
            <small>Show smooth transitions and animations</small>
          </div>
        </div>

        {/* Accessibility Settings */}
        <div className="setting-group">
          <h3>Accessibility</h3>
          
          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={localSettings.highContrast}
                onChange={(e) => handleChange('highContrast', e.target.checked)}
                disabled={isSaving}
              />
              High Contrast Mode
            </label>
            <small>Increase contrast for better visibility</small>
          </div>

          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={localSettings.reducedMotion}
                onChange={(e) => handleChange('reducedMotion', e.target.checked)}
                disabled={isSaving}
              />
              Reduce Motion
            </label>
            <small>Minimize animations and transitions</small>
          </div>
        </div>

        {/* Custom Colors */}
        {localSettings.colorScheme === 'custom' && (
          <div className="setting-group">
            <h3>Custom Colors</h3>
            
            <div className="color-grid">
              <div className="setting-item">
                <label htmlFor="primaryColor">Primary Color</label>
                <input
                  type="color"
                  id="primaryColor"
                  value={localSettings.customColors.primary}
                  onChange={(e) => handleColorChange('primary', e.target.value)}
                  disabled={isSaving}
                />
              </div>

              <div className="setting-item">
                <label htmlFor="secondaryColor">Secondary Color</label>
                <input
                  type="color"
                  id="secondaryColor"
                  value={localSettings.customColors.secondary}
                  onChange={(e) => handleColorChange('secondary', e.target.value)}
                  disabled={isSaving}
                />
              </div>

              <div className="setting-item">
                <label htmlFor="successColor">Success Color</label>
                <input
                  type="color"
                  id="successColor"
                  value={localSettings.customColors.success}
                  onChange={(e) => handleColorChange('success', e.target.value)}
                  disabled={isSaving}
                />
              </div>

              <div className="setting-item">
                <label htmlFor="warningColor">Warning Color</label>
                <input
                  type="color"
                  id="warningColor"
                  value={localSettings.customColors.warning}
                  onChange={(e) => handleColorChange('warning', e.target.value)}
                  disabled={isSaving}
                />
              </div>

              <div className="setting-item">
                <label htmlFor="dangerColor">Danger Color</label>
                <input
                  type="color"
                  id="dangerColor"
                  value={localSettings.customColors.danger}
                  onChange={(e) => handleColorChange('danger', e.target.value)}
                  disabled={isSaving}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="settings-actions">
        <button
          onClick={onSave}
          disabled={!hasUnsavedChanges || isSaving}
          className="save-button"
        >
          {isSaving ? 'Saving...' : 'Save Display Settings'}
        </button>
      </div>
    </div>
  );
};

export default DisplaySettings;
