import React, { createContext, useContext, useState, useEffect } from 'react';
import { useSocket } from '../utils';
import { logDebug, logError, logWarning, logInfo } from '../utils/utils';
import { ENV } from '../utils/env';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [authError, setAuthError] = useState(null);
  const { socket, connectionStatus, isConnected, setAuthenticating } = useSocket();

  logDebug('AuthProvider', 'AuthProvider rendering', {
    isAuthenticated,
    isLoading,
    connectionStatus,
    hasUser: !!user
  });

  // Check for existing authentication on app load
  useEffect(() => {
    try {
      logDebug('AuthProvider', 'Checking for saved authentication');
      const savedUser = localStorage.getItem('holi_user');

      if (savedUser) {
        try {
          const userData = JSON.parse(savedUser);
          logInfo('AuthProvider', 'Found saved user data', {
            username: userData.username,
            isManager: userData.isManager,
            loginTime: userData.loginTime
          });

          // Restore session data if available
          const savedSession = sessionStorage.getItem('holi_session');
          if (savedSession) {
            try {
              const sessionData = JSON.parse(savedSession);
              userData.sessionId = sessionData.sessionId;
              userData.csrfToken = sessionData.csrfToken;
            } catch (sessionError) {
              logWarning('AuthProvider', 'Invalid session data, removing', sessionError);
              sessionStorage.removeItem('holi_session');
            }
          }

          // Validate saved user data structure
          if (userData.username && typeof userData.isManager === 'boolean') {
            setUser(userData);
            setIsAuthenticated(true);
            setAuthError(null);
          } else {
            logWarning('AuthProvider', 'Invalid saved user data structure', userData);
            localStorage.removeItem('holi_user');
            sessionStorage.removeItem('holi_session');
          }
        } catch (parseError) {
          logError('AuthProvider', 'Error parsing saved user data', parseError);
          localStorage.removeItem('holi_user');
          sessionStorage.removeItem('holi_session');
          setAuthError('Invalid saved authentication data');
        }
      } else {
        logDebug('AuthProvider', 'No saved authentication found');
      }
    } catch (error) {
      logError('AuthProvider', 'Error during authentication check', error);
      setAuthError('Authentication check failed');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const login = async (username, password) => {
    return new Promise((resolve, reject) => {
      if (!socket || socket.readyState !== WebSocket.OPEN) {
        reject(new Error('Not connected to the server. Please try again later.'));
        return;
      }

      const request = {
        request_id: 10,
        data: { username, password },
      };

      const handleMessage = (event) => {
        try {
          const response = JSON.parse(event.data);
          
          if (response.request_id === 10) {
            socket.removeEventListener('message', handleMessage);
            
            if (response.data && response.data.user_exists) {
              // Handle new secure session format
              const userData = {
                username,
                isManager: response.data.is_manager,
                isAdmin: response.data.is_admin,
                loginTime: new Date().toISOString(),
                // Store secure session data
                sessionId: response.data.session_id,
                csrfToken: response.data.csrf_token,
                userId: response.data.user_data?.user_id,
                email: response.data.user_data?.email
              };

              setUser(userData);
              setIsAuthenticated(true);

              // Persist to localStorage (excluding sensitive tokens for security)
              const persistData = {
                username: userData.username,
                isManager: userData.isManager,
                isAdmin: userData.isAdmin,
                loginTime: userData.loginTime,
                userId: userData.userId,
                email: userData.email
              };
              localStorage.setItem('holi_user', JSON.stringify(persistData));

              // Store session data securely (could be moved to sessionStorage for better security)
              sessionStorage.setItem('holi_session', JSON.stringify({
                sessionId: userData.sessionId,
                csrfToken: userData.csrfToken
              }));

              resolve(userData);
            } else {
              const errorMessage = response.data?.error || 'Invalid username or password';
              reject(new Error(errorMessage));
            }
          }
        } catch (error) {
          socket.removeEventListener('message', handleMessage);
          reject(new Error('Error processing login response'));
        }
      };

      socket.addEventListener('message', handleMessage);
      socket.send(JSON.stringify(request));

      // Timeout after 10 seconds
      setTimeout(() => {
        socket.removeEventListener('message', handleMessage);
        reject(new Error('Login request timed out'));
      }, 10000);
    });
  };

  const googleLogin = async (userData) => {
    try {
      logDebug('AuthContext', 'Starting Google login session creation', {
        username: userData.username,
        isManager: userData.isManager
      });

      // Mark authentication in progress to prevent connection closes
      setAuthenticating(true);

      // Wait for socket to be available or use existing connection
      const waitForSocket = () => {
        return new Promise((resolve, reject) => {
          const maxWaitTime = 10000; // 10 seconds max wait
          const checkInterval = 100; // Check every 100ms
          let waitTime = 0;

          const checkSocket = () => {
            if (socket && socket.readyState === WebSocket.OPEN) {
              resolve(socket);
            } else if (waitTime >= maxWaitTime) {
              reject(new Error('WebSocket connection timeout'));
            } else {
              waitTime += checkInterval;
              setTimeout(checkSocket, checkInterval);
            }
          };

          checkSocket();
        });
      };

      const sessionSocket = await waitForSocket();

      await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          setAuthenticating(false);
          reject(new Error('Google session creation timed out'));
        }, 15000); // Increased timeout

        // Define request outside callbacks so it's accessible in both
        const request = {
          request_id: 69,  // GOOGLE_SESSION_CREATE
          data: {
            username: userData.username,
            isManager: userData.isManager,
            email: userData.email,
            googleId: userData.googleId
          }
        };

        // Send request immediately since socket is already open
        logDebug('AuthContext', 'Sending Google session creation request via existing socket');
        sessionSocket.send(JSON.stringify(request));

        // Set up temporary message handler for this request
        const originalOnMessage = sessionSocket.onmessage;
        sessionSocket.onmessage = (event) => {
          try {
            const response = JSON.parse(event.data);

            if (response.request_id === request.request_id) {
              clearTimeout(timeout);
              // Restore original message handler
              sessionSocket.onmessage = originalOnMessage;

              if (response.data && response.data.success) {
                logDebug('AuthContext', 'Google session created successfully', response);

                // Mark authentication as complete
                setAuthenticating(false);

                // Store user data with session info
                const completeUserData = {
                  ...userData,
                  sessionId: response.data.sessionId,
                  csrfToken: response.data.csrfToken,
                  userId: response.data.userId,
                  loginMethod: 'google'
                };

                setUser(completeUserData);
                setIsAuthenticated(true);
                setAuthError(null);

                // Persist user data
                const persistData = {
                  username: completeUserData.username,
                  isManager: completeUserData.isManager,
                  userId: completeUserData.userId,
                  email: completeUserData.email,
                  googleId: completeUserData.googleId,
                  loginMethod: 'google'
                };
                localStorage.setItem('holi_user', JSON.stringify(persistData));

                // Store session data
                sessionStorage.setItem('holi_session', JSON.stringify({
                  sessionId: response.data.sessionId,
                  csrfToken: response.data.csrfToken
                }));

                resolve(completeUserData);
              } else {
                // Mark authentication as complete (even on failure)
                setAuthenticating(false);
                const errorMessage = response.data?.error || response.error || 'Failed to create Google session';
                logError('AuthContext', 'Google session creation failed', { error: errorMessage });
                reject(new Error(errorMessage));
              }
            }
          } catch (error) {
            clearTimeout(timeout);
            // Restore original message handler
            sessionSocket.onmessage = originalOnMessage;
            setAuthenticating(false);
            logError('AuthContext', 'Error processing Google session response', error);
            reject(error);
          }
        };
      });

    } catch (error) {
      setAuthenticating(false);
      logError('AuthContext', 'Google login session creation failed', error);

      // Fallback: Set user without session (will need to handle this gracefully)
      setUser(userData);
      setIsAuthenticated(true);
      setAuthError('Session creation failed, some features may be limited');

      // Store basic user data
      localStorage.setItem('holi_user', JSON.stringify({
        ...userData,
        loginMethod: 'google',
        sessionFailed: true
      }));
    }
  };

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('holi_user');
    sessionStorage.removeItem('holi_session');
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    googleLogin,
    logout,
    isManager: user?.isManager || false,
    username: user?.username || ''
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
