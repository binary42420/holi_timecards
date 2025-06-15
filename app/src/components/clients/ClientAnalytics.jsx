import React from 'react';
import './ClientAnalytics.css';

const ClientAnalytics = ({ analytics, isLoading }) => {
  if (isLoading) {
    return (
      <div className="analytics-loading">
        <div className="loading-spinner"></div>
        <p>Loading analytics...</p>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="analytics-error">
        <p>Unable to load analytics data.</p>
      </div>
    );
  }

  const { overview, recent_activity, top_clients } = analytics;

  const calculateGrowthRate = (current, previous) => {
    if (!previous || previous === 0) return 0;
    return ((current - previous) / previous * 100).toFixed(1);
  };

  return (
    <div className="client-analytics-container">
      <div className="analytics-header">
        <h2>Client Analytics Dashboard</h2>
        <p>Comprehensive insights into your client relationships</p>
      </div>

      {/* Overview Cards */}
      <div className="analytics-overview">
        <div className="overview-card">
          <div className="card-icon">🏢</div>
          <div className="card-content">
            <h3>{overview.total_companies}</h3>
            <p>Total Companies</p>
          </div>
        </div>

        <div className="overview-card">
          <div className="card-icon">👥</div>
          <div className="card-content">
            <h3>{overview.total_client_users}</h3>
            <p>Client Users</p>
            <span className="card-subtitle">
              {overview.active_client_users} active
            </span>
          </div>
        </div>

        <div className="overview-card">
          <div className="card-icon">💼</div>
          <div className="card-content">
            <h3>{overview.total_jobs}</h3>
            <p>Total Jobs</p>
            <span className="card-subtitle">
              {overview.active_jobs} active
            </span>
          </div>
        </div>

        <div className="overview-card">
          <div className="card-icon">✅</div>
          <div className="card-content">
            <h3>{overview.approved_client_users}</h3>
            <p>Approved Users</p>
            <span className="card-subtitle">
              {((overview.approved_client_users / overview.total_client_users) * 100).toFixed(1)}% approval rate
            </span>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="analytics-section">
        <h3>Recent Activity (Last 30 Days)</h3>
        <div className="activity-grid">
          <div className="activity-card">
            <div className="activity-number">{recent_activity.new_users_30_days}</div>
            <div className="activity-label">New Users</div>
          </div>
          <div className="activity-card">
            <div className="activity-number">{recent_activity.new_jobs_30_days}</div>
            <div className="activity-label">New Jobs</div>
          </div>
          <div className="activity-card">
            <div className="activity-number">{recent_activity.jobs_completed_30_days}</div>
            <div className="activity-label">Jobs Completed</div>
          </div>
        </div>
      </div>

      {/* Top Clients */}
      <div className="analytics-section">
        <h3>Top Client Companies</h3>
        <div className="top-clients-list">
          {top_clients.map((client, index) => (
            <div key={client.company_id} className="top-client-item">
              <div className="client-rank">#{index + 1}</div>
              <div className="client-info">
                <h4>{client.company_name}</h4>
                <div className="client-stats">
                  <span className="stat">
                    <strong>{client.job_count}</strong> total jobs
                  </span>
                  <span className="stat">
                    <strong>{client.active_job_count}</strong> active
                  </span>
                  <span className="stat">
                    <strong>{client.user_count}</strong> users
                  </span>
                </div>
              </div>
              <div className="client-score">
                <div className="score-bar">
                  <div 
                    className="score-fill" 
                    style={{ width: `${Math.min((client.job_count / Math.max(...top_clients.map(c => c.job_count))) * 100, 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {top_clients.length === 0 && (
          <div className="no-data">
            <p>No client data available yet.</p>
          </div>
        )}
      </div>

      {/* Performance Metrics */}
      <div className="analytics-section">
        <h3>Performance Metrics</h3>
        <div className="metrics-grid">
          <div className="metric-card">
            <h4>User Engagement</h4>
            <div className="metric-value">
              {overview.total_client_users > 0 
                ? ((overview.active_client_users / overview.total_client_users) * 100).toFixed(1)
                : 0}%
            </div>
            <p>Active user rate</p>
          </div>

          <div className="metric-card">
            <h4>Job Success Rate</h4>
            <div className="metric-value">
              {overview.total_jobs > 0 
                ? (((overview.total_jobs - overview.active_jobs) / overview.total_jobs) * 100).toFixed(1)
                : 0}%
            </div>
            <p>Completed jobs</p>
          </div>

          <div className="metric-card">
            <h4>Average Jobs per Client</h4>
            <div className="metric-value">
              {overview.total_companies > 0 
                ? (overview.total_jobs / overview.total_companies).toFixed(1)
                : 0}
            </div>
            <p>Jobs per company</p>
          </div>

          <div className="metric-card">
            <h4>Average Users per Client</h4>
            <div className="metric-value">
              {overview.total_companies > 0 
                ? (overview.total_client_users / overview.total_companies).toFixed(1)
                : 0}
            </div>
            <p>Users per company</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClientAnalytics;
