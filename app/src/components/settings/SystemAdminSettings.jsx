import React, { useState, useEffect } from 'react';
import ToggleSwitch from '../ToggleSwitch';

const SystemAdminSettings = ({ settings, onUpdate, onMarkUnsaved, isLoading }) => {
  const [formData, setFormData] = useState({
    // Backup & Recovery
    auto_backup_enabled: true,
    backup_frequency: 'daily',
    backup_time: '02:00',
    backup_retention_days: 30,
    cloud_backup_enabled: true,
    local_backup_enabled: false,
    
    // Database Maintenance
    auto_optimize_database: true,
    database_cleanup_frequency: 'weekly',
    purge_old_logs_days: 90,
    compress_old_data: true,
    vacuum_database: true,
    
    // System Monitoring
    system_health_monitoring: true,
    performance_monitoring: true,
    error_tracking: true,
    uptime_monitoring: true,
    resource_usage_alerts: true,
    
    // Audit Logging
    audit_logging_enabled: true,
    log_user_actions: true,
    log_data_changes: true,
    log_system_events: true,
    log_security_events: true,
    audit_log_retention_years: 7,
    
    // Security Settings
    enable_rate_limiting: true,
    max_requests_per_minute: 100,
    enable_ip_whitelisting: false,
    blocked_ip_addresses: [],
    security_scan_frequency: 'weekly',
    
    // System Limits
    max_concurrent_users: 500,
    max_file_upload_size_mb: 10,
    session_timeout_minutes: 480,
    api_timeout_seconds: 30,
    max_database_connections: 100,
    
    // Maintenance Mode
    maintenance_mode_enabled: false,
    maintenance_message: 'System is currently under maintenance. Please try again later.',
    allow_admin_access_during_maintenance: true,
    scheduled_maintenance_notifications: true,
    
    // Email System
    email_service_provider: 'smtp',
    smtp_server: '',
    smtp_port: 587,
    smtp_username: '',
    smtp_password: '',
    email_rate_limit_per_hour: 1000,
    
    // API Configuration
    api_versioning_enabled: true,
    current_api_version: 'v1',
    deprecated_api_support: true,
    api_documentation_enabled: true,
    cors_enabled: true,
    allowed_origins: ['https://handsonlabor.com'],
    
    // Caching
    redis_caching_enabled: false,
    cache_ttl_minutes: 60,
    cache_user_sessions: true,
    cache_database_queries: true,
    cache_static_content: true,
    
    // Error Handling
    detailed_error_messages: false,
    error_notification_emails: true,
    error_notification_recipients: ['admin@handsonlabor.com'],
    automatic_error_reporting: true,
    
    // System Updates
    auto_update_enabled: false,
    update_check_frequency: 'weekly',
    beta_updates_enabled: false,
    update_notification_emails: true,
    
    // Data Export/Import
    allow_data_export: true,
    export_rate_limit_per_day: 10,
    allow_bulk_import: true,
    import_validation_strict: true,
    
    // Compliance
    gdpr_compliance_mode: true,
    data_anonymization_enabled: false,
    right_to_be_forgotten_enabled: true,
    consent_tracking_enabled: true,
  });

  const [systemStatus, setSystemStatus] = useState({
    uptime: '99.9%',
    last_backup: '2024-01-15 02:00:00',
    database_size: '2.3 GB',
    active_users: 45,
    system_load: 'Normal',
    disk_usage: '65%',
    memory_usage: '42%',
    cpu_usage: '23%'
  });

  useEffect(() => {
    if (settings?.system_admin) {
      setFormData(prev => ({
        ...prev,
        ...settings.system_admin
      }));
      if (settings.system_admin.system_status) {
        setSystemStatus(settings.system_admin.system_status);
      }
    }
  }, [settings]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    onMarkUnsaved();
  };

  const handleToggle = (field) => {
    setFormData(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
    onMarkUnsaved();
  };

  const handleTestBackup = () => {
    console.log('Testing backup system...');
  };

  const handleManualBackup = () => {
    console.log('Starting manual backup...');
  };

  const handleSystemHealthCheck = () => {
    console.log('Running system health check...');
  };

  const handleSave = () => {
    onUpdate('system-admin', formData);
  };

  return (
    <div className="settings-section">
      <div className="settings-header">
        <h2>System Administration Settings</h2>
        <p>Configure system backup, monitoring, security, maintenance, and administrative features.</p>
      </div>

      {/* System Status Dashboard */}
      <div className="settings-card">
        <div className="settings-card-header">
          <span className="settings-card-icon">📊</span>
          <h3 className="settings-card-title">System Status</h3>
        </div>
        <div className="system-status-grid">
          <div className="status-item">
            <div className="status-label">System Uptime</div>
            <div className="status-value">{systemStatus.uptime}</div>
          </div>
          <div className="status-item">
            <div className="status-label">Last Backup</div>
            <div className="status-value">{systemStatus.last_backup}</div>
          </div>
          <div className="status-item">
            <div className="status-label">Database Size</div>
            <div className="status-value">{systemStatus.database_size}</div>
          </div>
          <div className="status-item">
            <div className="status-label">Active Users</div>
            <div className="status-value">{systemStatus.active_users}</div>
          </div>
          <div className="status-item">
            <div className="status-label">System Load</div>
            <div className="status-value">{systemStatus.system_load}</div>
          </div>
          <div className="status-item">
            <div className="status-label">Disk Usage</div>
            <div className="status-value">{systemStatus.disk_usage}</div>
          </div>
          <div className="status-item">
            <div className="status-label">Memory Usage</div>
            <div className="status-value">{systemStatus.memory_usage}</div>
          </div>
          <div className="status-item">
            <div className="status-label">CPU Usage</div>
            <div className="status-value">{systemStatus.cpu_usage}</div>
          </div>
        </div>
        <div className="status-actions">
          <button onClick={handleSystemHealthCheck} className="btn btn-secondary">
            Run Health Check
          </button>
        </div>
      </div>

      {/* Backup & Recovery */}
      <div className="settings-card">
        <div className="settings-card-header">
          <span className="settings-card-icon">💾</span>
          <h3 className="settings-card-title">Backup & Recovery</h3>
        </div>
        <div className="form-grid">
          <div className="form-group">
            <div className="toggle-setting">
              <div className="toggle-info">
                <div className="toggle-title">Auto Backup</div>
                <div className="toggle-description">Automatically backup system data</div>
              </div>
              <ToggleSwitch
                checked={formData.auto_backup_enabled}
                onChange={() => handleToggle('auto_backup_enabled')}
              />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Backup Frequency</label>
            <select
              className="form-select"
              value={formData.backup_frequency}
              onChange={(e) => handleInputChange('backup_frequency', e.target.value)}
              disabled={!formData.auto_backup_enabled}
            >
              <option value="hourly">Hourly</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Backup Time</label>
            <input
              type="time"
              className="form-input"
              value={formData.backup_time}
              onChange={(e) => handleInputChange('backup_time', e.target.value)}
              disabled={!formData.auto_backup_enabled}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Backup Retention (Days)</label>
            <input
              type="number"
              min="7"
              max="365"
              className="form-input"
              value={formData.backup_retention_days}
              onChange={(e) => handleInputChange('backup_retention_days', parseInt(e.target.value))}
            />
          </div>
          <div className="form-group">
            <div className="toggle-setting">
              <div className="toggle-info">
                <div className="toggle-title">Cloud Backup</div>
                <div className="toggle-description">Store backups in cloud storage</div>
              </div>
              <ToggleSwitch
                checked={formData.cloud_backup_enabled}
                onChange={() => handleToggle('cloud_backup_enabled')}
              />
            </div>
          </div>
        </div>
        <div className="backup-actions">
          <button onClick={handleTestBackup} className="btn btn-secondary">
            Test Backup
          </button>
          <button onClick={handleManualBackup} className="btn btn-primary">
            Manual Backup
          </button>
        </div>
      </div>

      {/* System Monitoring */}
      <div className="settings-card">
        <div className="settings-card-header">
          <span className="settings-card-icon">📈</span>
          <h3 className="settings-card-title">System Monitoring</h3>
        </div>
        <div className="form-grid">
          <div className="form-group">
            <div className="toggle-setting">
              <div className="toggle-info">
                <div className="toggle-title">System Health Monitoring</div>
                <div className="toggle-description">Monitor overall system health and performance</div>
              </div>
              <ToggleSwitch
                checked={formData.system_health_monitoring}
                onChange={() => handleToggle('system_health_monitoring')}
              />
            </div>
          </div>
          <div className="form-group">
            <div className="toggle-setting">
              <div className="toggle-info">
                <div className="toggle-title">Performance Monitoring</div>
                <div className="toggle-description">Track system performance metrics</div>
              </div>
              <ToggleSwitch
                checked={formData.performance_monitoring}
                onChange={() => handleToggle('performance_monitoring')}
              />
            </div>
          </div>
          <div className="form-group">
            <div className="toggle-setting">
              <div className="toggle-info">
                <div className="toggle-title">Error Tracking</div>
                <div className="toggle-description">Track and log system errors</div>
              </div>
              <ToggleSwitch
                checked={formData.error_tracking}
                onChange={() => handleToggle('error_tracking')}
              />
            </div>
          </div>
          <div className="form-group">
            <div className="toggle-setting">
              <div className="toggle-info">
                <div className="toggle-title">Resource Usage Alerts</div>
                <div className="toggle-description">Alert when resource usage is high</div>
              </div>
              <ToggleSwitch
                checked={formData.resource_usage_alerts}
                onChange={() => handleToggle('resource_usage_alerts')}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Security Settings */}
      <div className="settings-card">
        <div className="settings-card-header">
          <span className="settings-card-icon">🔒</span>
          <h3 className="settings-card-title">Security Settings</h3>
        </div>
        <div className="form-grid">
          <div className="form-group">
            <div className="toggle-setting">
              <div className="toggle-info">
                <div className="toggle-title">Rate Limiting</div>
                <div className="toggle-description">Limit API requests per user</div>
              </div>
              <ToggleSwitch
                checked={formData.enable_rate_limiting}
                onChange={() => handleToggle('enable_rate_limiting')}
              />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Max Requests Per Minute</label>
            <input
              type="number"
              min="10"
              max="1000"
              className="form-input"
              value={formData.max_requests_per_minute}
              onChange={(e) => handleInputChange('max_requests_per_minute', parseInt(e.target.value))}
              disabled={!formData.enable_rate_limiting}
            />
          </div>
          <div className="form-group">
            <div className="toggle-setting">
              <div className="toggle-info">
                <div className="toggle-title">IP Whitelisting</div>
                <div className="toggle-description">Only allow access from approved IP addresses</div>
              </div>
              <ToggleSwitch
                checked={formData.enable_ip_whitelisting}
                onChange={() => handleToggle('enable_ip_whitelisting')}
              />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Security Scan Frequency</label>
            <select
              className="form-select"
              value={formData.security_scan_frequency}
              onChange={(e) => handleInputChange('security_scan_frequency', e.target.value)}
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>
        </div>
      </div>

      {/* Audit Logging */}
      <div className="settings-card">
        <div className="settings-card-header">
          <span className="settings-card-icon">📝</span>
          <h3 className="settings-card-title">Audit Logging</h3>
        </div>
        <div className="form-grid">
          <div className="form-group">
            <div className="toggle-setting">
              <div className="toggle-info">
                <div className="toggle-title">Enable Audit Logging</div>
                <div className="toggle-description">Log all system activities for audit purposes</div>
              </div>
              <ToggleSwitch
                checked={formData.audit_logging_enabled}
                onChange={() => handleToggle('audit_logging_enabled')}
              />
            </div>
          </div>
          <div className="form-group">
            <div className="toggle-setting">
              <div className="toggle-info">
                <div className="toggle-title">Log User Actions</div>
                <div className="toggle-description">Log all user actions and interactions</div>
              </div>
              <ToggleSwitch
                checked={formData.log_user_actions}
                onChange={() => handleToggle('log_user_actions')}
                disabled={!formData.audit_logging_enabled}
              />
            </div>
          </div>
          <div className="form-group">
            <div className="toggle-setting">
              <div className="toggle-info">
                <div className="toggle-title">Log Data Changes</div>
                <div className="toggle-description">Log all data modifications</div>
              </div>
              <ToggleSwitch
                checked={formData.log_data_changes}
                onChange={() => handleToggle('log_data_changes')}
                disabled={!formData.audit_logging_enabled}
              />
            </div>
          </div>
          <div className="form-group">
            <div className="toggle-setting">
              <div className="toggle-info">
                <div className="toggle-title">Log Security Events</div>
                <div className="toggle-description">Log security-related events</div>
              </div>
              <ToggleSwitch
                checked={formData.log_security_events}
                onChange={() => handleToggle('log_security_events')}
                disabled={!formData.audit_logging_enabled}
              />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Audit Log Retention (Years)</label>
            <input
              type="number"
              min="1"
              max="25"
              className="form-input"
              value={formData.audit_log_retention_years}
              onChange={(e) => handleInputChange('audit_log_retention_years', parseInt(e.target.value))}
              disabled={!formData.audit_logging_enabled}
            />
          </div>
        </div>
      </div>

      {/* System Limits */}
      <div className="settings-card">
        <div className="settings-card-header">
          <span className="settings-card-icon">⚡</span>
          <h3 className="settings-card-title">System Limits</h3>
        </div>
        <div className="form-grid">
          <div className="form-group">
            <label className="form-label">Max Concurrent Users</label>
            <input
              type="number"
              min="10"
              max="10000"
              className="form-input"
              value={formData.max_concurrent_users}
              onChange={(e) => handleInputChange('max_concurrent_users', parseInt(e.target.value))}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Max File Upload Size (MB)</label>
            <input
              type="number"
              min="1"
              max="100"
              className="form-input"
              value={formData.max_file_upload_size_mb}
              onChange={(e) => handleInputChange('max_file_upload_size_mb', parseInt(e.target.value))}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Session Timeout (Minutes)</label>
            <input
              type="number"
              min="30"
              max="1440"
              className="form-input"
              value={formData.session_timeout_minutes}
              onChange={(e) => handleInputChange('session_timeout_minutes', parseInt(e.target.value))}
            />
          </div>
          <div className="form-group">
            <label className="form-label">API Timeout (Seconds)</label>
            <input
              type="number"
              min="10"
              max="300"
              className="form-input"
              value={formData.api_timeout_seconds}
              onChange={(e) => handleInputChange('api_timeout_seconds', parseInt(e.target.value))}
            />
          </div>
        </div>
      </div>

      {/* Maintenance Mode */}
      <div className="settings-card">
        <div className="settings-card-header">
          <span className="settings-card-icon">🔧</span>
          <h3 className="settings-card-title">Maintenance Mode</h3>
        </div>
        <div className="form-grid">
          <div className="form-group">
            <div className="toggle-setting">
              <div className="toggle-info">
                <div className="toggle-title">Enable Maintenance Mode</div>
                <div className="toggle-description">Put system in maintenance mode</div>
              </div>
              <ToggleSwitch
                checked={formData.maintenance_mode_enabled}
                onChange={() => handleToggle('maintenance_mode_enabled')}
              />
            </div>
          </div>
          <div className="form-group full-width">
            <label className="form-label">Maintenance Message</label>
            <textarea
              className="form-textarea"
              value={formData.maintenance_message}
              onChange={(e) => handleInputChange('maintenance_message', e.target.value)}
              rows="3"
              disabled={!formData.maintenance_mode_enabled}
            />
          </div>
          <div className="form-group">
            <div className="toggle-setting">
              <div className="toggle-info">
                <div className="toggle-title">Allow Admin Access</div>
                <div className="toggle-description">Allow administrators to access system during maintenance</div>
              </div>
              <ToggleSwitch
                checked={formData.allow_admin_access_during_maintenance}
                onChange={() => handleToggle('allow_admin_access_during_maintenance')}
                disabled={!formData.maintenance_mode_enabled}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="settings-actions">
        <button 
          onClick={handleSave} 
          className="btn btn-primary"
          disabled={isLoading}
        >
          {isLoading ? 'Saving...' : 'Save System Administration Settings'}
        </button>
      </div>
    </div>
  );
};

export default SystemAdminSettings;
