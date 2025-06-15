import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSocket } from '../utils';
import './ShiftTimesheetEntry.css';

const ShiftTimesheetEntry = () => {
  const { shiftId } = useParams();
  const navigate = useNavigate();
  const { socket } = useSocket();
  
  const [shiftData, setShiftData] = useState(null);
  const [workers, setWorkers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [selectedWorkers, setSelectedWorkers] = useState(new Set());
  const [expandedWorkers, setExpandedWorkers] = useState(new Set());
  const [currentTime, setCurrentTime] = useState(new Date());

  // Update current time every minute
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      fetchShiftData();
    }
  }, [socket, shiftId]);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);

        if (response.request_id === 1010) { // Get shift timesheet data
          if (response.success) {
            setShiftData(response.data.shift_details);
            setWorkers(response.data.timesheet_data || []);
          } else {
            setError(response.error || 'Failed to load shift data');
          }
          setLoading(false);
        } else if (response.request_id === 1011) { // Update worker timesheet
          if (response.success) {
            setSuccessMessage('Timesheet updated successfully');
            fetchShiftData(); // Refresh data
            setTimeout(() => setSuccessMessage(''), 3000);
          } else {
            setError(response.error || 'Failed to update timesheet');
          }
          setSaving(false);
        } else if (response.request_id === 1012) { // Submit timesheets
          if (response.success) {
            setSuccessMessage(response.message || 'Timesheets submitted successfully');
            fetchShiftData(); // Refresh data
            setSelectedWorkers(new Set());
            setTimeout(() => setSuccessMessage(''), 5000);
          } else {
            setError(response.error || 'Failed to submit timesheets');
          }
          setSaving(false);
        }
      } catch (e) {
        console.error('Error parsing WebSocket message:', e);
        setError('Error processing server response');
        setLoading(false);
        setSaving(false);
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => socket.removeEventListener('message', handleMessage);
  }, [socket]);

  const fetchShiftData = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      setLoading(true);
      const request = {
        request_id: 1010,
        data: { shift_id: parseInt(shiftId) }
      };
      socket.send(JSON.stringify(request));
    }
  };

  const handleTimeChange = (workerId, pairIndex, field, value) => {
    setWorkers(prev => prev.map(worker => {
      if (worker.user_id === workerId) {
        const updatedTimePairs = [...(worker.timesheet?.time_pairs || [])];
        
        // Ensure we have enough pairs
        while (updatedTimePairs.length <= pairIndex) {
          updatedTimePairs.push({
            pair_number: updatedTimePairs.length + 1,
            clock_in: '',
            clock_out: ''
          });
        }
        
        updatedTimePairs[pairIndex] = {
          ...updatedTimePairs[pairIndex],
          [field]: value
        };

        return {
          ...worker,
          timesheet: {
            ...worker.timesheet,
            time_pairs: updatedTimePairs
          },
          hasChanges: true
        };
      }
      return worker;
    }));
  };

  const handleNotesChange = (workerId, notes) => {
    setWorkers(prev => prev.map(worker => {
      if (worker.user_id === workerId) {
        return {
          ...worker,
          timesheet: {
            ...worker.timesheet,
            notes: notes
          },
          hasChanges: true
        };
      }
      return worker;
    }));
  };

  const handleAbsentToggle = (workerId) => {
    setWorkers(prev => prev.map(worker => {
      if (worker.user_id === workerId) {
        return {
          ...worker,
          timesheet: {
            ...worker.timesheet,
            is_absent: !worker.timesheet?.is_absent
          },
          hasChanges: true
        };
      }
      return worker;
    }));
  };

  const calculateHours = (timePairs) => {
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

  const saveWorkerTimesheet = (workerId) => {
    const worker = workers.find(w => w.user_id === workerId);
    if (!worker || !worker.hasChanges) return;

    setSaving(true);
    const request = {
      request_id: 1011,
      data: {
        shift_id: parseInt(shiftId),
        worker_user_id: workerId,
        role_assigned: worker.role_assigned,
        time_pairs: worker.timesheet?.time_pairs || [],
        notes: worker.timesheet?.notes || '',
        is_absent: worker.timesheet?.is_absent || false
      }
    };
    socket.send(JSON.stringify(request));
  };

  const submitSelectedTimesheets = () => {
    if (selectedWorkers.size === 0) {
      setError('Please select workers to submit timesheets for');
      return;
    }

    if (!window.confirm(`Submit timesheets for ${selectedWorkers.size} worker(s)?`)) {
      return;
    }

    setSaving(true);
    const request = {
      request_id: 1012,
      data: {
        shift_id: parseInt(shiftId),
        worker_ids: Array.from(selectedWorkers)
      }
    };
    socket.send(JSON.stringify(request));
  };

  const toggleWorkerSelection = (workerId, checked) => {
    setSelectedWorkers(prev => {
      const newSet = new Set(prev);
      if (checked) {
        newSet.add(workerId);
      } else {
        newSet.delete(workerId);
      }
      return newSet;
    });
  };

  const toggleWorkerExpansion = (workerId) => {
    setExpandedWorkers(prev => {
      const newSet = new Set(prev);
      if (newSet.has(workerId)) {
        newSet.delete(workerId);
      } else {
        newSet.add(workerId);
      }
      return newSet;
    });
  };

  const selectAllWorkers = (checked) => {
    if (checked) {
      setSelectedWorkers(new Set(workers.map(w => w.user_id)));
    } else {
      setSelectedWorkers(new Set());
    }
  };

  if (loading) {
    return (
      <div className="timesheet-entry-container">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading shift timesheet data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="timesheet-entry-container">
      {/* Header */}
      <div className="timesheet-header">
        <div className="header-content">
          <button onClick={() => navigate(-1)} className="back-button">
            ← Back
          </button>
          <div className="shift-info">
            <h1>Shift Timesheet Entry</h1>
            {shiftData && (
              <div className="shift-details">
                <span>Shift #{shiftId}</span>
                <span>•</span>
                <span>{new Date(shiftData.shift_date).toLocaleDateString()}</span>
                <span>•</span>
                <span>{shiftData.job_name}</span>
              </div>
            )}
          </div>
          <div className="current-time">
            <div className="time-display">
              {currentTime.toLocaleTimeString()}
            </div>
            <div className="date-display">
              {currentTime.toLocaleDateString()}
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div className="message error-message">
          <span className="message-icon">⚠️</span>
          {error}
          <button onClick={() => setError('')} className="close-message">×</button>
        </div>
      )}
      
      {successMessage && (
        <div className="message success-message">
          <span className="message-icon">✅</span>
          {successMessage}
          <button onClick={() => setSuccessMessage('')} className="close-message">×</button>
        </div>
      )}

      {/* Bulk Actions */}
      <div className="bulk-actions">
        <div className="selection-controls">
          <label className="select-all-checkbox">
            <input
              type="checkbox"
              checked={selectedWorkers.size === workers.length && workers.length > 0}
              onChange={(e) => selectAllWorkers(e.target.checked)}
              disabled={saving}
            />
            Select All ({selectedWorkers.size} of {workers.length})
          </label>
        </div>
        
        <div className="action-buttons">
          <button
            onClick={submitSelectedTimesheets}
            disabled={selectedWorkers.size === 0 || saving}
            className="submit-button primary"
          >
            {saving ? 'Submitting...' : `Submit ${selectedWorkers.size} Timesheet(s)`}
          </button>
        </div>
      </div>

      {/* Workers List */}
      <div className="workers-list">
        {workers.length === 0 ? (
          <div className="empty-state">
            <h3>No Workers Assigned</h3>
            <p>No workers are assigned to this shift yet.</p>
          </div>
        ) : (
          workers.map(worker => (
            <WorkerTimesheetCard
              key={worker.user_id}
              worker={worker}
              isSelected={selectedWorkers.has(worker.user_id)}
              isExpanded={expandedWorkers.has(worker.user_id)}
              onSelectionChange={toggleWorkerSelection}
              onExpansionToggle={toggleWorkerExpansion}
              onTimeChange={handleTimeChange}
              onNotesChange={handleNotesChange}
              onAbsentToggle={handleAbsentToggle}
              onSave={saveWorkerTimesheet}
              calculateHours={calculateHours}
              saving={saving}
            />
          ))
        )}
      </div>
    </div>
  );
};

// Worker Timesheet Card Component
const WorkerTimesheetCard = ({
  worker,
  isSelected,
  isExpanded,
  onSelectionChange,
  onExpansionToggle,
  onTimeChange,
  onNotesChange,
  onAbsentToggle,
  onSave,
  calculateHours,
  saving
}) => {
  const totalHours = calculateHours(worker.timesheet?.time_pairs || []);
  const isSubmitted = worker.timesheet?.times_submitted_at;
  const isApproved = worker.timesheet?.is_approved;
  const isAbsent = worker.timesheet?.is_absent;
  const hasChanges = worker.hasChanges;

  const getStatusBadge = () => {
    if (isAbsent) return { text: 'Absent', class: 'absent' };
    if (isApproved) return { text: 'Approved', class: 'approved' };
    if (isSubmitted) return { text: 'Submitted', class: 'submitted' };
    return { text: 'Draft', class: 'draft' };
  };

  const status = getStatusBadge();

  return (
    <div className={`worker-card ${isSelected ? 'selected' : ''} ${isAbsent ? 'absent' : ''}`}>
      <div className="worker-card-header">
        <div className="worker-info">
          <label className="worker-checkbox">
            <input
              type="checkbox"
              checked={isSelected}
              onChange={(e) => onSelectionChange(worker.user_id, e.target.checked)}
              disabled={saving}
            />
            <div className="worker-details">
              <h3 className="worker-name">{worker.name}</h3>
              <span className="worker-role">{worker.role_assigned?.replace('_', ' ')}</span>
            </div>
          </label>
        </div>

        <div className="worker-status">
          <span className={`status-badge ${status.class}`}>
            {status.text}
          </span>
          <div className="hours-display">
            <span className="hours-value">{totalHours}h</span>
            {parseFloat(totalHours) > 8 && (
              <span className="overtime-indicator">OT</span>
            )}
          </div>
        </div>

        <div className="worker-actions">
          <button
            onClick={() => onAbsentToggle(worker.user_id)}
            disabled={isSubmitted || saving}
            className={`absent-button ${isAbsent ? 'active' : ''}`}
          >
            {isAbsent ? 'Present' : 'Absent'}
          </button>

          <button
            onClick={() => onExpansionToggle(worker.user_id)}
            className="expand-button"
          >
            {isExpanded ? '▼' : '▶'}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="worker-card-details">
          {!isAbsent ? (
            <>
              <div className="time-pairs-section">
                <h4>Time Entries</h4>
                <div className="time-pairs">
                  {[0, 1, 2].map(pairIndex => (
                    <TimePairInput
                      key={pairIndex}
                      pairIndex={pairIndex}
                      workerId={worker.user_id}
                      timePair={worker.timesheet?.time_pairs?.[pairIndex]}
                      onTimeChange={onTimeChange}
                      disabled={isSubmitted || saving}
                    />
                  ))}
                </div>
              </div>

              <div className="notes-section">
                <label htmlFor={`notes-${worker.user_id}`}>Notes:</label>
                <textarea
                  id={`notes-${worker.user_id}`}
                  value={worker.timesheet?.notes || ''}
                  onChange={(e) => onNotesChange(worker.user_id, e.target.value)}
                  disabled={isSubmitted || saving}
                  placeholder="Add notes about this worker's shift..."
                  rows={3}
                />
              </div>
            </>
          ) : (
            <div className="absent-notice">
              <p>Worker marked as absent for this shift.</p>
            </div>
          )}

          {hasChanges && !isSubmitted && (
            <div className="save-section">
              <button
                onClick={() => onSave(worker.user_id)}
                disabled={saving}
                className="save-button"
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          )}

          {isSubmitted && (
            <div className="submission-info">
              <p>
                <strong>Submitted:</strong> {new Date(worker.timesheet.times_submitted_at).toLocaleString()}
              </p>
              {worker.timesheet.times_submitted_by && (
                <p><strong>By:</strong> User ID {worker.timesheet.times_submitted_by}</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Time Pair Input Component
const TimePairInput = ({ pairIndex, workerId, timePair, onTimeChange, disabled }) => {
  const pairLabels = [
    'Start of Shift → First Break',
    'Return from Break → Second Break',
    'Return from Break → End of Shift'
  ];

  const clockInValue = timePair?.clock_in ?
    new Date(timePair.clock_in).toISOString().slice(0, 16) : '';
  const clockOutValue = timePair?.clock_out ?
    new Date(timePair.clock_out).toISOString().slice(0, 16) : '';

  const calculatePairHours = () => {
    if (!clockInValue || !clockOutValue) return 0;
    const clockIn = new Date(clockInValue);
    const clockOut = new Date(clockOutValue);
    if (clockOut <= clockIn) return 0;
    return ((clockOut - clockIn) / (1000 * 60 * 60)).toFixed(2);
  };

  return (
    <div className="time-pair">
      <div className="pair-header">
        <span className="pair-label">Pair {pairIndex + 1}</span>
        <span className="pair-description">{pairLabels[pairIndex]}</span>
        <span className="pair-hours">{calculatePairHours()}h</span>
      </div>

      <div className="time-inputs">
        <div className="time-input-group">
          <label>Clock In:</label>
          <input
            type="datetime-local"
            value={clockInValue}
            onChange={(e) => onTimeChange(workerId, pairIndex, 'clock_in', e.target.value)}
            disabled={disabled}
          />
        </div>

        <div className="time-input-group">
          <label>Clock Out:</label>
          <input
            type="datetime-local"
            value={clockOutValue}
            onChange={(e) => onTimeChange(workerId, pairIndex, 'clock_out', e.target.value)}
            disabled={disabled}
            min={clockInValue || undefined}
          />
        </div>
      </div>

      {clockInValue && clockOutValue && new Date(clockOutValue) <= new Date(clockInValue) && (
        <div className="validation-error">
          Clock out time must be after clock in time
        </div>
      )}
    </div>
  );
};

export default ShiftTimesheetEntry;
