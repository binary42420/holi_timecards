import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSocket } from '../utils';
import TimesheetTable from './timesheet/TimesheetTable';
import ShiftDetailsHeader from './timesheet/ShiftDetailsHeader';
import TimesheetActions from './timesheet/TimesheetActions';
import './EnhancedTimesheetManager.css';

const EnhancedTimesheetManager = () => {
  const { shiftId } = useParams();
  const navigate = useNavigate();
  const { socket } = useSocket();
  
  const [shiftDetails, setShiftDetails] = useState(null);
  const [timesheetData, setTimesheetData] = useState([]);
  const [userPermissions, setUserPermissions] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [selectedWorkers, setSelectedWorkers] = useState(new Set());

  useEffect(() => {
    if (socket && socket.readyState === WebSocket.OPEN && shiftId) {
      loadTimesheetData();
    }
  }, [socket, shiftId]);

  useEffect(() => {
    if (socket) {
      const handleMessage = (event) => {
        const response = JSON.parse(event.data);
        
        if (response.request_id === 1010) { // Get shift timesheet details
          setIsLoading(false);
          if (response.success) {
            setShiftDetails(response.data.shift_details);
            setTimesheetData(response.data.timesheet_data);
            setUserPermissions(response.data.user_permissions);
            setError('');
          } else {
            setError(response.error || 'Failed to load timesheet data');
          }
        } else if (response.request_id === 1011) { // Update worker timesheet
          setIsSaving(false);
          if (response.success) {
            // Update the specific worker's data in the table
            setTimesheetData(prev => prev.map(worker => 
              worker.user_id === response.data.user_id && 
              worker.role_assigned === response.data.role_assigned
                ? { ...worker, timesheet: response.data }
                : worker
            ));
            setSuccessMessage('Timesheet updated successfully!');
            setTimeout(() => setSuccessMessage(''), 3000);
          } else {
            setError(response.error || 'Failed to update timesheet');
          }
        } else if (response.request_id === 1012) { // Submit timesheet
          setIsSaving(false);
          if (response.success) {
            loadTimesheetData(); // Reload to get updated submission status
            setSuccessMessage(response.message || 'Timesheet submitted successfully!');
            setTimeout(() => setSuccessMessage(''), 3000);
          } else {
            setError(response.error || 'Failed to submit timesheet');
          }
        } else if (response.request_id === 1013) { // Approve timesheet
          setIsSaving(false);
          if (response.success) {
            loadTimesheetData(); // Reload to get updated approval status
            setSuccessMessage(response.message || 'Timesheet approved successfully!');
            setTimeout(() => setSuccessMessage(''), 3000);
          } else {
            setError(response.error || 'Failed to approve timesheet');
          }
        }
      };

      socket.addEventListener('message', handleMessage);
      return () => socket.removeEventListener('message', handleMessage);
    }
  }, [socket]);

  const loadTimesheetData = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      setIsLoading(true);
      setError('');
      const request = {
        request_id: 1010,
        data: { shift_id: parseInt(shiftId) }
      };
      socket.send(JSON.stringify(request));
    }
  };

  const handleUpdateTimesheet = (workerUserId, roleAssigned, timePairs, notes) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError('Connection lost. Please refresh the page.');
      return;
    }

    setIsSaving(true);
    setError('');
    setSuccessMessage('');

    const request = {
      request_id: 1011,
      data: {
        shift_id: parseInt(shiftId),
        worker_user_id: workerUserId,
        role_assigned: roleAssigned,
        time_pairs: timePairs,
        notes: notes
      }
    };

    socket.send(JSON.stringify(request));
  };

  const handleSubmitTimesheet = (workerIds = []) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError('Connection lost. Please refresh the page.');
      return;
    }

    const workersToSubmit = workerIds.length > 0 ? workerIds : Array.from(selectedWorkers);
    
    if (workersToSubmit.length === 0) {
      setError('Please select workers to submit timesheet for.');
      return;
    }

    setIsSaving(true);
    setError('');
    setSuccessMessage('');

    const request = {
      request_id: 1012,
      data: {
        shift_id: parseInt(shiftId),
        worker_ids: workersToSubmit
      }
    };

    socket.send(JSON.stringify(request));
  };

  const handleApproveTimesheet = (workerIds = []) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError('Connection lost. Please refresh the page.');
      return;
    }

    const workersToApprove = workerIds.length > 0 ? workerIds : Array.from(selectedWorkers);
    
    if (workersToApprove.length === 0) {
      setError('Please select workers to approve timesheet for.');
      return;
    }

    if (!window.confirm(`Are you sure you want to approve timesheet for ${workersToApprove.length} worker(s)?`)) {
      return;
    }

    setIsSaving(true);
    setError('');
    setSuccessMessage('');

    const request = {
      request_id: 1013,
      data: {
        shift_id: parseInt(shiftId),
        worker_ids: workersToApprove
      }
    };

    socket.send(JSON.stringify(request));
  };

  const handleWorkerSelection = (workerId, isSelected) => {
    setSelectedWorkers(prev => {
      const newSet = new Set(prev);
      if (isSelected) {
        newSet.add(workerId);
      } else {
        newSet.delete(workerId);
      }
      return newSet;
    });
  };

  const handleSelectAll = (isSelected) => {
    if (isSelected) {
      setSelectedWorkers(new Set(timesheetData.map(worker => worker.user_id)));
    } else {
      setSelectedWorkers(new Set());
    }
  };

  if (isLoading) {
    return (
      <div className="timesheet-manager">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading timesheet data...</p>
        </div>
      </div>
    );
  }

  if (error && !shiftDetails) {
    return (
      <div className="timesheet-manager">
        <div className="error-container">
          <h3>Error Loading Timesheet</h3>
          <p>{error}</p>
          <button onClick={() => navigate(-1)} className="back-button">
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="timesheet-manager">
      <div className="timesheet-header">
        <button onClick={() => navigate(-1)} className="back-button">
          ← Back
        </button>
        <h1>Timesheet Management</h1>
      </div>

      {error && (
        <div className="alert alert-error">
          <span className="alert-icon">⚠️</span>
          {error}
        </div>
      )}

      {successMessage && (
        <div className="alert alert-success">
          <span className="alert-icon">✅</span>
          {successMessage}
        </div>
      )}

      {shiftDetails && (
        <ShiftDetailsHeader 
          shiftDetails={shiftDetails}
          userPermissions={userPermissions}
        />
      )}

      <TimesheetActions
        userPermissions={userPermissions}
        selectedWorkers={selectedWorkers}
        timesheetData={timesheetData}
        onSubmitTimesheet={handleSubmitTimesheet}
        onApproveTimesheet={handleApproveTimesheet}
        onSelectAll={handleSelectAll}
        isLoading={isSaving}
      />

      <TimesheetTable
        timesheetData={timesheetData}
        userPermissions={userPermissions}
        selectedWorkers={selectedWorkers}
        onUpdateTimesheet={handleUpdateTimesheet}
        onWorkerSelection={handleWorkerSelection}
        isLoading={isSaving}
      />
    </div>
  );
};

export default EnhancedTimesheetManager;
