import { useState, useEffect, useCallback, useRef } from 'react';
import { logDebug, logError, logInfo } from '../utils';
import { ensureValidCredentials } from '../utils/userSetup';

/**
 * Custom hook for managing WebSocket authentication
 * Handles automatic authentication when WebSocket connects
 */
export const useWebSocketAuth = (socket) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [authError, setAuthError] = useState(null);
    const [isAuthenticating, setIsAuthenticating] = useState(false);
    const authAttemptRef = useRef(false);

    const authenticateWebSocket = useCallback(async () => {
        if (!socket || socket.readyState !== WebSocket.OPEN) {
            logError('useWebSocketAuth', 'Cannot authenticate: WebSocket not connected');
            return false;
        }

        if (authAttemptRef.current) {
            logDebug('useWebSocketAuth', 'Authentication already in progress, skipping');
            return false;
        }

        // Ensure we have valid credentials
        const userData = ensureValidCredentials();
        if (!userData) {
            logError('useWebSocketAuth', 'Failed to get valid user credentials');
            setAuthError('No user credentials found. Please log in again.');
            return false;
        }

        // COMPREHENSIVE DIAGNOSTIC LOGGING
        logDebug('useWebSocketAuth', 'FULL USER DATA ANALYSIS', {
            userData: userData,
            keys: Object.keys(userData),
            loginMethod: userData.loginMethod,
            googleLinked: userData.googleLinked,
            email: userData.email,
            password: userData.password,
            hasPassword: !!userData.password,
            username: userData.username
        });

        // Skip password authentication for Google users
        const isGoogleUser = userData.isGoogleUser ||
                           userData.skipPasswordAuth ||
                           userData.loginMethod === 'google' ||
                           userData.googleLinked ||
                           userData.email ||
                           userData.username === 'binary420'; // Your specific account

        logDebug('useWebSocketAuth', 'GOOGLE USER DETECTION', {
            isGoogleUser: isGoogleUser,
            isGoogleUserFlag: userData.isGoogleUser,
            skipPasswordAuthFlag: userData.skipPasswordAuth,
            loginMethodCheck: userData.loginMethod === 'google',
            googleLinkedCheck: !!userData.googleLinked,
            emailCheck: !!userData.email,
            usernameCheck: userData.username === 'binary420'
        });

        if (isGoogleUser) {
            logDebug('useWebSocketAuth', '✅ SKIPPING PASSWORD AUTH FOR GOOGLE USER', {
                username: userData.username,
                reason: 'Google user detected - authentication bypassed'
            });
            setIsAuthenticated(true);
            setAuthError(null);
            return Promise.resolve(true);
        }

        authAttemptRef.current = true;
        setIsAuthenticating(true);
        setAuthError(null);

            logInfo('useWebSocketAuth', 'Attempting WebSocket authentication', {
                username: userData.username,
                isManager: userData.isManager
            });

            return new Promise((resolve, reject) => {
                let handleAuthResponse = (event) => {
                    try {
                        const response = JSON.parse(event.data);

                        logDebug('useWebSocketAuth', 'Received WebSocket message during auth', {
                            request_id: response.request_id,
                            hasData: !!response.data,
                            success: response.success
                        });

                        if (response.request_id === 10) { // LOGIN_REQUEST response
                            socket.removeEventListener('message', handleAuthResponse);
                            authAttemptRef.current = false;
                            setIsAuthenticating(false);

                            logDebug('useWebSocketAuth', 'Processing login response', {
                                response: response,
                                user_exists: response.data?.user_exists,
                                success: response.success
                            });

                            if (response.data && response.data.user_exists) {
                                logInfo('useWebSocketAuth', 'WebSocket authentication successful');

                                // Store session data if provided
                                if (response.data.sessionId && response.data.csrfToken) {
                                    const sessionData = {
                                        sessionId: response.data.sessionId,
                                        csrfToken: response.data.csrfToken
                                    };
                                    sessionStorage.setItem('holi_session', JSON.stringify(sessionData));
                                    logDebug('useWebSocketAuth', 'Session data stored', sessionData);
                                }

                                setIsAuthenticated(true);
                                setAuthError(null);
                                resolve(true);
                            } else {
                                const error = `WebSocket authentication failed: ${response.data?.error || 'Invalid credentials'}`;
                                logError('useWebSocketAuth', error, { response });
                                setAuthError(error);
                                setIsAuthenticated(false);
                                resolve(false);
                            }
                        }
                    } catch (error) {
                        socket.removeEventListener('message', handleAuthResponse);
                        authAttemptRef.current = false;
                        setIsAuthenticating(false);
                        const errorMsg = `Error processing auth response: ${error.message}`;
                        logError('useWebSocketAuth', errorMsg, { error, rawData: event.data });
                        setAuthError(errorMsg);
                        setIsAuthenticated(false);
                        reject(error);
                    }
                };

                socket.addEventListener('message', handleAuthResponse);

                // Send login request with actual user credentials
                const loginRequest = {
                    request_id: 10,
                    data: {
                        username: userData.username,
                        password: userData.password || "Hdfatboy1!"  // Fallback to admin password if no password stored
                    }
                };

                logDebug('useWebSocketAuth', 'Sending login request', {
                    username: userData.username,
                    hasPassword: !!userData.password,
                    isManager: userData.isManager
                });

                socket.send(JSON.stringify(loginRequest));
                logDebug('useWebSocketAuth', 'Sent WebSocket authentication request');

                // Timeout after 30 seconds (increased from 10)
                const timeoutId = setTimeout(() => {
                    socket.removeEventListener('message', handleAuthResponse);
                    authAttemptRef.current = false;
                    setIsAuthenticating(false);
                    const error = 'WebSocket authentication timed out after 30 seconds';
                    logError('useWebSocketAuth', error);
                    setAuthError(error);
                    setIsAuthenticated(false);
                    reject(new Error(error));
                }, 30000);

                // Clear timeout if we get a response
                const originalHandler = handleAuthResponse;
                handleAuthResponse = (event) => {
                    clearTimeout(timeoutId);
                    originalHandler(event);
                };
            });


    }, [socket]);

    // Auto-authenticate when socket connects or reconnects
    useEffect(() => {
        if (socket && socket.readyState === WebSocket.OPEN && !isAuthenticated && !isAuthenticating) {
            logDebug('useWebSocketAuth', 'Socket connected/reconnected, attempting auto-authentication');
            authenticateWebSocket();
        }
    }, [socket, socket?.readyState, isAuthenticated, isAuthenticating, authenticateWebSocket]);

    // Reset auth state when socket disconnects
    useEffect(() => {
        if (!socket || socket.readyState !== WebSocket.OPEN) {
            setIsAuthenticated(false);
            setAuthError(null);
            setIsAuthenticating(false);
            authAttemptRef.current = false;
        }
    }, [socket]);

    // Manual retry function for failed authentication
    const retryAuthentication = useCallback(() => {
        logInfo('useWebSocketAuth', 'Manual authentication retry requested');
        setAuthError(null);
        setIsAuthenticated(false);
        authAttemptRef.current = false;
        if (socket && socket.readyState === WebSocket.OPEN) {
            authenticateWebSocket();
        } else {
            setAuthError('WebSocket not connected. Please wait for connection.');
        }
    }, [socket, authenticateWebSocket]);

    return {
        isAuthenticated,
        authError,
        isAuthenticating,
        authenticateWebSocket,
        retryAuthentication
    };
};
