import React, { useState, useEffect } from 'react';
import './TimesheetRow.css';

const TimesheetRow = ({ worker, userPermissions, onUpdateTimesheet, isLoading }) => {
  const [timePairs, setTimePairs] = useState([
    { pair_number: 1, clock_in: '', clock_out: '', description: 'Start of shift to first break' },
    { pair_number: 2, clock_in: '', clock_out: '', description: 'Return from first break to second break' },
    { pair_number: 3, clock_in: '', clock_out: '', description: 'Return from second break to end of shift' }
  ]);
  const [notes, setNotes] = useState('');
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    // Initialize with existing timesheet data
    if (worker.timesheet.time_pairs) {
      const existingPairs = [...timePairs];
      worker.timesheet.time_pairs.forEach(pair => {
        const index = pair.pair_number - 1;
        if (index >= 0 && index < existingPairs.length) {
          existingPairs[index] = {
            ...existingPairs[index],
            clock_in: pair.clock_in ? pair.clock_in.slice(0, 16) : '', // Format for datetime-local
            clock_out: pair.clock_out ? pair.clock_out.slice(0, 16) : ''
          };
        }
      });
      setTimePairs(existingPairs);
    }
    
    setNotes(worker.timesheet.notes || '');
  }, [worker.timesheet]);

  const handleTimeChange = (pairIndex, field, value) => {
    setTimePairs(prev => {
      const newPairs = [...prev];
      newPairs[pairIndex] = { ...newPairs[pairIndex], [field]: value };
      return newPairs;
    });
    setHasChanges(true);
  };

  const handleNotesChange = (value) => {
    setNotes(value);
    setHasChanges(true);
  };

  const handleSave = () => {
    // Filter out empty pairs and format for API
    const validPairs = timePairs
      .filter(pair => pair.clock_in || pair.clock_out)
      .map(pair => ({
        pair_number: pair.pair_number,
        clock_in: pair.clock_in ? new Date(pair.clock_in).toISOString() : null,
        clock_out: pair.clock_out ? new Date(pair.clock_out).toISOString() : null
      }));

    onUpdateTimesheet(worker.user_id, worker.role_assigned, validPairs, notes);
    setHasChanges(false);
  };

  const handleReset = () => {
    // Reset to original values
    if (worker.timesheet.time_pairs) {
      const resetPairs = [...timePairs];
      worker.timesheet.time_pairs.forEach(pair => {
        const index = pair.pair_number - 1;
        if (index >= 0 && index < resetPairs.length) {
          resetPairs[index] = {
            ...resetPairs[index],
            clock_in: pair.clock_in ? pair.clock_in.slice(0, 16) : '',
            clock_out: pair.clock_out ? pair.clock_out.slice(0, 16) : ''
          };
        }
      });
      setTimePairs(resetPairs);
    }
    setNotes(worker.timesheet.notes || '');
    setHasChanges(false);
  };

  const calculatePairHours = (pair) => {
    if (!pair.clock_in || !pair.clock_out) return 0;
    
    const clockIn = new Date(pair.clock_in);
    const clockOut = new Date(pair.clock_out);
    
    if (clockOut <= clockIn) return 0;
    
    const diffMs = clockOut - clockIn;
    return (diffMs / (1000 * 60 * 60)).toFixed(2);
  };

  const getTotalHours = () => {
    return timePairs.reduce((total, pair) => {
      return total + parseFloat(calculatePairHours(pair));
    }, 0).toFixed(2);
  };

  const canEdit = worker.can_edit && !worker.timesheet.is_approved;
  const isSubmitted = worker.timesheet.times_submitted_at;
  const isApproved = worker.timesheet.is_approved;

  return (
    <div className="timesheet-row-details">
      <div className="timesheet-header">
        <h4>Time Entry for {worker.name}</h4>
        <div className="timesheet-meta">
          <span className="role-info">Role: {worker.role_assigned.replace('_', ' ')}</span>
          <span className="total-hours">Total: {getTotalHours()}h</span>
        </div>
      </div>

      <div className="time-pairs-container">
        <h5>Clock In/Out Times</h5>
        <div className="time-pairs-grid">
          {timePairs.map((pair, index) => (
            <div key={pair.pair_number} className="time-pair">
              <div className="pair-header">
                <span className="pair-number">Pair {pair.pair_number}</span>
                <span className="pair-description">{pair.description}</span>
                <span className="pair-hours">{calculatePairHours(pair)}h</span>
              </div>
              
              <div className="time-inputs">
                <div className="time-input-group">
                  <label>Clock In:</label>
                  <input
                    type="datetime-local"
                    value={pair.clock_in}
                    onChange={(e) => handleTimeChange(index, 'clock_in', e.target.value)}
                    disabled={!canEdit || isLoading}
                    className={!canEdit ? 'disabled' : ''}
                  />
                </div>
                
                <div className="time-input-group">
                  <label>Clock Out:</label>
                  <input
                    type="datetime-local"
                    value={pair.clock_out}
                    onChange={(e) => handleTimeChange(index, 'clock_out', e.target.value)}
                    disabled={!canEdit || isLoading}
                    className={!canEdit ? 'disabled' : ''}
                    min={pair.clock_in || undefined}
                  />
                </div>
              </div>
              
              {pair.clock_in && pair.clock_out && new Date(pair.clock_out) <= new Date(pair.clock_in) && (
                <div className="validation-error">
                  Clock out time must be after clock in time
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="notes-section">
        <label htmlFor={`notes-${worker.user_id}`}>Notes:</label>
        <textarea
          id={`notes-${worker.user_id}`}
          value={notes}
          onChange={(e) => handleNotesChange(e.target.value)}
          disabled={!canEdit || isLoading}
          className={!canEdit ? 'disabled' : ''}
          placeholder="Add any notes about this timesheet entry..."
          rows={3}
        />
      </div>

      <div className="timesheet-status">
        <div className="status-info">
          {isSubmitted && (
            <div className="status-item">
              <span className="status-label">Submitted:</span>
              <span className="status-value">
                {new Date(worker.timesheet.times_submitted_at).toLocaleString()}
              </span>
            </div>
          )}
          
          {isApproved && (
            <div className="status-item">
              <span className="status-label">Approved:</span>
              <span className="status-value">
                {new Date(worker.timesheet.approved_at).toLocaleString()}
              </span>
            </div>
          )}
          
          {worker.timesheet.total_hours_worked && (
            <div className="status-item">
              <span className="status-label">Calculated Hours:</span>
              <span className="status-value">{worker.timesheet.total_hours_worked}h</span>
            </div>
          )}
          
          {worker.timesheet.overtime_hours > 0 && (
            <div className="status-item overtime">
              <span className="status-label">Overtime:</span>
              <span className="status-value">{worker.timesheet.overtime_hours}h</span>
            </div>
          )}
        </div>
      </div>

      {canEdit && (
        <div className="timesheet-actions">
          <button
            onClick={handleSave}
            disabled={!hasChanges || isLoading}
            className="save-button"
          >
            {isLoading ? 'Saving...' : 'Save Changes'}
          </button>
          
          <button
            onClick={handleReset}
            disabled={!hasChanges || isLoading}
            className="reset-button"
          >
            Reset
          </button>
        </div>
      )}

      {!canEdit && (
        <div className="readonly-notice">
          {isApproved ? (
            <p><strong>This timesheet has been approved and cannot be modified.</strong></p>
          ) : isSubmitted ? (
            <p><strong>This timesheet has been submitted and is awaiting approval.</strong></p>
          ) : (
            <p><strong>You don't have permission to edit this timesheet.</strong></p>
          )}
        </div>
      )}
    </div>
  );
};

export default TimesheetRow;
