import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
import CompanyProfileSettings from './settings/CompanyProfileSettings';
import UserManagementSettings from './settings/UserManagementSettings';
import CertificationsSettings from './settings/CertificationsSettings';
import ClientManagementSettings from './settings/ClientManagementSettings';
import JobConfigurationSettings from './settings/JobConfigurationSettings';
import SchedulingSettings from './settings/SchedulingSettings';
import TimesheetAdvancedSettings from './settings/TimesheetAdvancedSettings';
import NotificationSettings from './settings/NotificationSettings';
import GoogleIntegrationSettings from './settings/GoogleIntegrationSettings';
import ReportingSettings from './settings/ReportingSettings';
import SecuritySettings from './settings/SecuritySettings';
import MobileAccessibilitySettings from './settings/MobileAccessibilitySettings';
import SystemAdminSettings from './settings/SystemAdminSettings';
import DisplaySettings from './settings/DisplaySettings';
import './EnhancedSettingsPage.css';

const EnhancedSettingsPage = () => {
  const { socket } = useSocket();
  const [settings, setSettings] = useState(null);
  const [activeTab, setActiveTab] = useState('company-profile');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const tabs = [
    { id: 'company-profile', label: 'Company Profile', icon: '🏢', description: 'Company information, branding, and contact details' },
    { id: 'user-management', label: 'User Management', icon: '👥', description: 'Role management, permissions, and approval workflows' },
    { id: 'certifications', label: 'Certifications & Roles', icon: '🎓', description: 'Employee certifications, role definitions, and training' },
    { id: 'client-management', label: 'Client Management', icon: '🤝', description: 'Client onboarding, communication, and billing settings' },
    { id: 'job-configuration', label: 'Job & Shift Config', icon: '⚙️', description: 'Job templates, shift requirements, and locations' },
    { id: 'scheduling', label: 'Scheduling', icon: '📅', description: 'Shift scheduling and timing preferences' },
    { id: 'timesheet-advanced', label: 'Advanced Timesheets', icon: '⏱️', description: 'Clock rules, overtime policies, and approvals' },
    { id: 'notifications', label: 'Notifications', icon: '🔔', description: 'Email, SMS, and push notification settings' },
    { id: 'google-integration', label: 'Google Integration', icon: '🔗', description: 'OAuth, calendar sync, and Google services' },
    { id: 'reporting', label: 'Reporting & Analytics', icon: '📊', description: 'Report preferences, data retention, and exports' },
    { id: 'security', label: 'Security & Access', icon: '🔒', description: 'Authentication, access control, and compliance' },
    { id: 'mobile-accessibility', label: 'Mobile & Accessibility', icon: '📱', description: 'Mobile app settings and accessibility options' },
    { id: 'system-admin', label: 'System Administration', icon: '🛠️', description: 'Backup, audit logs, and system maintenance' },
    { id: 'display', label: 'Display & UI', icon: '🎨', description: 'Interface appearance and preferences' }
  ];

  useEffect(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      loadSettings();
    }
  }, [socket]);

  useEffect(() => {
    if (socket) {
      const handleMessage = (event) => {
        const response = JSON.parse(event.data);
        
        if (response.request_id === 995) { // Get all settings
          setIsLoading(false);
          if (response.success) {
            setSettings(response.data);
            setError('');
          } else {
            setError(response.error || 'Failed to load settings');
          }
        } else if ([996, 997, 998, 999, 1000, 1001, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020].includes(response.request_id)) {
          // Update settings responses
          setIsSaving(false);
          if (response.success) {
            setSettings(response.data);
            setSuccessMessage('Settings updated successfully!');
            setHasUnsavedChanges(false);
            setTimeout(() => setSuccessMessage(''), 3000);
          } else {
            setError(response.error || 'Failed to update settings');
          }
        } else if (response.request_id === 1002) { // Reset to defaults
          setIsSaving(false);
          if (response.success) {
            setSettings(response.data);
            setSuccessMessage('Settings reset to defaults successfully!');
            setHasUnsavedChanges(false);
            setTimeout(() => setSuccessMessage(''), 3000);
          } else {
            setError(response.error || 'Failed to reset settings');
          }
        }
      };

      socket.addEventListener('message', handleMessage);
      return () => socket.removeEventListener('message', handleMessage);
    }
  }, [socket]);

  const loadSettings = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      setIsLoading(true);
      setError('');
      const request = { request_id: 1111 }; // GET_ALL_EXTENDED_SETTINGS
      socket.send(JSON.stringify(request));
    }
  };

  const updateSettings = (category, data) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError('Connection lost. Please refresh the page.');
      return;
    }

    setIsSaving(true);
    setError('');
    setSuccessMessage('');

    const requestIdMap = {
      'company-profile': 1100,
      'user-management': 1101,
      'certifications': 1102,
      'client-management': 1103,
      'job-configuration': 1104,
      'workplace_settings': 1117, // Added for WorkplaceSettings (scheduling, notifications, display etc.)
      'timesheet-advanced': 1105,
      'google-integration': 1106,
      'reporting': 1107,
      'security': 1108,
      'mobile-accessibility': 1109,
      'system-admin-settings': 1110, // For the SystemAdminSettings model itself
      // Note: 'scheduling' and 'display' might map to specific fields within WorkplaceSettings or CompanyProfile
      // Or they might need their own dedicated backend handlers if they are separate models/tables.
      // For now, assuming they are part of other settings or need specific handling.
      // 'scheduling': 996, // This was an old ID, WorkplaceSettings now covers scheduling
      // 'display': 1001, // This was an old ID, CompanyProfile or WorkplaceSettings might cover display
    };

    const request = {
      request_id: requestIdMap[category],
      data: data
    };

    socket.send(JSON.stringify(request));
  };

  const resetToDefaults = () => {
    if (!window.confirm('Are you sure you want to reset all settings to defaults? This action cannot be undone.')) {
      return;
    }

    if (socket && socket.readyState === WebSocket.OPEN) {
      setIsSaving(true);
      setError('');
      const request = { request_id: 1002 }; // Reset to defaults
      socket.send(JSON.stringify(request));
    }
  };

  const handleTabChange = (tabId) => {
    if (hasUnsavedChanges) {
      if (!window.confirm('You have unsaved changes. Are you sure you want to switch tabs?')) {
        return;
      }
      setHasUnsavedChanges(false);
    }
    setActiveTab(tabId);
    setError('');
    setSuccessMessage('');
  };

  const renderTabContent = () => {
    if (!settings) return null;

    const commonProps = {
      settings,
      onUpdate: updateSettings,
      onMarkUnsaved: () => setHasUnsavedChanges(true),
      isLoading: isSaving
    };

    switch (activeTab) {
      case 'company-profile':
        return <CompanyProfileSettings {...commonProps} />;
      case 'user-management':
        return <UserManagementSettings {...commonProps} />;
      case 'certifications':
        return <CertificationsSettings {...commonProps} />;
      case 'client-management':
        return <ClientManagementSettings {...commonProps} />;
      case 'job-configuration':
        return <JobConfigurationSettings {...commonProps} />;
      case 'scheduling':
        return <SchedulingSettings {...commonProps} />;
      case 'timesheet-advanced':
        return <TimesheetAdvancedSettings {...commonProps} />;
      case 'notifications':
        return <NotificationSettings {...commonProps} />;
      case 'google-integration':
        return <GoogleIntegrationSettings {...commonProps} />;
      case 'reporting':
        return <ReportingSettings {...commonProps} />;
      case 'security':
        return <SecuritySettings {...commonProps} />;
      case 'mobile-accessibility':
        return <MobileAccessibilitySettings {...commonProps} />;
      case 'system-admin':
        return <SystemAdminSettings {...commonProps} />;
      case 'display':
        return <DisplaySettings {...commonProps} />;
      default:
        return <div>Select a settings category</div>;
    }
  };

  if (isLoading) {
    return (
      <div className="settings-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="settings-page">
      <div className="settings-header">
        <h1>Workplace Settings</h1>
        <div className="settings-actions">
          {hasUnsavedChanges && (
            <span className="unsaved-indicator">● Unsaved changes</span>
          )}
          <button 
            onClick={resetToDefaults} 
            className="reset-button"
            disabled={isSaving}
          >
            Reset to Defaults
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <span className="alert-icon">⚠️</span>
          {error}
        </div>
      )}

      {successMessage && (
        <div className="alert alert-success">
          <span className="alert-icon">✅</span>
          {successMessage}
        </div>
      )}

      <div className="settings-container">
        <div className="settings-sidebar">
          <nav className="settings-nav">
            {tabs.map(tab => (
              <button
                key={tab.id}
                className={`nav-item ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => handleTabChange(tab.id)}
                disabled={isSaving}
              >
                <span className="nav-icon">{tab.icon}</span>
                <div className="nav-content">
                  <span className="nav-label">{tab.label}</span>
                  <span className="nav-description">{tab.description}</span>
                </div>
              </button>
            ))}
          </nav>
        </div>

        <div className="settings-content">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

export default EnhancedSettingsPage;
