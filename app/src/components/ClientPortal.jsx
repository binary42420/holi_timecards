import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
import { useAuth } from '../contexts/AuthContext';
import './ClientPortal.css';

const ClientPortal = () => {
  const { socket, connectionStatus } = useSocket();
  const { user } = useAuth();
  const [clientData, setClientData] = useState(null);
  const [activeJobs, setActiveJobs] = useState([]);
  const [upcomingShifts, setUpcomingShifts] = useState([]);
  const [recentTimesheets, setRecentTimesheets] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'jobs', label: 'Active Jobs', icon: '💼' },
    { id: 'shifts', label: 'Upcoming Shifts', icon: '📅' },
    { id: 'timesheets', label: 'Timesheets', icon: '⏰' },
    { id: 'invoices', label: 'Invoices', icon: '💰' },
    { id: 'reports', label: 'Reports', icon: '📋' }
  ];

  useEffect(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      fetchClientData();
    }
  }, [socket]);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        
        if (response.request_id === 800) { // GET_CLIENT_DASHBOARD_DATA
          setIsLoading(false);
          if (response.success) {
            const data = response.data;
            setClientData(data.client_info);
            setActiveJobs(data.active_jobs || []);
            setUpcomingShifts(data.upcoming_shifts || []);
            setRecentTimesheets(data.recent_timesheets || []);
            setInvoices(data.invoices || []);
            setError('');
          } else {
            setError(response.error || 'Failed to load client data');
          }
        }
      } catch (e) {
        console.error('Error parsing client portal response:', e);
        setIsLoading(false);
        setError('Error processing client data');
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => socket.removeEventListener('message', handleMessage);
  }, [socket]);

  const fetchClientData = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      setIsLoading(true);
      setError('');
      const request = { request_id: 800 }; // GET_CLIENT_DASHBOARD_DATA
      socket.send(JSON.stringify(request));
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getShiftStatus = (shift) => {
    const now = new Date();
    const shiftStart = new Date(shift.shift_start_datetime);
    const shiftEnd = new Date(shift.shift_end_datetime);

    if (now < shiftStart) return { status: 'upcoming', color: '#007bff' };
    if (now >= shiftStart && now <= shiftEnd) return { status: 'in-progress', color: '#28a745' };
    return { status: 'completed', color: '#6c757d' };
  };

  const renderOverview = () => (
    <div className="overview-content">
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">💼</div>
          <div className="stat-content">
            <div className="stat-value">{activeJobs.length}</div>
            <div className="stat-label">Active Jobs</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📅</div>
          <div className="stat-content">
            <div className="stat-value">{upcomingShifts.length}</div>
            <div className="stat-label">Upcoming Shifts</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⏰</div>
          <div className="stat-content">
            <div className="stat-value">{recentTimesheets.length}</div>
            <div className="stat-label">Recent Timesheets</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">💰</div>
          <div className="stat-content">
            <div className="stat-value">{invoices.filter(i => i.status === 'pending').length}</div>
            <div className="stat-label">Pending Invoices</div>
          </div>
        </div>
      </div>

      <div className="recent-activity">
        <h3>Recent Activity</h3>
        <div className="activity-list">
          {upcomingShifts.slice(0, 5).map(shift => (
            <div key={shift.id} className="activity-item">
              <div className="activity-icon">📅</div>
              <div className="activity-content">
                <div className="activity-title">{shift.job_name}</div>
                <div className="activity-description">
                  Shift scheduled for {formatDate(shift.shift_start_datetime)} at {formatTime(shift.shift_start_datetime)}
                </div>
              </div>
              <div className="activity-time">{formatDate(shift.shift_start_datetime)}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderJobs = () => (
    <div className="jobs-content">
      <div className="content-header">
        <h3>Active Jobs</h3>
      </div>
      {activeJobs.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">💼</div>
          <h4>No active jobs</h4>
          <p>You don't have any active jobs at the moment.</p>
        </div>
      ) : (
        <div className="jobs-grid">
          {activeJobs.map(job => (
            <div key={job.id} className="job-card">
              <div className="job-header">
                <h4>{job.name}</h4>
                <span className={`job-status status-${job.status}`}>
                  {job.status}
                </span>
              </div>
              <div className="job-details">
                <div className="job-detail">
                  <strong>Venue:</strong> {job.venue_name}
                </div>
                <div className="job-detail">
                  <strong>Address:</strong> {job.venue_address}
                </div>
                {job.description && (
                  <div className="job-detail">
                    <strong>Description:</strong> {job.description}
                  </div>
                )}
                <div className="job-detail">
                  <strong>Total Shifts:</strong> {job.shift_count || 0}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderShifts = () => (
    <div className="shifts-content">
      <div className="content-header">
        <h3>Upcoming Shifts</h3>
      </div>
      {upcomingShifts.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📅</div>
          <h4>No upcoming shifts</h4>
          <p>No shifts are scheduled for your jobs.</p>
        </div>
      ) : (
        <div className="shifts-list">
          {upcomingShifts.map(shift => {
            const status = getShiftStatus(shift);
            return (
              <div key={shift.id} className="shift-card">
                <div className="shift-header">
                  <div className="shift-job">{shift.job_name}</div>
                  <span 
                    className="shift-status"
                    style={{ backgroundColor: status.color }}
                  >
                    {status.status}
                  </span>
                </div>
                <div className="shift-details">
                  <div className="shift-time">
                    <strong>Date:</strong> {formatDate(shift.shift_start_datetime)}
                  </div>
                  <div className="shift-time">
                    <strong>Time:</strong> {formatTime(shift.shift_start_datetime)} - {formatTime(shift.shift_end_datetime)}
                  </div>
                  <div className="shift-workers">
                    <strong>Workers:</strong> {shift.assigned_workers || 0} assigned
                  </div>
                  {shift.client_po_number && (
                    <div className="shift-po">
                      <strong>PO #:</strong> {shift.client_po_number}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );

  const renderTimesheets = () => (
    <div className="timesheets-content">
      <div className="content-header">
        <h3>Recent Timesheets</h3>
      </div>
      {recentTimesheets.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">⏰</div>
          <h4>No timesheets available</h4>
          <p>No timesheet data is available for your jobs.</p>
        </div>
      ) : (
        <div className="timesheets-table">
          <div className="table-header">
            <div className="header-cell">Job</div>
            <div className="header-cell">Date</div>
            <div className="header-cell">Workers</div>
            <div className="header-cell">Total Hours</div>
            <div className="header-cell">Status</div>
          </div>
          {recentTimesheets.map(timesheet => (
            <div key={timesheet.id} className="table-row">
              <div className="table-cell">{timesheet.job_name}</div>
              <div className="table-cell">{formatDate(timesheet.shift_date)}</div>
              <div className="table-cell">{timesheet.worker_count}</div>
              <div className="table-cell">{timesheet.total_hours}h</div>
              <div className="table-cell">
                <span className={`status-badge status-${timesheet.status}`}>
                  {timesheet.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderInvoices = () => (
    <div className="invoices-content">
      <div className="content-header">
        <h3>Invoices</h3>
      </div>
      {invoices.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">💰</div>
          <h4>No invoices</h4>
          <p>No invoices have been generated yet.</p>
        </div>
      ) : (
        <div className="invoices-table">
          <div className="table-header">
            <div className="header-cell">Invoice #</div>
            <div className="header-cell">Date</div>
            <div className="header-cell">Amount</div>
            <div className="header-cell">Status</div>
            <div className="header-cell">Actions</div>
          </div>
          {invoices.map(invoice => (
            <div key={invoice.id} className="table-row">
              <div className="table-cell">{invoice.invoice_number}</div>
              <div className="table-cell">{formatDate(invoice.created_at)}</div>
              <div className="table-cell">{formatCurrency(invoice.amount)}</div>
              <div className="table-cell">
                <span className={`status-badge status-${invoice.status}`}>
                  {invoice.status}
                </span>
              </div>
              <div className="table-cell">
                <button className="download-btn" title="Download Invoice">
                  📥
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'overview': return renderOverview();
      case 'jobs': return renderJobs();
      case 'shifts': return renderShifts();
      case 'timesheets': return renderTimesheets();
      case 'invoices': return renderInvoices();
      case 'reports': return <div>Reports coming soon...</div>;
      default: return renderOverview();
    }
  };

  if (isLoading) {
    return (
      <div className="client-portal loading">
        <div className="loading-message">Loading your dashboard...</div>
      </div>
    );
  }

  return (
    <div className="client-portal">
      <div className="portal-header">
        <div className="header-content">
          <h1>Client Portal</h1>
          {clientData && (
            <div className="client-info">
              <h2>{clientData.company_name}</h2>
              <p>Welcome back, {user?.name || 'Client'}</p>
            </div>
          )}
        </div>
        <div className="connection-status" style={{ 
          color: connectionStatus === 'connected' ? '#28a745' : '#dc3545' 
        }}>
          ● {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={fetchClientData} className="retry-btn">
            Retry
          </button>
        </div>
      )}

      <div className="portal-navigation">
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

      <div className="portal-content">
        {renderContent()}
      </div>
    </div>
  );
};

export default ClientPortal;
