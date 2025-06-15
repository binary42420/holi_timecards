import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
import { logDebug, logInfo, logWarning, logError } from '../utils';

const WebSocketHealthMonitor = ({ showDetails = false, compact = false }) => {
    const { socket, connectionStatus, lastError, connectionAttempts, reconnect, waitForConnection } = useSocket();
    const [healthCheck, setHealthCheck] = useState(null);
    const [lastPingTime, setLastPingTime] = useState(null);
    const [pingLatency, setPingLatency] = useState(null);

    // Periodic health check
    useEffect(() => {
        if (!socket || socket.readyState !== WebSocket.OPEN) return;

        const healthCheckInterval = setInterval(() => {
            performHealthCheck();
        }, 30000); // Check every 30 seconds

        return () => clearInterval(healthCheckInterval);
    }, [socket]);

    const performHealthCheck = async () => {
        if (!socket || socket.readyState !== WebSocket.OPEN) {
            setHealthCheck('❌ Socket not connected');
            return;
        }

        try {
            const startTime = Date.now();
            
            // Send a ping request
            const pingRequest = {
                request_id: 999, // Use a special request ID for ping
                data: { ping: true, timestamp: startTime }
            };

            const messageHandler = (event) => {
                try {
                    const response = JSON.parse(event.data);
                    if (response.request_id === 999) {
                        const endTime = Date.now();
                        const latency = endTime - startTime;
                        setPingLatency(latency);
                        setLastPingTime(new Date().toLocaleTimeString());
                        setHealthCheck(`✅ Healthy (${latency}ms)`);
                        socket.removeEventListener('message', messageHandler);
                    }
                } catch (error) {
                    logError('WebSocketHealthMonitor', 'Error parsing ping response', error);
                }
            };

            socket.addEventListener('message', messageHandler);
            socket.send(JSON.stringify(pingRequest));

            // Timeout after 5 seconds
            setTimeout(() => {
                socket.removeEventListener('message', messageHandler);
                if (!pingLatency || Date.now() - startTime > 5000) {
                    setHealthCheck('⚠️ Ping timeout');
                }
            }, 5000);

        } catch (error) {
            setHealthCheck(`❌ Health check failed: ${error.message}`);
            logError('WebSocketHealthMonitor', 'Health check error', error);
        }
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

    const getStatusIcon = () => {
        switch (connectionStatus) {
            case 'connected': return '🟢';
            case 'connecting': return '🟡';
            case 'reconnecting': return '🟠';
            case 'disconnected': return '🔴';
            case 'error': return '❌';
            case 'failed': return '⚫';
            default: return '❓';
        }
    };

    if (compact) {
        return (
            <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '4px 8px',
                backgroundColor: `${getStatusColor()}15`,
                border: `1px solid ${getStatusColor()}`,
                borderRadius: '4px',
                fontSize: '12px'
            }}>
                <span>{getStatusIcon()}</span>
                <span>{connectionStatus}</span>
                {pingLatency && <span>({pingLatency}ms)</span>}
            </div>
        );
    }

    return (
        <div style={{
            padding: '12px',
            border: `2px solid ${getStatusColor()}`,
            borderRadius: '8px',
            backgroundColor: `${getStatusColor()}10`,
            marginBottom: '16px'
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span style={{ fontSize: '18px' }}>{getStatusIcon()}</span>
                <strong>WebSocket Status: {connectionStatus}</strong>
            </div>

            {showDetails && (
                <div style={{ fontSize: '14px', color: '#666' }}>
                    <div>Ready State: {socket ? socket.readyState : 'No socket'} (0=CONNECTING, 1=OPEN, 2=CLOSING, 3=CLOSED)</div>
                    <div>Connection Attempts: {connectionAttempts}</div>
                    {lastError && <div style={{ color: '#dc3545' }}>Last Error: {lastError}</div>}
                    {healthCheck && <div>Health: {healthCheck}</div>}
                    {lastPingTime && <div>Last Ping: {lastPingTime}</div>}
                </div>
            )}

            <div style={{ marginTop: '8px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {connectionStatus !== 'connected' && (
                    <button
                        onClick={reconnect}
                        style={{
                            padding: '6px 12px',
                            backgroundColor: '#007bff',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '12px'
                        }}
                    >
                        🔄 Reconnect
                    </button>
                )}

                <button
                    onClick={performHealthCheck}
                    disabled={!socket || socket.readyState !== WebSocket.OPEN}
                    style={{
                        padding: '6px 12px',
                        backgroundColor: socket && socket.readyState === WebSocket.OPEN ? '#28a745' : '#6c757d',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: socket && socket.readyState === WebSocket.OPEN ? 'pointer' : 'not-allowed',
                        fontSize: '12px'
                    }}
                >
                    🏥 Health Check
                </button>
            </div>
        </div>
    );
};

export default WebSocketHealthMonitor;
