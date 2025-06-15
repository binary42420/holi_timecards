import React, { useState, useEffect, useCallback } from 'react';
import { useSocket } from '../../utils';

const ClientDirectoryDebug = () => {
  const { socket, connectionStatus } = useSocket();
  const [clientDirectory, setClientDirectory] = useState([]);
  const [summary, setSummary] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [debugLog, setDebugLog] = useState([]);

  const addDebugLog = (message) => {
    const timestamp = new Date().toLocaleTimeString();
    setDebugLog(prev => [...prev, `[${timestamp}] ${message}`]);
    console.log(`[ClientDirectoryDebug] ${message}`);
  };

  const fetchClientDirectory = useCallback(() => {
    addDebugLog(`Attempting to fetch client directory. Socket state: ${socket?.readyState}, Connection status: ${connectionStatus}`);
    
    if (socket && socket.readyState === WebSocket.OPEN) {
      setIsLoading(true);
      setError('');
      const request = { request_id: 212 };
      socket.send(JSON.stringify(request));
      addDebugLog(`Client directory request sent: ${JSON.stringify(request)}`);
    } else {
      const errorMsg = `Cannot fetch client directory: WebSocket is not connected. Socket: ${!!socket}, ReadyState: ${socket?.readyState}, Status: ${connectionStatus}`;
      setError(errorMsg);
      addDebugLog(errorMsg);
    }
  }, [socket, connectionStatus]);

  useEffect(() => {
    addDebugLog(`Socket effect triggered. Socket: ${!!socket}, ReadyState: ${socket?.readyState}, Status: ${connectionStatus}`);
    if (socket && socket.readyState === WebSocket.OPEN) {
      fetchClientDirectory();
    }
  }, [socket, connectionStatus, fetchClientDirectory]);

  useEffect(() => {
    if (!socket) {
      addDebugLog('No socket available for message listener');
      return;
    }

    addDebugLog('Setting up WebSocket message listener');

    const handleMessage = (event) => {
      try {
        addDebugLog(`Received WebSocket message: ${event.data.substring(0, 200)}...`);
        const response = JSON.parse(event.data);
        setIsLoading(false);

        if (response.request_id === 212) {
          addDebugLog(`Client Directory response received. Success: ${response.success}`);
          
          if (response.success) {
            const companies = response.data.companies;
            const summaryData = response.data.summary;
            
            addDebugLog(`Setting client directory: ${companies.length} companies`);
            addDebugLog(`Summary: ${JSON.stringify(summaryData)}`);
            
            setClientDirectory(companies);
            setSummary(summaryData);
            setError('');
          } else {
            const errorMsg = response.error || 'Failed to fetch client directory.';
            addDebugLog(`Client directory error: ${errorMsg}`);
            setError(errorMsg);
          }
        } else {
          addDebugLog(`Ignoring message with request_id: ${response.request_id}`);
        }
      } catch (e) {
        setIsLoading(false);
        const errorMsg = 'Error processing server response.';
        addDebugLog(`Message parsing error: ${e.message}`);
        setError(errorMsg);
      }
    };

    socket.addEventListener('message', handleMessage);
    addDebugLog('WebSocket message listener added');

    return () => {
      socket.removeEventListener('message', handleMessage);
      addDebugLog('WebSocket message listener removed');
    };
  }, [socket]);

  const handleRefresh = () => {
    addDebugLog('Manual refresh triggered');
    fetchClientDirectory();
  };

  const clearDebugLog = () => {
    setDebugLog([]);
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Client Directory Debug</h1>
      
      <div style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ccc', borderRadius: '5px' }}>
        <h3>Connection Status</h3>
        <p><strong>Status:</strong> {connectionStatus}</p>
        <p><strong>Socket:</strong> {socket ? 'Available' : 'Not available'}</p>
        <p><strong>Ready State:</strong> {socket?.readyState} (1 = OPEN)</p>
        <button onClick={handleRefresh} disabled={isLoading}>
          {isLoading ? 'Loading...' : 'Fetch Client Directory'}
        </button>
      </div>

      <div style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ccc', borderRadius: '5px' }}>
        <h3>Data Status</h3>
        <p><strong>Loading:</strong> {isLoading ? 'Yes' : 'No'}</p>
        <p><strong>Error:</strong> {error || 'None'}</p>
        <p><strong>Companies Count:</strong> {clientDirectory.length}</p>
        <p><strong>Summary:</strong> {JSON.stringify(summary)}</p>
      </div>

      {clientDirectory.length > 0 && (
        <div style={{ marginBottom: '20px', padding: '15px', border: '1px solid #green', borderRadius: '5px' }}>
          <h3>Client Companies ({clientDirectory.length})</h3>
          {clientDirectory.map((client, index) => (
            <div key={client.id} style={{ marginBottom: '10px', padding: '10px', backgroundColor: '#f5f5f5' }}>
              <h4>{client.name} (ID: {client.id})</h4>
              <p>Jobs: {client.statistics.total_jobs} (Active: {client.statistics.active_jobs})</p>
              <p>Users: {client.statistics.total_users} (Active: {client.statistics.active_users})</p>
              <p>Recent Activity: {client.recent_activity.length} items</p>
            </div>
          ))}
        </div>
      )}

      <div style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ccc', borderRadius: '5px' }}>
        <h3>Debug Log</h3>
        <button onClick={clearDebugLog} style={{ marginBottom: '10px' }}>Clear Log</button>
        <div style={{ maxHeight: '300px', overflowY: 'auto', backgroundColor: '#f8f8f8', padding: '10px' }}>
          {debugLog.map((log, index) => (
            <div key={index} style={{ fontSize: '12px', marginBottom: '2px' }}>
              {log}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ClientDirectoryDebug;
