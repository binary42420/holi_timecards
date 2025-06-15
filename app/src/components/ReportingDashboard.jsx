import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
import './ReportingDashboard.css';

const ReportingDashboard = () => {
  const { socket, connectionStatus } = useSocket();
  const [reports, setReports] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedDateRange, setSelectedDateRange] = useState('last_30_days');
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);

  const reportTemplates = [
    {
      id: 'timesheet_summary',
      name: 'Timesheet Summary',
      description: 'Summary of all employee timesheets',
      icon: '⏰',
      color: '#28a745',
      formats: ['xlsx', 'pdf', 'csv']
    },
    {
      id: 'client_billing',
      name: 'Client Billing Report',
      description: 'Billing summary for all clients',
      icon: '💰',
      color: '#007bff',
      formats: ['xlsx', 'pdf']
    },
    {
      id: 'employee_performance',
      name: 'Employee Performance',
      description: 'Performance metrics and analytics',
      icon: '📊',
      color: '#6f42c1',
      formats: ['xlsx', 'pdf']
    },
    {
      id: 'job_profitability',
      name: 'Job Profitability',
      description: 'Profit analysis by job and client',
      icon: '📈',
      color: '#fd7e14',
      formats: ['xlsx', 'pdf']
    },
    {
      id: 'schedule_utilization',
      name: 'Schedule Utilization',
      description: 'Worker and equipment utilization rates',
      icon: '📅',
      color: '#20c997',
      formats: ['xlsx', 'pdf', 'csv']
    },
    {
      id: 'certification_tracking',
      name: 'Certification Tracking',
      description: 'Employee certifications and expiry dates',
      icon: '🏆',
      color: '#dc3545',
      formats: ['xlsx', 'csv']
    }
  ];

  const dateRangeOptions = [
    { value: 'last_7_days', label: 'Last 7 Days' },
    { value: 'last_30_days', label: 'Last 30 Days' },
    { value: 'last_90_days', label: 'Last 90 Days' },
    { value: 'current_month', label: 'Current Month' },
    { value: 'last_month', label: 'Last Month' },
    { value: 'current_quarter', label: 'Current Quarter' },
    { value: 'current_year', label: 'Current Year' },
    { value: 'custom', label: 'Custom Range' }
  ];

  useEffect(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      fetchReports();
      fetchAnalytics();
    }
  }, [socket, selectedDateRange]);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        
        if (response.request_id === 700) { // GET_REPORTS
          setIsLoading(false);
          if (response.success) {
            setReports(response.data || []);
            setError('');
          } else {
            setError(response.error || 'Failed to load reports');
          }
        } else if (response.request_id === 701) { // GET_ANALYTICS
          if (response.success) {
            setAnalytics(response.data || {});
          }
        } else if (response.request_id === 702) { // GENERATE_REPORT
          setIsGeneratingReport(false);
          if (response.success) {
            // Handle successful report generation
            setReports(prev => [response.data, ...prev]);
          } else {
            setError(response.error || 'Failed to generate report');
          }
        }
      } catch (e) {
        console.error('Error parsing reporting response:', e);
        setIsLoading(false);
        setError('Error processing reports');
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => socket.removeEventListener('message', handleMessage);
  }, [socket]);

  const fetchReports = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      setIsLoading(true);
      setError('');
      const request = {
        request_id: 700, // GET_REPORTS
        data: { date_range: selectedDateRange }
      };
      socket.send(JSON.stringify(request));
    }
  };

  const fetchAnalytics = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      const request = {
        request_id: 701, // GET_ANALYTICS
        data: { date_range: selectedDateRange }
      };
      socket.send(JSON.stringify(request));
    }
  };

  const generateReport = (templateId, format = 'xlsx') => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      setIsGeneratingReport(true);
      setError('');
      const request = {
        request_id: 702, // GENERATE_REPORT
        data: {
          template_id: templateId,
          format: format,
          date_range: selectedDateRange
        }
      };
      socket.send(JSON.stringify(request));
    }
  };

  const downloadReport = (reportId) => {
    // Trigger download
    const link = document.createElement('a');
    link.href = `/api/reports/${reportId}/download`;
    link.download = '';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="reporting-dashboard">
      <div className="dashboard-header">
        <h1>Reports & Analytics</h1>
        <div className="header-controls">
          <select
            value={selectedDateRange}
            onChange={(e) => setSelectedDateRange(e.target.value)}
            className="date-range-select"
          >
            {dateRangeOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={fetchReports} className="retry-btn">
            Retry
          </button>
        </div>
      )}

      {/* Analytics Overview */}
      <div className="analytics-overview">
        <h2>Analytics Overview</h2>
        <div className="analytics-grid">
          <div className="analytics-card">
            <div className="analytics-icon">👥</div>
            <div className="analytics-content">
              <div className="analytics-value">{analytics.total_employees || 0}</div>
              <div className="analytics-label">Total Employees</div>
            </div>
          </div>
          <div className="analytics-card">
            <div className="analytics-icon">⏰</div>
            <div className="analytics-content">
              <div className="analytics-value">{analytics.total_hours || 0}</div>
              <div className="analytics-label">Total Hours Worked</div>
            </div>
          </div>
          <div className="analytics-card">
            <div className="analytics-icon">💰</div>
            <div className="analytics-content">
              <div className="analytics-value">${analytics.total_revenue || 0}</div>
              <div className="analytics-label">Total Revenue</div>
            </div>
          </div>
          <div className="analytics-card">
            <div className="analytics-icon">📊</div>
            <div className="analytics-content">
              <div className="analytics-value">{analytics.efficiency_rate || 0}%</div>
              <div className="analytics-label">Efficiency Rate</div>
            </div>
          </div>
        </div>
      </div>

      {/* Report Templates */}
      <div className="report-templates">
        <h2>Generate Reports</h2>
        <div className="templates-grid">
          {reportTemplates.map(template => (
            <div key={template.id} className="template-card">
              <div className="template-header">
                <div className="template-icon" style={{ color: template.color }}>
                  {template.icon}
                </div>
                <div className="template-info">
                  <h3>{template.name}</h3>
                  <p>{template.description}</p>
                </div>
              </div>
              <div className="template-actions">
                {template.formats.map(format => (
                  <button
                    key={format}
                    onClick={() => generateReport(template.id, format)}
                    disabled={isGeneratingReport || connectionStatus !== 'connected'}
                    className={`generate-btn format-${format}`}
                  >
                    {format.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Reports */}
      <div className="recent-reports">
        <h2>Recent Reports</h2>
        {isLoading ? (
          <div className="loading-message">Loading reports...</div>
        ) : reports.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📊</div>
            <h3>No reports generated yet</h3>
            <p>Generate your first report using the templates above.</p>
          </div>
        ) : (
          <div className="reports-table">
            <div className="table-header">
              <div className="header-cell">Report Name</div>
              <div className="header-cell">Type</div>
              <div className="header-cell">Generated</div>
              <div className="header-cell">Size</div>
              <div className="header-cell">Actions</div>
            </div>
            {reports.map(report => (
              <div key={report.id} className="table-row">
                <div className="table-cell">
                  <div className="report-name">{report.name}</div>
                  <div className="report-description">{report.description}</div>
                </div>
                <div className="table-cell">
                  <span className={`format-badge format-${report.format}`}>
                    {report.format.toUpperCase()}
                  </span>
                </div>
                <div className="table-cell">
                  {formatDate(report.created_at)}
                </div>
                <div className="table-cell">
                  {formatFileSize(report.file_size)}
                </div>
                <div className="table-cell">
                  <button
                    onClick={() => downloadReport(report.id)}
                    className="download-btn"
                    title="Download Report"
                  >
                    📥
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {isGeneratingReport && (
        <div className="generating-overlay">
          <div className="generating-message">
            <div className="spinner"></div>
            <p>Generating report...</p>
          </div>
        </div>
      )}

      {connectionStatus !== 'connected' && (
        <div className="connection-warning">
          ⚠️ Not connected. Reports may not be up to date.
        </div>
      )}
    </div>
  );
};

export default ReportingDashboard;
