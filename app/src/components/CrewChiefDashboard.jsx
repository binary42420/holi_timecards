import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSocket } from '../utils';
import '../css/CrewChiefDashboard.css';

const CrewChiefDashboard = () => {
  const navigate = useNavigate();
  const { socket } = useSocket();
  const [supervisedShifts, setSupervisedShifts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      const request = {
        request_id: 100, // Request ID for fetching crew chief's supervised shifts
      };
      socket.send(JSON.stringify(request));
      setLoading(true);
      setError(null);

      const handleMessage = (event) => {
        try {
          const response = JSON.parse(event.data);
          if (response && response.request_id === 100) {
            if (response.success && response.data) {
              setSupervisedShifts(response.data);
            } else {
              setError(response.error || 'Failed to fetch supervised shifts.');
            }
            setLoading(false);
            if (socket && typeof socket.removeEventListener === 'function') {
              socket.removeEventListener('message', handleMessage);
            }
          }
        } catch (e) {
          setError('Error parsing response from server.');
          setLoading(false);
          console.error('Error parsing WebSocket message:', e);
          if (socket && typeof socket.removeEventListener === 'function') {
            socket.removeEventListener('message', handleMessage);
          }
        }
      };

      socket.addEventListener('message', handleMessage);

      return () => {
        if (socket && typeof socket.removeEventListener === 'function') {
          socket.removeEventListener('message', handleMessage);
        }
      };
    } else if (socket && socket.readyState !== WebSocket.OPEN) {
        setError('WebSocket connection is not open. Please try again later.');
        setLoading(false);
    } else if (!socket) {
        setError('WebSocket connection not available.');
        setLoading(false);
    }
  }, [socket]);

  if (loading) {
    return <div className="crew-chief-dashboard-loading">Loading supervised shifts...</div>;
  }

  if (error) {
    return <div className="crew-chief-dashboard-error">Error: {error}</div>;
  }

  return (
    <div className="crew-chief-dashboard-container">
      <h2>Supervised Shifts</h2>
      {supervisedShifts.length === 0 ? (
        <p>No supervised shifts found.</p>
      ) : (
        <table className="shifts-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Shift Part</th>
              <th>Job Name</th>
              <th>Client Company</th>
            </tr>
          </thead>
          <tbody>
            {supervisedShifts.map((shift) => (
              <tr
                key={shift.shift_id}
                className="clickable-row"
                onClick={() => navigate(`/timesheet/${shift.shift_id}`, { state: { shiftDetails: shift } })}
              >
                <td>{new Date(shift.shift_date).toLocaleDateString()}</td>
                <td>{shift.shift_part}</td>
                <td>{shift.job_name}</td>
                <td>{shift.client_company_name}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default CrewChiefDashboard;
