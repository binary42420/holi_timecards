import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSocket } from '../utils';
import { useAuth } from '../contexts/AuthContext';
import GoogleSignIn from './auth/GoogleSignIn';
import '../css/SignUpClient.css';

const SignUpClient = () => {
    const [formData, setFormData] = useState({
        companyName: '',
        contactName: '',
        email: '',
        phone: '',
        address: '',
        username: '',
        password: '',
        confirmPassword: ''
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { socket } = useSocket();
    const navigate = useNavigate();
    const { login } = useAuth();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        // Validation
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (formData.password.length < 6) {
            setError('Password must be at least 6 characters long');
            return;
        }

        if (!socket || socket.readyState !== WebSocket.OPEN) {
            setError('Not connected to server. Please try again.');
            return;
        }

        setIsLoading(true);

        try {
            const request = {
                request_id: 301, // CLIENT_SIGNUP
                data: {
                    companyName: formData.companyName,
                    contactName: formData.contactName,
                    email: formData.email,
                    phone: formData.phone,
                    address: formData.address,
                    username: formData.username,
                    password: formData.password
                }
            };

            const handleMessage = (event) => {
                try {
                    const response = JSON.parse(event.data);
                    if (response.request_id === 301) {
                        socket.removeEventListener('message', handleMessage);
                        setIsLoading(false);
                        
                        if (response.success) {
                            navigate('/login', { 
                                state: { 
                                    message: 'Client account created successfully! Please log in.' 
                                } 
                            });
                        } else {
                            setError(response.error || 'Failed to create client account');
                        }
                    }
                } catch (error) {
                    socket.removeEventListener('message', handleMessage);
                    setIsLoading(false);
                    setError('Error processing server response');
                }
            };

            socket.addEventListener('message', handleMessage);
            socket.send(JSON.stringify(request));

            // Timeout after 10 seconds
            setTimeout(() => {
                socket.removeEventListener('message', handleMessage);
                if (isLoading) {
                    setIsLoading(false);
                    setError('Request timed out. Please try again.');
                }
            }, 10000);

        } catch (error) {
            setIsLoading(false);
            setError('An error occurred. Please try again.');
        }
    };

    const handleGoogleSuccess = async (result) => {
        if (result.needsSignup) {
            // Handle Google signup for client
            try {
                const request = {
                    request_id: 71, // GOOGLE_SIGNUP_CLIENT
                    data: {
                        username: result.googleData.email.split('@')[0], // Default username from email
                        name: result.googleData.name,
                        email: result.googleData.email,
                        companyName: formData.companyName || result.googleData.name + ' Company',
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
            navigate('/client-profile');
        }
    };

    const handleGoogleError = (errorMessage) => {
        setError(errorMessage);
    };

    return (
        <div className="signup-client-container">
            <div className="signup-client-form">
                <h2>Client Registration</h2>
                <p>Register your company to request staffing services</p>

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
                
                <form onSubmit={handleSubmit}>
                    <div className="form-section">
                        <h3>Company Information</h3>
                        <div className="form-group">
                            <label htmlFor="companyName">Company Name *</label>
                            <input
                                type="text"
                                id="companyName"
                                name="companyName"
                                value={formData.companyName}
                                onChange={handleChange}
                                required
                                disabled={isLoading}
                            />
                        </div>
                        
                        <div className="form-group">
                            <label htmlFor="contactName">Contact Person *</label>
                            <input
                                type="text"
                                id="contactName"
                                name="contactName"
                                value={formData.contactName}
                                onChange={handleChange}
                                required
                                disabled={isLoading}
                            />
                        </div>
                        
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="email">Email *</label>
                                <input
                                    type="email"
                                    id="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    required
                                    disabled={isLoading}
                                />
                            </div>
                            
                            <div className="form-group">
                                <label htmlFor="phone">Phone *</label>
                                <input
                                    type="tel"
                                    id="phone"
                                    name="phone"
                                    value={formData.phone}
                                    onChange={handleChange}
                                    required
                                    disabled={isLoading}
                                />
                            </div>
                        </div>
                        
                        <div className="form-group">
                            <label htmlFor="address">Address</label>
                            <textarea
                                id="address"
                                name="address"
                                value={formData.address}
                                onChange={handleChange}
                                rows="3"
                                disabled={isLoading}
                            />
                        </div>
                    </div>
                    
                    <div className="form-section">
                        <h3>Account Credentials</h3>
                        <div className="form-group">
                            <label htmlFor="username">Username *</label>
                            <input
                                type="text"
                                id="username"
                                name="username"
                                value={formData.username}
                                onChange={handleChange}
                                required
                                disabled={isLoading}
                            />
                        </div>
                        
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="password">Password *</label>
                                <input
                                    type="password"
                                    id="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    required
                                    disabled={isLoading}
                                />
                            </div>
                            
                            <div className="form-group">
                                <label htmlFor="confirmPassword">Confirm Password *</label>
                                <input
                                    type="password"
                                    id="confirmPassword"
                                    name="confirmPassword"
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                    required
                                    disabled={isLoading}
                                />
                            </div>
                        </div>
                    </div>
                    
                    <div className="form-actions">
                        <button 
                            type="submit" 
                            className="submit-button"
                            disabled={isLoading}
                        >
                            {isLoading ? 'Creating Account...' : 'Create Client Account'}
                        </button>
                        
                        <button 
                            type="button" 
                            className="back-button"
                            onClick={() => navigate('/signup')}
                            disabled={isLoading}
                        >
                            Back
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default SignUpClient;
