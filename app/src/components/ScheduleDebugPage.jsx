import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
import { createAuthenticatedRequest, getSessionData, hasValidSession } from '../utils/sessionUtils';

const ScheduleDebugPage = () => {
  const { socket, connectionStatus } = useSocket();
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState('');
  const [requestSent, setRequestSent] = useState(false);
  const [basicResponse, setBasicResponse] = useState(null);
  const [basicLoading, setBasicLoading] = useState(false);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Received WebSocket message:', data);
        
        if (data.request_id === 2001) {
          setLoading(false);
          setResponse(data);
          if (!data.success) {
            setError(data.error || 'Unknown error');
          }
        } else if (data.request_id === 90) {
          setBasicLoading(false);
          setBasicResponse(data);
        }
      } catch (e) {
        console.error('Error parsing WebSocket message:', e);
        setError('Error parsing server response');
        setLoading(false);
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => socket.removeEventListener('message', handleMessage);
  }, [socket]);

  const testScheduleRequest = () => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError('WebSocket not connected');
      return;
    }

    setLoading(true);
    setError('');
    setResponse(null);
    setRequestSent(true);

    const now = new Date();
    const startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 7);
    const endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 7);

    const request = createAuthenticatedRequest(2001, {
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString(),
      view_type: 'week',
      include_workers: true,
      include_jobs: true,
      include_clients: true,
      filters: {}
    });

    console.log('Sending schedule request:', request);
    socket.send(JSON.stringify(request));
  };

  const testBasicRequest = () => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError('WebSocket not connected');
      return;
    }

    setBasicLoading(true);
    setBasicResponse(null);

    const request = {
      request_id: 90
    };

    console.log('Sending basic request (ID 90):', request);
    socket.send(JSON.stringify(request));
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Schedule Debug Page</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <h3>Connection Status: {connectionStatus}</h3>
        <p>Socket Ready State: {socket ? socket.readyState : 'No socket'}</p>
        <p>Socket URL: {socket ? socket.url : 'No socket'}</p>
        <p>Has Valid Session: {hasValidSession() ? '✅ Yes' : '❌ No'}</p>
        <p>Session Data: {getSessionData() ? 'Available' : 'Not available'}</p>
      </div>

      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <button
          onClick={testBasicRequest}
          disabled={basicLoading || !socket || socket.readyState !== WebSocket.OPEN}
          style={{
            padding: '10px 20px',
            backgroundColor: basicLoading ? '#ccc' : '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: basicLoading ? 'not-allowed' : 'pointer'
          }}
        >
          {basicLoading ? 'Loading...' : 'Test Basic Request (ID: 90)'}
        </button>

        <button
          onClick={testScheduleRequest}
          disabled={loading || !socket || socket.readyState !== WebSocket.OPEN}
          style={{
            padding: '10px 20px',
            backgroundColor: loading ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Loading...' : 'Test Schedule Request (ID: 2001)'}
        </button>
      </div>

      {requestSent && (
        <div style={{ marginTop: '20px' }}>
          <h3>Request Status:</h3>
          {loading && <p>⏳ Waiting for response...</p>}
          {error && (
            <div style={{ 
              padding: '10px', 
              backgroundColor: '#f8d7da', 
              color: '#721c24', 
              borderRadius: '4px',
              marginBottom: '10px'
            }}>
              <strong>Error:</strong> {error}
            </div>
          )}
          {response && (
            <div style={{ marginTop: '10px' }}>
              <h4>Server Response:</h4>
              <pre style={{ 
                backgroundColor: '#f8f9fa', 
                padding: '10px', 
                borderRadius: '4px',
                overflow: 'auto',
                maxHeight: '400px'
              }}>
                {JSON.stringify(response, null, 2)}
              </pre>
            </div>
          )}

          {basicResponse && (
            <div style={{ marginTop: '10px' }}>
              <h4>Basic Request Response (ID: 90):</h4>
              <pre style={{
                backgroundColor: '#e8f5e8',
                padding: '10px',
                borderRadius: '4px',
                overflow: 'auto',
                maxHeight: '300px'
              }}>
                {JSON.stringify(basicResponse, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}

      <div style={{ marginTop: '30px' }}>
        <h3>Debug Information:</h3>
        <ul>
          <li>This page tests the schedule data loading functionality</li>
          <li>It sends a request with ID 2001 to get schedule data</li>
          <li>Check the browser console for additional debug information</li>
          <li>The request includes a 2-week date range (1 week before and after today)</li>
        </ul>
      </div>
    </div>
  );
};

export default ScheduleDebugPage;
