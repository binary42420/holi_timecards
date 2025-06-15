import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useSocket } from '../utils';
import { createAuthenticatedRequest } from '../utils/sessionUtils';
import '../css/AuthenticatedHome.css';

const AuthenticatedHome = () => {
    const { user, isManager, logout } = useAuth();
    const navigate = useNavigate();
    const { socket } = useSocket();
    const [userProfile, setUserProfile] = useState(null);
    const [loading, setLoading] = useState(true);

    // Employee-specific state for shifts
    const [upcomingShifts, setUpcomingShifts] = useState([]);
    const [recentShifts, setRecentShifts] = useState([]);
    const [shiftsLoading, setShiftsLoading] = useState(false);

    // Function to fetch employee shifts
    const fetchEmployeeShifts = () => {
        if (socket && socket.readyState === WebSocket.OPEN && !isManager) {
            setShiftsLoading(true);
            const shiftsRequest = createAuthenticatedRequest(1020); // GET_USER_SHIFTS
            socket.send(JSON.stringify(shiftsRequest));
        }
    };

    useEffect(() => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            // Fetch user profile
            const profileRequest = { request_id: 70 }; // SEND_PROFILE
            socket.send(JSON.stringify(profileRequest));

            const handleMessage = (event) => {
                try {
                    const response = JSON.parse(event.data);
                    if (response.request_id === 70 && response.success) {
                        setUserProfile(response.data);
                        setLoading(false);

                        // Fetch shifts for employees after profile is loaded
                        if (!isManager) {
                            fetchEmployeeShifts();
                        }
                    } else if (response.request_id === 1020 && response.success) {
                        // Handle user shifts response
                        const shifts = response.data.shifts || [];
                        const now = new Date();

                        // Separate upcoming and recent shifts
                        const upcoming = shifts.filter(shift => {
                            const shiftDate = new Date(shift.shift_date);
                            return shiftDate >= now;
                        }).slice(0, 5); // Show max 5 upcoming shifts

                        const recent = shifts.filter(shift => {
                            const shiftDate = new Date(shift.shift_date);
                            return shiftDate < now;
                        }).slice(0, 5); // Show max 5 recent shifts

                        setUpcomingShifts(upcoming);
                        setRecentShifts(recent);
                        setShiftsLoading(false);
                    }
                } catch (error) {
                    console.error('Error parsing response:', error);
                    setLoading(false);
                    setShiftsLoading(false);
                }
            };

            socket.addEventListener('message', handleMessage);
            return () => socket.removeEventListener('message', handleMessage);
        } else {
            setLoading(false);
        }
    }, [socket, isManager]);

    const handleLogout = async () => {
        try {
            await logout();
            navigate('/');
        } catch (error) {
            console.error('Logout error:', error);
        }
    };

    const getGreeting = () => {
        const hour = new Date().getHours();
        if (hour < 12) return 'Good morning';
        if (hour < 17) return 'Good afternoon';
        return 'Good evening';
    };

    const getPersonalizedGreeting = () => {
        const greeting = getGreeting();
        const fullName = userProfile?.name || user?.username || 'User';
        const nameParts = fullName.split(' ');
        const firstName = nameParts[0];
        const lastName = nameParts.slice(1).join(' ');

        return `${greeting}, ${firstName}${lastName ? ' ' + lastName : ''}`;
    };

    const getTimecardStatus = (shift) => {
        if (!shift.timecard_status) {
            return { text: 'Not Received', color: '#6c757d', icon: '⏳' };
        }

        switch (shift.timecard_status.toLowerCase()) {
            case 'submitted':
            case 'pending':
                return { text: 'Pending Approval', color: '#ffc107', icon: '⏱️' };
            case 'approved':
                return { text: 'Approved', color: '#28a745', icon: '✅' };
            case 'rejected':
                return { text: 'Rejected', color: '#dc3545', icon: '❌' };
            default:
                return { text: 'Not Received', color: '#6c757d', icon: '⏳' };
        }
    };

    const managerQuickActions = [
        { title: 'Employee Directory', icon: '👥', path: '/employeeListPage', description: 'Manage your workforce' },
        { title: 'Schedule Management', icon: '📅', path: '/enhanced-schedule', description: 'Create and manage shifts' },
        { title: 'Client Companies', icon: '🏢', path: '/manager-clients', description: 'Manage client relationships' },
        { title: 'Job Management', icon: '💼', path: '/manager-jobs', description: 'Oversee active projects' },
        { title: 'Timesheets', icon: '⏰', path: '/manager-timesheets', description: 'Review and approve hours' },
        { title: 'Shift Requests', icon: '📋', path: '/managerViewShiftsRequests', description: 'Handle worker requests' }
    ];

    const employeeQuickActions = [
        { title: 'My Profile', icon: '👤', path: '/employee-profile', description: 'Update your information' },
        { title: 'My Shifts', icon: '📅', path: '/shiftsPage', description: 'View your schedule' },
        { title: 'Request Shifts', icon: '✋', path: '/signInShifts', description: 'Submit availability' },
        { title: 'Crew Chief Dashboard', icon: '👷‍♂️', path: '/crew-chief-dashboard', description: 'Manage your crew', condition: userProfile?.role?.includes('Crew Chief') }
    ];

    const quickActions = isManager ? managerQuickActions : employeeQuickActions.filter(action => !action.condition || action.condition);

    if (loading) {
        return (
            <div className="authenticated-home loading">
                <div className="loading-spinner">
                    <div className="spinner"></div>
                    <p>Loading your dashboard...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="authenticated-home">
            {/* Header Section */}
            <section className="dashboard-header">
                <div className="container">
                    <div className="header-content">
                        <div className="welcome-section">
                            <h1 className="welcome-title">
                                {getPersonalizedGreeting()}!
                            </h1>
                            <p className="welcome-subtitle">
                                Welcome to your Hands on Labor dashboard
                            </p>
                            <div className="user-info">
                                <span className="user-role">
                                    {isManager ? '👔 Manager' : '👷 Worker'}
                                </span>
                                {userProfile?.workplace && (
                                    <span className="user-workplace">
                                        📍 {userProfile.workplace}
                                    </span>
                                )}
                            </div>
                        </div>
                        <div className="header-actions">
                            <button onClick={handleLogout} className="logout-btn">
                                🚪 Sign Out
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            {/* Quick Actions Grid */}
            <section className="quick-actions-section">
                <div className="container">
                    <h2 className="section-title">Quick Actions</h2>
                    <div className="actions-grid">
                        {quickActions.map((action, index) => (
                            <Link 
                                key={index} 
                                to={action.path} 
                                className="action-card"
                            >
                                <div className="action-icon">{action.icon}</div>
                                <h3 className="action-title">{action.title}</h3>
                                <p className="action-description">{action.description}</p>
                                <div className="action-arrow">→</div>
                            </Link>
                        ))}
                    </div>
                </div>
            </section>

            {/* Employee Shifts Sections - Only show for employees */}
            {!isManager && (
                <>
                    {/* Upcoming Shifts Section */}
                    <section className="employee-shifts-section">
                        <div className="container">
                            <h2 className="section-title">My Upcoming Shifts</h2>
                            {shiftsLoading ? (
                                <div className="shifts-loading">
                                    <div className="spinner"></div>
                                    <p>Loading your shifts...</p>
                                </div>
                            ) : upcomingShifts.length > 0 ? (
                                <div className="shifts-grid">
                                    {upcomingShifts.map((shift, index) => {
                                        const status = getTimecardStatus(shift);
                                        return (
                                            <div key={index} className="shift-card upcoming">
                                                <div className="shift-header">
                                                    <div className="shift-date">
                                                        📅 {new Date(shift.shift_date).toLocaleDateString('en-US', {
                                                            weekday: 'short',
                                                            month: 'short',
                                                            day: 'numeric'
                                                        })}
                                                    </div>
                                                    <div className="shift-role">
                                                        {shift.role_assigned || 'Worker'}
                                                    </div>
                                                </div>
                                                <div className="shift-details">
                                                    <h4 className="shift-job">{shift.job_name || 'General Labor'}</h4>
                                                    <p className="shift-client">{shift.client_company_name || 'Hands on Labor'}</p>
                                                    <p className="shift-location">{shift.venue_name || 'Various Locations'}</p>
                                                </div>
                                                <div className="shift-status">
                                                    <span
                                                        className="status-badge"
                                                        style={{ backgroundColor: status.color }}
                                                    >
                                                        {status.icon} {status.text}
                                                    </span>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            ) : (
                                <div className="no-shifts">
                                    <div className="no-shifts-icon">📅</div>
                                    <h3>No Upcoming Shifts</h3>
                                    <p>You don't have any upcoming shifts scheduled.</p>
                                    <Link to="/signInShifts" className="request-shifts-btn">
                                        ✋ Request Shifts
                                    </Link>
                                </div>
                            )}
                        </div>
                    </section>

                    {/* Recent Shifts Section */}
                    <section className="employee-shifts-section">
                        <div className="container">
                            <h2 className="section-title">My Recent Shifts</h2>
                            {shiftsLoading ? (
                                <div className="shifts-loading">
                                    <div className="spinner"></div>
                                    <p>Loading your shifts...</p>
                                </div>
                            ) : recentShifts.length > 0 ? (
                                <div className="shifts-grid">
                                    {recentShifts.map((shift, index) => {
                                        const status = getTimecardStatus(shift);
                                        return (
                                            <div key={index} className="shift-card recent">
                                                <div className="shift-header">
                                                    <div className="shift-date">
                                                        📅 {new Date(shift.shift_date).toLocaleDateString('en-US', {
                                                            weekday: 'short',
                                                            month: 'short',
                                                            day: 'numeric'
                                                        })}
                                                    </div>
                                                    <div className="shift-role">
                                                        {shift.role_assigned || 'Worker'}
                                                    </div>
                                                </div>
                                                <div className="shift-details">
                                                    <h4 className="shift-job">{shift.job_name || 'General Labor'}</h4>
                                                    <p className="shift-client">{shift.client_company_name || 'Hands on Labor'}</p>
                                                    <p className="shift-location">{shift.venue_name || 'Various Locations'}</p>
                                                </div>
                                                <div className="shift-status">
                                                    <span
                                                        className="status-badge"
                                                        style={{ backgroundColor: status.color }}
                                                    >
                                                        {status.icon} {status.text}
                                                    </span>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            ) : (
                                <div className="no-shifts">
                                    <div className="no-shifts-icon">📋</div>
                                    <h3>No Recent Shifts</h3>
                                    <p>You haven't worked any shifts recently.</p>
                                    <Link to="/shiftsPage" className="view-shifts-btn">
                                        📅 View All Shifts
                                    </Link>
                                </div>
                            )}
                        </div>
                    </section>
                </>
            )}

            {/* Recent Activity Section */}
            <section className="recent-activity-section">
                <div className="container">
                    <h2 className="section-title">Recent Activity</h2>
                    <div className="activity-cards">
                        <div className="activity-card">
                            <div className="activity-icon">📊</div>
                            <div className="activity-content">
                                <h3>System Status</h3>
                                <p>All systems operational</p>
                                <span className="activity-time">Just now</span>
                            </div>
                        </div>
                        <div className="activity-card">
                            <div className="activity-icon">🔔</div>
                            <div className="activity-content">
                                <h3>Welcome to EasyShifts</h3>
                                <p>Your dashboard is ready to use</p>
                                <span className="activity-time">Today</span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Company Info Footer */}
            <section className="company-info-section">
                <div className="container">
                    <div className="company-info">
                        <div className="company-brand">
                            <h3>Hands on Labor</h3>
                            <p>Professional Staffing Solutions • San Diego, CA</p>
                        </div>
                        <div className="company-links">
                            <a href="https://handsonlabor.com" target="_blank" rel="noopener noreferrer">
                                🌐 Visit Website
                            </a>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default AuthenticatedHome;
