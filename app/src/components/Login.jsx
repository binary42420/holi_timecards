import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useGoogleAuth } from '../contexts/GoogleAuthContext';
import GoogleSignIn from './auth/GoogleSignIn';
import GoogleAccountLinking from './auth/GoogleAccountLinking';
import WebSocketDiagnosticPanel from './WebSocketDiagnosticPanel';
import './../css/Login.css';

function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showGoogleLinking, setShowGoogleLinking] = useState(false);
    const [googleLinkingData, setGoogleLinkingData] = useState(null);
    const [showDiagnostic, setShowDiagnostic] = useState(false);
    const { login, isAuthenticated, isManager } = useAuth();
    const { isConfigured } = useGoogleAuth();
    const navigate = useNavigate();
    const location = useLocation();

    // Redirect if already authenticated
    useEffect(() => {
        if (isAuthenticated) {
            const from = location.state?.from?.pathname || (isManager ? '/manager-profile' : '/employee-profile');
            navigate(from, { replace: true });
        }
    }, [isAuthenticated, isManager, navigate, location]);

    const handleLogin = async () => {
        if (username.trim() === '' || password.trim() === '') {
            setError('Please fill in all fields');
            return;
        }

        setIsLoading(true);
        setError('');

        try {
            await login(username, password);
            // Navigation will be handled by the useEffect above
        } catch (error) {
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

    const handleGoogleSuccess = (result) => {
        if (result.needsLinking) {
            setGoogleLinkingData(result.googleData);
            setShowGoogleLinking(true);
        } else {
            // User successfully logged in with Google
            const from = location.state?.from?.pathname || (result.isManager ? '/manager-profile' : '/employee-profile');
            navigate(from, { replace: true });
        }
    };

    const handleGoogleError = (errorMessage) => {
        setError(errorMessage);
    };

    const handleLinkingSuccess = (userData) => {
        setShowGoogleLinking(false);
        setGoogleLinkingData(null);
        const from = location.state?.from?.pathname || (userData.isManager ? '/manager-profile' : '/employee-profile');
        navigate(from, { replace: true });
    };

    const handleLinkingCancel = () => {
        setShowGoogleLinking(false);
        setGoogleLinkingData(null);
    };

    return (
        <>
            <div className="login-container">
                <div className="login-form">
                    <h2 className="login-title">Sign In to Hands on Labor</h2>
                    <p className="login-subtitle">Access your EasyShifts dashboard</p>

                    {error && (
                        <div className="error-message">
                            <span className="error-icon">⚠️</span>
                            {error}
                        </div>
                    )}

                    <GoogleSignIn
                        onSuccess={handleGoogleSuccess}
                        onError={handleGoogleError}
                        buttonText="sign_in_with"
                    />

                    {!isConfigured && (
                        <div className="oauth-setup-link">
                            <a href="/google-oauth-setup" target="_blank" rel="noopener noreferrer">
                                ⚙️ Setup Google Sign-In
                            </a>
                        </div>
                    )}

                    <div className="divider">
                        <span>or</span>
                    </div>

                    <div className="form-group">
                        <label htmlFor="username">Username:</label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            onKeyPress={handleKeyPress}
                            disabled={isLoading}
                            placeholder="Enter your username"
                            required
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
                            disabled={isLoading}
                            placeholder="Enter your password"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className="login-button"
                        onClick={handleLogin}
                        disabled={isLoading}
                    >
                        {isLoading ? 'Signing in...' : 'Sign In'}
                    </button>

                    <div className="signup-link">
                        Don't have an account? <a href="/signup">Sign Up</a>
                    </div>
                </div>
            </div>

            {showGoogleLinking && googleLinkingData && (
                <GoogleAccountLinking
                    googleData={googleLinkingData}
                    onSuccess={handleLinkingSuccess}
                    onCancel={handleLinkingCancel}
                />
            )}
        </>
    );
}

export default Login;
