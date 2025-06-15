import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
import './TimesheetSummary.css';

const TimesheetSummary = ({ employeeId = null, dateRange = null }) => {
  const { socket } = useSocket();
  const [summary, setSummary] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedDateRange, setSelectedDateRange] = useState(
    dateRange || {
      start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 days ago
      end_date: new Date().toISOString().split('T')[0] // today
    }
  );

  useEffect(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      fetchTimesheetSummary();
    }
  }, [socket, employeeId, selectedDateRange]);

  useEffect(() => {
    if (socket) {
      const handleMessage = (event) => {
        try {
          const response = JSON.parse(event.data);
          if (response.request_id === 800) { // GET_TIMESHEET_SUMMARY
            setIsLoading(false);
            if (response.success) {
              setSummary(response.data);
              setError('');
            } else {
              setError(response.error || 'Failed to load timesheet summary');
              setSummary(null);
            }
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      socket.addEventListener('message', handleMessage);
      return () => socket.removeEventListener('message', handleMessage);
    }
  }, [socket]);

  const fetchTimesheetSummary = () => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError('WebSocket connection not available.');
      return;
    }

    setIsLoading(true);
    setError('');

    const request = {
      request_id: 800, // GET_TIMESHEET_SUMMARY
      data: {
        employee_id: employeeId,
        date_range: selectedDateRange
      }
    };

    socket.send(JSON.stringify(request));
  };

  const handleDateRangeChange = (field, value) => {
    setSelectedDateRange(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const formatHours = (hours) => {
    if (!hours) return '0.00';
    return parseFloat(hours).toFixed(2);
  };

  const calculateAverageHours = () => {
    if (!summary || summary.shifts_worked === 0) return '0.00';
    return (summary.total_hours / summary.shifts_worked).toFixed(2);
  };

  return (
    <div className="timesheet-summary">
      <div className="summary-header">
        <h3>📊 Timesheet Summary</h3>
        
        {/* Date Range Selector */}
        <div className="date-range-selector">
          <div className="date-input-group">
            <label>From:</label>
            <input
              type="date"
              value={selectedDateRange.start_date}
              onChange={(e) => handleDateRangeChange('start_date', e.target.value)}
              disabled={isLoading}
            />
          </div>
          <div className="date-input-group">
            <label>To:</label>
            <input
              type="date"
              value={selectedDateRange.end_date}
              onChange={(e) => handleDateRangeChange('end_date', e.target.value)}
              disabled={isLoading}
            />
          </div>
          <button 
            onClick={fetchTimesheetSummary}
            disabled={isLoading}
            className="refresh-button"
          >
            {isLoading ? '⏳' : '🔄'} Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <span className="alert-icon">⚠️</span>
          {error}
        </div>
      )}

      {isLoading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <span>Loading timesheet summary...</span>
        </div>
      )}

      {summary && !isLoading && (
        <div className="summary-content">
          <div className="summary-cards">
            <div className="summary-card total-hours">
              <div className="card-icon">⏰</div>
              <div className="card-content">
                <div className="card-value">{formatHours(summary.total_hours)}</div>
                <div className="card-label">Total Hours</div>
              </div>
            </div>

            <div className="summary-card regular-hours">
              <div className="card-icon">📅</div>
              <div className="card-content">
                <div className="card-value">{formatHours(summary.regular_hours)}</div>
                <div className="card-label">Regular Hours</div>
              </div>
            </div>

            <div className="summary-card overtime-hours">
              <div className="card-icon">⚡</div>
              <div className="card-content">
                <div className="card-value">{formatHours(summary.overtime_hours)}</div>
                <div className="card-label">Overtime Hours</div>
              </div>
            </div>

            <div className="summary-card shifts-worked">
              <div className="card-icon">🎯</div>
              <div className="card-content">
                <div className="card-value">{summary.shifts_worked}</div>
                <div className="card-label">Shifts Worked</div>
              </div>
            </div>

            <div className="summary-card average-hours">
              <div className="card-icon">📊</div>
              <div className="card-content">
                <div className="card-value">{calculateAverageHours()}</div>
                <div className="card-label">Avg Hours/Shift</div>
              </div>
            </div>
          </div>

          {summary.overtime_hours > 0 && (
            <div className="overtime-notice">
              <span className="notice-icon">⚡</span>
              <span>This period includes {formatHours(summary.overtime_hours)} overtime hours</span>
            </div>
          )}
        </div>
      )}

      {!summary && !isLoading && !error && (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <h4>No Timesheet Data</h4>
          <p>No timesheet data found for the selected date range.</p>
        </div>
      )}
    </div>
  );
};

export default TimesheetSummary;
