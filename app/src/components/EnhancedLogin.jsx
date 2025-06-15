import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useEnhancedAuth } from '../contexts/EnhancedAuthContext';
import ConnectionStatusIndicator from './ConnectionStatusIndicator';
import { logDebug, logError, logInfo } from '../utils/utils';
import './../css/Login.css';

function EnhancedLogin() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showConnectionDetails, setShowConnectionDetails] = useState(false);
    
    const { 
        login, 
        isAuthenticated, 
        isManager, 
        isLoading: authLoading,
        authError,
        connectionStatus,
        isConnected
    } = useEnhancedAuth();
    
    const navigate = useNavigate();
    const location = useLocation();

    // Redirect if already authenticated
    useEffect(() => {
        if (isAuthenticated) {
            const from = location.state?.from?.pathname || (isManager ? '/manager-profile' : '/employee-profile');
            logInfo('EnhancedLogin', 'User authenticated, redirecting', { to: from });
            navigate(from, { replace: true });
        }
    }, [isAuthenticated, isManager, navigate, location]);

    // Update error state from auth context
    useEffect(() => {
        if (authError) {
            setError(authError);
        }
    }, [authError]);

    const handleLogin = async () => {
        if (username.trim() === '' || password.trim() === '') {
            setError('Please fill in all fields');
            return;
        }

        if (!isConnected) {
            setError('Not connected to server. Please wait for connection or refresh the page.');
            return;
        }

        setIsLoading(true);
        setError('');

        try {
            logInfo('EnhancedLogin', 'Attempting login', { username });
            await login(username, password);
            logInfo('EnhancedLogin', 'Login successful');
            // Navigation will be handled by the useEffect above
        } catch (error) {
            logError('EnhancedLogin', 'Login failed', error);
            setError(error.message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            handleLogin();
        }
    };

    const getConnectionMessage = () => {
        switch (connectionStatus) {
            case 'connecting':
                return 'Connecting to server...';
            case 'reconnecting':
                return 'Reconnecting to server...';
            case 'error':
            case 'failed':
                return 'Connection failed. Please refresh the page.';
            case 'connected':
                return 'Connected to server';
            default:
                return 'Disconnected from server';
        }
    };

    const isFormDisabled = isLoading || authLoading || !isConnected;

    if (authLoading) {
        return (
            <div className="login-container">
                <div className="login-form">
                    <h2>EasyShifts</h2>
                    <div style={{ 
                        display: 'flex', 
                        justifyContent: 'center', 
                        alignItems: 'center', 
                        height: '200px',
                        fontSize: '18px',
                        color: '#666'
                    }}>
                        Loading...
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="login-container">
            <div className="login-form">
                <h2>EasyShifts</h2>
                <p>Sign in to your account</p>

                {/* Connection Status */}
                <ConnectionStatusIndicator 
                    showDetails={showConnectionDetails} 
                    compact={false}
                />
                
                <button 
                    type="button"
                    onClick={() => setShowConnectionDetails(!showConnectionDetails)}
                    style={{
                        background: 'none',
                        border: 'none',
                        color: '#007bff',
                        textDecoration: 'underline',
                        cursor: 'pointer',
                        fontSize: '12px',
                        marginBottom: '16px'
                    }}
                >
                    {showConnectionDetails ? 'Hide' : 'Show'} Connection Details
                </button>

                {/* Connection Message */}
                <div style={{
                    padding: '8px',
                    marginBottom: '16px',
                    borderRadius: '4px',
                    backgroundColor: isConnected ? '#e8f5e8' : '#ffe8e8',
                    color: isConnected ? '#2e7d2e' : '#d32f2f',
                    fontSize: '14px',
                    textAlign: 'center'
                }}>
                    {getConnectionMessage()}
                </div>

                {/* Error Display */}
                {error && (
                    <div className="error-message" style={{
                        padding: '12px',
                        marginBottom: '16px',
                        backgroundColor: '#ffebee',
                        color: '#c62828',
                        borderRadius: '4px',
                        border: '1px solid #ffcdd2'
                    }}>
                        {error}
                    </div>
                )}

                {/* Login Form */}
                <div className="form-group">
                    <label htmlFor="username">Username:</label>
                    <input
                        type="text"
                        id="username"
                        name="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        onKeyPress={handleKeyPress}
                        disabled={isFormDisabled}
                        placeholder="Enter your username"
                        required
                        style={{
                            opacity: isFormDisabled ? 0.6 : 1
                        }}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="password">Password:</label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        onKeyPress={handleKeyPress}
                        disabled={isFormDisabled}
                        placeholder="Enter your password"
                        required
                        style={{
                            opacity: isFormDisabled ? 0.6 : 1
                        }}
                    />
                </div>

                <button
                    type="submit"
                    className="login-button"
                    onClick={handleLogin}
                    disabled={isFormDisabled}
                    style={{
                        opacity: isFormDisabled ? 0.6 : 1,
                        cursor: isFormDisabled ? 'not-allowed' : 'pointer'
                    }}
                >
                    {isLoading ? 'Signing in...' : 'Sign In'}
                </button>

                {/* Quick Login Buttons for Testing */}
                <div style={{ marginTop: '20px', borderTop: '1px solid #eee', paddingTop: '20px' }}>
                    <p style={{ fontSize: '12px', color: '#666', marginBottom: '10px' }}>
                        Quick Login (for testing):
                    </p>
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                        <button
                            type="button"
                            onClick={() => {
                                setUsername('admin');
                                setPassword('Hdfatboy1!');
                            }}
                            disabled={isFormDisabled}
                            style={{
                                padding: '4px 8px',
                                fontSize: '12px',
                                backgroundColor: '#f0f0f0',
                                border: '1px solid #ccc',
                                borderRadius: '4px',
                                cursor: isFormDisabled ? 'not-allowed' : 'pointer',
                                opacity: isFormDisabled ? 0.6 : 1
                            }}
                        >
                            Admin
                        </button>
                        <button
                            type="button"
                            onClick={() => {
                                setUsername('manager');
                                setPassword('password');
                            }}
                            disabled={isFormDisabled}
                            style={{
                                padding: '4px 8px',
                                fontSize: '12px',
                                backgroundColor: '#f0f0f0',
                                border: '1px solid #ccc',
                                borderRadius: '4px',
                                cursor: isFormDisabled ? 'not-allowed' : 'pointer',
                                opacity: isFormDisabled ? 0.6 : 1
                            }}
                        >
                            Manager
                        </button>
                        <button
                            type="button"
                            onClick={() => {
                                setUsername('employee');
                                setPassword('pass');
                            }}
                            disabled={isFormDisabled}
                            style={{
                                padding: '4px 8px',
                                fontSize: '12px',
                                backgroundColor: '#f0f0f0',
                                border: '1px solid #ccc',
                                borderRadius: '4px',
                                cursor: isFormDisabled ? 'not-allowed' : 'pointer',
                                opacity: isFormDisabled ? 0.6 : 1
                            }}
                        >
                            Employee
                        </button>
                    </div>
                </div>

                <div style={{ marginTop: '20px', textAlign: 'center' }}>
                    <p style={{ fontSize: '12px', color: '#666' }}>
                        Don't have an account? <a href="/signup">Sign up here</a>
                    </p>
                </div>
            </div>
        </div>
    );
}

export default EnhancedLogin;
