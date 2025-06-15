import React, { createContext, useContext } from 'react';
import { GoogleOAuthProvider } from '@react-oauth/google';

const GoogleAuthContext = createContext();

export const useGoogleAuth = () => {
  const context = useContext(GoogleAuthContext);
  if (!context) {
    throw new Error('useGoogleAuth must be used within a GoogleAuthProvider');
  }
  return context;
};

export const GoogleAuthContextProvider = ({ children }) => {
  // Get Google Client ID from both process.env and window._env_
  let GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;
  if (!GOOGLE_CLIENT_ID && typeof window !== 'undefined' && window._env_ && window._env_.REACT_APP_GOOGLE_CLIENT_ID) {
    GOOGLE_CLIENT_ID = window._env_.REACT_APP_GOOGLE_CLIENT_ID;
  }

  // Check if Google Client ID is properly configured
  const isGoogleConfigured = GOOGLE_CLIENT_ID &&
    GOOGLE_CLIENT_ID !== "your_google_client_id_here" &&
    GOOGLE_CLIENT_ID.includes('.apps.googleusercontent.com');

  const value = {
    clientId: GOOGLE_CLIENT_ID,
    isConfigured: isGoogleConfigured
  };

  // If Google OAuth is not configured, render children without GoogleOAuthProvider
  if (!isGoogleConfigured) {
    console.warn('Google OAuth not configured. Set REACT_APP_GOOGLE_CLIENT_ID in .env file or env-config.js');
    return (
      <GoogleAuthContext.Provider value={value}>
        {children}
      </GoogleAuthContext.Provider>
    );
  }

  return (
    <GoogleAuthContext.Provider value={value}>
      <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
        {children}
      </GoogleOAuthProvider>
    </GoogleAuthContext.Provider>
  );
};
