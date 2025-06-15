import React from 'react';
import './../css/Toolbar.css';
import {Link, useLocation, useNavigate} from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Toolbar = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { isAuthenticated, logout, username } = useAuth();

    // Don't show toolbar on home page for cleaner landing experience
    if (location.pathname === '/' || location.pathname === '/home') {
        return null;
    }

    const handleLogout = () => {
        logout();
        navigate('/', { replace: true });
    };

    return (
        <div className="toolbar">
            <Link to={isAuthenticated ? "/dashboard" : "/"} className="toolbar-logo">
                <h3>Hands on Labor</h3>
                <span className="toolbar-subtitle">EasyShifts</span>
            </Link>
            <div className="toolbar-nav">
                {isAuthenticated ? (
                    <>
                        <span className="user-info">Welcome, {username}</span>
                        <Link to="/dashboard" className="toolbar-link">Dashboard</Link>
                        <button onClick={handleLogout} className="toolbar-link logout-button">
                            Logout
                        </button>
                    </>
                ) : (
                    <>
                        <Link to="/" className="toolbar-link">Home</Link>
                        <Link to="/login" className="toolbar-link">Login</Link>
                    </>
                )}
            </div>
        </div>
    );
};

export default Toolbar;
