import React from 'react';
import './TimesheetActions.css';

const TimesheetActions = ({
  userPermissions,
  selectedWorkers,
  timesheetData,
  onSubmitTimesheet,
  onApproveTimesheet,
  onSelectAll,
  isLoading
}) => {
  const selectedCount = selectedWorkers.size;
  const totalWorkers = timesheetData.length;
  
  // Count workers by status
  const statusCounts = timesheetData.reduce((counts, worker) => {
    if (worker.timesheet.is_approved) {
      counts.approved++;
    } else if (worker.timesheet.times_submitted_at) {
      counts.submitted++;
    } else {
      counts.draft++;
    }
    return counts;
  }, { draft: 0, submitted: 0, approved: 0 });

  const canSubmit = userPermissions.can_edit_others && selectedCount > 0;
  const canApprove = userPermissions.can_approve && selectedCount > 0;

  // Check if selected workers have submitted timesheets (for approval)
  const selectedSubmittedWorkers = timesheetData.filter(worker => 
    selectedWorkers.has(worker.user_id) && 
    worker.timesheet.times_submitted_at && 
    !worker.timesheet.is_approved
  );

  const selectedDraftWorkers = timesheetData.filter(worker => 
    selectedWorkers.has(worker.user_id) && 
    !worker.timesheet.times_submitted_at
  );

  if (!userPermissions.can_edit_others && !userPermissions.can_approve) {
    return (
      <div className="timesheet-actions">
        <div className="status-summary">
          <h3>Timesheet Status Summary</h3>
          <div className="status-counts">
            <div className="status-count draft">
              <span className="count">{statusCounts.draft}</span>
              <span className="label">Draft</span>
            </div>
            <div className="status-count submitted">
              <span className="count">{statusCounts.submitted}</span>
              <span className="label">Submitted</span>
            </div>
            <div className="status-count approved">
              <span className="count">{statusCounts.approved}</span>
              <span className="label">Approved</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="timesheet-actions">
      <div className="actions-header">
        <div className="selection-info">
          <h3>Bulk Actions</h3>
          <div className="selection-controls">
            <button
              onClick={() => onSelectAll(selectedCount !== totalWorkers)}
              className="select-all-button"
              disabled={isLoading || totalWorkers === 0}
            >
              {selectedCount === totalWorkers ? 'Deselect All' : 'Select All'}
            </button>
            <span className="selection-count">
              {selectedCount} of {totalWorkers} selected
            </span>
          </div>
        </div>

        <div className="status-summary">
          <div className="status-counts">
            <div className="status-count draft">
              <span className="count">{statusCounts.draft}</span>
              <span className="label">Draft</span>
            </div>
            <div className="status-count submitted">
              <span className="count">{statusCounts.submitted}</span>
              <span className="label">Submitted</span>
            </div>
            <div className="status-count approved">
              <span className="count">{statusCounts.approved}</span>
              <span className="label">Approved</span>
            </div>
          </div>
        </div>
      </div>

      <div className="action-buttons">
        {userPermissions.can_edit_others && (
          <div className="action-group">
            <button
              onClick={() => onSubmitTimesheet()}
              disabled={!canSubmit || selectedDraftWorkers.length === 0 || isLoading}
              className="submit-button"
            >
              {isLoading ? 'Submitting...' : `Submit ${selectedDraftWorkers.length} Timesheet(s)`}
            </button>
            {selectedCount > 0 && selectedDraftWorkers.length === 0 && (
              <span className="action-note">Selected workers have already been submitted</span>
            )}
          </div>
        )}

        {userPermissions.can_approve && (
          <div className="action-group">
            <button
              onClick={() => onApproveTimesheet()}
              disabled={!canApprove || selectedSubmittedWorkers.length === 0 || isLoading}
              className="approve-button"
            >
              {isLoading ? 'Approving...' : `Approve ${selectedSubmittedWorkers.length} Timesheet(s)`}
            </button>
            {selectedCount > 0 && selectedSubmittedWorkers.length === 0 && (
              <span className="action-note">
                {timesheetData.filter(w => selectedWorkers.has(w.user_id) && w.timesheet.is_approved).length > 0
                  ? 'Selected workers are already approved'
                  : 'Selected workers need to be submitted first'
                }
              </span>
            )}
          </div>
        )}
      </div>

      {selectedCount === 0 && (userPermissions.can_edit_others || userPermissions.can_approve) && (
        <div className="no-selection-message">
          <p>Select workers above to submit or approve their timesheets in bulk.</p>
        </div>
      )}

      <div className="workflow-info">
        <h4>Timesheet Workflow:</h4>
        <div className="workflow-steps">
          <div className="workflow-step">
            <span className="step-number">1</span>
            <span className="step-text">Workers or crew chiefs enter time data</span>
          </div>
          <div className="workflow-arrow">→</div>
          <div className="workflow-step">
            <span className="step-number">2</span>
            <span className="step-text">Crew chiefs or managers submit timesheets</span>
          </div>
          <div className="workflow-arrow">→</div>
          <div className="workflow-step">
            <span className="step-number">3</span>
            <span className="step-text">Managers approve final timesheets</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TimesheetActions;
