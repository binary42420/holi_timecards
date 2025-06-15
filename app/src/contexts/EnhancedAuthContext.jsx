import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useEnhancedSocket } from '../hooks/useEnhancedSocket';
import { logDebug, logError, logWarning, logInfo } from '../utils/utils';

const EnhancedAuthContext = createContext();

export const useEnhancedAuth = () => {
  const context = useContext(EnhancedAuthContext);
  if (!context) {
    throw new Error('useEnhancedAuth must be used within an EnhancedAuthProvider');
  }
  return context;
};

export const EnhancedAuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [authError, setAuthError] = useState(null);
  
  const { 
    socket, 
    connectionStatus, 
    authStatus, 
    authenticate, 
    setAuthenticationData, 
    clearAuthenticationData,
    isConnected,
    isAuthenticated: socketAuthenticated,
    lastError
  } = useEnhancedSocket();

  logDebug('EnhancedAuthProvider', 'Provider state', {
    isAuthenticated,
    isLoading,
    connectionStatus,
    authStatus,
    hasUser: !!user,
    socketAuthenticated
  });

  // Sync authentication state with socket
  useEffect(() => {
    if (socketAuthenticated && !isAuthenticated) {
      logDebug('EnhancedAuthProvider', 'Socket authenticated but context not. Attempting to sync from localStorage.', {
        socketAuthenticated,
        isAuthenticated
      });
      // Socket is authenticated but context isn't - sync the state
      const savedUser = localStorage.getItem('holi_user');
      if (savedUser) {
        try {
          const userData = JSON.parse(savedUser);
          setUser(userData);
          setIsAuthenticated(true);
          setAuthError(null);
          logInfo('EnhancedAuthProvider', 'Synced authentication state from socket/localStorage', { userData });
        } catch (e) {
          logError('EnhancedAuthProvider', 'Failed to parse user data from localStorage', e);
          setAuthError('Failed to restore user session from localStorage.');
        }
      } else {
        logWarning('EnhancedAuthProvider', 'No user data found in localStorage to sync.');
      }
    } else if (!socketAuthenticated && isAuthenticated) {
      // Context is authenticated but socket isn't - this might be a reconnection issue
      logWarning('EnhancedAuthProvider', 'Authentication state mismatch - socket not authenticated');
    }
  }, [socketAuthenticated, isAuthenticated]);

  // Handle connection errors
  useEffect(() => {
    if (lastError && connectionStatus === 'error') {
      setAuthError(`Connection error: ${lastError}`);
    } else if (authStatus === 'failed') {
      setAuthError('Authentication failed');
    } else if (connectionStatus === 'connected' && authStatus === 'authenticated') {
      setAuthError(null);
    }
  }, [lastError, connectionStatus, authStatus]);

  // Check for existing authentication on app load
  useEffect(() => {
    const checkExistingAuth = async () => {
      try {
        logDebug('EnhancedAuthProvider', 'Checking for saved authentication');
        const savedUser = localStorage.getItem('holi_user');
        const savedSession = sessionStorage.getItem('holi_session');

        if (savedUser) {
          try {
            const userData = JSON.parse(savedUser);
            logInfo('EnhancedAuthProvider', 'Found saved user data', {
              username: userData.username,
              isManager: userData.isManager,
              loginTime: userData.loginTime
            });

            // Validate saved user data structure
            if (userData.username && typeof userData.isManager === 'boolean') {
              setUser(userData);
              
              // Set authentication data for socket reconnections
              setAuthenticationData(userData.username, null, userData);
              
              // Wait for socket to connect and authenticate
              if (isConnected && socketAuthenticated) {
                setIsAuthenticated(true);
                setAuthError(null);
              } else {
                // Wait for socket authentication
                logDebug('EnhancedAuthProvider', 'Waiting for socket authentication');
              }
            } else {
              logWarning('EnhancedAuthProvider', 'Invalid saved user data structure', userData);
              localStorage.removeItem('holi_user');
              sessionStorage.removeItem('holi_session');
            }
          } catch (parseError) {
            logError('EnhancedAuthProvider', 'Error parsing saved user data', parseError);
            localStorage.removeItem('holi_user');
            sessionStorage.removeItem('holi_session');
            setAuthError('Invalid saved authentication data');
          }
        } else {
          logDebug('EnhancedAuthProvider', 'No saved authentication found');
        }
      } catch (error) {
        logError('EnhancedAuthProvider', 'Error during authentication check', error);
        setAuthError('Authentication check failed');
      } finally {
        setIsLoading(false);
      }
    };

    checkExistingAuth();
  }, [setAuthenticationData, isConnected, socketAuthenticated]);

  const login = useCallback(async (username, password) => {
    try {
      logInfo('EnhancedAuthProvider', 'Starting login process', { username });
      setAuthError(null);

      if (!isConnected) {
        throw new Error('Not connected to the server. Please try again later.');
      }

      // Authenticate with the socket
      const authResult = await authenticate(username, password);
      
      if (authResult && authResult.user_exists) {
        // Create user data object
        const userData = {
          username,
          isManager: authResult.is_manager,
          isAdmin: authResult.is_admin,
          loginTime: new Date().toISOString(),
          userId: authResult.user_data?.user_id,
          email: authResult.user_data?.email
        };

        setUser(userData);
        setIsAuthenticated(true);
        setAuthError(null);

        // Persist to localStorage (excluding sensitive tokens)
        const persistData = {
          username: userData.username,
          isManager: userData.isManager,
          isAdmin: userData.isAdmin,
          loginTime: userData.loginTime,
          userId: userData.userId,
          email: userData.email
        };
        localStorage.setItem('holi_user', JSON.stringify(persistData));

        // Store session data securely
        if (authResult.session_id && authResult.csrf_token) {
          sessionStorage.setItem('holi_session', JSON.stringify({
            sessionId: authResult.session_id,
            csrfToken: authResult.csrf_token
          }));
        }

        logInfo('EnhancedAuthProvider', 'Login successful', {
          username: userData.username,
          isManager: userData.isManager
        });

        return userData;
      } else {
        const errorMessage = authResult?.error || 'Invalid username or password';
        throw new Error(errorMessage);
      }
    } catch (error) {
      logError('EnhancedAuthProvider', 'Login failed', error);
      setAuthError(error.message);
      setIsAuthenticated(false);
      throw error;
    }
  }, [authenticate, isConnected]);

  const logout = useCallback(() => {
    logInfo('EnhancedAuthProvider', 'Logging out user');
    
    setUser(null);
    setIsAuthenticated(false);
    setAuthError(null);
    
    // Clear stored data
    localStorage.removeItem('holi_user');
    sessionStorage.removeItem('holi_session');
    
    // Clear socket authentication data
    clearAuthenticationData();
  }, [clearAuthenticationData]);

  // Google login placeholder (can be implemented later)
  const googleLogin = useCallback(async (userData) => {
    logInfo('EnhancedAuthProvider', 'Google login not yet implemented in enhanced context');
    throw new Error('Google login not yet implemented');
  }, []);

  const value = {
    user,
    isAuthenticated,
    isLoading,
    authError,
    login,
    googleLogin,
    logout,
    isManager: user?.isManager || false,
    isAdmin: user?.isAdmin || false,
    username: user?.username || '',
    
    // Socket-related states
    connectionStatus,
    authStatus,
    isConnected,
    socketAuthenticated,
    lastError
  };

  return (
    <EnhancedAuthContext.Provider value={value}>
      {children}
    </EnhancedAuthContext.Provider>
  );
};
