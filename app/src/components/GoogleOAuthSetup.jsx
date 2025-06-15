import React, { useState } from 'react';
import { useGoogleAuth } from '../contexts/GoogleAuthContext';
import './GoogleOAuthSetup.css';

const GoogleOAuthSetup = () => {
  const { isConfigured, clientId } = useGoogleAuth();
  const [showInstructions, setShowInstructions] = useState(false);

  if (isConfigured) {
    return (
      <div className="oauth-setup-container">
        <div className="setup-status success">
          <span className="status-icon">✅</span>
          <div className="status-content">
            <h3>Google OAuth Configured</h3>
            <p>Google Sign-In is working properly!</p>
            <small>Client ID: {clientId?.substring(0, 20)}...</small>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="oauth-setup-container">
      <div className="setup-status error">
        <span className="status-icon">⚠️</span>
        <div className="status-content">
          <h3>Google OAuth Not Configured</h3>
          <p>Google Sign-In is currently unavailable.</p>
          <button 
            className="setup-btn"
            onClick={() => setShowInstructions(!showInstructions)}
          >
            {showInstructions ? 'Hide' : 'Show'} Setup Instructions
          </button>
        </div>
      </div>

      {showInstructions && (
        <div className="setup-instructions">
          <h4>🔧 Google OAuth Setup Instructions</h4>
          
          <div className="instruction-step">
            <h5>Step 1: Create Google Cloud Project</h5>
            <ol>
              <li>Go to <a href="https://console.cloud.google.com/" target="_blank" rel="noopener noreferrer">Google Cloud Console</a></li>
              <li>Create a new project or select existing one</li>
              <li>Name it "EasyShifts-OAuth" or similar</li>
            </ol>
          </div>

          <div className="instruction-step">
            <h5>Step 2: Enable Google Identity API</h5>
            <ol>
              <li>Go to "APIs & Services" → "Library"</li>
              <li>Search for "Google Identity" or "Google+ API"</li>
              <li>Click "Enable"</li>
            </ol>
          </div>

          <div className="instruction-step">
            <h5>Step 3: Create OAuth 2.0 Credentials</h5>
            <ol>
              <li>Go to "APIs & Services" → "Credentials"</li>
              <li>Click "Create Credentials" → "OAuth 2.0 Client IDs"</li>
              <li>Choose "Web application"</li>
              <li>Configure as follows:</li>
            </ol>
            
            <div className="config-example">
              <strong>Name:</strong> EasyShifts Web Client<br/>
              <strong>Authorized JavaScript origins:</strong><br/>
              <code>http://localhost:3000</code><br/>
              <code>http://127.0.0.1:3000</code><br/>
              <code>https://localhost:3000</code><br/>
              <strong>Authorized redirect URIs:</strong><br/>
              <code>http://localhost:3000</code><br/>
              <code>http://localhost:3000/signup</code><br/>
              <code>http://localhost:3000/login</code>
            </div>
          </div>

          <div className="instruction-step">
            <h5>Step 4: Configure Environment Variable</h5>
            <ol>
              <li>Copy the generated Client ID</li>
              <li>Open <code>app/.env</code> file</li>
              <li>Replace the placeholder:</li>
            </ol>
            
            <div className="config-example">
              <code>REACT_APP_GOOGLE_CLIENT_ID=your_actual_client_id.apps.googleusercontent.com</code>
            </div>
          </div>

          <div className="instruction-step">
            <h5>Step 5: Restart Application</h5>
            <ol>
              <li>Stop the development server (Ctrl+C)</li>
              <li>Run <code>npm start</code> again</li>
              <li>Google Sign-In should now work!</li>
            </ol>
          </div>

          <div className="troubleshooting">
            <h5>🔍 Troubleshooting Common Errors</h5>
            <ul>
              <li><strong>"The given origin is not allowed"</strong> - Add http://localhost:3000 to authorized origins</li>
              <li><strong>"Cross-Origin-Opener-Policy"</strong> - Try incognito mode or different browser</li>
              <li><strong>"Provided button width is invalid"</strong> - Fixed in latest version</li>
              <li><strong>"Authentication request timed out"</strong> - Check backend is running on port 8080</li>
              <li><strong>Popup blocked</strong> - Allow popups for localhost:3000</li>
              <li><strong>Still not working?</strong> - Clear browser cache and restart both servers</li>
            </ul>
          </div>

          <div className="help-note">
            <span className="help-icon">💡</span>
            <strong>Need Help?</strong> Make sure your .env file is in the correct location (app/.env) and restart the development server after making changes.
          </div>
        </div>
      )}
    </div>
  );
};

export default GoogleOAuthSetup;
