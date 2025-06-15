import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSocket } from '../utils';
import { useAuth } from '../contexts/AuthContext';
import GoogleSignIn from './auth/GoogleSignIn';
import './../css/SignUpEmployee.css';

const SignUpEmployee = () => {
    const { socket } = useSocket();
    const navigate = useNavigate();
    const { login } = useAuth();

    const [formData, setFormData] = useState({
        username: '',
        password: '',
        confirmPassword: '',
        name: '',
        email: '',
        phone: '',
        businessName: '',
        // Role certifications
        canCrewChief: false,
        canForklift: false,
        canTruck: false
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
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
                request_id: 20, // EMPLOYEE_SIGNUP
                data: {
                    username: formData.username,
                    password: formData.password,
                    name: formData.name,
                    email: formData.email,
                    phone: formData.phone,
                    businessName: formData.businessName,
                    certifications: {
                        canCrewChief: formData.canCrewChief,
                        canForklift: formData.canForklift,
                        canTruck: formData.canTruck
                    }
                }
            };

            socket.send(JSON.stringify(request));
        } catch (error) {
            setIsLoading(false);
            setError('An error occurred. Please try again.');
        }
    };

    const handleGoogleSuccess = async (result) => {
        if (result.needsSignup) {
            // Handle Google signup for employee
            try {
                const request = {
                    request_id: 69, // GOOGLE_SIGNUP_EMPLOYEE
                    data: {
                        username: result.googleData.email.split('@')[0], // Default username from email
                        name: result.googleData.name,
                        email: result.googleData.email,
                        businessName: formData.businessName || '',
                        googleData: result.googleData,
                        certifications: {
                            canCrewChief: formData.canCrewChief,
                            canForklift: formData.canForklift,
                            canTruck: formData.canTruck
                        }
                    }
                };

                socket.send(JSON.stringify(request));
            } catch (error) {
                setError('Google signup failed. Please try again.');
            }
        } else if (result.username) {
            // User successfully signed up
            login(result.username, null, result.isManager, true);
            navigate('/employee-profile');
        }
    };

    const handleGoogleError = (errorMessage) => {
        setError(errorMessage);
    };

    useEffect(() => {
        if (!socket) return;

        const handleMessage = (event) => {
            try {
                const response = JSON.parse(event.data);
                if (response.request_id === 20) {
                    setIsLoading(false);

                    if (response.success) {
                        navigate('/login', {
                            state: {
                                message: 'Employee account created successfully! Please wait for manager approval.'
                            }
                        });
                    } else {
                        setError(response.error || 'Failed to create employee account');
                    }
                }
            } catch (error) {
                setIsLoading(false);
                setError('Error processing server response');
            }
        };

        socket.addEventListener('message', handleMessage);
        return () => {
            socket.removeEventListener('message', handleMessage);
        };
    }, [socket, navigate]);

    return (
        <div className="signup-employee-container">
            <div className="signup-employee-form">
                <h2>Employee Registration</h2>
                <p>Join as a stagehand with optional specialized certifications</p>

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
                        <h3>Personal Information</h3>
                        <div className="form-group">
                            <label htmlFor="name">Full Name *</label>
                            <input
                                type="text"
                                id="name"
                                name="name"
                                value={formData.name}
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
                            <label htmlFor="businessName">Current/Previous Employer</label>
                            <input
                                type="text"
                                id="businessName"
                                name="businessName"
                                value={formData.businessName}
                                onChange={handleChange}
                                disabled={isLoading}
                                placeholder="Optional"
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

                    <div className="form-section">
                        <h3>Role Certifications</h3>
                        <p className="certification-note">
                            All employees start as Stagehands. Check the boxes below for additional roles you're certified for:
                        </p>

                        <div className="certifications-grid">
                            <div className="certification-item">
                                <input
                                    type="checkbox"
                                    id="canCrewChief"
                                    name="canCrewChief"
                                    checked={formData.canCrewChief}
                                    onChange={handleChange}
                                    disabled={isLoading}
                                />
                                <label htmlFor="canCrewChief" className="certification-label">
                                    <span className="cert-icon">👷‍♂️</span>
                                    <div>
                                        <strong>Crew Chief</strong>
                                        <p>Lead teams and coordinate shift operations</p>
                                    </div>
                                </label>
                            </div>

                            <div className="certification-item">
                                <input
                                    type="checkbox"
                                    id="canForklift"
                                    name="canForklift"
                                    checked={formData.canForklift}
                                    onChange={handleChange}
                                    disabled={isLoading}
                                />
                                <label htmlFor="canForklift" className="certification-label">
                                    <span className="cert-icon">🚜</span>
                                    <div>
                                        <strong>Forklift Operator</strong>
                                        <p>Operate forklifts and heavy machinery</p>
                                    </div>
                                </label>
                            </div>

                            <div className="certification-item">
                                <input
                                    type="checkbox"
                                    id="canTruck"
                                    name="canTruck"
                                    checked={formData.canTruck}
                                    onChange={handleChange}
                                    disabled={isLoading}
                                />
                                <label htmlFor="canTruck" className="certification-label">
                                    <span className="cert-icon">🚛</span>
                                    <div>
                                        <strong>Truck Driver</strong>
                                        <p>Drive pickup trucks and delivery vehicles</p>
                                    </div>
                                </label>
                            </div>
                        </div>
                    </div>

                    <div className="form-actions">
                        <button
                            type="submit"
                            className="submit-button"
                            disabled={isLoading}
                        >
                            {isLoading ? 'Creating Account...' : 'Create Employee Account'}
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

export default SignUpEmployee;