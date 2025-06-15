import React, { useState, useEffect } from 'react';
import { WebSocketDiagnostic } from '../utils/websocketDiagnostic';
import { useSocket } from '../utils';
import './WebSocketDiagnosticPanel.css';

const WebSocketDiagnosticPanel = ({ onClose }) => {
  const [diagnostic, setDiagnostic] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState(null);
  const { socket, connectionStatus, reconnect, isConnected, hasError } = useSocket();

  useEffect(() => {
    setDiagnostic(new WebSocketDiagnostic());
  }, []);

  const runDiagnostic = async () => {
    if (!diagnostic) return;
    
    setIsRunning(true);
    setResults(null);
    
    try {
      const diagnosticResults = await diagnostic.runFullDiagnostic();
      setResults(diagnosticResults);
      diagnostic.printResults();
    } catch (error) {
      console.error('Diagnostic failed:', error);
      setResults({
        success: false,
        error: error.message,
        testResults: diagnostic.getResults()
      });
    } finally {
      setIsRunning(false);
    }
  };

  const getStatusIcon = (success) => {
    return success ? '✅' : '❌';
  };

  const getStatusColor = (success) => {
    return success ? '#28a745' : '#dc3545';
  };

  return (
    <div className="diagnostic-panel-overlay">
      <div className="diagnostic-panel">
        <div className="diagnostic-header">
          <h3>🔍 WebSocket Connection Diagnostic</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="diagnostic-content">
          <div className="current-status">
            <h4>Current Connection Status</h4>
            <div className="status-grid">
              <div className="status-item">
                <span className="status-label">Connection Status:</span>
                <span className={`status-value ${connectionStatus}`}>
                  {connectionStatus.toUpperCase()}
                </span>
              </div>
              <div className="status-item">
                <span className="status-label">Is Connected:</span>
                <span className={`status-value ${isConnected ? 'connected' : 'disconnected'}`}>
                  {isConnected ? 'YES' : 'NO'}
                </span>
              </div>
              <div className="status-item">
                <span className="status-label">Has Error:</span>
                <span className={`status-value ${hasError ? 'error' : 'ok'}`}>
                  {hasError ? 'YES' : 'NO'}
                </span>
              </div>
              <div className="status-item">
                <span className="status-label">Socket State:</span>
                <span className="status-value">
                  {socket ? socket.readyState : 'No Socket'}
                </span>
              </div>
            </div>
          </div>

          <div className="diagnostic-actions">
            <button 
              className="btn btn-primary"
              onClick={runDiagnostic}
              disabled={isRunning}
            >
              {isRunning ? 'Running Diagnostic...' : 'Run Full Diagnostic'}
            </button>
            
            <button 
              className="btn btn-secondary"
              onClick={reconnect}
              disabled={isRunning}
            >
              Force Reconnect
            </button>
          </div>

          {results && (
            <div className="diagnostic-results">
              <h4>Diagnostic Results</h4>
              
              <div className="overall-status">
                <span className={`overall-result ${results.success ? 'success' : 'failure'}`}>
                  {getStatusIcon(results.success)} 
                  {results.success ? 'All Tests Passed' : 'Issues Detected'}
                </span>
              </div>

              {results.results && (
                <div className="test-summary">
                  <div className="test-item">
                    <span className="test-name">Environment Config:</span>
                    <span 
                      className="test-result"
                      style={{ color: getStatusColor(results.results.environmentConfig) }}
                    >
                      {getStatusIcon(results.results.environmentConfig)}
                    </span>
                  </div>
                  <div className="test-item">
                    <span className="test-name">WebSocket Connection:</span>
                    <span 
                      className="test-result"
                      style={{ color: getStatusColor(results.results.webSocketConnection) }}
                    >
                      {getStatusIcon(results.results.webSocketConnection)}
                    </span>
                  </div>
                  <div className="test-item">
                    <span className="test-name">Authentication Flow:</span>
                    <span 
                      className="test-result"
                      style={{ color: getStatusColor(results.results.authenticationFlow) }}
                    >
                      {getStatusIcon(results.results.authenticationFlow)}
                    </span>
                  </div>
                </div>
              )}

              {results.testResults && results.testResults.length > 0 && (
                <div className="detailed-results">
                  <h5>Detailed Test Results</h5>
                  <div className="test-list">
                    {results.testResults.map((test, index) => (
                      <div key={index} className={`test-detail ${test.success ? 'success' : 'failure'}`}>
                        <div className="test-header">
                          <span className="test-icon">{getStatusIcon(test.success)}</span>
                          <span className="test-title">{test.test}</span>
                          <span className="test-time">{new Date(test.timestamp).toLocaleTimeString()}</span>
                        </div>
                        <div className="test-message">{test.result}</div>
                        {test.details && (
                          <details className="test-details">
                            <summary>Details</summary>
                            <pre>{JSON.stringify(test.details, null, 2)}</pre>
                          </details>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {results.error && (
                <div className="error-message">
                  <h5>Error</h5>
                  <p>{results.error}</p>
                </div>
              )}
            </div>
          )}

          <div className="diagnostic-help">
            <h4>Troubleshooting Tips</h4>
            <ul>
              <li><strong>Connection Timeout:</strong> Check your internet connection and firewall settings</li>
              <li><strong>Authentication Errors:</strong> Verify Google OAuth configuration</li>
              <li><strong>Server Errors:</strong> The backend service may be down or restarting</li>
              <li><strong>Environment Issues:</strong> Check that REACT_APP_API_URL is correctly set</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WebSocketDiagnosticPanel;
