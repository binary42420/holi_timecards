import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { useSocket } from '../utils';

const ShiftTimecard = () => {
  const { shiftId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { socket } = useSocket();
  
  const [timecardData, setTimecardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [editingNotes, setEditingNotes] = useState({});
  const [notesText, setNotesText] = useState({});

  // Get shift info from navigation state
  const shiftInfo = location.state || {};

  useEffect(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      fetchTimecardData();
    }
  }, [socket, shiftId]);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);

        if (response.request_id === 240) { // Get Shift Timecard
          if (response.success) {
            setTimecardData(response.data);
            // Initialize notes text state
            const initialNotes = {};
            response.data.workers.forEach(worker => {
              initialNotes[worker.user_id] = worker.shift_notes || '';
            });
            setNotesText(initialNotes);
          } else {
            setError(response.error || 'Failed to load timecard data');
          }
          setLoading(false);
        } else if ([241, 242, 243, 244].includes(response.request_id)) {
          // Clock in/out, absent, notes, end shift responses
          if (response.success) {
            setSuccessMessage('Action completed successfully');
            fetchTimecardData(); // Refresh data
            setTimeout(() => setSuccessMessage(''), 3000);
          } else {
            setError(response.error || 'Action failed');
            setTimeout(() => setError(''), 5000);
          }
        }
      } catch (e) {
        console.error('Error parsing WebSocket message in ShiftTimecard:', e);
        setError('Error processing server response.');
        setLoading(false);
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => {
      socket.removeEventListener('message', handleMessage);
    };
  }, [socket]);

  const fetchTimecardData = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      setLoading(true);
      const request = {
        request_id: 240,
        data: { shift_id: parseInt(shiftId) }
      };
      socket.send(JSON.stringify(request));
    }
  };

  const handleClockInOut = (userId, action) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      const request = {
        request_id: 241,
        data: {
          shift_id: parseInt(shiftId),
          user_id: userId,
          action: action
        }
      };
      socket.send(JSON.stringify(request));
    }
  };

  const handleMarkAbsent = (userId) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      const request = {
        request_id: 242,
        data: {
          shift_id: parseInt(shiftId),
          user_id: userId
        }
      };
      socket.send(JSON.stringify(request));
    }
  };

  const handleUpdateNotes = (userId) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      const request = {
        request_id: 243,
        data: {
          shift_id: parseInt(shiftId),
          user_id: userId,
          notes: notesText[userId] || ''
        }
      };
      socket.send(JSON.stringify(request));
      setEditingNotes(prev => ({ ...prev, [userId]: false }));
    }
  };

  const handleEndShift = () => {
    if (socket && socket.readyState === WebSocket.OPEN && 
        window.confirm('Are you sure you want to end this shift and clock out all workers?')) {
      const request = {
        request_id: 244,
        data: { shift_id: parseInt(shiftId) }
      };
      socket.send(JSON.stringify(request));
    }
  };

  const formatTime = (timeString) => {
    if (!timeString) return 'Not set';
    return new Date(timeString).toLocaleTimeString();
  };

  const formatDuration = (hours) => {
    if (!hours) return '0h 0m';
    const h = Math.floor(hours);
    const m = Math.round((hours - h) * 60);
    return `${h}h ${m}m`;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'clocked_in': return '#28a745';
      case 'clocked_out': return '#6c757d';
      case 'absent': return '#dc3545';
      default: return '#ffc107';
    }
  };

  const getNextAction = (status) => {
    return status === 'clocked_in' ? 'clock_out' : 'clock_in';
  };

  const getActionButtonText = (status) => {
    return status === 'clocked_in' ? 'Clock Out' : 'Clock In';
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h2>Loading Timecard...</h2>
      </div>
    );
  }

  if (!timecardData) {
    return (
      <div style={{ padding: '20px' }}>
        <h2>Shift Timecard</h2>
        <p>No timecard data available.</p>
        {error && <div style={{ color: 'red', marginTop: '10px' }}>{error}</div>}
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '30px', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
        <h2 style={{ margin: '0 0 15px 0', color: '#333' }}>Shift Timecard</h2>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px', fontSize: '14px' }}>
          <div>
            <strong>Shift ID:</strong> {shiftId}
          </div>
          <div>
            <strong>Start Time:</strong> {formatTime(timecardData.shift_info.shift_start_datetime)}
          </div>
          <div>
            <strong>End Time:</strong> {formatTime(timecardData.shift_info.shift_end_datetime)}
          </div>
        </div>
        {timecardData.shift_info.shift_description && (
          <div style={{ marginTop: '10px' }}>
            <strong>Description:</strong> {timecardData.shift_info.shift_description}
          </div>
        )}
      </div>

      {/* Messages */}
      {error && (
        <div style={{ backgroundColor: '#f8d7da', color: '#721c24', padding: '10px', borderRadius: '4px', marginBottom: '20px' }}>
          {error}
        </div>
      )}
      {successMessage && (
        <div style={{ backgroundColor: '#d4edda', color: '#155724', padding: '10px', borderRadius: '4px', marginBottom: '20px' }}>
          {successMessage}
        </div>
      )}

      {/* Action Buttons */}
      <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <button
          onClick={() => navigate(`/shift/${shiftId}/timesheet-entry`)}
          style={{
            padding: '12px 24px',
            backgroundColor: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: 'pointer'
          }}
        >
          📝 Advanced Timesheet Entry
        </button>

        <button
          onClick={handleEndShift}
          style={{
            padding: '12px 24px',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: 'pointer'
          }}
        >
          End Shift & Clock Out All
        </button>
      </div>

      {/* Workers Table */}
      <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#e9ecef' }}>
              <th style={{ padding: '15px', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>Employee</th>
              <th style={{ padding: '15px', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>Role</th>
              <th style={{ padding: '15px', textAlign: 'center', borderBottom: '2px solid #dee2e6' }}>Status</th>
              <th style={{ padding: '15px', textAlign: 'center', borderBottom: '2px solid #dee2e6' }}>Last Action</th>
              <th style={{ padding: '15px', textAlign: 'center', borderBottom: '2px solid #dee2e6' }}>Total Hours</th>
              <th style={{ padding: '15px', textAlign: 'center', borderBottom: '2px solid #dee2e6' }}>Actions</th>
              <th style={{ padding: '15px', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>Notes</th>
            </tr>
          </thead>
          <tbody>
            {timecardData.workers.map((worker, index) => (
              <tr key={worker.user_id} style={{ borderBottom: '1px solid #dee2e6', backgroundColor: index % 2 === 0 ? '#f8f9fa' : 'white' }}>
                <td style={{ padding: '15px', fontWeight: 'bold' }}>
                  {worker.user_name}
                  {worker.is_absent && <span style={{ color: '#dc3545', marginLeft: '8px' }}>(ABSENT)</span>}
                </td>
                <td style={{ padding: '15px' }}>
                  <span style={{ 
                    backgroundColor: '#007bff', 
                    color: 'white', 
                    padding: '4px 8px', 
                    borderRadius: '4px', 
                    fontSize: '12px' 
                  }}>
                    {worker.role_assigned || 'N/A'}
                  </span>
                </td>
                <td style={{ padding: '15px', textAlign: 'center' }}>
                  <span style={{
                    backgroundColor: getStatusColor(worker.current_status),
                    color: 'white',
                    padding: '6px 12px',
                    borderRadius: '20px',
                    fontSize: '12px',
                    fontWeight: 'bold'
                  }}>
                    {worker.current_status?.replace('_', ' ').toUpperCase() || 'NOT STARTED'}
                  </span>
                </td>
                <td style={{ padding: '15px', textAlign: 'center' }}>
                  {formatTime(worker.last_action_time)}
                </td>
                <td style={{ padding: '15px', textAlign: 'center', fontWeight: 'bold' }}>
                  {formatDuration(worker.total_hours_worked)}
                </td>
                <td style={{ padding: '15px', textAlign: 'center' }}>
                  <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', flexWrap: 'wrap' }}>
                    {!worker.is_absent && (
                      <button
                        onClick={() => handleClockInOut(worker.user_id, getNextAction(worker.current_status))}
                        style={{
                          padding: '6px 12px',
                          backgroundColor: worker.current_status === 'clocked_in' ? '#dc3545' : '#28a745',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          fontSize: '12px',
                          cursor: 'pointer'
                        }}
                      >
                        {getActionButtonText(worker.current_status)}
                      </button>
                    )}
                    <button
                      onClick={() => handleMarkAbsent(worker.user_id)}
                      disabled={worker.is_absent}
                      style={{
                        padding: '6px 12px',
                        backgroundColor: worker.is_absent ? '#6c757d' : '#ffc107',
                        color: worker.is_absent ? 'white' : 'black',
                        border: 'none',
                        borderRadius: '4px',
                        fontSize: '12px',
                        cursor: worker.is_absent ? 'not-allowed' : 'pointer'
                      }}
                    >
                      {worker.is_absent ? 'Absent' : 'Mark Absent'}
                    </button>
                  </div>
                </td>
                <td style={{ padding: '15px' }}>
                  {editingNotes[worker.user_id] ? (
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                      <textarea
                        value={notesText[worker.user_id] || ''}
                        onChange={(e) => setNotesText(prev => ({ ...prev, [worker.user_id]: e.target.value }))}
                        placeholder="Add notes about this employee's shift..."
                        rows="2"
                        style={{
                          flex: 1,
                          padding: '6px',
                          border: '1px solid #ddd',
                          borderRadius: '4px',
                          fontSize: '12px',
                          resize: 'vertical'
                        }}
                      />
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        <button
                          onClick={() => handleUpdateNotes(worker.user_id)}
                          style={{
                            padding: '4px 8px',
                            backgroundColor: '#28a745',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            fontSize: '10px',
                            cursor: 'pointer'
                          }}
                        >
                          Save
                        </button>
                        <button
                          onClick={() => setEditingNotes(prev => ({ ...prev, [worker.user_id]: false }))}
                          style={{
                            padding: '4px 8px',
                            backgroundColor: '#6c757d',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            fontSize: '10px',
                            cursor: 'pointer'
                          }}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ flex: 1, fontSize: '12px', color: worker.shift_notes ? '#333' : '#999' }}>
                        {worker.shift_notes || 'No notes'}
                      </span>
                      <button
                        onClick={() => setEditingNotes(prev => ({ ...prev, [worker.user_id]: true }))}
                        style={{
                          padding: '4px 8px',
                          backgroundColor: '#007bff',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          fontSize: '10px',
                          cursor: 'pointer'
                        }}
                      >
                        {worker.shift_notes ? 'Edit' : 'Add'} Notes
                      </button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {timecardData.workers.length === 0 && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
          <h3>No workers assigned to this shift</h3>
          <p>Assign workers to this shift to start tracking their time.</p>
        </div>
      )}
    </div>
  );
};

export default ShiftTimecard;
