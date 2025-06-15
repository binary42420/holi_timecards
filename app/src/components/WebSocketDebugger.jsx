import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
import ENV from '../utils/env';

const WebSocketDebugger = () => {
    const { socket, connectionStatus, reconnect, lastError, connectionAttempts } = useSocket();
    const [debugLog, setDebugLog] = useState([]);
    const [testResults, setTestResults] = useState({});

    const addLog = (message, type = 'info') => {
        const timestamp = new Date().toLocaleTimeString();
        setDebugLog(prev => [...prev.slice(-50), { timestamp, message, type }]);
    };

    useEffect(() => {
        addLog(`WebSocket status changed to: ${connectionStatus}`, 'status');
        if (lastError) {
            addLog(`Error: ${lastError}`, 'error');
        }
    }, [connectionStatus, lastError]);

    const testEnvironmentConfig = () => {
        const results = {
            buildTimeEnv: process.env.REACT_APP_API_URL,
            runtimeEnv: window._env_?.REACT_APP_API_URL,
            finalUrl: ENV.API_URL,
            windowEnvExists: !!window._env_,
            windowEnvContent: window._env_,
            processEnvKeys: Object.keys(process.env).filter(key => key.startsWith('REACT_APP_')),
        };
        
        setTestResults(results);
        addLog('Environment configuration tested', 'test');
        return results;
    };

    const testDirectConnection = async () => {
        const url = ENV.API_URL;
        addLog(`Testing direct WebSocket connection to: ${url}`, 'test');
        
        try {
            const testSocket = new WebSocket(url);
            
            testSocket.onopen = () => {
                addLog('✅ Direct connection successful!', 'success');
                testSocket.close();
            };
            
            testSocket.onerror = (error) => {
                addLog(`❌ Direct connection failed: ${error}`, 'error');
            };
            
            testSocket.onclose = (event) => {
                addLog(`Connection closed: Code ${event.code}, Reason: ${event.reason}`, 'info');
            };
            
            // Timeout after 10 seconds
            setTimeout(() => {
                if (testSocket.readyState === WebSocket.CONNECTING) {
                    addLog('⏰ Direct connection test timed out', 'error');
                    testSocket.close();
                }
            }, 10000);
            
        } catch (error) {
            addLog(`❌ Failed to create test socket: ${error.message}`, 'error');
        }
    };

    const testHttpEndpoint = async () => {
        const wsUrl = ENV.API_URL;
        const httpUrl = wsUrl.replace('wss://', 'https://').replace('ws://', 'http://').replace('/ws', '/health');
        
        addLog(`Testing HTTP health endpoint: ${httpUrl}`, 'test');
        
        try {
            const response = await fetch(httpUrl, {
                method: 'GET',
                headers: { 'Accept': 'application/json' }
            });
            
            if (response.ok) {
                const data = await response.json();
                addLog(`✅ HTTP endpoint accessible: ${JSON.stringify(data)}`, 'success');
            } else {
                addLog(`❌ HTTP endpoint returned ${response.status}: ${response.statusText}`, 'error');
            }
        } catch (error) {
            addLog(`❌ HTTP endpoint test failed: ${error.message}`, 'error');
        }
    };

    const clearLog = () => {
        setDebugLog([]);
    };

    const getStatusColor = () => {
        switch (connectionStatus) {
            case 'connected': return '#28a745';
            case 'connecting': return '#ffc107';
            case 'reconnecting': return '#fd7e14';
            case 'disconnected': return '#dc3545';
            case 'error': return '#dc3545';
            case 'failed': return '#6c757d';
            default: return '#6c757d';
        }
    };

    return (
        <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', maxWidth: '1200px' }}>
            <h1>🔧 WebSocket Connection Debugger</h1>
            
            {/* Connection Status */}
            <div style={{ 
                padding: '15px', 
                border: '2px solid', 
                borderColor: getStatusColor(),
                borderRadius: '8px',
                marginBottom: '20px',
                backgroundColor: `${getStatusColor()}15`
            }}>
                <h3>Connection Status: {connectionStatus}</h3>
                <p><strong>Socket Available:</strong> {socket ? 'Yes' : 'No'}</p>
                <p><strong>Ready State:</strong> {socket?.readyState} (0=CONNECTING, 1=OPEN, 2=CLOSING, 3=CLOSED)</p>
                <p><strong>Connection Attempts:</strong> {connectionAttempts}</p>
                <p><strong>Last Error:</strong> {lastError || 'None'}</p>
                
                <button 
                    onClick={reconnect}
                    style={{
                        padding: '10px 20px',
                        backgroundColor: '#007bff',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        marginRight: '10px'
                    }}
                >
                    🔄 Force Reconnect
                </button>
            </div>

            {/* Test Buttons */}
            <div style={{ marginBottom: '20px' }}>
                <button onClick={testEnvironmentConfig} style={{ marginRight: '10px', padding: '8px 16px' }}>
                    🔍 Test Environment Config
                </button>
                <button onClick={testDirectConnection} style={{ marginRight: '10px', padding: '8px 16px' }}>
                    🔗 Test Direct Connection
                </button>
                <button onClick={testHttpEndpoint} style={{ marginRight: '10px', padding: '8px 16px' }}>
                    🌐 Test HTTP Endpoint
                </button>
                <button onClick={clearLog} style={{ padding: '8px 16px' }}>
                    🗑️ Clear Log
                </button>
            </div>

            {/* Environment Test Results */}
            {Object.keys(testResults).length > 0 && (
                <div style={{ 
                    marginBottom: '20px', 
                    padding: '15px', 
                    border: '1px solid #ccc', 
                    borderRadius: '5px',
                    backgroundColor: '#f8f9fa'
                }}>
                    <h3>Environment Configuration Results</h3>
                    <pre style={{ fontSize: '12px', overflow: 'auto' }}>
                        {JSON.stringify(testResults, null, 2)}
                    </pre>
                </div>
            )}

            {/* Debug Log */}
            <div>
                <h3>Debug Log ({debugLog.length} entries)</h3>
                <div style={{ 
                    maxHeight: '400px', 
                    overflowY: 'auto', 
                    border: '1px solid #ccc', 
                    padding: '10px',
                    backgroundColor: '#f8f9fa',
                    fontSize: '12px'
                }}>
                    {debugLog.length === 0 ? (
                        <p>No log entries yet</p>
                    ) : (
                        debugLog.map((entry, index) => (
                            <div key={index} style={{ 
                                marginBottom: '5px',
                                padding: '5px',
                                backgroundColor: entry.type === 'error' ? '#ffebee' : 
                                               entry.type === 'success' ? '#e8f5e8' :
                                               entry.type === 'test' ? '#fff3cd' : 'white',
                                borderRadius: '3px'
                            }}>
                                <strong>[{entry.timestamp}]</strong> {entry.message}
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default WebSocketDebugger;
