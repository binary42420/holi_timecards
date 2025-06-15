import React from 'react';
import { logError } from '../utils';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null,
      errorId: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Generate unique error ID for tracking
    const errorId = `ERR_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Log the error with comprehensive details
    logError('ErrorBoundary', 'React component error caught', {
      errorId,
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack
      },
      errorInfo: {
        componentStack: errorInfo.componentStack
      },
      props: this.props,
      url: window.location.href,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString()
    });

    // Update state with error details
    this.setState({
      error,
      errorInfo,
      errorId
    });

    // In production, send to error reporting service
    if (process.env.NODE_ENV === 'production') {
      this.reportError(error, errorInfo, errorId);
    }
  }

  reportError = (error, errorInfo, errorId) => {
    // Example: Send to error reporting service
    try {
      // You can integrate with services like Sentry, LogRocket, etc.
      if (window.gtag) {
        window.gtag('event', 'exception', {
          description: `${error.name}: ${error.message}`,
          fatal: true,
          custom_map: {
            error_id: errorId,
            component_stack: errorInfo.componentStack
          }
        });
      }
    } catch (reportingError) {
      logError('ErrorBoundary', 'Failed to report error', reportingError);
    }
  };

  handleRetry = () => {
    logError('ErrorBoundary', 'User triggered error recovery', { errorId: this.state.errorId });
    this.setState({ 
      hasError: false, 
      error: null, 
      errorInfo: null,
      errorId: null 
    });
  };

  handleReload = () => {
    logError('ErrorBoundary', 'User triggered page reload', { errorId: this.state.errorId });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // Custom error UI
      return (
        <div style={{
          padding: '40px',
          textAlign: 'center',
          backgroundColor: '#f8f9fa',
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center'
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '40px',
            borderRadius: '12px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
            maxWidth: '600px',
            width: '100%'
          }}>
            <h1 style={{ 
              color: '#dc3545', 
              marginBottom: '20px',
              fontSize: '2rem'
            }}>
              🚨 Something went wrong
            </h1>
            
            <p style={{ 
              color: '#6c757d', 
              marginBottom: '30px',
              fontSize: '1.1rem',
              lineHeight: '1.5'
            }}>
              We're sorry, but something unexpected happened. Our team has been notified.
            </p>

            {this.state.errorId && (
              <p style={{ 
                color: '#6c757d', 
                fontSize: '0.9rem',
                marginBottom: '30px',
                fontFamily: 'monospace',
                backgroundColor: '#f8f9fa',
                padding: '10px',
                borderRadius: '4px'
              }}>
                Error ID: {this.state.errorId}
              </p>
            )}

            <div style={{ 
              display: 'flex', 
              gap: '15px', 
              justifyContent: 'center',
              flexWrap: 'wrap'
            }}>
              <button
                onClick={this.handleRetry}
                style={{
                  backgroundColor: '#007bff',
                  color: 'white',
                  border: 'none',
                  padding: '12px 24px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '1rem',
                  fontWeight: '500'
                }}
              >
                Try Again
              </button>
              
              <button
                onClick={this.handleReload}
                style={{
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  padding: '12px 24px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '1rem',
                  fontWeight: '500'
                }}
              >
                Reload Page
              </button>
            </div>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details style={{ 
                marginTop: '30px', 
                textAlign: 'left',
                backgroundColor: '#f8f9fa',
                padding: '20px',
                borderRadius: '6px',
                border: '1px solid #dee2e6'
              }}>
                <summary style={{ 
                  cursor: 'pointer', 
                  fontWeight: 'bold',
                  marginBottom: '10px'
                }}>
                  Error Details (Development Only)
                </summary>
                <pre style={{ 
                  fontSize: '0.8rem', 
                  overflow: 'auto',
                  backgroundColor: 'white',
                  padding: '15px',
                  borderRadius: '4px',
                  border: '1px solid #dee2e6'
                }}>
                  {this.state.error.toString()}
                  {this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
