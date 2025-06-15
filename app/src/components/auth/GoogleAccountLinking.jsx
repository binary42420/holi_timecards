import React, { useState } from 'react';
import { useSocket } from '../../utils';
import { useAuth } from '../../contexts/AuthContext';
import './GoogleAccountLinking.css';

const GoogleAccountLinking = ({ googleData, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [mode, setMode] = useState('link'); // 'link' or 'create'
  const { socket, waitForConnection, isConnected } = useSocket();
  const { googleLogin } = useAuth();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const handleLinkAccount = async (e) => {
    e.preventDefault();
    
    if (!formData.username.trim() || !formData.password.trim()) {
      setError('Please enter both username and password');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      // Ensure connection is available
      let activeSocket = socket;
      if (!isConnected) {
        try {
          activeSocket = await waitForConnection(10000);
        } catch (connectionError) {
          throw new Error('Could not establish server connection. Please try again.');
        }
      }

      const request = {
        request_id: 67, // LINK_GOOGLE_ACCOUNT
        data: {
          username: formData.username,
          password: formData.password,
          googleData: googleData
        }
      };

        const handleMessage = (event) => {
          try {
            const response = JSON.parse(event.data);
            
            if (response.request_id === 67) {
              activeSocket.removeEventListener('message', handleMessage);
              
              if (response.success) {
                // Account linked successfully, log user in
                const userData = {
                  username: formData.username,
                  isManager: response.data.is_manager,
                  loginTime: new Date().toISOString(),
                  googleLinked: true,
                  email: googleData.email
                };
                
                googleLogin(userData);
                
                if (onSuccess) {
                  onSuccess(userData);
                }
              } else {
                setError(response.error || 'Failed to link Google account');
              }
            }
          } catch (error) {
            activeSocket.removeEventListener('message', handleMessage);
            setError('Error processing response');
          } finally {
            setIsLoading(false);
          }
        };

        activeSocket.addEventListener('message', handleMessage);
        activeSocket.send(JSON.stringify(request));

        setTimeout(() => {
          activeSocket.removeEventListener('message', handleMessage);
          setIsLoading(false);
          setError('Request timed out');
        }, 10000);
    } catch (error) {
      setIsLoading(false);
      setError(error.message || 'Failed to link account');
    }
  };

  const handleCreateAccount = async (e) => {
    e.preventDefault();
    
    if (!formData.username.trim()) {
      setError('Please enter a username');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      // Ensure connection is available
      let activeSocket = socket;
      if (!isConnected) {
        try {
          activeSocket = await waitForConnection(10000);
        } catch (connectionError) {
          throw new Error('Could not establish server connection. Please try again.');
        }
      }

      const request = {
        request_id: 68, // CREATE_ACCOUNT_WITH_GOOGLE
        data: {
          username: formData.username,
          googleData: googleData,
          name: googleData.name,
          email: googleData.email
        }
      };

        const handleMessage = (event) => {
          try {
            const response = JSON.parse(event.data);
            
            if (response.request_id === 68) {
              activeSocket.removeEventListener('message', handleMessage);
              
              if (response.success) {
                // Account created successfully, log user in
                const userData = {
                  username: formData.username,
                  isManager: false, // New accounts are employees by default
                  loginTime: new Date().toISOString(),
                  googleLinked: true,
                  email: googleData.email
                };
                
                googleLogin(userData);
                
                if (onSuccess) {
                  onSuccess(userData);
                }
              } else {
                setError(response.error || 'Failed to create account');
              }
            }
          } catch (error) {
            activeSocket.removeEventListener('message', handleMessage);
            setError('Error processing response');
          } finally {
            setIsLoading(false);
          }
        };

        activeSocket.addEventListener('message', handleMessage);
        activeSocket.send(JSON.stringify(request));

        setTimeout(() => {
          activeSocket.removeEventListener('message', handleMessage);
          setIsLoading(false);
          setError('Request timed out');
        }, 10000);
    } catch (error) {
      setIsLoading(false);
      setError(error.message || 'Failed to create account');
    }
  };

  return (
    <div className="google-linking-container">
      <div className="google-linking-modal">
        <div className="modal-header">
          <h2>Link Google Account</h2>
          <button className="modal-close" onClick={onCancel}>
            ✕
          </button>
        </div>

        <div className="google-user-info">
          <div className="user-avatar">
            {googleData.picture ? (
              <img src={googleData.picture} alt="Profile" />
            ) : (
              <div className="avatar-placeholder">
                {googleData.name?.charAt(0)?.toUpperCase() || '?'}
              </div>
            )}
          </div>
          <div className="user-details">
            <h3>{googleData.name}</h3>
            <p>{googleData.email}</p>
          </div>
        </div>

        <div className="linking-options">
          <div className="option-tabs">
            <button 
              className={`tab ${mode === 'link' ? 'active' : ''}`}
              onClick={() => setMode('link')}
            >
              Link Existing Account
            </button>
            <button 
              className={`tab ${mode === 'create' ? 'active' : ''}`}
              onClick={() => setMode('create')}
            >
              Create New Account
            </button>
          </div>

          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}

          {mode === 'link' ? (
            <form onSubmit={handleLinkAccount} className="linking-form">
              <p className="form-description">
                Enter your existing EasyShifts credentials to link your Google account:
              </p>
              
              <div className="form-group">
                <label htmlFor="username">Username</label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="Enter your EasyShifts username"
                  disabled={isLoading}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">Password</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Enter your EasyShifts password"
                  disabled={isLoading}
                  required
                />
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={onCancel}
                  disabled={isLoading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={isLoading}
                >
                  {isLoading ? 'Linking...' : 'Link Account'}
                </button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleCreateAccount} className="linking-form">
              <p className="form-description">
                Create a new EasyShifts account linked to your Google account:
              </p>
              
              <div className="form-group">
                <label htmlFor="username">Choose Username</label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="Choose a username"
                  disabled={isLoading}
                  required
                />
              </div>

              <div className="info-note">
                <span className="info-icon">ℹ️</span>
                Your account will be created with your Google email and name. 
                You can sign in using either Google or your username.
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={onCancel}
                  disabled={isLoading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-success"
                  disabled={isLoading}
                >
                  {isLoading ? 'Creating...' : 'Create Account'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default GoogleAccountLinking;
