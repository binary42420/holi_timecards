import { useEffect, useState, useCallback, useRef } from "react";
import { ENV } from './utils/env';

// Import and re-export logging utilities
export { logDebug, logError, logWarning, logInfo } from './utils/utils';

let socket_obj = null;
let reconnectAttempts = 0;
let isConnecting = false;
let connectionListeners = new Set();
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 3000; // 3 seconds

export function useSocket() {
    const [socket, setSocket] = useState(/** @type {WebSocket | null} */ (socket_obj));
    const [connectionStatus, setConnectionStatus] = useState('connecting');
    const [lastError, setLastError] = useState(null);
    const [connectionAttempts, setConnectionAttempts] = useState(0);
    const reconnectTimeoutRef = useRef(null);
    const connectionPromiseRef = useRef(null);
    const heartbeatIntervalRef = useRef(null);
    // Store last sent auth/session tokens for re-authentication
    const lastAuthDataRef = useRef(null);
    // Track if we're in the middle of an authentication flow
    const isAuthenticatingRef = useRef(false);

    const connectWebSocket = useCallback(() => {
        // Return existing promise if connection is in progress
        if (connectionPromiseRef.current || isConnecting) {
            logDebug('useSocket', 'Connection already in progress, returning existing promise');
            return connectionPromiseRef.current || Promise.resolve(socket_obj);
        }

        // Prevent multiple simultaneous connections
        isConnecting = true;

        connectionPromiseRef.current = new Promise((resolve, reject) => {
            try {
                logDebug('useSocket', 'connectWebSocket called', {
                    currentSocketState: socket_obj?.readyState,
                    reconnectAttempts,
                    connectionStatus,
                    isConnecting
                });

                if (socket_obj && socket_obj.readyState === WebSocket.OPEN) {
                    logDebug('useSocket', 'Socket already connected, resolving immediately');
                    connectionPromiseRef.current = null;
                    isConnecting = false;
                    resolve(socket_obj);
                    return;
                }

                if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
                    logError('useSocket', 'Maximum reconnection attempts reached', { attempts: reconnectAttempts });
                    setConnectionStatus('failed');
                    setLastError(`Failed to connect after ${MAX_RECONNECT_ATTEMPTS} attempts`);
                    connectionPromiseRef.current = null;
                    reject(new Error(`Failed to connect after ${MAX_RECONNECT_ATTEMPTS} attempts`));
                    return;
                }

                const wsUrl = ENV.API_URL;
                if (!wsUrl) {
                    logError('useSocket', 'WebSocket URL is not configured', {
                        ENV_API_URL: ENV.API_URL,
                        window_env: window._env_,
                        process_env_API_URL: process.env.REACT_APP_API_URL
                    });
                    setConnectionStatus('error');
                    setLastError('WebSocket URL not configured');
                    connectionPromiseRef.current = null;
                    reject(new Error('WebSocket URL not configured'));
                    return;
                }

                logDebug('useSocket', 'Attempting WebSocket connection', {
                    url: wsUrl,
                    attempt: reconnectAttempts + 1,
                    ENV_object: ENV,
                    window_env: window._env_
                });
                setConnectionAttempts(prev => prev + 1);

                const newSocket = new WebSocket(wsUrl);

                // Set up event handlers with comprehensive error handling
                newSocket.onopen = () => {
                    logDebug('useSocket', 'WebSocket connection established successfully', {
                        isReconnection: reconnectAttempts > 0,
                        previousAttempts: reconnectAttempts
                    });
                    setConnectionStatus('connected');
                    setLastError(null);
                    reconnectAttempts = 0; // Reset reconnect attempts on successful connection
                    isConnecting = false; // Reset connecting flag
                    socket_obj = newSocket;
                    setSocket(newSocket);
                    connectionPromiseRef.current = null;

                    // Send last known auth/session tokens if available
                    if (lastAuthDataRef.current) {
                        try {
                            newSocket.send(JSON.stringify(lastAuthDataRef.current));
                        } catch (e) {
                            logError('useSocket', 'Failed to send auth/session tokens on reconnect', e);
                        }
                    }

                    // Start heartbeat interval
                    if (heartbeatIntervalRef.current) {
                        clearInterval(heartbeatIntervalRef.current);
                    }
                    heartbeatIntervalRef.current = setInterval(() => {
                        if (newSocket.readyState === WebSocket.OPEN) {
                            try {
                                newSocket.send(JSON.stringify({ type: 'heartbeat', timestamp: Date.now() }));
                            } catch (e) {
                                logError('useSocket', 'Failed to send heartbeat', e);
                            }
                        }
                    }, 30000); // 30 seconds
                    resolve(newSocket);
                };

                // Store last sent auth/session tokens on send
                const origSend = newSocket.send;
                newSocket.send = function (data) {
                    try {
                        const parsed = JSON.parse(data);
                        if (parsed && (parsed.session_id || parsed.csrf_token)) {
                            lastAuthDataRef.current = parsed;
                        }
                    } catch {}
                    return origSend.apply(this, arguments);
                };

                newSocket.onerror = (error) => {
                    logError('useSocket', 'WebSocket error occurred', {
                        error: error,
                        url: wsUrl,
                        readyState: newSocket.readyState,
                        timestamp: new Date().toISOString()
                    });
                    setConnectionStatus('error');
                    setLastError(`WebSocket connection error to ${wsUrl}`);
                    isConnecting = false; // Reset connecting flag on error
                    connectionPromiseRef.current = null;
                    reject(new Error(`WebSocket connection error to ${wsUrl}`));
                };

                newSocket.onclose = (event) => {
                    logDebug('useSocket', 'WebSocket connection closed', {
                        code: event.code,
                        reason: event.reason,
                        wasClean: event.wasClean
                    });

                    setConnectionStatus('disconnected');
                    socket_obj = null;
                    setSocket(null);
                    isConnecting = false; // Reset connecting flag on close

                    // Clear heartbeat interval
                    if (heartbeatIntervalRef.current) {
                        clearInterval(heartbeatIntervalRef.current);
                        heartbeatIntervalRef.current = null;
                    }

                    // If this was the socket we were waiting for, reject the promise
                    if (connectionPromiseRef.current) {
                        connectionPromiseRef.current = null;
                        reject(new Error(`Connection closed: ${event.reason || 'Unknown reason'}`));
                    }

                    // Attempt to reconnect with exponential backoff
                    // Only skip reconnection if it was an intentional close (code 1000) AND we're not in the middle of authentication
                    const isIntentionalClose = event.code === 1000 && event.reason === 'Component unmounting';

                    if (!isIntentionalClose && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                        reconnectAttempts++;
                        const delay = Math.min(RECONNECT_DELAY * Math.pow(2, reconnectAttempts - 1), 60000); // Max 60s
                        logDebug('useSocket', `Attempting to reconnect (${reconnectAttempts})`, {
                            delay,
                            code: event.code,
                            reason: event.reason,
                            wasClean: event.wasClean
                        });
                        setConnectionStatus('reconnecting');
                        reconnectTimeoutRef.current = setTimeout(() => {
                            connectWebSocket();
                        }, delay);
                    } else {
                        logDebug('useSocket', 'Not attempting reconnect', {
                            isIntentionalClose,
                            code: event.code,
                            reason: event.reason,
                            reconnectAttempts,
                            maxAttempts: MAX_RECONNECT_ATTEMPTS
                        });
                    }
                };

            } catch (error) {
                logError('useSocket', 'Failed to create WebSocket connection', error);
                setConnectionStatus('error');
                setLastError(`Connection creation failed: ${error.message}`);
                isConnecting = false; // Reset connecting flag on error
                connectionPromiseRef.current = null;
                reject(error);
            }
        });

        return connectionPromiseRef.current;
    }, []);

    useEffect(() => {
        if (!socket_obj && !isConnecting) {
            connectWebSocket();
        }

        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (heartbeatIntervalRef.current) {
                clearInterval(heartbeatIntervalRef.current);
                heartbeatIntervalRef.current = null;
            }
        };
    }, [connectWebSocket]);

    // Provide a manual reconnect function
    const reconnect = useCallback(() => {
        try {
            logDebug('useSocket', 'Manual reconnect triggered');

            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }

            // Clear any pending connection promise
            connectionPromiseRef.current = null;
            isConnecting = false; // Reset connecting flag

            reconnectAttempts = 0;
            setConnectionAttempts(0);
            setLastError(null);

            if (socket_obj) {
                logDebug('useSocket', 'Closing existing socket for reconnect');
                socket_obj.close();
            }

            socket_obj = null;
            setSocket(null);
            setConnectionStatus('connecting');
            return connectWebSocket();
        } catch (error) {
            logError('useSocket', 'Error during manual reconnect', error);
            setLastError(`Reconnect failed: ${error.message}`);
            return Promise.reject(error);
        }
    }, [connectWebSocket]);

    // Function to wait for connection with timeout
    const waitForConnection = useCallback((timeoutMs = 10000) => {
        return new Promise((resolve, reject) => {
            // If already connected, resolve immediately
            if (socket_obj && socket_obj.readyState === WebSocket.OPEN) {
                resolve(socket_obj);
                return;
            }

            // If connection is in progress, wait for it
            if (connectionPromiseRef.current) {
                const timeoutId = setTimeout(() => {
                    reject(new Error('Connection timeout'));
                }, timeoutMs);

                connectionPromiseRef.current
                    .then((socket) => {
                        clearTimeout(timeoutId);
                        resolve(socket);
                    })
                    .catch((error) => {
                        clearTimeout(timeoutId);
                        reject(error);
                    });
                return;
            }

            // Start new connection
            const timeoutId = setTimeout(() => {
                reject(new Error('Connection timeout'));
            }, timeoutMs);

            connectWebSocket()
                .then((socket) => {
                    clearTimeout(timeoutId);
                    resolve(socket);
                })
                .catch((error) => {
                    clearTimeout(timeoutId);
                    reject(error);
                });
        });
    }, [connectWebSocket]);

    // Cleanup on component unmount
    useEffect(() => {
        return () => {
            // Clear reconnection timeout
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
                reconnectTimeoutRef.current = null;
            }

            // Close WebSocket connection
            if (socket_obj && socket_obj.readyState === WebSocket.OPEN) {
                logDebug('useSocket', 'Closing WebSocket connection on cleanup');
                socket_obj.close(1000, 'Component unmounting');
                socket_obj = null;
            }

            // Clear connection promise
            connectionPromiseRef.current = null;
        };
    }, []);

    // Method to mark authentication in progress
    const setAuthenticating = useCallback((isAuth) => {
        isAuthenticatingRef.current = isAuth;
        logDebug('useSocket', 'Authentication status changed', { isAuthenticating: isAuth });
    }, []);

    return {
        socket,
        connectionStatus,
        reconnect,
        waitForConnection,
        setAuthenticating,
        lastError,
        connectionAttempts,
        isConnected: socket && socket.readyState === WebSocket.OPEN,
        isConnecting: connectionStatus === 'connecting' || connectionStatus === 'reconnecting',
        hasError: connectionStatus === 'error' || connectionStatus === 'failed'
    };
}