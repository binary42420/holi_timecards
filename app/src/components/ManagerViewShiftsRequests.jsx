import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
// It's good practice to have a separate CSS file for styling
// import './ManagerViewShiftsRequests.css'; 

const ManagerViewShiftsRequests = () => {
  const { socket } = useSocket();
  const [requestsData, setRequestsData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      const request = {
        request_id: 50, // Request ID for Manager Get Employees Requests
        // data: {} // No specific data payload needed for this request based on backend
      };
      socket.send(JSON.stringify(request));
      setLoading(true);
      setError(null);

      const handleMessage = (event) => {
        try {
          const response = JSON.parse(event.data);
          // Assuming the direct response from this handler is the data or an error object
          // based on the backend structure for request_id 50 after the proposed fix.
          if (response && response.success === true && response.data) {
            setRequestsData(response.data);
          } else if (response && response.success === false) {
            setError(response.error || 'Failed to fetch employee requests.');
          } else {
            // If the response structure is different (e.g. data is directly the object without success/data wrapper)
            // This part might need adjustment based on actual server response for ID 50
            // For now, assuming the backend handler for ID 50 is fixed to return {success, data/error}
            if (typeof response === 'object' && response !== null && !response.request_id) {
                 // Fallback if server sends data directly without success wrapper for this specific ID
                 setRequestsData(response);
            } else {
                 setError('Received unexpected data format for employee requests.');
            }
          }
        } catch (e) {
          setError('Error parsing response from server.');
          console.error('Error parsing WebSocket message:', e);
        } finally {
          setLoading(false);
          // Clean up listener if it's a one-time response, or manage based on component lifecycle
          // socket.removeEventListener('message', handleMessage); 
        }
      };
      
      // It's safer to add a temporary listener that checks request_id if the socket is shared
      const specificListener = (event) => {
        const tempResponse = JSON.parse(event.data);
        if (tempResponse && tempResponse.request_id === 50) {
            handleMessage(event);
            socket.removeEventListener('message', specificListener);
        } else if (tempResponse && !tempResponse.request_id && Object.keys(tempResponse).length > 0) {
            // Heuristic: if no request_id and it's an object, assume it's the direct data for req 50
            // This is a fallback due to potential inconsistencies in backend responses
            let isLikelyReq50Data = true;
            for (const key in tempResponse) {
                if (typeof tempResponse[key] !== 'string') {
                    isLikelyReq50Data = false;
                    break;
                }
            }
            if (isLikelyReq50Data) {
                handleMessage(event); // The data is directly the requests object
                socket.removeEventListener('message', specificListener);
            }
        }
      };

      socket.addEventListener('message', specificListener);

      return () => {
        if (socket && typeof socket.removeEventListener === 'function') {
          socket.removeEventListener('message', specificListener);
        }
      };
    } else if (!socket) {
      setError('WebSocket connection not available.');
      setLoading(false);
    } else if (socket.readyState !== WebSocket.OPEN) {
      setError('WebSocket is not open. Cannot fetch requests.');
      setLoading(false);
    }
  }, [socket]);

  if (loading) {
    return <div>Loading employee requests...</div>;
  }

  if (error) {
    return <div style={{ color: 'red' }}>Error: {error}</div>;
  }

  const hasRequests = Object.keys(requestsData).length > 0;

  return (
    <div style={{ padding: '20px' }}>
      <h2>Employee Shift Requests</h2>
      {!hasRequests ? (
        <p>No shift requests found.</p>
      ) : (
        <ul style={{ listStyleType: 'none', padding: 0 }}>
          {Object.entries(requestsData).map(([employeeName, requestString]) => (
            <li key={employeeName} style={{ border: '1px solid #ddd', padding: '10px', marginBottom: '10px', borderRadius: '4px' }}>
              <strong>{employeeName}:</strong>
              <p style={{ whiteSpace: 'pre-wrap', margin: '5px 0 0 0' }}>{requestString || "No request submitted."}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ManagerViewShiftsRequests;
