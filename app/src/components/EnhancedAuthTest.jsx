import React, { useState } from 'react';
import { EnhancedAuthProvider, useEnhancedAuth } from '../contexts/EnhancedAuthContext';
import ConnectionStatusIndicator from './ConnectionStatusIndicator';
import EnhancedLogin from './EnhancedLogin';

const AuthTestContent = () => {
  const { 
    user, 
    isAuthenticated, 
    isLoading, 
    login, 
    logout,
    connectionStatus,
    authStatus,
    isConnected,
    socketAuthenticated,
    lastError,
    authError
  } = useEnhancedAuth();

  const [testUsername, setTestUsername] = useState('admin');
  const [testPassword, setTestPassword] = useState('Hdfatboy1!');

  const handleTestLogin = async () => {
    try {
      await login(testUsername, testPassword);
    } catch (error) {
      console.error('Test login failed:', error);
    }
  };

  if (isLoading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h2>Loading Enhanced Authentication System...</h2>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <EnhancedLogin />;
  }

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Enhanced Authentication Test</h1>
      
      {/* Connection Status */}
      <div style={{ marginBottom: '20px' }}>
        <h3>Connection Status</h3>
        <ConnectionStatusIndicator showDetails={true} />
      </div>

      {/* User Information */}
      <div style={{ 
        marginBottom: '20px', 
        padding: '16px', 
        backgroundColor: '#f0f8ff', 
        borderRadius: '8px',
        border: '1px solid #b3d9ff'
      }}>
        <h3>User Information</h3>
        <div style={{ fontFamily: 'monospace', fontSize: '14px' }}>
          <div><strong>Username:</strong> {user?.username}</div>
          <div><strong>Is Manager:</strong> {user?.isManager ? 'Yes' : 'No'}</div>
          <div><strong>Is Admin:</strong> {user?.isAdmin ? 'Yes' : 'No'}</div>
          <div><strong>User ID:</strong> {user?.userId}</div>
          <div><strong>Email:</strong> {user?.email || 'Not set'}</div>
          <div><strong>Login Time:</strong> {user?.loginTime}</div>
        </div>
      </div>

      {/* System Status */}
      <div style={{ 
        marginBottom: '20px', 
        padding: '16px', 
        backgroundColor: '#f8f9fa', 
        borderRadius: '8px',
        border: '1px solid #dee2e6'
      }}>
        <h3>System Status</h3>
        <div style={{ fontFamily: 'monospace', fontSize: '14px' }}>
          <div><strong>Connection Status:</strong> {connectionStatus}</div>
          <div><strong>Auth Status:</strong> {authStatus}</div>
          <div><strong>Is Connected:</strong> {isConnected ? 'Yes' : 'No'}</div>
          <div><strong>Socket Authenticated:</strong> {socketAuthenticated ? 'Yes' : 'No'}</div>
          <div><strong>Context Authenticated:</strong> {isAuthenticated ? 'Yes' : 'No'}</div>
          {lastError && <div style={{ color: '#dc3545' }}><strong>Last Error:</strong> {lastError}</div>}
          {authError && <div style={{ color: '#dc3545' }}><strong>Auth Error:</strong> {authError}</div>}
        </div>
      </div>

      {/* Test Actions */}
      <div style={{ 
        marginBottom: '20px', 
        padding: '16px', 
        backgroundColor: '#fff3cd', 
        borderRadius: '8px',
        border: '1px solid #ffeaa7'
      }}>
        <h3>Test Actions</h3>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '16px' }}>
          <button
            onClick={logout}
            style={{
              padding: '8px 16px',
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
          
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: '8px 16px',
              backgroundColor: '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Refresh Page
          </button>
        </div>
        
        <div style={{ fontSize: '12px', color: '#856404' }}>
          <p><strong>Test Instructions:</strong></p>
          <ul>
            <li>Try logging out and back in</li>
            <li>Refresh the page to test session persistence</li>
            <li>Open browser dev tools to see detailed logs</li>
            <li>Navigate to other pages to test connection persistence</li>
          </ul>
        </div>
      </div>

      {/* Navigation Test */}
      <div style={{ 
        marginBottom: '20px', 
        padding: '16px', 
        backgroundColor: '#d1ecf1', 
        borderRadius: '8px',
        border: '1px solid #bee5eb'
      }}>
        <h3>Navigation Test</h3>
        <p>Test connection persistence across navigation:</p>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <a href="/dashboard" style={{ 
            padding: '8px 16px', 
            backgroundColor: '#007bff', 
            color: 'white', 
            textDecoration: 'none', 
            borderRadius: '4px' 
          }}>
            Dashboard
          </a>
          <a href="/manager-profile" style={{ 
            padding: '8px 16px', 
            backgroundColor: '#28a745', 
            color: 'white', 
            textDecoration: 'none', 
            borderRadius: '4px' 
          }}>
            Manager Profile
          </a>
          <a href="/employee-profile" style={{ 
            padding: '8px 16px', 
            backgroundColor: '#17a2b8', 
            color: 'white', 
            textDecoration: 'none', 
            borderRadius: '4px' 
          }}>
            Employee Profile
          </a>
        </div>
      </div>

      {/* Session Data */}
      <div style={{ 
        marginBottom: '20px', 
        padding: '16px', 
        backgroundColor: '#f8f9fa', 
        borderRadius: '8px',
        border: '1px solid #dee2e6'
      }}>
        <h3>Session Data</h3>
        <div style={{ fontFamily: 'monospace', fontSize: '12px' }}>
          <div><strong>localStorage:</strong></div>
          <pre style={{ backgroundColor: '#e9ecef', padding: '8px', borderRadius: '4px', overflow: 'auto' }}>
            {localStorage.getItem('holi_user') || 'No data'}
          </pre>
          <div><strong>sessionStorage:</strong></div>
          <pre style={{ backgroundColor: '#e9ecef', padding: '8px', borderRadius: '4px', overflow: 'auto' }}>
            {sessionStorage.getItem('holi_session') || 'No data'}
          </pre>
        </div>
      </div>
    </div>
  );
};

const EnhancedAuthTest = () => {
  return (
    <EnhancedAuthProvider>
      <AuthTestContent />
    </EnhancedAuthProvider>
  );
};

export default EnhancedAuthTest;
