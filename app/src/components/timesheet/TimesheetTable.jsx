import React, { useState } from 'react';
import TimesheetRow from './TimesheetRow';
import './TimesheetTable.css';

const TimesheetTable = ({
  timesheetData,
  userPermissions,
  selectedWorkers,
  onUpdateTimesheet,
  onWorkerSelection,
  isLoading
}) => {
  const [expandedRows, setExpandedRows] = useState(new Set());

  const toggleRowExpansion = (workerId) => {
    setExpandedRows(prev => {
      const newSet = new Set(prev);
      if (newSet.has(workerId)) {
        newSet.delete(workerId);
      } else {
        newSet.add(workerId);
      }
      return newSet;
    });
  };

  const calculateTotalHours = (timePairs) => {
    if (!timePairs || timePairs.length === 0) return 0;
    
    let totalMinutes = 0;
    
    timePairs.forEach(pair => {
      if (pair.clock_in && pair.clock_out) {
        const clockIn = new Date(pair.clock_in);
        const clockOut = new Date(pair.clock_out);
        if (clockOut > clockIn) {
          totalMinutes += (clockOut - clockIn) / (1000 * 60);
        }
      }
    });
    
    return (totalMinutes / 60).toFixed(2);
  };

  const getStatusBadge = (timesheet) => {
    if (timesheet.is_approved) {
      return <span className="status-badge approved">Approved</span>;
    } else if (timesheet.times_submitted_at) {
      return <span className="status-badge submitted">Submitted</span>;
    } else {
      return <span className="status-badge draft">Draft</span>;
    }
  };

  const getStatusColor = (timesheet) => {
    if (timesheet.is_approved) return '#27ae60';
    if (timesheet.times_submitted_at) return '#f39c12';
    return '#95a5a6';
  };

  if (!timesheetData || timesheetData.length === 0) {
    return (
      <div className="timesheet-table-container">
        <div className="empty-state">
          <h3>No Workers Found</h3>
          <p>No workers are assigned to this shift or you don't have permission to view them.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="timesheet-table-container">
      <div className="table-header">
        <h3>Worker Timesheets</h3>
        <div className="table-info">
          <span className="worker-count">{timesheetData.length} worker(s)</span>
          {selectedWorkers.size > 0 && (
            <span className="selected-count">{selectedWorkers.size} selected</span>
          )}
        </div>
      </div>

      <div className="timesheet-table-wrapper">
        <table className="timesheet-table">
          <thead>
            <tr>
              {(userPermissions.can_edit_others || userPermissions.can_approve) && (
                <th className="checkbox-column">
                  <input
                    type="checkbox"
                    checked={selectedWorkers.size === timesheetData.length && timesheetData.length > 0}
                    onChange={(e) => {
                      const allWorkerIds = timesheetData.map(w => w.user_id);
                      allWorkerIds.forEach(id => onWorkerSelection(id, e.target.checked));
                    }}
                    disabled={isLoading}
                  />
                </th>
              )}
              <th className="worker-column">Worker</th>
              <th className="role-column">Role</th>
              <th className="hours-column">Total Hours</th>
              <th className="status-column">Status</th>
              <th className="actions-column">Actions</th>
            </tr>
          </thead>
          <tbody>
            {timesheetData.map((worker) => {
              const isExpanded = expandedRows.has(worker.user_id);
              const totalHours = calculateTotalHours(worker.timesheet.time_pairs);
              
              return (
                <React.Fragment key={`${worker.user_id}-${worker.role_assigned}`}>
                  <tr 
                    className={`worker-row ${isExpanded ? 'expanded' : ''}`}
                    style={{ borderLeft: `4px solid ${getStatusColor(worker.timesheet)}` }}
                  >
                    {(userPermissions.can_edit_others || userPermissions.can_approve) && (
                      <td className="checkbox-cell">
                        <input
                          type="checkbox"
                          checked={selectedWorkers.has(worker.user_id)}
                          onChange={(e) => onWorkerSelection(worker.user_id, e.target.checked)}
                          disabled={isLoading}
                        />
                      </td>
                    )}
                    <td className="worker-cell">
                      <div className="worker-info">
                        <span className="worker-name">{worker.name}</span>
                        <span className="worker-id">ID: {worker.user_id}</span>
                      </div>
                    </td>
                    <td className="role-cell">
                      <span className="role-badge">{worker.role_assigned.replace('_', ' ')}</span>
                    </td>
                    <td className="hours-cell">
                      <span className="hours-value">{totalHours}h</span>
                      {worker.timesheet.overtime_hours > 0 && (
                        <span className="overtime-indicator">
                          +{worker.timesheet.overtime_hours}h OT
                        </span>
                      )}
                    </td>
                    <td className="status-cell">
                      {getStatusBadge(worker.timesheet)}
                    </td>
                    <td className="actions-cell">
                      <button
                        onClick={() => toggleRowExpansion(worker.user_id)}
                        className="expand-button"
                        disabled={isLoading}
                      >
                        {isExpanded ? '▼' : '▶'} {isExpanded ? 'Collapse' : 'Expand'}
                      </button>
                    </td>
                  </tr>
                  {isExpanded && (
                    <tr className="expanded-row">
                      <td colSpan={userPermissions.can_edit_others || userPermissions.can_approve ? 6 : 5}>
                        <TimesheetRow
                          worker={worker}
                          userPermissions={userPermissions}
                          onUpdateTimesheet={onUpdateTimesheet}
                          isLoading={isLoading}
                        />
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="table-footer">
        <div className="legend">
          <h4>Status Legend:</h4>
          <div className="legend-items">
            <div className="legend-item">
              <span className="status-badge draft">Draft</span>
              <span>Times can be edited</span>
            </div>
            <div className="legend-item">
              <span className="status-badge submitted">Submitted</span>
              <span>Awaiting approval</span>
            </div>
            <div className="legend-item">
              <span className="status-badge approved">Approved</span>
              <span>Finalized timesheet</span>
            </div>
          </div>
        </div>
        
        {userPermissions.is_client && (
          <div className="client-notice">
            <p><strong>Note:</strong> As a client, you can view timesheet data but cannot make changes.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TimesheetTable;
