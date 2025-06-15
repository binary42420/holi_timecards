import React, {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {useSocket} from '../utils';
import { useAuth } from '../contexts/AuthContext';
import GoogleSignIn from './auth/GoogleSignIn';


function SignUpManager() {
    const navigate = useNavigate();
    const { socket } = useSocket();
    const { login } = useAuth();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [error, setError] = useState('');

    const handleSignUpManager = () => {
        const isManager = 1;
        const isActive = 1;

        if (socket && socket.readyState === WebSocket.OPEN) {
            const request = {
                request_id: 30,
                data: {username, password, isManager, isActive, name},
            };
            socket.send(JSON.stringify(request));
            navigate('/manager-profile');
        } else {
            console.log('Not connected to the server');
        }
    };

    const handleGoogleSuccess = async (result) => {
        if (result.needsSignup) {
            // Handle Google signup for manager
            try {
                const request = {
                    request_id: 70, // GOOGLE_SIGNUP_MANAGER
                    data: {
                        username: result.googleData.email.split('@')[0], // Default username from email
                        name: result.googleData.name,
                        email: result.googleData.email,
                        googleData: result.googleData
                    }
                };

                socket.send(JSON.stringify(request));
            } catch (error) {
                setError('Google signup failed. Please try again.');
            }
        } else if (result.username) {
            // User successfully signed up
            login(result.username, null, result.isManager, true);
            navigate('/manager-profile');
        }
    };

    const handleGoogleError = (errorMessage) => {
        setError(errorMessage);
    };

    return (
        <div className="signup-container">
            <div className="signup-form">
                <h2>Manager Registration</h2>
                <p>Create your manager account to oversee shifts and employees</p>

                {error && <div className="error-message">{error}</div>}

                {/* Google Signup Option */}
                <div className="google-signup-section">
                    <GoogleSignIn
                        onSuccess={handleGoogleSuccess}
                        onError={handleGoogleError}
                        buttonText="signup_with"
                    />
                    <div className="google-signup-note">
                        <small>Quick signup with your Google account</small>
                    </div>
                </div>

                <div className="divider">
                    <span>or fill out the form below</span>
                </div>

                <form>
                    <div>
                        <label htmlFor="managerUsername">Username:</label>
                        <input
                            type="text"
                            id="managerUsername"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                        />
                    </div>
                    <div>
                        <label htmlFor="managerPassword">Password:</label>
                        <input
                            type="password"
                            id="managerPassword"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>
                    <div>
                        <label htmlFor="name">Name:</label>
                        <input
                            type="text"
                            id="name"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                        />
                    </div>
                    <button type="button" onClick={handleSignUpManager}>
                        Create Manager Account
                    </button>
                </form>
            </div>
        </div>
    );
}

export default SignUpManager;
