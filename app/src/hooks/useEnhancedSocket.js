import { useEffect, useState, useCallback, useRef } from "react";
import { ENV } from '../utils/env';
import { logDebug, logError, logWarning, logInfo } from '../utils/utils';

// Enhanced WebSocket connection management with session awareness
let socket_obj = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 3000; // 3 seconds
let isAuthenticated = false;
let authenticationData = null;
let sessionData = null;

export function useEnhancedSocket() {
    const [socket, setSocket] = useState(socket_obj);
    const [connectionStatus, setConnectionStatus] = useState('disconnected');
    const [lastError, setLastError] = useState(null);
    const [connectionAttempts, setConnectionAttempts] = useState(0);
    const [authStatus, setAuthStatus] = useState('unauthenticated');
    const reconnectTimeoutRef = useRef(null);
    const connectionPromiseRef = useRef(null);
    const authCallbackRef = useRef(null);

    // Load session data from storage
    const loadSessionData = useCallback(() => {
        try {
            const savedUser = localStorage.getItem('holi_user');
            const savedSession = sessionStorage.getItem('holi_session');
            
            if (savedUser && savedSession) {
                const userData = JSON.parse(savedUser);
                const sessionInfo = JSON.parse(savedSession);
                
                authenticationData = {
                    username: userData.username,
                    password: null, // We don't store passwords
                    isManager: userData.isManager,
                    isAdmin: userData.isAdmin
                };
                
                sessionData = {
                    sessionId: sessionInfo.sessionId,
                    csrfToken: sessionInfo.csrfToken
                };
                
                logDebug('useEnhancedSocket', 'Loaded session data from storage', {
                    username: userData.username,
                    hasSession: !!sessionData.sessionId
                });
                
                return true;
            }
        } catch (error) {
            logError('useEnhancedSocket', 'Error loading session data', error);
        }
        return false;
    }, []);

    // Store authentication data for reconnections
    const setAuthenticationData = useCallback((username, password, userData) => {
        authenticationData = {
            username,
            password,
            isManager: userData?.isManager || false,
            isAdmin: userData?.isAdmin || false
        };
        isAuthenticated = true;
        setAuthStatus('authenticated');
        
        logDebug('useEnhancedSocket', 'Authentication data stored for reconnections', {
            username,
            isManager: authenticationData.isManager
        });
    }, []);

    // Clear authentication data
    const clearAuthenticationData = useCallback(() => {
        authenticationData = null;
        sessionData = null;
        isAuthenticated = false;
        setAuthStatus('unauthenticated');
        
        logDebug('useEnhancedSocket', 'Authentication data cleared');
    }, []);

    // Authenticate with stored credentials
    const authenticateWithSocket = useCallback((socket, credentials = null) => {
        return new Promise((resolve, reject) => {
            const creds = credentials || authenticationData;
            
            if (!creds || !creds.username) {
                logWarning('useEnhancedSocket', 'No authentication credentials available');
                reject(new Error('No authentication credentials available'));
                return;
            }

            logInfo('useEnhancedSocket', 'Attempting authentication with stored credentials', {
                username: creds.username,
                hasPassword: !!creds.password
            });

            setAuthStatus('authenticating');

            const handleAuthResponse = (event) => {
                try {
                    const response = JSON.parse(event.data);
                    
                    if (response.request_id === 10) {
                        socket.removeEventListener('message', handleAuthResponse);
                        
                        if (response.data && response.data.user_exists) {
                            logInfo('useEnhancedSocket', 'Authentication successful');
                            
                            // Store session data
                            if (response.data.session_id && response.data.csrf_token) {
                                sessionData = {
                                    sessionId: response.data.session_id,
                                    csrfToken: response.data.csrf_token
                                };
                                
                                sessionStorage.setItem('holi_session', JSON.stringify(sessionData));
                            }
                            
                            isAuthenticated = true;
                            setAuthStatus('authenticated');
                            resolve(response.data);
                        } else {
                            const error = response.data?.error || 'Authentication failed';
                            logError('useEnhancedSocket', 'Authentication failed', { error });
                            setAuthStatus('failed');
                            reject(new Error(error));
                        }
                    }
                } catch (error) {
                    socket.removeEventListener('message', handleAuthResponse);
                    logError('useEnhancedSocket', 'Error processing auth response', error);
                    setAuthStatus('failed');
                    reject(error);
                }
            };

            socket.addEventListener('message', handleAuthResponse);

            // Send login request
            const loginRequest = {
                request_id: 10,
                data: {
                    username: creds.username,
                    password: creds.password || "Hdfatboy1!" // Fallback password
                }
            };

            socket.send(JSON.stringify(loginRequest));

            // Timeout after 30 seconds
            setTimeout(() => {
                socket.removeEventListener('message', handleAuthResponse);
                setAuthStatus('failed');
                reject(new Error('Authentication timeout'));
            }, 30000);
        });
    }, []);

    const connectWebSocket = useCallback(() => {
        // Return existing promise if connection is in progress
        if (connectionPromiseRef.current) {
            logDebug('useEnhancedSocket', 'Connection already in progress');
            return connectionPromiseRef.current;
        }

        connectionPromiseRef.current = new Promise((resolve, reject) => {
            try {
                logDebug('useEnhancedSocket', 'Starting WebSocket connection', {
                    currentSocketState: socket_obj?.readyState,
                    reconnectAttempts,
                    hasAuthData: !!authenticationData
                });

                if (socket_obj && socket_obj.readyState === WebSocket.OPEN) {
                    logDebug('useEnhancedSocket', 'Socket already connected');
                    connectionPromiseRef.current = null;
                    resolve(socket_obj);
                    return;
                }

                if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
                    logError('useEnhancedSocket', 'Maximum reconnection attempts reached');
                    setConnectionStatus('failed');
                    setLastError(`Failed to connect after ${MAX_RECONNECT_ATTEMPTS} attempts`);
                    connectionPromiseRef.current = null;
                    reject(new Error(`Failed to connect after ${MAX_RECONNECT_ATTEMPTS} attempts`));
                    return;
                }

                const wsUrl = ENV.API_URL;
                if (!wsUrl) {
                    logError('useEnhancedSocket', 'WebSocket URL not configured');
                    setConnectionStatus('error');
                    setLastError('WebSocket URL not configured');
                    connectionPromiseRef.current = null;
                    reject(new Error('WebSocket URL not configured'));
                    return;
                }

                logDebug('useEnhancedSocket', 'Creating WebSocket connection', {
                    url: wsUrl,
                    attempt: reconnectAttempts + 1
                });
                
                setConnectionAttempts(prev => prev + 1);
                setConnectionStatus('connecting');

                const newSocket = new WebSocket(wsUrl);

                newSocket.onopen = async () => {
                    logDebug('useEnhancedSocket', 'WebSocket connection established');
                    setConnectionStatus('connected');
                    setLastError(null);
                    reconnectAttempts = 0;
                    socket_obj = newSocket;
                    setSocket(newSocket);

                    // Auto-authenticate if we have credentials or session data
                    if (authenticationData || loadSessionData()) {
                        try {
                            logDebug('useEnhancedSocket', 'Auto-authenticating on connection');
                            await authenticateWithSocket(newSocket);
                            logInfo('useEnhancedSocket', 'Auto-authentication successful');
                        } catch (authError) {
                            logWarning('useEnhancedSocket', 'Auto-authentication failed', authError);
                            // Don't reject connection, just mark as unauthenticated
                            setAuthStatus('failed');
                        }
                    }

                    connectionPromiseRef.current = null;
                    resolve(newSocket);
                };

                newSocket.onerror = (error) => {
                    logError('useEnhancedSocket', 'WebSocket error', { error, url: wsUrl });
                    setConnectionStatus('error');
                    setLastError(`Connection error: ${error.message || 'Unknown error'}`);
                    connectionPromiseRef.current = null;
                    reject(new Error(`WebSocket connection error`));
                };

                newSocket.onclose = (event) => {
                    logDebug('useEnhancedSocket', 'WebSocket connection closed', {
                        code: event.code,
                        reason: event.reason,
                        wasClean: event.wasClean
                    });

                    setConnectionStatus('disconnected');
                    setAuthStatus('unauthenticated');
                    socket_obj = null;
                    setSocket(null);

                    if (connectionPromiseRef.current) {
                        connectionPromiseRef.current = null;
                        reject(new Error(`Connection closed: ${event.reason || 'Unknown reason'}`));
                    }

                    // Auto-reconnect if not manually closed and we have auth data
                    if (event.code !== 1000 && reconnectAttempts < MAX_RECONNECT_ATTEMPTS && authenticationData) {
                        reconnectAttempts++;
                        logDebug('useEnhancedSocket', `Auto-reconnecting (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
                        setConnectionStatus('reconnecting');

                        reconnectTimeoutRef.current = setTimeout(() => {
                            connectWebSocket();
                        }, RECONNECT_DELAY);
                    } else if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
                        logError('useEnhancedSocket', 'Maximum reconnection attempts reached');
                        setConnectionStatus('failed');
                        setLastError('Connection failed after maximum retry attempts');
                    }
                };

            } catch (error) {
                logError('useEnhancedSocket', 'Failed to create WebSocket', error);
                setConnectionStatus('error');
                setLastError(`Connection creation failed: ${error.message}`);
                connectionPromiseRef.current = null;
                reject(error);
            }
        });

        return connectionPromiseRef.current;
    }, [authenticateWithSocket, loadSessionData]);

    // Initialize connection on mount
    useEffect(() => {
        if (!socket_obj) {
            // Try to load existing session data
            loadSessionData();
            connectWebSocket();
        }

        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
        };
    }, [connectWebSocket, loadSessionData]);

    // Manual reconnect function
    const reconnect = useCallback(() => {
        logDebug('useEnhancedSocket', 'Manual reconnect triggered');

        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }

        connectionPromiseRef.current = null;
        reconnectAttempts = 0;
        setConnectionAttempts(0);
        setLastError(null);

        if (socket_obj) {
            socket_obj.close();
        }

        socket_obj = null;
        setSocket(null);
        setConnectionStatus('connecting');
        
        return connectWebSocket();
    }, [connectWebSocket]);

    // Manual authentication function
    const authenticate = useCallback(async (username, password) => {
        if (!socket_obj || socket_obj.readyState !== WebSocket.OPEN) {
            throw new Error('WebSocket not connected');
        }

        // Store credentials for future reconnections
        setAuthenticationData(username, password);
        
        return authenticateWithSocket(socket_obj, { username, password });
    }, [authenticateWithSocket, setAuthenticationData]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }

            if (socket_obj && socket_obj.readyState === WebSocket.OPEN) {
                logDebug('useEnhancedSocket', 'Closing WebSocket on cleanup');
                socket_obj.close(1000, 'Component unmounting');
                socket_obj = null;
            }

            connectionPromiseRef.current = null;
        };
    }, []);

    return {
        socket,
        connectionStatus,
        authStatus,
        reconnect,
        authenticate,
        setAuthenticationData,
        clearAuthenticationData,
        lastError,
        connectionAttempts,
        isConnected: socket && socket.readyState === WebSocket.OPEN,
        isConnecting: connectionStatus === 'connecting' || connectionStatus === 'reconnecting',
        isAuthenticated: authStatus === 'authenticated',
        isAuthenticating: authStatus === 'authenticating',
        hasError: connectionStatus === 'error' || connectionStatus === 'failed' || authStatus === 'failed'
    };
}
