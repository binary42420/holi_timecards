import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useLocation, useNavigate, Link } from 'react-router-dom';
import { useSocket, logDebug, logError, logWarning, logInfo } from '../utils';
import { useWebSocketAuth } from '../hooks/useWebSocketAuth';
import { createAuthenticatedRequest } from '../utils/sessionUtils';
import ShiftAssignmentRow from './ShiftAssignmentRow';
import RoleRequirementBuilder from './RoleRequirementBuilder';
import ShiftRequirementsEditor from './ShiftRequirementsEditor';
import './ManagerShiftEditor.css';

// Helper to get EmployeeType values - in a real app, this might come from an API or a shared constant
const employeeTypes = [
  { value: 'crew_chief', label: 'Crew Chief' },
  { value: 'stagehand', label: 'Stagehand' },
  { value: 'fork_operator', label: 'Fork Operator' },
  { value: 'pickup_truck_driver', label: 'Pickup Truck Driver' },
  { value: 'general_employee', label: 'General Employee' },
];

const ManagerShiftEditor = () => {
  logDebug('ManagerShiftEditor', 'Component rendering', { jobId: useParams().jobId });

  const { jobId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { socket, connectionStatus, isConnected, hasError, lastError } = useSocket();
  const { isAuthenticated, authError, isAuthenticating, retryAuthentication } = useWebSocketAuth(socket);

  const jobName = location.state?.jobName;
  const clientCompanyId = location.state?.clientCompanyId;
  const clientCompanyName = location.state?.clientCompanyName;

  const [shifts, setShifts] = useState([]);
  const [availableWorkers, setAvailableWorkers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showRequirementsEditor, setShowRequirementsEditor] = useState(false);
  const [selectedShiftForEdit, setSelectedShiftForEdit] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [retryCount, setRetryCount] = useState(0);
  const [lastFetchTime, setLastFetchTime] = useState(null);

  // Form state for new shift
  const [newShiftStartDateTime, setNewShiftStartDateTime] = useState('');
  const [newShiftEndDateTime, setNewShiftEndDateTime] = useState('');
  const [newClientPoNumber, setNewClientPoNumber] = useState('');
  const [newRequiredCounts, setNewRequiredCounts] = useState(
    employeeTypes.reduce((acc, type) => ({ ...acc, [type.value]: 0 }), {})
  );

  const fetchAvailableWorkers = useCallback(() => {
    if (socket && socket.readyState === WebSocket.OPEN && isAuthenticated) {
      logDebug('ManagerShiftEditor', 'Fetching available workers');
      const request = createAuthenticatedRequest(94); // GET_ALL_APPROVED_WORKER_DETAILS
      socket.send(JSON.stringify(request));
    } else {
      logWarning('ManagerShiftEditor', 'Cannot fetch workers - not authenticated', {
        socketReady: socket?.readyState === WebSocket.OPEN,
        isAuthenticated
      });
    }
  }, [socket, isAuthenticated]);

  const fetchShiftsForJob = useCallback(() => {
    try {
      logDebug('ManagerShiftEditor', 'fetchShiftsForJob called', {
        jobId,
        socketState: socket?.readyState,
        connectionStatus
      });

      if (!jobId) {
        const errorMsg = 'Job ID is missing';
        logError('ManagerShiftEditor', errorMsg);
        setError(errorMsg);
        return;
      }

      if (!socket) {
        const errorMsg = 'WebSocket not available';
        logError('ManagerShiftEditor', errorMsg);
        setError(errorMsg);
        return;
      }

      if (socket.readyState !== WebSocket.OPEN) {
        const errorMsg = `WebSocket not connected (state: ${socket.readyState})`;
        logWarning('ManagerShiftEditor', errorMsg);
        setError('Connection not ready. Please wait or try refreshing.');
        return;
      }

      if (!isAuthenticated) {
        if (isAuthenticating) {
          logDebug('ManagerShiftEditor', 'Authentication in progress, waiting...');
          setError('Authenticating...');
          return;
        } else {
          const errorMsg = 'WebSocket not authenticated. Please log in again.';
          logWarning('ManagerShiftEditor', errorMsg);
          setError(errorMsg);
          return;
        }
      }

      setIsLoading(true);
      setError('');
      setLastFetchTime(new Date().toISOString());

      const request = createAuthenticatedRequest(221, { job_id: parseInt(jobId, 10) }); // GET_SHIFTS_BY_JOB

      logDebug('ManagerShiftEditor', 'Sending shifts request', request);
      socket.send(JSON.stringify(request));

      // Set timeout for request using a ref to track current loading state
      const timeoutId = setTimeout(() => {
        setIsLoading(prevLoading => {
          if (prevLoading) {
            logWarning('ManagerShiftEditor', 'Shifts request timeout');
            setError('Request timed out. Please try again.');
            return false;
          }
          return prevLoading;
        });
      }, 10000);

      // Store timeout ID for cleanup if needed
      return timeoutId;

    } catch (error) {
      logError('ManagerShiftEditor', 'Error in fetchShiftsForJob', error);
      setIsLoading(false);
      setError(`Failed to fetch shifts: ${error.message}`);
    }
  }, [socket, jobId, connectionStatus, isAuthenticated, isAuthenticating]); // Added auth dependencies

  // Initial load effect
  useEffect(() => {
    if (!jobName || !jobId) {
      logWarning('ManagerShiftEditor', 'Job details not found');
      setError('Job details are missing. Please navigate from the Job Management page.');
      return;
    }

    // Only fetch if we have a valid connection and are authenticated
    if (socket && socket.readyState === WebSocket.OPEN && isAuthenticated) {
      logDebug('ManagerShiftEditor', 'Initial data fetch - authenticated and connected');
      fetchShiftsForJob();
      fetchAvailableWorkers();
    }
  }, [jobId, jobName, socket, isAuthenticated]); // Added socket and auth dependencies

  // Connection status effect
  useEffect(() => {
    if (jobId && jobName && socket && socket.readyState === WebSocket.OPEN && isAuthenticated && shifts.length === 0 && !isLoading) {
      // Fetch data when connection becomes available and we don't have data yet
      logDebug('ManagerShiftEditor', 'Connection available and authenticated, fetching data');
      fetchShiftsForJob();
      fetchAvailableWorkers();
    }
  }, [socket, connectionStatus, isConnected, isAuthenticated]); // React to connection and auth changes

  // Add retry functionality
  const handleRetry = useCallback(() => {
    if (retryCount < 3) {
      logInfo('ManagerShiftEditor', 'Retrying data fetch', { attempt: retryCount + 1 });
      setRetryCount(prev => prev + 1);
      setError('');
      fetchShiftsForJob();
      fetchAvailableWorkers();
    } else {
      logError('ManagerShiftEditor', 'Maximum retry attempts reached');
      setError('Maximum retry attempts reached. Please refresh the page.');
    }
  }, [retryCount, fetchShiftsForJob, fetchAvailableWorkers]);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);

        logDebug('ManagerShiftEditor', 'Received WebSocket message', {
          request_id: response.request_id,
          success: response.success
        });

        if (response.request_id === 221) { // Get Shifts by Job
          setIsLoading(false);
          if (response.success && Array.isArray(response.data)) {
            logInfo('ManagerShiftEditor', 'Shifts loaded successfully', { count: response.data.length });
            setShifts(response.data);
            setError(''); // Clear any previous errors
          } else {
            logError('ManagerShiftEditor', 'Failed to fetch shifts', response.error);
            setError(response.error || 'Failed to fetch shifts for this job.');
            setShifts([]);
          }
        } else if (response.request_id === 220) { // Create Shift
          if (response.success && response.data) {
            setSuccessMessage(`Shift created successfully!`);
            // Sort by start datetime or fallback to legacy date/part
            setShifts(prevShifts => [...prevShifts, response.data].sort((a, b) => {
              const aDateTime = a.shift_start_datetime || `${a.shiftDate}T00:00:00`;
              const bDateTime = b.shift_start_datetime || `${b.shiftDate}T00:00:00`;
              return new Date(aDateTime) - new Date(bDateTime);
            }));
            // Reset form
            setNewShiftStartDateTime('');
            setNewShiftEndDateTime('');
            setNewClientPoNumber('');
            setNewRequiredCounts(employeeTypes.reduce((acc, type) => ({ ...acc, [type.value]: 0 }), {}));
            setError('');
          } else {
            setSuccessMessage('');
            setError(response.error || 'Failed to create shift.');
          }
        } else if (response.request_id === 94) { // Get All Approved Worker Details
          if (response.success && Array.isArray(response.data)) {
            setAvailableWorkers(response.data);
          } else {
            setError(response.error || 'Failed to fetch available workers.');
            setAvailableWorkers([]); // Ensure it's an array in case of error
          }
        } else if (response.request_id === 230) { // Assign Worker to Shift
          if (response.success && response.data) {
            const { shiftID, userID, role_assigned } = response.data;
            const workerAssigned = availableWorkers.find(w => w.id === userID);
            if (workerAssigned) {
              setShifts(prevShifts => prevShifts.map(shift => {
                if (shift.id === shiftID) {
                  // Add new worker if not already present (shouldn't be, but good practice)
                  const existingWorkerIndex = shift.workers.findIndex(w => w.id === userID && w.role_assigned === role_assigned);
                  if (existingWorkerIndex === -1) {
                    return {
                      ...shift,
                      workers: [...shift.workers, { id: userID, name: workerAssigned.name, role_assigned }]
                    };
                  }
                }
                return shift;
              }));
              setSuccessMessage(`Worker ${workerAssigned.name} assigned to ${role_assigned.replace('_', ' ')}.`);
            } else {
              // Worker details not found in availableWorkers, might need a refresh or handle error
              setError('Assigned worker details not found, refreshing shifts might be needed.');
              fetchShiftsForJob(); // Optionally refresh all shifts for the job
            }
          } else {
            setError(response.error || 'Failed to assign worker.');
          }
        } else if (response.request_id === 231) { // Unassign Worker from Shift
          if (response.success) {
            // We need to know which shift_id, user_id, and role were involved.
            // This info is not in the success response, so we rely on the UI action's context.
            // For now, we'll assume the success message is enough and a full re-fetch might be simplest
            // or the component initiating the unassign action can provide context for a more targeted update.
            setSuccessMessage(response.message || 'Worker unassigned successfully.');
            // Re-fetch shifts to reflect the unassignment accurately
            if (socket && socket.readyState === WebSocket.OPEN && jobId) {
              const request = createAuthenticatedRequest(221, { job_id: parseInt(jobId, 10) }); // GET_SHIFTS_BY_JOB
              socket.send(JSON.stringify(request));
            }
          } else {
            setError(response.error || 'Failed to unassign worker.');
          }
        } else if (response.request_id === 232) { // Update Shift Requirements
          if (response.success && response.data) {
            // Update the specific shift with new requirements
            setShifts(prevShifts => prevShifts.map(shift => {
              if (shift.id === response.data.shift_id) {
                return {
                  ...shift,
                  required_employee_counts: response.data.required_employee_counts
                };
              }
              return shift;
            }));
            setSuccessMessage('Shift requirements updated successfully!');
            setShowRequirementsEditor(false);
            setSelectedShiftForEdit(null);
          } else {
            setError(response.error || 'Failed to update shift requirements.');
          }
        }
      } catch (e) {
        setIsLoading(false);
        setError('Error processing server response for shifts.');
        console.error('WebSocket message error in ManagerShiftEditor:', e);
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => {
      socket.removeEventListener('message', handleMessage);
    };
  }, [socket]);

  const handleRequiredCountChange = (role, value) => {
    const count = parseInt(value, 10);
    setNewRequiredCounts(prev => ({
      ...prev,
      [role]: Math.max(0, count || 0) // Ensure count is not negative
    }));
  };

  const handleCreateShiftSubmit = (e) => {
    e.preventDefault();
    if (!newShiftStartDateTime) {
      setError('Shift start date and time are required.');
      return;
    }

    // Validate end time is after start time if provided
    if (newShiftEndDateTime && new Date(newShiftEndDateTime) <= new Date(newShiftStartDateTime)) {
      setError('End time must be after start time.');
      return;
    }

    if (socket && socket.readyState === WebSocket.OPEN && isAuthenticated && jobId) {
      setIsLoading(true);
      setError('');
      setSuccessMessage('');

      const requestData = {
        job_id: parseInt(jobId, 10),
        shift_start_datetime: newShiftStartDateTime,
        client_po_number: newClientPoNumber,
        required_employee_counts: newRequiredCounts,
      };

      // Add end datetime if provided
      if (newShiftEndDateTime) {
        requestData.shift_end_datetime = newShiftEndDateTime;
      }

      const request = createAuthenticatedRequest(220, requestData); // CREATE_SHIFT
      socket.send(JSON.stringify(request));
    } else {
      if (!isAuthenticated) {
        setError('Not authenticated. Please wait for authentication to complete.');
      } else {
        setError('WebSocket is not connected or Job ID is missing.');
      }
    }
  };

  const handleAssignWorkerToShiftSlot = (shiftId, userId, role) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      setIsLoading(true); // Consider a more granular loading state if needed
      const request = createAuthenticatedRequest(230, {
        shift_id: shiftId,
        user_id: userId,
        role_assigned: role, // role is the key like 'crew_chief'
      }); // ASSIGN_WORKER_TO_SHIFT
      socket.send(JSON.stringify(request));
    } else {
      setError('WebSocket is not connected.');
    }
  };

  const handleUnassignWorkerFromShiftSlot = (shiftId, userId, role) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      setIsLoading(true);
      const request = createAuthenticatedRequest(231, {
        shift_id: shiftId,
        user_id: userId,
        role_assigned: role,
      }); // UNASSIGN_WORKER_FROM_SHIFT
      socket.send(JSON.stringify(request));
    } else {
      setError('WebSocket is not connected.');
    }
  };
  
  if (!jobName || !jobId) {
    return <div style={{ padding: '20px', color: 'red' }}>Error: Job details not available. Please return to the job management page.</div>;
  }

  return (
    <div className="manager-shift-editor">
      <button onClick={() => navigate('/manager-jobs')} className="back-button">
        &larr; Back to Jobs
      </button>

      <div className="page-header">
        <h2 className="page-title">Manage Shifts for Job: {jobName || `ID ${jobId}`}</h2>
        {clientCompanyName && <p className="client-info">Client: {clientCompanyName}</p>}
      </div>

      {/* Connection and authentication status indicators */}
      {!isConnected && (
        <div className="alert alert-warning">
          <span>🔌</span>
          Connection status: {connectionStatus}
          {connectionStatus === 'reconnecting' && <span>...</span>}
        </div>
      )}

      {isConnected && !isAuthenticated && !authError && (
        <div className="alert alert-warning">
          <span>🔐</span>
          {isAuthenticating ? 'Authenticating...' : 'Authentication required'}
          {isAuthenticating && <span>...</span>}
        </div>
      )}

      {(error || authError) && (
        <div className="alert alert-error">
          Error: {authError || error}
          {retryCount < 3 && !authError && (
            <button
              onClick={handleRetry}
              style={{ marginLeft: '10px', padding: '5px 10px', fontSize: '12px' }}
            >
              Retry ({retryCount}/3)
            </button>
          )}
          {authError && (
            <div style={{ marginTop: '5px', fontSize: '12px' }}>
              Authentication failed: {authError}
              <button
                onClick={retryAuthentication}
                style={{ marginLeft: '10px', padding: '5px 10px', fontSize: '12px' }}
                disabled={isAuthenticating}
              >
                {isAuthenticating ? 'Retrying...' : 'Retry Auth'}
              </button>
            </div>
          )}
        </div>
      )}
      {successMessage && <div className="alert alert-success">{successMessage}</div>}

      <div className="create-shift-section">
        <h3 className="section-title">Create New Shift</h3>
        <form onSubmit={handleCreateShiftSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="newShiftStartDateTime" className="form-label">Shift Start Date & Time:</label>
              <input
                type="datetime-local"
                id="newShiftStartDateTime"
                value={newShiftStartDateTime}
                onChange={(e) => setNewShiftStartDateTime(e.target.value)}
                required
                className="form-input"
                min={new Date().toISOString().slice(0, 16)} // Prevent past dates
              />
            </div>
            <div className="form-group">
              <label htmlFor="newShiftEndDateTime" className="form-label">Shift End Date & Time (Optional):</label>
              <input
                type="datetime-local"
                id="newShiftEndDateTime"
                value={newShiftEndDateTime}
                onChange={(e) => setNewShiftEndDateTime(e.target.value)}
                className="form-input"
                min={newShiftStartDateTime || new Date().toISOString().slice(0, 16)}
              />
            </div>
            <div className="form-group form-group-full">
              <label htmlFor="newClientPoNumber" className="form-label">Client PO # (Optional):</label>
              <input
                type="text"
                id="newClientPoNumber"
                value={newClientPoNumber}
                onChange={(e) => setNewClientPoNumber(e.target.value)}
                className="form-input"
              />
            </div>
          </div>
          
          <RoleRequirementBuilder
            requiredCounts={newRequiredCounts}
            onCountChange={handleRequiredCountChange}
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading} className="submit-button">
            {isLoading ? 'Creating Shift...' : 'Create Shift'}
          </button>
        </form>
      </div>

      <div className="shifts-section">
        <h3 className="section-title">Existing Shifts for this Job</h3>
        {isLoading && shifts.length === 0 && <p className="loading-message">Loading shifts...</p>}
        {!isLoading && shifts.length === 0 && !error && <p className="empty-message">No shifts found for this job. Create one above!</p>}
      {shifts.length > 0 && (
        <ul className="shifts-list">
          {shifts.map((shift) => (
            <li key={shift.id} className="shift-card">
              <div className="shift-header">
                <div className="shift-info">
                  <h4 className="shift-date">
                    {shift.shift_start_datetime ? (
                      <>
                        {new Date(shift.shift_start_datetime).toLocaleString()}
                        {shift.shift_end_datetime && (
                          <span> - {new Date(shift.shift_end_datetime).toLocaleString()}</span>
                        )}
                      </>
                    ) : (
                      // Fallback to legacy format
                      `${new Date(shift.shiftDate).toLocaleDateString()} - ${shift.shiftPart}`
                    )}
                  </h4>
                  {shift.client_po_number && (
                    <p className="shift-details">Client PO #: {shift.client_po_number}</p>
                  )}
                </div>
                <div className="shift-actions">
                  <button
                    onClick={() => {
                      setSelectedShiftForEdit(shift);
                      setShowRequirementsEditor(true);
                    }}
                    className="edit-requirements-btn"
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#6c757d',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      fontSize: '14px',
                      fontWeight: 'bold',
                      marginRight: '10px',
                      cursor: 'pointer'
                    }}
                    title="Edit Worker Requirements"
                  >
                    ⚙️ Edit Requirements
                  </button>
                  <Link
                    to={`/shift/${shift.id}/timecard`}
                    className="timecard-link"
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#28a745',
                      color: 'white',
                      textDecoration: 'none',
                      borderRadius: '4px',
                      fontSize: '14px',
                      fontWeight: 'bold',
                      marginRight: '10px'
                    }}
                  >
                    🕐 Shift Timecard
                  </Link>
                  <Link
                    to={`/timesheet/${shift.id}`}
                    className="timesheet-link"
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#007bff',
                      color: 'white',
                      textDecoration: 'none',
                      borderRadius: '4px',
                      fontSize: '14px',
                      fontWeight: 'bold'
                    }}
                  >
                    📋 Manage Timesheet
                  </Link>
                </div>
              </div>

              <div className="required-counts">
                <h5>Required Workers:</h5>
                <ul className="counts-list">
                  {Object.entries(shift.required_employee_counts || {}).map(([role, count]) =>
                    count > 0 && (
                      <li key={role} className="count-item">
                        {role.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}: {count}
                      </li>
                    )
                  )}
                </ul>
              </div>

              <div className="assignments-section">
                <h5 className="assignments-title">Worker Assignments:</h5>
              {/* Render ShiftAssignmentRow for each role based on required_employee_counts */}
              {Object.entries(shift.required_employee_counts || {}).map(([roleKey, requiredCount]) => {
                if (requiredCount === 0 && !(shift.workers || []).some(w => w.role_assigned === roleKey)) {
                  return null; // Don't render if 0 required and no one assigned to this role
                }
                const currentRoleLabel = employeeTypes.find(et => et.value === roleKey)?.label || roleKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
                const workersForThisRole = (shift.workers || []).filter(worker => worker.role_assigned === roleKey);
                return (
                  <ShiftAssignmentRow
                    key={`${shift.id}-${roleKey}`}
                    shiftId={shift.id}
                    role={roleKey}
                    roleLabel={currentRoleLabel}
                    requiredCount={requiredCount}
                    assignedWorkers={workersForThisRole}
                    availableWorkers={availableWorkers}
                    onAssignWorker={handleAssignWorkerToShiftSlot}
                    onUnassignWorker={handleUnassignWorkerFromShiftSlot}
                    isLoading={isLoading} // Or a more specific loading state for assignments
                  />
                );
              })}
                {/* Fallback for shifts that might have assigned workers but no corresponding required_employee_counts entry (less ideal) */}
                {(shift.workers || []).filter(w => !(shift.required_employee_counts || {}).hasOwnProperty(w.role_assigned)).map(worker => (
                   <div key={`${shift.id}-${worker.id}-${worker.role_assigned}-adhoc`} className="adhoc-assignment">
                      * Assigned (adhoc): {worker.name} as {worker.role_assigned.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      <button onClick={() => handleUnassignWorkerFromShiftSlot(shift.id, worker.id, worker.role_assigned)} className="unassign-btn">
                        Unassign
                      </button>
                   </div>
                ))}
              </div>
            </li>
          ))}
        </ul>
      )}
      </div>

      {/* Shift Requirements Editor Modal */}
      {showRequirementsEditor && selectedShiftForEdit && (
        <ShiftRequirementsEditor
          shift={selectedShiftForEdit}
          onUpdate={(updatedData) => {
            // The WebSocket handler will update the shifts state
            setSuccessMessage('Shift requirements updated successfully!');
          }}
          onClose={() => {
            setShowRequirementsEditor(false);
            setSelectedShiftForEdit(null);
          }}
          isModal={true}
        />
      )}
    </div>
  );
};

export default ManagerShiftEditor;
