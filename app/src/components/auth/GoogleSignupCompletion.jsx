import React, { useState } from 'react';
import { useSocket } from '../../utils';
import { useAuth } from '../../contexts/AuthContext';
import './../../css/GoogleSignupCompletion.css';

const GoogleSignupCompletion = ({ googleData, onComplete, onCancel }) => {
    const [formData, setFormData] = useState({
        username: '',
        role: '',
        businessName: '', // For employees
        companyName: '', // For clients
        // Employee certifications
        canCrewChief: false,
        canForklift: false,
        canTruck: false
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { socket } = useSocket();
    const { login } = useAuth();

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
        if (!formData.username.trim()) {
            setError('Username is required');
            return;
        }

        if (!formData.role) {
            setError('Please select a role');
            return;
        }

        if (formData.role === 'employee' && !formData.businessName.trim()) {
            setError('Business name is required for employees');
            return;
        }

        if (formData.role === 'client' && !formData.companyName.trim()) {
            setError('Company name is required for clients');
            return;
        }

        if (!socket || socket.readyState !== WebSocket.OPEN) {
            setError('Not connected to server. Please try again.');
            return;
        }

        setIsLoading(true);

        try {
            // Prepare request data based on role
            let requestData = {
                username: formData.username,
                name: googleData.name,
                email: googleData.email,
                googleData: googleData
            };

            let requestId;

            if (formData.role === 'employee') {
                requestId = 69; // GOOGLE_SIGNUP_EMPLOYEE
                requestData.businessName = formData.businessName;
                requestData.certifications = {
                    canCrewChief: formData.canCrewChief,
                    canForklift: formData.canForklift,
                    canTruck: formData.canTruck
                };
            } else if (formData.role === 'manager') {
                requestId = 70; // GOOGLE_SIGNUP_MANAGER
            } else if (formData.role === 'client') {
                requestId = 71; // GOOGLE_SIGNUP_CLIENT
                requestData.companyName = formData.companyName;
            }

            const request = {
                request_id: requestId,
                data: requestData
            };

            console.log('Sending Google signup request:', request);

            // Set up response handler
            const handleResponse = (event) => {
                try {
                    console.log('Received response:', event.data);
                    const response = JSON.parse(event.data);

                    if (response.request_id === requestId) {
                        socket.removeEventListener('message', handleResponse);
                        setIsLoading(false);

                        console.log('Google signup response:', response);

                        if (response.success) {
                            console.log('Signup successful:', response.data);
                            // Auto-login the user
                            login(response.data.username, null, response.data.is_manager, true); // true for Google auth
                            onComplete(response.data);
                        } else {
                            console.error('Signup failed:', response.error);
                            setError(response.error || 'Signup failed');
                        }
                    }
                } catch (error) {
                    console.error('Error parsing response:', error);
                    setError('An error occurred. Please try again.');
                    setIsLoading(false);
                }
            };

            socket.addEventListener('message', handleResponse);
            socket.send(JSON.stringify(request));

        } catch (error) {
            setIsLoading(false);
            setError('An error occurred. Please try again.');
            console.error('Google signup error:', error);
        }
    };

    return (
        <div className="google-signup-completion-container">
            <div className="google-signup-completion-form">
                <div className="google-user-info">
                    <img src={googleData.picture} alt="Profile" className="google-profile-pic" />
                    <div className="google-user-details">
                        <h3>Welcome, {googleData.name}!</h3>
                        <p>{googleData.email}</p>
                    </div>
                </div>

                <h2>Complete Your Signup</h2>
                <p>Just a few more details to get you started</p>

                {error && <div className="error-message">{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="username">Username *</label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            placeholder="Choose a username"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Role *</label>
                        <div className="role-selection">
                            <label className="role-option">
                                <input
                                    type="radio"
                                    name="role"
                                    value="employee"
                                    checked={formData.role === 'employee'}
                                    onChange={handleChange}
                                />
                                <span>Employee</span>
                            </label>
                            <label className="role-option">
                                <input
                                    type="radio"
                                    name="role"
                                    value="manager"
                                    checked={formData.role === 'manager'}
                                    onChange={handleChange}
                                />
                                <span>Manager</span>
                            </label>
                            <label className="role-option">
                                <input
                                    type="radio"
                                    name="role"
                                    value="client"
                                    checked={formData.role === 'client'}
                                    onChange={handleChange}
                                />
                                <span>Client</span>
                            </label>
                        </div>
                    </div>

                    {/* Employee-specific fields */}
                    {formData.role === 'employee' && (
                        <>
                            <div className="form-group">
                                <label htmlFor="businessName">Business Name *</label>
                                <input
                                    type="text"
                                    id="businessName"
                                    name="businessName"
                                    value={formData.businessName}
                                    onChange={handleChange}
                                    placeholder="Enter business name"
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label>Certifications (Optional)</label>
                                <div className="certifications">
                                    <label className="certification-option">
                                        <input
                                            type="checkbox"
                                            name="canCrewChief"
                                            checked={formData.canCrewChief}
                                            onChange={handleChange}
                                        />
                                        <span>Crew Chief</span>
                                    </label>
                                    <label className="certification-option">
                                        <input
                                            type="checkbox"
                                            name="canForklift"
                                            checked={formData.canForklift}
                                            onChange={handleChange}
                                        />
                                        <span>Forklift Operator</span>
                                    </label>
                                    <label className="certification-option">
                                        <input
                                            type="checkbox"
                                            name="canTruck"
                                            checked={formData.canTruck}
                                            onChange={handleChange}
                                        />
                                        <span>Truck Driver</span>
                                    </label>
                                </div>
                            </div>
                        </>
                    )}

                    {/* Client-specific fields */}
                    {formData.role === 'client' && (
                        <div className="form-group">
                            <label htmlFor="companyName">Company Name *</label>
                            <input
                                type="text"
                                id="companyName"
                                name="companyName"
                                value={formData.companyName}
                                onChange={handleChange}
                                placeholder="Enter company name"
                                required
                            />
                        </div>
                    )}

                    <div className="form-actions">
                        <button
                            type="button"
                            onClick={onCancel}
                            className="cancel-button"
                            disabled={isLoading}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="submit-button"
                            disabled={isLoading}
                        >
                            {isLoading ? 'Creating Account...' : 'Complete Signup'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default GoogleSignupCompletion;
