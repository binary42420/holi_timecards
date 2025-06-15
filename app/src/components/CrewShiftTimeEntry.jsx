import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { useSocket } from '../utils';
import '../css/CrewShiftTimeEntry.css';

const CrewShiftTimeEntry = () => {
  const { shiftId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { socket } = useSocket();

  const [shiftDetails, setShiftDetails] = useState(location.state?.shiftDetails || null);
  const [crewMembers, setCrewMembers] = useState([]);
  const [workerTimes, setWorkerTimes] = useState({}); // Stores { userId_role: { clock_in_time, clock_out_time } }
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  useEffect(() => {
    if (!socket) {
      setError('WebSocket connection not available.');
      setLoading(false);
      return;
    }

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        if (response.request_id === 101 && response.data) {
          if (response.success) {
            setCrewMembers(response.data);
            const initialTimes = {};
            response.data.forEach(member => {
              const key = `${member.user_id}_${member.role_assigned}`;
              initialTimes[key] = {
                clock_in_time: member.clock_in_time ? member.clock_in_time.substring(0, 16) : '',
                clock_out_time: member.clock_out_time ? member.clock_out_time.substring(0, 16) : '',
                role_assigned: member.role_assigned,
                times_submitted_at: member.times_submitted_at
              };
            });
            setWorkerTimes(initialTimes);
          } else {
            setError(response.error || 'Failed to fetch crew members.');
          }
          setLoading(false);
        } else if (response.request_id === 102) {
          if (response.success) {
            setSuccessMessage(response.message || 'Times submitted successfully!');
            setError(null);
            const updatedCrewMembers = crewMembers.map(cm => ({
                ...cm,
                times_submitted_at: new Date().toISOString()
            }));
            setCrewMembers(updatedCrewMembers);
            const newWorkerTimes = { ...workerTimes };
            Object.keys(newWorkerTimes).forEach(key => {
                if (response.data?.updated_workers?.find(w => `${w.user_id}_${w.role_assigned}` === key)) { // Check if this worker was part of the successful submission
                    newWorkerTimes[key].times_submitted_at = new Date().toISOString();
                }
            });
            setWorkerTimes(newWorkerTimes);
          } else {
            setError(response.error || 'Failed to submit times.');
            setSuccessMessage(null);
          }
        }
      } catch (e) {
        console.error('Error parsing WebSocket message:', e);
        setError('Error processing response from server.');
        setLoading(false);
      }
    };

    socket.addEventListener('message', handleMessage);

    if (socket.readyState === WebSocket.OPEN) {
      const request = {
        request_id: 101,
        data: { shift_id: parseInt(shiftId) }
      };
      socket.send(JSON.stringify(request));
    } else {
        const timeoutId = setTimeout(() => {
            if (socket && socket.readyState === WebSocket.OPEN) {
                const request = {
                    request_id: 101,
                    data: { shift_id: parseInt(shiftId) }
                };
                socket.send(JSON.stringify(request));
            } else {
                setError('WebSocket is not open. Cannot fetch crew members.');
                setLoading(false);
            }
        }, 1000);
        return () => clearTimeout(timeoutId);
    }

    return () => {
      if (socket && typeof socket.removeEventListener === 'function') {
        socket.removeEventListener('message', handleMessage);
      }
    };
  }, [socket, shiftId]);

  const handleTimeChange = (userId, role, field, value) => {
    const key = `${userId}_${role}`;
    setWorkerTimes(prev => ({
      ...prev,
      [key]: {
        ...prev[key],
        [field]: value,
        role_assigned: role
      }
    }));
  };

  const handleSubmitTimes = () => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError('WebSocket is not open. Cannot submit times.');
      return;
    }
    setError(null);
    setSuccessMessage(null);

    const payloadWorkerTimes = Object.entries(workerTimes)
      .filter(([key, times]) => !times.times_submitted_at)
      .map(([key, times]) => {
        const [userId] = key.split('_');
        return {
          user_id: parseInt(userId),
          role_assigned: times.role_assigned,
          clock_in_time: times.clock_in_time ? new Date(times.clock_in_time).toISOString() : null,
          clock_out_time: times.clock_out_time ? new Date(times.clock_out_time).toISOString() : null,
        };
      });
    
    if (payloadWorkerTimes.length === 0) {
        setSuccessMessage("All times already submitted or no changes to submit.");
        return;
    }

    const request = {
      request_id: 102,
      data: {
        shift_id: parseInt(shiftId),
        worker_times: payloadWorkerTimes
      }
    };
    socket.send(JSON.stringify(request));
  };

  if (loading) {
    return <div className="crew-time-entry-loading">Loading crew members...</div>;
  }

  return (
    <div className="crew-time-entry-container">
      <button onClick={() => navigate(-1)} className="back-button">Back to Dashboard</button>
      <h2>Time Entry for Shift</h2>
      {shiftDetails && (
        <div className="shift-info-header">
          <p><strong>Date:</strong> {new Date(shiftDetails.shift_date).toLocaleDateString()}</p>
          <p><strong>Part:</strong> {shiftDetails.shift_part}</p>
          <p><strong>Job:</strong> {shiftDetails.job_name}</p>
          <p><strong>Client:</strong> {shiftDetails.client_company_name}</p>
        </div>
      )}
      {error && <div className="error-message">{error}</div>}
      {successMessage && <div className="success-message">{successMessage}</div>}
      {crewMembers.length === 0 && !loading && !error && <p>No crew members found for this shift.</p>}
      {crewMembers.length > 0 && (
        <div className="crew-times-form">
          <div className="form-actions">
            <button
              type="button"
              onClick={handleSubmitTimes}
              className="submit-times-button"
              disabled={Object.values(workerTimes).every(times => times.times_submitted_at)}
            >
              Submit All Times
            </button>
          </div>
          <table className="crew-times-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Role</th>
                <th>Clock In</th>
                <th>Clock Out</th>
                <th>Hours</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {crewMembers.map(member => {
                const key = `${member.user_id}_${member.role_assigned}`;
                const times = workerTimes[key] || { clock_in_time: '', clock_out_time: '', role_assigned: member.role_assigned, times_submitted_at: null };
                const isSubmitted = !!times.times_submitted_at;

                // Calculate hours worked
                let hoursWorked = '';
                if (times.clock_in_time && times.clock_out_time) {
                  const clockIn = new Date(times.clock_in_time);
                  const clockOut = new Date(times.clock_out_time);
                  const diffMs = clockOut - clockIn;
                  const diffHours = diffMs / (1000 * 60 * 60);
                  hoursWorked = diffHours > 0 ? `${diffHours.toFixed(2)}h` : 'Invalid';
                }

                return (
                  <tr key={key} className={isSubmitted ? 'submitted-row' : ''}>
                    <td className="name-cell">{member.name}</td>
                    <td className="role-cell">{member.role_assigned}</td>
                    <td>
                      <input
                        type="datetime-local"
                        value={times.clock_in_time}
                        onChange={(e) => handleTimeChange(member.user_id, member.role_assigned, 'clock_in_time', e.target.value)}
                        disabled={isSubmitted}
                        className={isSubmitted ? 'disabled-input' : ''}
                      />
                    </td>
                    <td>
                      <input
                        type="datetime-local"
                        value={times.clock_out_time}
                        onChange={(e) => handleTimeChange(member.user_id, member.role_assigned, 'clock_out_time', e.target.value)}
                        disabled={isSubmitted}
                        className={isSubmitted ? 'disabled-input' : ''}
                      />
                    </td>
                    <td className="hours-cell">{hoursWorked}</td>
                    <td className="status-cell">
                      {isSubmitted ? (
                        <span className="status-submitted">
                          ✓ Submitted<br/>
                          <small>{new Date(times.times_submitted_at).toLocaleString()}</small>
                        </span>
                      ) : (
                        <span className="status-pending">⏳ Pending</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default CrewShiftTimeEntry;
