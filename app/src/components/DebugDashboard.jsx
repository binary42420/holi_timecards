import React, { useState, useEffect } from 'react';
import { useSocket, logDebug, logError, logInfo } from '../utils';
import { useAuth } from '../contexts/AuthContext';

const DebugDashboard = () => {
  const { socket, connectionStatus, lastError, connectionAttempts, isConnected, hasError } = useSocket();
  const { user, isAuthenticated, isLoading } = useAuth();
  const [debugLogs, setDebugLogs] = useState([]);
  const [systemInfo, setSystemInfo] = useState({});
  const [testResults, setTestResults] = useState({});

  useEffect(() => {
    // Collect system information
    const info = {
      userAgent: navigator.userAgent,
      url: window.location.href,
      timestamp: new Date().toISOString(),
      localStorage: {
        hasUser: !!localStorage.getItem('holi_user'),
        userDataSize: localStorage.getItem('holi_user')?.length || 0
      },
      environment: {
        nodeEnv: process.env.NODE_ENV,
        apiUrl: process.env.REACT_APP_API_URL,
        hasGoogleClientId: !!process.env.REACT_APP_GOOGLE_CLIENT_ID
      }
    };
    setSystemInfo(info);
    logInfo('DebugDashboard', 'System info collected', info);
  }, []);

  const runConnectionTest = async () => {
    logInfo('DebugDashboard', 'Running connection test');
    const results = {};

    try {
      // Test current WebSocket connection
      results.currentWebSocket = {
        available: !!socket,
        readyState: socket?.readyState,
        connectionStatus,
        lastError,
        connectionAttempts,
        isConnected,
        hasError
      };

      // Test fresh WebSocket connection
      results.websocketTest = await testWebSocketConnection();

      // Test API endpoint (convert WebSocket URL to HTTP)
      try {
        const wsUrl = process.env.REACT_APP_API_URL || '';
        const httpUrl = wsUrl.replace('wss://', 'https://').replace('ws://', 'http://').replace('/ws', '/health');

        logInfo('DebugDashboard', 'Testing API health endpoint', { httpUrl });

        const response = await fetch(httpUrl, {
          method: 'GET',
          headers: {
            'Accept': 'application/json'
          }
        });

        const responseData = await response.json();

        results.apiHealth = {
          status: response.status,
          ok: response.ok,
          statusText: response.statusText,
          url: httpUrl,
          data: responseData
        };
      } catch (apiError) {
        logError('DebugDashboard', 'API health test failed', apiError);
        results.apiHealth = {
          error: apiError.message,
          available: false,
          url: process.env.REACT_APP_API_URL
        };
      }

      // Test authentication
      results.authentication = {
        isAuthenticated,
        isLoading,
        hasUser: !!user,
        userType: user?.isManager ? 'manager' : 'employee'
      };

      setTestResults(results);
      logInfo('DebugDashboard', 'Connection test completed', results);
    } catch (error) {
      logError('DebugDashboard', 'Connection test failed', error);
      setTestResults({ error: error.message });
    }
  };

  const testWebSocketConnection = async () => {
    return new Promise((resolve) => {
      try {
        const wsUrl = process.env.REACT_APP_API_URL || '';
        logInfo('DebugDashboard', 'Testing WebSocket connection', { wsUrl });

        const testSocket = new WebSocket(wsUrl);
        const timeout = setTimeout(() => {
          testSocket.close();
          resolve({
            success: false,
            error: 'Connection timeout',
            url: wsUrl
          });
        }, 5000);

        testSocket.onopen = () => {
          clearTimeout(timeout);
          testSocket.close();
          resolve({
            success: true,
            message: 'WebSocket connection successful',
            url: wsUrl
          });
        };

        testSocket.onerror = (error) => {
          clearTimeout(timeout);
          resolve({
            success: false,
            error: 'WebSocket connection failed',
            details: error,
            url: wsUrl
          });
        };

        testSocket.onclose = (event) => {
          if (event.code !== 1000) {
            resolve({
              success: false,
              error: `WebSocket closed with code ${event.code}`,
              reason: event.reason,
              url: wsUrl
            });
          }
        };
      } catch (error) {
        resolve({
          success: false,
          error: error.message,
          url: process.env.REACT_APP_API_URL
        });
      }
    });
  };

  const sendTestMessage = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      const testMessage = {
        request_id: 999,
        test: true,
        timestamp: new Date().toISOString()
      };

      logInfo('DebugDashboard', 'Sending test message', testMessage);
      socket.send(JSON.stringify(testMessage));
    } else {
      logError('DebugDashboard', 'Cannot send test message - socket not available');
    }
  };

  const clearLogs = () => {
    setDebugLogs([]);
    console.clear();
    logInfo('DebugDashboard', 'Debug logs cleared');
  };

  const exportDebugData = () => {
    const debugData = {
      timestamp: new Date().toISOString(),
      systemInfo,
      testResults,
      debugLogs,
      socketState: {
        available: !!socket,
        readyState: socket?.readyState,
        connectionStatus,
        lastError,
        connectionAttempts
      },
      authState: {
        isAuthenticated,
        isLoading,
        hasUser: !!user
      }
    };

    const blob = new Blob([JSON.stringify(debugData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `easyshifts-debug-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    logInfo('DebugDashboard', 'Debug data exported');
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace', fontSize: '14px' }}>
      <h1>🔧 EasyShifts Debug Dashboard</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        
        {/* Connection Status */}
        <div style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px' }}>
          <h3>🔌 Connection Status</h3>
          <div>Status: <span style={{ color: isConnected ? 'green' : 'red' }}>{connectionStatus}</span></div>
          <div>Socket Available: {socket ? '✅' : '❌'}</div>
          <div>Ready State: {socket?.readyState} {socket?.readyState === 1 ? '(OPEN)' : ''}</div>
          <div>Connection Attempts: {connectionAttempts}</div>
          {lastError && <div style={{ color: 'red' }}>Last Error: {lastError}</div>}
          
          <div style={{ marginTop: '10px' }}>
            <button onClick={runConnectionTest} style={{ marginRight: '10px' }}>Test Connection</button>
            <button onClick={sendTestMessage} disabled={!isConnected} style={{ marginRight: '10px' }}>Send Test Message</button>
            <button onClick={async () => {
              const result = await testWebSocketConnection();
              console.log('WebSocket Test Result:', result);
              alert(`WebSocket Test: ${result.success ? 'Success' : 'Failed'}\n${result.error || result.message || ''}`);
            }}>Test WebSocket</button>
          </div>
        </div>

        {/* Authentication Status */}
        <div style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px' }}>
          <h3>👤 Authentication Status</h3>
          <div>Authenticated: {isAuthenticated ? '✅' : '❌'}</div>
          <div>Loading: {isLoading ? '⏳' : '✅'}</div>
          <div>User Type: {user?.isManager ? 'Manager' : user ? 'Employee' : 'None'}</div>
          <div>Username: {user?.username || 'N/A'}</div>
          <div>Login Time: {user?.loginTime || 'N/A'}</div>
        </div>

        {/* System Information */}
        <div style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px' }}>
          <h3>💻 System Information</h3>
          <div>Environment: {systemInfo.environment?.nodeEnv}</div>
          <div>API URL: {systemInfo.environment?.apiUrl || 'Not set'}</div>
          <div>Google OAuth: {systemInfo.environment?.hasGoogleClientId ? '✅' : '❌'}</div>
          <div>Local Storage: {systemInfo.localStorage?.hasUser ? '✅' : '❌'}</div>
          <div>Current URL: {window.location.href}</div>
        </div>

        {/* Test Results */}
        {Object.keys(testResults).length > 0 && (
          <div style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px' }}>
            <h3>🧪 Test Results</h3>
            <pre style={{ fontSize: '12px', overflow: 'auto', maxHeight: '200px' }}>
              {JSON.stringify(testResults, null, 2)}
            </pre>
          </div>
        )}

        {/* Actions */}
        <div style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px' }}>
          <h3>⚡ Actions</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <button onClick={runConnectionTest}>🔍 Run Full Test</button>
            <button onClick={clearLogs}>🗑️ Clear Console</button>
            <button onClick={exportDebugData}>💾 Export Debug Data</button>
            <button onClick={() => window.location.reload()}>🔄 Reload Page</button>
          </div>
        </div>

        {/* Quick Links */}
        <div style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px' }}>
          <h3>🔗 Quick Links</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
            <a href="/login">Login Page</a>
            <a href="/manager-clients">Client Directory</a>
            <a href="/manager-clients-debug">Client Debug</a>
            <a href="/manager-jobs">Job Management</a>
            <a href="/manager-profile">Manager Profile</a>
            <a href="/manager-timesheets">Timesheets Management</a>
            <a href="/enhanced-schedule">Enhanced Schedule</a>
          </div>
        </div>
      </div>

      {/* Console Output */}
      <div style={{ marginTop: '20px', border: '1px solid #ccc', padding: '15px', borderRadius: '8px' }}>
        <h3>📝 Recent Console Activity</h3>
        <div style={{ 
          backgroundColor: '#f5f5f5', 
          padding: '10px', 
          borderRadius: '4px', 
          maxHeight: '300px', 
          overflow: 'auto',
          fontSize: '12px'
        }}>
          <div>Check browser console (F12) for detailed logs</div>
          <div>Debug logging is currently enabled</div>
          <div>All WebSocket messages are being logged</div>
        </div>
      </div>
    </div>
  );
};

export default DebugDashboard;
