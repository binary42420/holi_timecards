import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
import './TimesheetEditor.css';

const TimesheetEditor = ({ 
  shiftId, 
  workerId, 
  workerName, 
  initialTimesheet = null,
  canEdit = true,
  onSave,
  onCancel 
}) => {
  const { socket, connectionStatus } = useSocket();
  const [timesheet, setTimesheet] = useState({
    time_pairs: [
      { clock_in: '', clock_out: '' },
      { clock_in: '', clock_out: '' },
      { clock_in: '', clock_out: '' }
    ],
    role_assigned: 'stagehand',
    notes: '',
    is_absent: false
  });
  const [totalHours, setTotalHours] = useState(0);
  const [overtimeHours, setOvertimeHours] = useState(0);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const roleOptions = [
    { value: 'stagehand', label: 'Stagehand', rate: 25.00 },
    { value: 'crew_chief', label: 'Crew Chief', rate: 30.00 },
    { value: 'forklift_operator', label: 'Forklift Operator', rate: 28.00 },
    { value: 'truck_driver', label: 'Truck Driver', rate: 32.00 }
  ];

  useEffect(() => {
    if (initialTimesheet) {
      setTimesheet({
        time_pairs: initialTimesheet.time_pairs || [
          { clock_in: '', clock_out: '' },
          { clock_in: '', clock_out: '' },
          { clock_in: '', clock_out: '' }
        ],
        role_assigned: initialTimesheet.role_assigned || 'stagehand',
        notes: initialTimesheet.notes || '',
        is_absent: initialTimesheet.is_absent || false
      });
    }
  }, [initialTimesheet]);

  useEffect(() => {
    calculateHours();
  }, [timesheet.time_pairs]);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        if (response.request_id === 1011) { // UPDATE_WORKER_TIMESHEET
          setIsSaving(false);
          if (response.success) {
            setSuccessMessage('Timesheet saved successfully!');
            setError('');
            if (onSave) {
              onSave(timesheet);
            }
          } else {
            setError(response.error || 'Failed to save timesheet');
            setSuccessMessage('');
          }
        }
      } catch (e) {
        console.error('Error parsing timesheet response:', e);
        setIsSaving(false);
        setError('Error processing server response');
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => socket.removeEventListener('message', handleMessage);
  }, [socket, timesheet, onSave]);

  const calculateHours = () => {
    let total = 0;
    
    timesheet.time_pairs.forEach(pair => {
      if (pair.clock_in && pair.clock_out) {
        const clockIn = new Date(`1970-01-01T${pair.clock_in}:00`);
        const clockOut = new Date(`1970-01-01T${pair.clock_out}:00`);
        
        if (clockOut > clockIn) {
          const hours = (clockOut - clockIn) / (1000 * 60 * 60);
          total += hours;
        }
      }
    });

    setTotalHours(total);
    setOvertimeHours(Math.max(0, total - 8)); // Overtime after 8 hours
  };

  const handleTimeChange = (pairIndex, field, value) => {
    const newTimePairs = [...timesheet.time_pairs];
    newTimePairs[pairIndex] = {
      ...newTimePairs[pairIndex],
      [field]: value
    };
    
    setTimesheet(prev => ({
      ...prev,
      time_pairs: newTimePairs
    }));
  };

  const handleRoleChange = (role) => {
    setTimesheet(prev => ({
      ...prev,
      role_assigned: role
    }));
  };

  const handleNotesChange = (notes) => {
    setTimesheet(prev => ({
      ...prev,
      notes: notes
    }));
  };

  const handleAbsentToggle = (isAbsent) => {
    setTimesheet(prev => ({
      ...prev,
      is_absent: isAbsent,
      time_pairs: isAbsent ? [
        { clock_in: '', clock_out: '' },
        { clock_in: '', clock_out: '' },
        { clock_in: '', clock_out: '' }
      ] : prev.time_pairs
    }));
  };

  const handleSave = () => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError('Cannot save: WebSocket is not connected');
      return;
    }

    setIsSaving(true);
    setError('');
    setSuccessMessage('');

    const request = {
      request_id: 1011, // UPDATE_WORKER_TIMESHEET
      data: {
        shift_id: shiftId,
        worker_user_id: workerId,
        role_assigned: timesheet.role_assigned,
        time_pairs: timesheet.time_pairs,
        notes: timesheet.notes,
        is_absent: timesheet.is_absent
      }
    };

    socket.send(JSON.stringify(request));
  };

  const getCurrentRate = () => {
    const role = roleOptions.find(r => r.value === timesheet.role_assigned);
    return role ? role.rate : 25.00;
  };

  const calculatePay = () => {
    const rate = getCurrentRate();
    const regularHours = Math.min(totalHours, 8);
    const overtimeRate = rate * 1.5;
    
    return {
      regular: regularHours * rate,
      overtime: overtimeHours * overtimeRate,
      total: (regularHours * rate) + (overtimeHours * overtimeRate)
    };
  };

  const isConnected = connectionStatus === 'connected';
  const pay = calculatePay();

  return (
    <div className="timesheet-editor">
      <div className="timesheet-header">
        <h3>Timesheet Editor</h3>
        {workerName && (
          <div className="worker-info">
            <strong>{workerName}</strong>
            <span className="shift-id">Shift #{shiftId}</span>
          </div>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}
      {successMessage && <div className="success-message">{successMessage}</div>}

      <div className="timesheet-form">
        {/* Role Selection */}
        <div className="form-section">
          <label className="section-label">Role Assignment</label>
          <div className="role-selector">
            {roleOptions.map(role => (
              <label key={role.value} className="role-option">
                <input
                  type="radio"
                  name="role"
                  value={role.value}
                  checked={timesheet.role_assigned === role.value}
                  onChange={() => handleRoleChange(role.value)}
                  disabled={!canEdit || isSaving}
                />
                <span className="role-label">
                  {role.label} (${role.rate}/hr)
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Absent Toggle */}
        <div className="form-section">
          <label className="absent-toggle">
            <input
              type="checkbox"
              checked={timesheet.is_absent}
              onChange={(e) => handleAbsentToggle(e.target.checked)}
              disabled={!canEdit || isSaving}
            />
            <span>Mark as Absent</span>
          </label>
        </div>

        {/* Time Pairs */}
        {!timesheet.is_absent && (
          <div className="form-section">
            <label className="section-label">Clock In/Out Times</label>
            <div className="time-pairs">
              {timesheet.time_pairs.map((pair, index) => (
                <div key={index} className="time-pair">
                  <div className="time-pair-label">
                    {index === 0 ? 'Work Period' : `Break ${index}`}
                  </div>
                  <div className="time-inputs">
                    <input
                      type="time"
                      value={pair.clock_in}
                      onChange={(e) => handleTimeChange(index, 'clock_in', e.target.value)}
                      disabled={!canEdit || isSaving}
                      placeholder="Clock In"
                    />
                    <span className="time-separator">to</span>
                    <input
                      type="time"
                      value={pair.clock_out}
                      onChange={(e) => handleTimeChange(index, 'clock_out', e.target.value)}
                      disabled={!canEdit || isSaving}
                      placeholder="Clock Out"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Hours Summary */}
        {!timesheet.is_absent && totalHours > 0 && (
          <div className="hours-summary">
            <div className="hours-row">
              <span>Regular Hours:</span>
              <span>{Math.min(totalHours, 8).toFixed(2)}</span>
            </div>
            {overtimeHours > 0 && (
              <div className="hours-row overtime">
                <span>Overtime Hours:</span>
                <span>{overtimeHours.toFixed(2)}</span>
              </div>
            )}
            <div className="hours-row total">
              <span>Total Hours:</span>
              <span>{totalHours.toFixed(2)}</span>
            </div>
            <div className="pay-summary">
              <div className="pay-row">
                <span>Regular Pay:</span>
                <span>${pay.regular.toFixed(2)}</span>
              </div>
              {pay.overtime > 0 && (
                <div className="pay-row">
                  <span>Overtime Pay:</span>
                  <span>${pay.overtime.toFixed(2)}</span>
                </div>
              )}
              <div className="pay-row total">
                <span>Total Pay:</span>
                <span>${pay.total.toFixed(2)}</span>
              </div>
            </div>
          </div>
        )}

        {/* Notes */}
        <div className="form-section">
          <label className="section-label">Notes</label>
          <textarea
            value={timesheet.notes}
            onChange={(e) => handleNotesChange(e.target.value)}
            disabled={!canEdit || isSaving}
            placeholder="Add any notes about this shift..."
            rows="3"
          />
        </div>

        {/* Actions */}
        {canEdit && (
          <div className="timesheet-actions">
            <button
              onClick={onCancel}
              disabled={isSaving}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving || !isConnected}
              className="btn btn-primary"
            >
              {isSaving ? 'Saving...' : 'Save Timesheet'}
            </button>
          </div>
        )}

        {!isConnected && (
          <div className="connection-warning">
            ⚠️ Not connected to server. Changes cannot be saved.
          </div>
        )}
      </div>
    </div>
  );
};

export default TimesheetEditor;
