/**
 * WebSocket Connection Diagnostic Tool
 * Helps diagnose and fix WebSocket connection issues
 */

import { logDebug, logError, logInfo, logWarning } from './utils';
import ENV from './env';

export class WebSocketDiagnostic {
  constructor() {
    this.testResults = [];
    this.connectionAttempts = 0;
  }

  addResult(test, result, success = true, details = null) {
    const timestamp = new Date().toISOString();
    this.testResults.push({
      timestamp,
      test,
      result,
      success,
      details
    });
    
    const logLevel = success ? logInfo : logError;
    logLevel('WebSocketDiagnostic', `${test}: ${result}`, details);
  }

  async testEnvironmentConfig() {
    logInfo('WebSocketDiagnostic', 'Testing environment configuration');
    
    try {
      const apiUrl = ENV.API_URL;
      const googleClientId = ENV.GOOGLE_CLIENT_ID;
      
      if (!apiUrl) {
        this.addResult('Environment Config', 'API_URL is missing', false);
        return false;
      }
      
      if (!apiUrl.startsWith('wss://') && !apiUrl.startsWith('ws://')) {
        this.addResult('Environment Config', 'API_URL must start with wss:// or ws://', false);
        return false;
      }
      
      if (!googleClientId) {
        this.addResult('Environment Config', 'Google Client ID is missing', false, {
          note: 'This may affect Google Sign-In functionality'
        });
      }
      
      this.addResult('Environment Config', 'Configuration looks good', true, {
        apiUrl,
        hasGoogleClientId: !!googleClientId
      });
      
      return true;
    } catch (error) {
      this.addResult('Environment Config', 'Failed to check configuration', false, error);
      return false;
    }
  }

  async testWebSocketConnection(timeout = 10000) {
    logInfo('WebSocketDiagnostic', 'Testing WebSocket connection');
    
    return new Promise((resolve) => {
      try {
        const wsUrl = ENV.API_URL;
        this.connectionAttempts++;
        
        logDebug('WebSocketDiagnostic', `Attempting connection to: ${wsUrl}`);
        
        const socket = new WebSocket(wsUrl);
        let resolved = false;
        
        const cleanup = () => {
          if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
            socket.close();
          }
        };
        
        const timeoutId = setTimeout(() => {
          if (!resolved) {
            resolved = true;
            cleanup();
            this.addResult('WebSocket Connection', 'Connection timeout', false, {
              timeout: `${timeout}ms`,
              attempt: this.connectionAttempts
            });
            resolve(false);
          }
        }, timeout);
        
        socket.onopen = () => {
          if (!resolved) {
            resolved = true;
            clearTimeout(timeoutId);
            this.addResult('WebSocket Connection', 'Connection successful', true, {
              attempt: this.connectionAttempts,
              readyState: socket.readyState
            });
            cleanup();
            resolve(true);
          }
        };
        
        socket.onerror = (error) => {
          if (!resolved) {
            resolved = true;
            clearTimeout(timeoutId);
            this.addResult('WebSocket Connection', 'Connection error', false, {
              error: error.message || 'Unknown error',
              attempt: this.connectionAttempts
            });
            cleanup();
            resolve(false);
          }
        };
        
        socket.onclose = (event) => {
          if (!resolved) {
            resolved = true;
            clearTimeout(timeoutId);
            this.addResult('WebSocket Connection', 'Connection closed unexpectedly', false, {
              code: event.code,
              reason: event.reason,
              wasClean: event.wasClean,
              attempt: this.connectionAttempts
            });
            resolve(false);
          }
        };
        
      } catch (error) {
        this.addResult('WebSocket Connection', 'Failed to create connection', false, error);
        resolve(false);
      }
    });
  }

  async testAuthenticationFlow() {
    logInfo('WebSocketDiagnostic', 'Testing authentication flow');
    
    return new Promise((resolve) => {
      try {
        const wsUrl = ENV.API_URL;
        const socket = new WebSocket(wsUrl);
        let resolved = false;
        
        const cleanup = () => {
          if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
            socket.close();
          }
        };
        
        const timeoutId = setTimeout(() => {
          if (!resolved) {
            resolved = true;
            cleanup();
            this.addResult('Authentication Flow', 'Test timeout', false);
            resolve(false);
          }
        }, 15000);
        
        socket.onopen = () => {
          logDebug('WebSocketDiagnostic', 'Sending test authentication request');
          
          // Send a test authentication request
          const testRequest = {
            request_id: 1, // LOGIN request
            data: {
              username: 'test',
              password: 'test'
            }
          };
          
          socket.send(JSON.stringify(testRequest));
        };
        
        socket.onmessage = (event) => {
          try {
            const response = JSON.parse(event.data);
            
            if (!resolved) {
              resolved = true;
              clearTimeout(timeoutId);
              
              if (response.request_id === 1) {
                this.addResult('Authentication Flow', 'Server responded to auth request', true, {
                  success: response.success,
                  hasError: !!response.error
                });
              } else {
                this.addResult('Authentication Flow', 'Received unexpected response', true, {
                  request_id: response.request_id
                });
              }
              
              cleanup();
              resolve(true);
            }
          } catch (error) {
            if (!resolved) {
              resolved = true;
              clearTimeout(timeoutId);
              this.addResult('Authentication Flow', 'Failed to parse server response', false, error);
              cleanup();
              resolve(false);
            }
          }
        };
        
        socket.onerror = (error) => {
          if (!resolved) {
            resolved = true;
            clearTimeout(timeoutId);
            this.addResult('Authentication Flow', 'WebSocket error during auth test', false, error);
            cleanup();
            resolve(false);
          }
        };
        
      } catch (error) {
        this.addResult('Authentication Flow', 'Failed to test authentication', false, error);
        resolve(false);
      }
    });
  }

  async runFullDiagnostic() {
    logInfo('WebSocketDiagnostic', 'Starting full WebSocket diagnostic');
    this.testResults = [];
    
    const results = {
      environmentConfig: await this.testEnvironmentConfig(),
      webSocketConnection: await this.testWebSocketConnection(),
      authenticationFlow: false
    };
    
    // Only test auth flow if connection works
    if (results.webSocketConnection) {
      results.authenticationFlow = await this.testAuthenticationFlow();
    }
    
    const overallSuccess = results.environmentConfig && results.webSocketConnection;
    
    this.addResult('Full Diagnostic', 
      overallSuccess ? 'All tests passed' : 'Some tests failed', 
      overallSuccess, 
      results
    );
    
    return {
      success: overallSuccess,
      results,
      testResults: this.testResults
    };
  }

  getResults() {
    return this.testResults;
  }

  printResults() {
    console.group('🔍 WebSocket Diagnostic Results');
    this.testResults.forEach(result => {
      const icon = result.success ? '✅' : '❌';
      console.log(`${icon} ${result.test}: ${result.result}`);
      if (result.details) {
        console.log('   Details:', result.details);
      }
    });
    console.groupEnd();
  }
}

export default WebSocketDiagnostic;
