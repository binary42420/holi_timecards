import React, { useState, useEffect, useCallback } from 'react';
import { useSocket } from '../utils';
// import './ManagerWorkersList.css'; // Optional: for styling

const ManagerWorkersList = () => {
  const { socket } = useSocket();
  const [workers, setWorkers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchWorkers = useCallback(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      setIsLoading(true);
      setError('');
      const request = { request_id: 94 }; // GET_ALL_APPROVED_WORKER_DETAILS
      socket.send(JSON.stringify(request));
    } else {
      setError('Cannot fetch workers: WebSocket is not connected.');
      setIsLoading(false);
    }
  }, [socket]);

  useEffect(() => {
    if (socket) {
      fetchWorkers();
    }
  }, [socket, fetchWorkers]);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        
        if (response.request_id === 94) {
          setIsLoading(false);
          if (response.success && Array.isArray(response.data)) {
            setWorkers(response.data);
          } else {
            setError(response.error || 'Failed to fetch workers list.');
            setWorkers([]);
          }
        }
      } catch (e) {
        setIsLoading(false);
        setError('Error processing server response for workers list.');
        console.error('WebSocket message error in ManagerWorkersList:', e);
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => {
      socket.removeEventListener('message', handleMessage);
    };
  }, [socket]);

  if (isLoading) {
    return <div style={{ padding: '20px' }}>Loading workers list...</div>;
  }

  if (error) {
    return <div style={{ padding: '20px', color: 'red' }}>Error: {error}</div>;
  }

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h2>Managed Workers</h2>
      {workers.length === 0 ? (
        <p>No workers found or associated with your workplace.</p>
      ) : (
        <ul style={{ listStyleType: 'none', padding: 0 }}>
          {workers.map((worker) => (
            <li key={worker.id} style={{ border: '1px solid #eee', padding: '15px', marginBottom: '10px', borderRadius: '4px', backgroundColor: '#fff' }}>
              <h4>{worker.name} (ID: {worker.id})</h4>
              <p>Role: {worker.employee_type ? worker.employee_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'N/A'}</p>
              {/* Add more worker details or actions here if needed */}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ManagerWorkersList;
