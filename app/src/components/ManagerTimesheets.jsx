import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
import TimesheetSummary from './TimesheetSummary';
import '../css/ManagerTimesheets.css';

const ManagerTimesheets = () => {
  const { socket } = useSocket();
  const [timesheets, setTimesheets] = useState([]);
  const [filteredTimesheets, setFilteredTimesheets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all'); // 'all', 'pending', 'approved'

  const fetchTimesheets = () => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError('WebSocket connection not available.');
      setLoading(false);
      return;
    }

    const request = {
      request_id: 103, // Request ID for fetching all submitted timesheets for manager
    };
    socket.send(JSON.stringify(request));
    setLoading(true);
    setError(null);
    setSuccessMessage(null);
  };

  useEffect(() => {
    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        if (response.request_id === 103) {
          if (response.success && response.data) {
            setTimesheets(response.data);
            setFilteredTimesheets(response.data);
          } else {
            setError(response.error || 'Failed to fetch timesheets.');
          }
          setLoading(false);
        } else if (response.request_id === 104) {
          if (response.success) {
            setSuccessMessage(response.message || 'Timesheet status updated successfully!');
            // Re-fetch timesheets to reflect the updated status
            fetchTimesheets();
          } else {
            setError(response.error || 'Failed to update timesheet status.');
          }
        }
      } catch (e) {
        console.error('Error parsing WebSocket message:', e);
        setError('Error processing response from server.');
        setLoading(false);
      }
    };

    socket.addEventListener('message', handleMessage);

    fetchTimesheets(); // Initial fetch

    return () => {
      if (socket && typeof socket.removeEventListener === 'function') {
        socket.removeEventListener('message', handleMessage);
      }
    };
  }, [socket]);

  const handleApproveReject = (timesheet, isApproved) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError('WebSocket connection not available.');
      return;
    }

    const request = {
      request_id: 104, // Request ID for updating timesheet status
      data: {
        shift_id: timesheet.shift_id,
        user_id: timesheet.user_id,
        role_assigned: timesheet.role_assigned,
        is_approved: isApproved,
      },
    };
    socket.send(JSON.stringify(request));
  };

  // Filter timesheets based on search term and status
  const filterTimesheets = () => {
    let filtered = timesheets;

    // Filter by search term (employee name, job name, or client company)
    if (searchTerm) {
      filtered = filtered.filter(ts =>
        ts.employee_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ts.job_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ts.client_company_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(ts =>
        statusFilter === 'approved' ? ts.is_approved : !ts.is_approved
      );
    }

    setFilteredTimesheets(filtered);
  };

  // Effect to filter timesheets when search term or status filter changes
  React.useEffect(() => {
    filterTimesheets();
  }, [searchTerm, statusFilter, timesheets]);

  if (loading) {
    return <div className="manager-timesheets-loading">Loading timesheets...</div>;
  }

  if (error) {
    return <div className="manager-timesheets-error">Error: {error}</div>;
  }

  return (
    <div className="manager-timesheets-container">
      <h2>Employee Timesheets</h2>
      {successMessage && <div className="success-message">{successMessage}</div>}

      {/* Timesheet Summary Section */}
      <TimesheetSummary />

      {/* Search and Filter Controls */}
      <div className="timesheets-controls">
        <div className="search-container">
          <input
            type="text"
            placeholder="Search by employee, job, or client..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        <div className="filter-container">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="status-filter"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending Only</option>
            <option value="approved">Approved Only</option>
          </select>
        </div>
        <div className="results-info">
          Showing {filteredTimesheets.length} of {timesheets.length} timesheets
        </div>
      </div>

      {timesheets.length === 0 ? (
        <p>No timesheets submitted yet.</p>
      ) : filteredTimesheets.length === 0 ? (
        <p>No timesheets match your search criteria.</p>
      ) : (
        <table className="timesheets-table">
          <thead>
            <tr>
              <th>Employee Name</th>
              <th>Role</th>
              <th>Shift Date</th>
              <th>Shift Part</th>
              <th>Job Name</th>
              <th>Client Company</th>
              <th>Clock In</th>
              <th>Clock Out</th>
              <th>Hours</th>
              <th>Submitted At</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredTimesheets.map((ts) => {
              // Calculate hours worked
              let hoursWorked = '';
              if (ts.clock_in_time && ts.clock_out_time) {
                const clockIn = new Date(ts.clock_in_time);
                const clockOut = new Date(ts.clock_out_time);
                const diffMs = clockOut - clockIn;
                const diffHours = diffMs / (1000 * 60 * 60);
                hoursWorked = diffHours > 0 ? `${diffHours.toFixed(2)}h` : 'Invalid';
              }

              return (
                <tr key={`${ts.shift_id}-${ts.user_id}-${ts.role_assigned}`} className={ts.is_approved ? 'approved-row' : 'pending-row'}>
                  <td className="employee-name">{ts.employee_name}</td>
                  <td>{ts.role_assigned}</td>
                  <td>{new Date(ts.shift_date).toLocaleDateString()}</td>
                  <td>{ts.shift_part}</td>
                  <td>{ts.job_name}</td>
                  <td>{ts.client_company_name}</td>
                  <td>{ts.clock_in_time ? new Date(ts.clock_in_time).toLocaleString() : 'N/A'}</td>
                  <td>{ts.clock_out_time ? new Date(ts.clock_out_time).toLocaleString() : 'N/A'}</td>
                  <td className="hours-worked">{hoursWorked}</td>
                  <td>{ts.times_submitted_at ? new Date(ts.times_submitted_at).toLocaleString() : 'N/A'}</td>
                  <td>
                    <span className={`status-badge ${ts.is_approved ? 'status-approved' : 'status-pending'}`}>
                      {ts.is_approved ? '✓ Approved' : '⏳ Pending'}
                    </span>
                  </td>
                  <td>
                    {!ts.is_approved && (
                      <button onClick={() => handleApproveReject(ts, true)} className="approve-button">Approve</button>
                    )}
                    {ts.is_approved && (
                      <button onClick={() => handleApproveReject(ts, false)} className="reject-button">Reject</button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ManagerTimesheets;
