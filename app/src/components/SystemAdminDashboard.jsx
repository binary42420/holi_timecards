import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
import './SystemAdminDashboard.css';

const SystemAdminDashboard = () => {
  const { socket, connectionStatus } = useSocket();
  const [systemStats, setSystemStats] = useState({});
  const [userActivity, setUserActivity] = useState([]);
  const [systemLogs, setSystemLogs] = useState([]);
  const [performanceMetrics, setPerformanceMetrics] = useState({});
  const [securityAlerts, setSecurityAlerts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', label: 'System Overview', icon: '🖥️' },
    { id: 'users', label: 'User Management', icon: '👥' },
    { id: 'performance', label: 'Performance', icon: '📊' },
    { id: 'security', label: 'Security', icon: '🔒' },
    { id: 'logs', label: 'System Logs', icon: '📋' },
    { id: 'maintenance', label: 'Maintenance', icon: '🔧' }
  ];

  useEffect(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      fetchSystemData();
    }
  }, [socket]);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        
        if (response.request_id === 900) { // GET_SYSTEM_STATS
          setIsLoading(false);
          if (response.success) {
            setSystemStats(response.data || {});
            setError('');
          } else {
            setError(response.error || 'Failed to load system data');
          }
        } else if (response.request_id === 901) { // GET_USER_ACTIVITY
          if (response.success) {
            setUserActivity(response.data || []);
          }
        } else if (response.request_id === 902) { // GET_SYSTEM_LOGS
          if (response.success) {
            setSystemLogs(response.data || []);
          }
        } else if (response.request_id === 903) { // GET_PERFORMANCE_METRICS
          if (response.success) {
            setPerformanceMetrics(response.data || {});
          }
        } else if (response.request_id === 904) { // GET_SECURITY_ALERTS
          if (response.success) {
            setSecurityAlerts(response.data || []);
          }
        }
      } catch (e) {
        console.error('Error parsing admin dashboard response:', e);
        setIsLoading(false);
        setError('Error processing system data');
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => socket.removeEventListener('message', handleMessage);
  }, [socket]);

  const fetchSystemData = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      setIsLoading(true);
      setError('');
      
      // Fetch all admin data
      const requests = [
        { request_id: 900 }, // GET_SYSTEM_STATS
        { request_id: 901 }, // GET_USER_ACTIVITY
        { request_id: 902 }, // GET_SYSTEM_LOGS
        { request_id: 903 }, // GET_PERFORMANCE_METRICS
        { request_id: 904 }  // GET_SECURITY_ALERTS
      ];

      requests.forEach(request => {
        socket.send(JSON.stringify(request));
      });
    }
  };

  const formatUptime = (seconds) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': case 'online': case 'active': return '#28a745';
      case 'warning': case 'degraded': return '#ffc107';
      case 'critical': case 'offline': case 'error': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const renderOverview = () => (
    <div className="overview-content">
      <div className="system-health">
        <h3>System Health</h3>
        <div className="health-grid">
          <div className="health-card">
            <div className="health-icon" style={{ color: getStatusColor(systemStats.overall_status) }}>
              🖥️
            </div>
            <div className="health-content">
              <div className="health-title">System Status</div>
              <div className="health-value">{systemStats.overall_status || 'Unknown'}</div>
            </div>
          </div>
          <div className="health-card">
            <div className="health-icon">⏱️</div>
            <div className="health-content">
              <div className="health-title">Uptime</div>
              <div className="health-value">{formatUptime(systemStats.uptime_seconds || 0)}</div>
            </div>
          </div>
          <div className="health-card">
            <div className="health-icon">💾</div>
            <div className="health-content">
              <div className="health-title">Memory Usage</div>
              <div className="health-value">{systemStats.memory_usage_percent || 0}%</div>
            </div>
          </div>
          <div className="health-card">
            <div className="health-icon">💽</div>
            <div className="health-content">
              <div className="health-title">Disk Usage</div>
              <div className="health-value">{systemStats.disk_usage_percent || 0}%</div>
            </div>
          </div>
        </div>
      </div>

      <div className="quick-stats">
        <h3>Quick Statistics</h3>
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-label">Total Users</div>
            <div className="stat-value">{systemStats.total_users || 0}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Active Sessions</div>
            <div className="stat-value">{systemStats.active_sessions || 0}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Database Size</div>
            <div className="stat-value">{formatBytes(systemStats.database_size_bytes || 0)}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">API Requests (24h)</div>
            <div className="stat-value">{systemStats.api_requests_24h || 0}</div>
          </div>
        </div>
      </div>

      <div className="recent-alerts">
        <h3>Recent Security Alerts</h3>
        {securityAlerts.length === 0 ? (
          <div className="no-alerts">No security alerts</div>
        ) : (
          <div className="alerts-list">
            {securityAlerts.slice(0, 5).map(alert => (
              <div key={alert.id} className={`alert-item severity-${alert.severity}`}>
                <div className="alert-icon">
                  {alert.severity === 'high' ? '🚨' : alert.severity === 'medium' ? '⚠️' : 'ℹ️'}
                </div>
                <div className="alert-content">
                  <div className="alert-title">{alert.title}</div>
                  <div className="alert-description">{alert.description}</div>
                  <div className="alert-time">{new Date(alert.created_at).toLocaleString()}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  const renderUsers = () => (
    <div className="users-content">
      <div className="content-header">
        <h3>User Activity</h3>
        <div className="header-actions">
          <button className="refresh-btn" onClick={fetchSystemData}>
            🔄 Refresh
          </button>
        </div>
      </div>
      
      <div className="user-stats">
        <div className="user-stat-card">
          <div className="stat-number">{systemStats.total_users || 0}</div>
          <div className="stat-label">Total Users</div>
        </div>
        <div className="user-stat-card">
          <div className="stat-number">{systemStats.active_users_24h || 0}</div>
          <div className="stat-label">Active (24h)</div>
        </div>
        <div className="user-stat-card">
          <div className="stat-number">{systemStats.new_users_7d || 0}</div>
          <div className="stat-label">New (7d)</div>
        </div>
      </div>

      <div className="activity-table">
        <div className="table-header">
          <div className="header-cell">User</div>
          <div className="header-cell">Action</div>
          <div className="header-cell">IP Address</div>
          <div className="header-cell">Time</div>
        </div>
        {userActivity.map(activity => (
          <div key={activity.id} className="table-row">
            <div className="table-cell">{activity.username}</div>
            <div className="table-cell">{activity.action}</div>
            <div className="table-cell">{activity.ip_address}</div>
            <div className="table-cell">{new Date(activity.timestamp).toLocaleString()}</div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderPerformance = () => (
    <div className="performance-content">
      <h3>Performance Metrics</h3>
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-title">Response Time</div>
          <div className="metric-value">{performanceMetrics.avg_response_time || 0}ms</div>
          <div className="metric-trend">
            {performanceMetrics.response_time_trend === 'up' ? '📈' : '📉'}
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-title">Throughput</div>
          <div className="metric-value">{performanceMetrics.requests_per_second || 0}/s</div>
          <div className="metric-trend">
            {performanceMetrics.throughput_trend === 'up' ? '📈' : '📉'}
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-title">Error Rate</div>
          <div className="metric-value">{performanceMetrics.error_rate_percent || 0}%</div>
          <div className="metric-trend">
            {performanceMetrics.error_rate_trend === 'up' ? '📈' : '📉'}
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-title">CPU Usage</div>
          <div className="metric-value">{performanceMetrics.cpu_usage_percent || 0}%</div>
          <div className="metric-trend">
            {performanceMetrics.cpu_trend === 'up' ? '📈' : '📉'}
          </div>
        </div>
      </div>
    </div>
  );

  const renderSecurity = () => (
    <div className="security-content">
      <h3>Security Overview</h3>
      <div className="security-stats">
        <div className="security-stat">
          <div className="stat-icon">🔒</div>
          <div className="stat-content">
            <div className="stat-title">Failed Login Attempts (24h)</div>
            <div className="stat-value">{systemStats.failed_logins_24h || 0}</div>
          </div>
        </div>
        <div className="security-stat">
          <div className="stat-icon">🛡️</div>
          <div className="stat-content">
            <div className="stat-title">Blocked IPs</div>
            <div className="stat-value">{systemStats.blocked_ips || 0}</div>
          </div>
        </div>
        <div className="security-stat">
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <div className="stat-title">Security Alerts</div>
            <div className="stat-value">{securityAlerts.length}</div>
          </div>
        </div>
      </div>

      <div className="security-alerts">
        <h4>Security Alerts</h4>
        {securityAlerts.length === 0 ? (
          <div className="no-alerts">No security alerts</div>
        ) : (
          <div className="alerts-list">
            {securityAlerts.map(alert => (
              <div key={alert.id} className={`alert-item severity-${alert.severity}`}>
                <div className="alert-header">
                  <span className="alert-title">{alert.title}</span>
                  <span className="alert-severity">{alert.severity}</span>
                </div>
                <div className="alert-description">{alert.description}</div>
                <div className="alert-time">{new Date(alert.created_at).toLocaleString()}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  const renderLogs = () => (
    <div className="logs-content">
      <h3>System Logs</h3>
      <div className="logs-table">
        <div className="table-header">
          <div className="header-cell">Level</div>
          <div className="header-cell">Message</div>
          <div className="header-cell">Source</div>
          <div className="header-cell">Time</div>
        </div>
        {systemLogs.map(log => (
          <div key={log.id} className={`table-row log-${log.level}`}>
            <div className="table-cell">
              <span className={`log-level level-${log.level}`}>
                {log.level.toUpperCase()}
              </span>
            </div>
            <div className="table-cell">{log.message}</div>
            <div className="table-cell">{log.source}</div>
            <div className="table-cell">{new Date(log.timestamp).toLocaleString()}</div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderMaintenance = () => (
    <div className="maintenance-content">
      <h3>System Maintenance</h3>
      <div className="maintenance-actions">
        <div className="action-card">
          <div className="action-icon">🗑️</div>
          <div className="action-content">
            <div className="action-title">Clear Cache</div>
            <div className="action-description">Clear application cache to free up memory</div>
          </div>
          <button className="action-btn">Clear</button>
        </div>
        <div className="action-card">
          <div className="action-icon">📊</div>
          <div className="action-content">
            <div className="action-title">Generate Report</div>
            <div className="action-description">Generate system health report</div>
          </div>
          <button className="action-btn">Generate</button>
        </div>
        <div className="action-card">
          <div className="action-icon">💾</div>
          <div className="action-content">
            <div className="action-title">Backup Database</div>
            <div className="action-description">Create a backup of the database</div>
          </div>
          <button className="action-btn">Backup</button>
        </div>
        <div className="action-card">
          <div className="action-icon">🔄</div>
          <div className="action-content">
            <div className="action-title">Restart Services</div>
            <div className="action-description">Restart application services</div>
          </div>
          <button className="action-btn danger">Restart</button>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'overview': return renderOverview();
      case 'users': return renderUsers();
      case 'performance': return renderPerformance();
      case 'security': return renderSecurity();
      case 'logs': return renderLogs();
      case 'maintenance': return renderMaintenance();
      default: return renderOverview();
    }
  };

  if (isLoading) {
    return (
      <div className="admin-dashboard loading">
        <div className="loading-message">Loading system data...</div>
      </div>
    );
  }

  return (
    <div className="system-admin-dashboard">
      <div className="dashboard-header">
        <h1>System Administration</h1>
        <div className="connection-status" style={{ 
          color: connectionStatus === 'connected' ? '#28a745' : '#dc3545' 
        }}>
          ● {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={fetchSystemData} className="retry-btn">
            Retry
          </button>
        </div>
      )}

      <div className="dashboard-navigation">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </div>

      <div className="dashboard-content">
        {renderContent()}
      </div>
    </div>
  );
};

export default SystemAdminDashboard;
