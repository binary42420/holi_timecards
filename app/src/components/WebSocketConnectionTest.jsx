import React, { useState } from 'react';
import { useSocket } from '../utils';
import { logDebug, logInfo, logError } from '../utils';
import WebSocketHealthMonitor from './WebSocketHealthMonitor';

const WebSocketConnectionTest = () => {
    const { socket, connectionStatus, waitForConnection, reconnect } = useSocket();
    const [testResults, setTestResults] = useState([]);
    const [isRunningTest, setIsRunningTest] = useState(false);

    const addTestResult = (test, result, success = true) => {
        const timestamp = new Date().toLocaleTimeString();
        setTestResults(prev => [...prev, {
            timestamp,
            test,
            result,
            success
        }]);
    };

    const runConnectionTests = async () => {
        setIsRunningTest(true);
        setTestResults([]);

        try {
            // Test 1: Basic connection status
            addTestResult('Connection Status', `Current status: ${connectionStatus}`);

            // Test 2: Socket ready state
            const readyState = socket ? socket.readyState : 'No socket';
            addTestResult('Socket Ready State', `Ready state: ${readyState}`);

            // Test 3: Wait for connection
            addTestResult('Connection Wait Test', 'Starting connection wait test...');
            try {
                const startTime = Date.now();
                const connectedSocket = await waitForConnection(15000);
                const endTime = Date.now();
                addTestResult(
                    'Connection Wait Test',
                    `✅ Connection established in ${endTime - startTime}ms`,
                    true
                );
            } catch (error) {
                addTestResult(
                    'Connection Wait Test',
                    `❌ Connection failed: ${error.message}`,
                    false
                );
            }

            // Test 4: Send test message
            if (socket && socket.readyState === WebSocket.OPEN) {
                addTestResult('Message Send Test', 'Sending test message...');
                try {
                    const testMessage = {
                        request_id: 998,
                        data: { test: true, timestamp: Date.now() }
                    };

                    const messageHandler = (event) => {
                        try {
                            const response = JSON.parse(event.data);
                            if (response.request_id === 998) {
                                addTestResult(
                                    'Message Send Test',
                                    `✅ Received response: ${JSON.stringify(response)}`,
                                    true
                                );
                                socket.removeEventListener('message', messageHandler);
                            }
                        } catch (error) {
                            addTestResult(
                                'Message Send Test',
                                `❌ Error parsing response: ${error.message}`,
                                false
                            );
                        }
                    };

                    socket.addEventListener('message', messageHandler);
                    socket.send(JSON.stringify(testMessage));

                    // Timeout after 5 seconds
                    setTimeout(() => {
                        socket.removeEventListener('message', messageHandler);
                    }, 5000);

                } catch (error) {
                    addTestResult(
                        'Message Send Test',
                        `❌ Failed to send message: ${error.message}`,
                        false
                    );
                }
            } else {
                addTestResult(
                    'Message Send Test',
                    '⚠️ Skipped - socket not connected',
                    false
                );
            }

            // Test 5: Google Sign-in simulation
            addTestResult('Google Sign-in Simulation', 'Testing Google sign-in flow...');
            try {
                // Simulate the Google sign-in connection check
                if (!socket || socket.readyState !== WebSocket.OPEN) {
                    const startTime = Date.now();
                    const connectedSocket = await waitForConnection(10000);
                    const endTime = Date.now();
                    addTestResult(
                        'Google Sign-in Simulation',
                        `✅ Connection ready for Google sign-in in ${endTime - startTime}ms`,
                        true
                    );
                } else {
                    addTestResult(
                        'Google Sign-in Simulation',
                        '✅ Socket already connected for Google sign-in',
                        true
                    );
                }
            } catch (error) {
                addTestResult(
                    'Google Sign-in Simulation',
                    `❌ Google sign-in would fail: ${error.message}`,
                    false
                );
            }

        } catch (error) {
            addTestResult('Test Suite', `❌ Test suite error: ${error.message}`, false);
            logError('WebSocketConnectionTest', 'Test suite error', error);
        } finally {
            setIsRunningTest(false);
        }
    };

    const clearResults = () => {
        setTestResults([]);
    };

    return (
        <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', maxWidth: '800px' }}>
            <h2>WebSocket Connection Test Suite</h2>
            
            <WebSocketHealthMonitor showDetails={true} />

            <div style={{ marginBottom: '20px' }}>
                <button
                    onClick={runConnectionTests}
                    disabled={isRunningTest}
                    style={{
                        padding: '12px 24px',
                        backgroundColor: isRunningTest ? '#6c757d' : '#007bff',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: isRunningTest ? 'not-allowed' : 'pointer',
                        marginRight: '10px'
                    }}
                >
                    {isRunningTest ? '🔄 Running Tests...' : '🧪 Run Connection Tests'}
                </button>

                <button
                    onClick={clearResults}
                    style={{
                        padding: '12px 24px',
                        backgroundColor: '#6c757d',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                    }}
                >
                    🗑️ Clear Results
                </button>
            </div>

            <div>
                <h3>Test Results ({testResults.length})</h3>
                <div style={{
                    maxHeight: '400px',
                    overflowY: 'auto',
                    border: '1px solid #ccc',
                    borderRadius: '4px',
                    backgroundColor: '#f8f9fa'
                }}>
                    {testResults.length === 0 ? (
                        <p style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
                            No test results yet. Click "Run Connection Tests" to start.
                        </p>
                    ) : (
                        testResults.map((result, index) => (
                            <div
                                key={index}
                                style={{
                                    padding: '12px',
                                    borderBottom: '1px solid #dee2e6',
                                    backgroundColor: result.success ? '#d4edda' : '#f8d7da'
                                }}
                            >
                                <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
                                    {result.timestamp} - {result.test}
                                </div>
                                <div style={{ fontSize: '14px', fontFamily: 'monospace' }}>
                                    {result.result}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default WebSocketConnectionTest;
