import React from 'react';
import { useEnhancedAuth } from '../contexts/EnhancedAuthContext';

const ConnectionStatusIndicator = ({ showDetails = false, compact = false }) => {
  const { 
    connectionStatus, 
    authStatus, 
    isConnected, 
    isAuthenticated, 
    lastError,
    authError 
  } = useEnhancedAuth();

  const getStatusColor = () => {
    if (isConnected && isAuthenticated) return '#4CAF50'; // Green
    if (isConnected && !isAuthenticated) return '#FF9800'; // Orange
    if (connectionStatus === 'connecting' || connectionStatus === 'reconnecting') return '#2196F3'; // Blue
    if (connectionStatus === 'error' || connectionStatus === 'failed') return '#F44336'; // Red
    return '#9E9E9E'; // Gray
  };

  const getStatusText = () => {
    if (isConnected && isAuthenticated) return 'Connected & Authenticated';
    if (isConnected && authStatus === 'authenticating') return 'Authenticating...';
    if (isConnected && !isAuthenticated) return 'Connected (Not Authenticated)';
    if (connectionStatus === 'connecting') return 'Connecting...';
    if (connectionStatus === 'reconnecting') return 'Reconnecting...';
    if (connectionStatus === 'error') return 'Connection Error';
    if (connectionStatus === 'failed') return 'Connection Failed';
    return 'Disconnected';
  };

  const getStatusIcon = () => {
    if (isConnected && isAuthenticated) return '🟢';
    if (isConnected && authStatus === 'authenticating') return '🔄';
    if (isConnected && !isAuthenticated) return '🟡';
    if (connectionStatus === 'connecting' || connectionStatus === 'reconnecting') return '🔄';
    if (connectionStatus === 'error' || connectionStatus === 'failed') return '🔴';
    return '⚫';
  };

  if (compact) {
    return (
      <div style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        fontSize: '12px',
        color: getStatusColor(),
        padding: '2px 6px',
        borderRadius: '4px',
        backgroundColor: 'rgba(0,0,0,0.05)'
      }}>
        <span>{getStatusIcon()}</span>
        <span>{getStatusText()}</span>
      </div>
    );
  }

  return (
    <div style={{
      padding: '12px',
      margin: '8px 0',
      borderRadius: '8px',
      backgroundColor: '#f5f5f5',
      border: `2px solid ${getStatusColor()}`,
      fontFamily: 'monospace'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        marginBottom: showDetails ? '8px' : '0'
      }}>
        <span style={{ fontSize: '16px' }}>{getStatusIcon()}</span>
        <span style={{ 
          fontWeight: 'bold', 
          color: getStatusColor(),
          fontSize: '14px'
        }}>
          {getStatusText()}
        </span>
      </div>

      {showDetails && (
        <div style={{ fontSize: '12px', color: '#666' }}>
          <div>Connection: {connectionStatus}</div>
          <div>Authentication: {authStatus}</div>
          {(lastError || authError) && (
            <div style={{ 
              color: '#F44336', 
              marginTop: '4px',
              fontWeight: 'bold'
            }}>
              Error: {authError || lastError}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ConnectionStatusIndicator;
