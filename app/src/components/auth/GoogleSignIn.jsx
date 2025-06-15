import React, { useState, useEffect } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../../contexts/AuthContext';
import { useGoogleAuth } from '../../contexts/GoogleAuthContext';
import { useSocket } from '../../utils';
import { logDebug, logError, logWarning, logInfo } from '../../utils/utils';
import './GoogleSignIn.css';

const GoogleSignIn = ({ onSuccess, onError, buttonText = "Continue with Google" }) => {
  const [isLoading, setIsLoading] = useState(false);
  const { googleLogin } = useAuth();
  const { isConfigured } = useGoogleAuth();
  const { socket, connectionStatus, reconnect, waitForConnection, isConnected, hasError } = useSocket();

  // Monitor connection status
  useEffect(() => {
    logDebug('GoogleSignIn', 'WebSocket connection status changed', {
      connectionStatus,
      isConnected,
      hasError
    });
  }, [connectionStatus, isConnected, hasError]);

  const handleGoogleSuccess = async (credentialResponse) => {
    logInfo('GoogleSignIn', 'Received credential response');
    setIsLoading(true);

    try {
      // Enhanced connection logic with better diagnostics
      let activeSocket = socket;

      if (!isConnected) {
        logWarning('GoogleSignIn', 'WebSocket not connected, attempting to establish connection', {
          connectionStatus,
          socketReadyState: socket?.readyState,
          hasError
        });

        try {
          // First, try to reconnect if there's an error  TODO       if (hasError || !socket) {
          if (!socket) {
            logInfo('GoogleSignIn', 'Triggering reconnection due to error state');
            await reconnect();
            // Wait a bit for reconnection to establish
            await new Promise(resolve => setTimeout(resolve, 3000));
          }

          // Wait for connection with extended timeout for Google auth
          activeSocket = await waitForConnection(20000);
          logDebug('GoogleSignIn', 'Connection established successfully for Google auth');

          // Verify the connection is actually working
          if (!activeSocket || activeSocket.readyState !== WebSocket.OPEN) {
            throw new Error('Connection established but socket is not in OPEN state');
          }

          // Add a buffer to ensure server is ready
          await new Promise(resolve => setTimeout(resolve, 1250));
          logDebug('GoogleSignIn', 'Connection buffer completed, ready to send auth request');
        } catch (connectionError) {
          logError('GoogleSignIn', 'Failed to establish connection for Google auth', {
            error: connectionError.message,
            connectionStatus,
            socketState: socket?.readyState,
            hasError
          });

          // Provide more specific error messages
          if (connectionError.message.includes('timeout')) {
            throw new Error('Server connection timed out. Please check your internet connection and try again.');
          } else {
            throw new Error('Could not establish server connection. Please refresh the page and try again.');
          }
        }
      }

      logInfo('GoogleSignIn', 'Sending authentication request');
      
      // Create request
      const request = {
        request_id: 66, // GOOGLE_AUTH_LOGIN
        data: {
          credential: credentialResponse.credential,
          clientId: credentialResponse.clientId
        }
      };
      
      // Set up message listener for Google auth response
      const handleMessage = (event) => {
        try {
          const response = JSON.parse(event.data);
          logDebug('GoogleSignIn', 'Received response', {
            request_id: response.request_id,
            success: response.success,
            hasData: !!response.data
          });

          if (response.request_id === 66) {
            activeSocket.removeEventListener('message', handleMessage);

            if (response.success && response.data) {
              // Process successful response
              if (response.data.user_exists) {
                logInfo('GoogleSignIn', 'User authenticated successfully', {
                  username: response.data.username,
                  isManager: response.data.is_manager
                });
                const userData = {
                  username: response.data.username,
                  isManager: response.data.is_manager,
                  userId: response.data.userId,
                  loginTime: new Date().toISOString(),
                  googleLinked: true,
                  loginMethod: 'google',
                  email: response.data.email,
                  googleId: response.data.googleId || response.data.google_id
                };

                // Update auth context
                googleLogin(userData);

                if (onSuccess) {
                  onSuccess(userData);
                }
              } else {
                // Handle signup or account linking
                logInfo('GoogleSignIn', 'User needs signup/linking', {
                  buttonText,
                  hasGoogleUserInfo: !!response.data.google_user_info
                });

                if (buttonText === "signup_with") {
                  if (onSuccess) {
                    onSuccess({
                      needsSignup: true,
                      googleData: response.data.google_user_info
                    });
                  }
                } else {
                  if (onSuccess) {
                    onSuccess({
                      needsLinking: true,
                      googleData: response.data.google_user_info
                    });
                  }
                }
              }
            } else {
              logError('GoogleSignIn', 'Authentication failed', response.error);
              throw new Error(response.error || 'Google authentication failed');
            }
          }
        } catch (error) {
          activeSocket.removeEventListener('message', handleMessage);
          logError('GoogleSignIn', 'Error processing authentication response', error);
          
          if (onError) {
            onError(error.message || 'Authentication failed');
          }
        } finally {
          setIsLoading(false);
        }
      };

      // Add message listener
      activeSocket.addEventListener('message', handleMessage);

      // Send request
      if (!activeSocket || activeSocket.readyState !== WebSocket.OPEN) {
        throw new Error('WebSocket connection not available');
      }

      activeSocket.send(JSON.stringify(request));
      logInfo('GoogleSignIn', 'Authentication request sent', { request_id: 66 });

      // Set timeout (increased to 15 seconds to match connection timeout)
      setTimeout(() => {
        activeSocket.removeEventListener('message', handleMessage);
        setIsLoading(false);
        logError('GoogleSignIn', 'Authentication request timed out after 15 seconds');
        if (onError) {
          onError('Authentication request timed out. Please try again.');
        }
      }, 15000);
    } catch (error) {
      setIsLoading(false);
      logError('GoogleSignIn', 'Google sign-in error', error);
      if (onError) {
        onError(error.message || 'Authentication failed');
      }
    }
  };

  const handleGoogleError = (error) => {
    setIsLoading(false);
    console.error('Google OAuth Error:', error);

    let errorMessage = 'Google sign-in failed';

    if (error && error.error) {
      switch (error.error) {
        case 'popup_blocked':
          errorMessage = 'Popup was blocked. Please allow popups for this site and try again.';
          break;
        case 'access_denied':
          errorMessage = 'Access denied. Please try again.';
          break;
        case 'popup_closed_by_user':
          errorMessage = 'Sign-in was cancelled.';
          break;
        default:
          errorMessage = `Google sign-in error: ${error.error}`;
      }
    }

    if (onError) {
      onError(errorMessage);
    }
  };

  return (
    <div className="google-signin-container">
      {isLoading ? (
        <div className="google-signin-loading">
          <div className="loading-spinner"></div>
          <span>Authenticating with Google...</span>
        </div>
      ) : (
        <GoogleLogin
          onSuccess={handleGoogleSuccess}
          onError={handleGoogleError}
          text={buttonText}
          theme="outline"
          size="large"
          width={400}
          shape="rectangular"
        />
      )}
    </div>
  );
};

export default GoogleSignIn;





