import React from 'react';
import './ShiftCard.css';

const ShiftCard = ({
  shift,
  workers,
  style,
  onClick,
  onDoubleClick,
  compact = false
}) => {
  // Calculate staffing status
  const getStaffingStatus = () => {
    const required = shift.role_requirements || {};
    const assigned = shift.assigned_workers || [];
    
    const totalRequired = Object.values(required).reduce((sum, count) => sum + count, 0);
    const totalAssigned = assigned.length;
    
    if (totalAssigned === 0) return 'no-workers';
    if (totalAssigned < totalRequired) return 'understaffed';
    if (totalAssigned === totalRequired) return 'fully-staffed';
    return 'overstaffed';
  };

  const getStaffingInfo = () => {
    const required = shift.role_requirements || {};
    const assigned = shift.assigned_workers || [];
    
    const totalRequired = Object.values(required).reduce((sum, count) => sum + count, 0);
    const totalAssigned = assigned.length;
    
    return {
      assigned: totalAssigned,
      required: totalRequired,
      status: getStaffingStatus()
    };
  };

  const formatTime = (dateTime) => {
    if (!dateTime) return '';
    const date = new Date(dateTime);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const formatDuration = () => {
    if (!shift.shift_start_datetime || !shift.shift_end_datetime) return '';
    
    const start = new Date(shift.shift_start_datetime);
    const end = new Date(shift.shift_end_datetime);
    const duration = (end - start) / (1000 * 60 * 60); // Hours
    
    return `${duration}h`;
  };

  const getJobInfo = () => {
    if (shift.job_name) return shift.job_name;
    if (shift.job_id) return `Job #${shift.job_id}`;
    return 'No Job Assigned';
  };

  const getClientInfo = () => {
    if (shift.client_company_name) return shift.client_company_name;
    return '';
  };

  const getRoleBreakdown = () => {
    const required = shift.role_requirements || {};
    const assigned = shift.assigned_workers || [];
    
    const breakdown = {};
    
    // Initialize with requirements
    Object.entries(required).forEach(([role, count]) => {
      if (count > 0) {
        breakdown[role] = { required: count, assigned: 0 };
      }
    });
    
    // Count assigned workers by role
    assigned.forEach(worker => {
      const role = worker.role_assigned || 'stagehand';
      if (!breakdown[role]) {
        breakdown[role] = { required: 0, assigned: 0 };
      }
      breakdown[role].assigned++;
    });
    
    return breakdown;
  };

  const staffingInfo = getStaffingInfo();
  const roleBreakdown = getRoleBreakdown();

  const handleClick = (e) => {
    e.stopPropagation();
    if (onClick) onClick(shift);
  };

  const handleDoubleClick = (e) => {
    e.stopPropagation();
    if (onDoubleClick) onDoubleClick(shift);
  };

  return (
    <div
      className={`shift-card ${staffingInfo.status} ${compact ? 'compact' : ''}`}
      style={style}
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
    >
      <div className="shift-header">
        <div className="shift-time">
          {shift.shift_start_datetime ? (
            <>
              <span className="start-time">{formatTime(shift.shift_start_datetime)}</span>
              {shift.shift_end_datetime && (
                <>
                  <span className="time-separator">-</span>
                  <span className="end-time">{formatTime(shift.shift_end_datetime)}</span>
                </>
              )}
              <span className="duration">({formatDuration()})</span>
            </>
          ) : (
            <span className="legacy-time">{shift.shiftPart}</span>
          )}
        </div>
        
        <div className="staffing-indicator">
          <span className="staffing-count">
            {staffingInfo.assigned}/{staffingInfo.required}
          </span>
          <div className={`status-dot ${staffingInfo.status}`}></div>
        </div>
      </div>

      <div className="shift-content">
        <div className="job-info">
          <div className="job-name" title={getJobInfo()}>
            {getJobInfo()}
          </div>
          {getClientInfo() && (
            <div className="client-name" title={getClientInfo()}>
              {getClientInfo()}
            </div>
          )}
        </div>

        {!compact && (
          <div className="role-breakdown">
            {Object.entries(roleBreakdown).map(([role, counts]) => (
              <div key={role} className="role-item">
                <span className="role-name">
                  {role.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                </span>
                <span className={`role-count ${counts.assigned < counts.required ? 'understaffed' : counts.assigned > counts.required ? 'overstaffed' : 'adequate'}`}>
                  {counts.assigned}/{counts.required}
                </span>
              </div>
            ))}
          </div>
        )}

        {shift.assigned_workers && shift.assigned_workers.length > 0 && (
          <div className="assigned-workers">
            {compact ? (
              <div className="worker-count">
                👥 {shift.assigned_workers.length} worker(s)
              </div>
            ) : (
              <div className="worker-list">
                {shift.assigned_workers.slice(0, 3).map(worker => (
                  <div key={`${worker.user_id}-${worker.role_assigned}`} className="worker-item">
                    <span className="worker-name">{worker.name}</span>
                    <span className="worker-role">({worker.role_assigned})</span>
                  </div>
                ))}
                {shift.assigned_workers.length > 3 && (
                  <div className="more-workers">
                    +{shift.assigned_workers.length - 3} more
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="shift-footer">
        <div className="shift-actions">
          {shift.client_po_number && (
            <span className="po-number" title="PO Number">
              PO: {shift.client_po_number}
            </span>
          )}
          
          <div className="action-buttons">
            <button
              className="timesheet-button"
              onClick={(e) => {
                e.stopPropagation();
                window.open(`/timesheet/${shift.id}`, '_blank');
              }}
              title="Open Timesheet"
            >
              📋
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ShiftCard;
