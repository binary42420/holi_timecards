import React, {useState} from 'react';
import {Link, useNavigate} from 'react-router-dom';
import GoogleSignIn from './auth/GoogleSignIn';
import GoogleAccountLinking from './auth/GoogleAccountLinking';
import GoogleSignupCompletion from './auth/GoogleSignupCompletion';
import './../css/SignUp.css';

const SignUp = () => {
    const [role, setRole] = useState('');
    const [showGoogleLinking, setShowGoogleLinking] = useState(false);
    const [showGoogleSignup, setShowGoogleSignup] = useState(false);
    const [googleLinkingData, setGoogleLinkingData] = useState(null);
    const [googleSignupData, setGoogleSignupData] = useState(null);
    const navigate = useNavigate();

    const handleRoleChange = (event) => {
        setRole(event.target.value);
    };

    const handleGoogleSuccess = (result) => {
        if (result.needsLinking) {
            setGoogleLinkingData(result.googleData);
            setShowGoogleLinking(true);
        } else if (result.needsSignup) {
            // New user needs to complete signup with role selection
            setGoogleSignupData(result.googleData);
            setShowGoogleSignup(true);
        } else {
            // User successfully logged in with Google
            navigate(result.isManager ? '/manager-profile' : '/employee-profile');
        }
    };

    const handleGoogleError = (errorMessage) => {
        console.error('Google sign-up error:', errorMessage);
    };

    const handleLinkingSuccess = (userData) => {
        setShowGoogleLinking(false);
        setGoogleLinkingData(null);
        navigate(userData.isManager ? '/manager-profile' : '/employee-profile');
    };

    const handleLinkingCancel = () => {
        setShowGoogleLinking(false);
        setGoogleLinkingData(null);
    };

    const handleGoogleSignupComplete = (userData) => {
        setShowGoogleSignup(false);
        setGoogleSignupData(null);
        navigate(userData.isManager ? '/manager-profile' : '/employee-profile');
    };

    const handleGoogleSignupCancel = () => {
        setShowGoogleSignup(false);
        setGoogleSignupData(null);
    };

    // Show Google signup completion form if user needs to complete signup
    if (showGoogleSignup && googleSignupData) {
        return (
            <GoogleSignupCompletion
                googleData={googleSignupData}
                onComplete={handleGoogleSignupComplete}
                onCancel={handleGoogleSignupCancel}
            />
        );
    }

    // Show Google account linking if needed
    if (showGoogleLinking && googleLinkingData) {
        return (
            <GoogleAccountLinking
                googleData={googleLinkingData}
                onSuccess={handleLinkingSuccess}
                onCancel={handleLinkingCancel}
            />
        );
    }

    return (
        <div className="signup-container">
            <div className="signup-form">
                <h1>Join EasyShifts</h1>
                <p>Choose how you'd like to sign up</p>

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
                    <span>or</span>
                </div>

                {/* Traditional Role-based Signup */}
                <div className="traditional-signup-section">
                    <h2>Pick your role</h2>
                    <form>
                        <div>
                            <div className="icons-container">
                                <img src="/businessman.png" alt="Manager Icon" className="icon"/>
                            </div>
                            <label>
                                <input
                                    type="radio"
                                    value="manager"
                                    checked={role === 'manager'}
                                    onChange={handleRoleChange}
                                />
                                Manager
                            </label>
                        </div>
                        <div>
                            <div className="icons-container">
                                <img src="/worker.png" alt="Employee Icon" className="icon"/>
                            </div>
                            <label>
                                <input
                                    type="radio"
                                    value="employee"
                                    checked={role === 'employee'}
                                    onChange={handleRoleChange}
                                />
                                Employee
                            </label>
                        </div>
                        <div>
                            <div className="icons-container">
                                <img src="/businessman.png" alt="Client Icon" className="icon"/>
                            </div>
                            <label>
                                <input
                                    type="radio"
                                    value="client"
                                    checked={role === 'client'}
                                    onChange={handleRoleChange}
                                />
                                Client
                            </label>
                        </div>
                        <Link
                            to={role === 'manager' ? '/SignUpManager' : (role === 'employee' ? '/SignUpEmployee' : (role === 'client' ? '/SignUpClient' : '/signup'))}>
                            <button disabled={!role}>Continue with Form</button>
                        </Link>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default SignUp;
