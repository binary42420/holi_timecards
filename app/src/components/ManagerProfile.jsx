import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSocket } from '../utils';
import '../css/ManagerProfile.css';
import {SolarSettingsBoldDuotone} from "./Icons/SolarSettingsBoldDuotone";
import {UimSchedule} from "./Icons/UimSchedule";
import {FluentPeopleTeam20Filled} from "./Icons/Team";
import {UimClockNine} from "./Icons/UimClockNine";

const ManagerProfile = ({name = "Hands on Labor"}) => {
    const navigate = useNavigate();
    const { socket, connectionStatus } = useSocket();
    const [dashboardStats, setDashboardStats] = useState({
        totalEmployees: 0,
        upcomingShifts: 0,
        pendingRequests: 0,
        activeJobs: 0
    });
    const [recentActivity, setRecentActivity] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    const handleSettingsClick = () => {
        navigate('/manager-settings');
        // setShowSchedule(false); // Already removed
        //setShowWorkers(false);
       // setShowClientsDirectory(false);
    };

    const handleScheduleClick = () => {
        navigate('/manager-schedule');
       // setShowSettings(false);
       // setShowWorkers(false);
       // setShowClientsDirectory(false);
    };

    const handleWorkersClick = () => {
        navigate('/employeeListPage');
    };

    const handleClientsDirectoryClick = () => {
        navigate('/manager-clients');
        // setShowSettings(false); // Already removed
        // setShowSchedule(false); // Already removed
        // setShowWorkers(false); // Already removed
    };

    const handleJobManagementClick = () => {
        navigate('/manager-jobs');
        // Ensure other submenu states are false if they are rendered within this component
       // setShowSettings(false);
       // setShowSchedule(false);
       // setShowWorkers(false);
        // setShowClientsDirectory(false);
    };

    const handleTimesheetsClick = () => {
        navigate('/manager-timesheets');
    };

    const handleTrashBinClick = () => {
        navigate('/trash-bin');
    };

    // Fetch dashboard statistics
    useEffect(() => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            // Request dashboard stats
            const statsRequest = { request_id: 300 }; // MANAGER_DASHBOARD_STATS
            socket.send(JSON.stringify(statsRequest));
        }
    }, [socket]);

    useEffect(() => {
        if (!socket) return;

        const handleMessage = (event) => {
            try {
                const response = JSON.parse(event.data);
                if (response.request_id === 300 && response.success) {
                    setDashboardStats(response.data);
                    setIsLoading(false);
                } else if (response.request_id === 301 && response.success) {
                    setRecentActivity(response.data);
                }
            } catch (e) {
                console.error('Error parsing dashboard message:', e);
                setIsLoading(false);
            }
        };

        socket.addEventListener('message', handleMessage);
        return () => socket.removeEventListener('message', handleMessage);
    }, [socket]);

    const getConnectionStatusColor = () => {
        switch (connectionStatus) {
            case 'connected': return '#28a745';
            case 'connecting': case 'reconnecting': return '#ffc107';
            case 'disconnected': case 'failed': case 'error': return '#dc3545';
            default: return '#6c757d';
        }
    };

 return (
        <div className="full-page">
            <div className="manager-profile">
                <div className="profile-header">
                    <div className="header-title">{name} Management Dashboard</div>
                    <div className="connection-status" style={{ color: getConnectionStatusColor() }}>
                        ● {connectionStatus === 'connected' ? 'Connected' : connectionStatus}
                    </div>
                </div>

                {/* Dashboard Stats */}
                <div className="dashboard-stats">
                    <div className="stat-card">
                        <div className="stat-number">{dashboardStats.totalEmployees}</div>
                        <div className="stat-label">Total Employees</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-number">{dashboardStats.upcomingShifts}</div>
                        <div className="stat-label">Upcoming Shifts</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-number">{dashboardStats.pendingRequests}</div>
                        <div className="stat-label">Pending Requests</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-number">{dashboardStats.activeJobs}</div>
                        <div className="stat-label">Active Jobs</div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="quick-actions">
                    <h3>Quick Actions</h3>
                    <div className="action-buttons">
                        <button onClick={() => navigate('/enhanced-schedule')} className="quick-action-btn">
                            📅 Create Shift
                        </button>
                        <button onClick={() => navigate('/employeeListPage')} className="quick-action-btn">
                            👤 Add Employee
                        </button>
                        <button onClick={() => navigate('/manager-jobs')} className="quick-action-btn">
                            💼 New Job
                        </button>
                        <button onClick={() => navigate('/manager-timesheets')} className="quick-action-btn">
                            ⏰ Review Timesheets
                        </button>
                    </div>
                </div>

                <div className="menu">
                    <div className="icon-wrapper" onClick={handleSettingsClick}>
                        <SolarSettingsBoldDuotone className="icon" style={{width: '5em', height: '5em'}}/>
                        <br/>
                        Settings
                    </div>

                    <div className="icon-wrapper" onClick={handleScheduleClick}>
                        <UimSchedule className="icon" style={{width: '5em', height: '5em'}}/>
                        <br/>
                        Schedule
                    </div>

                    <div className="icon-wrapper" onClick={handleWorkersClick} title="Enhanced Employee Directory">
                        <FluentPeopleTeam20Filled className="icon" style={{width: '5em', height: '5em'}}/>
                        <br/>
                        Employee Directory
                    </div>

                    <div className="icon-wrapper" onClick={handleClientsDirectoryClick}>
                        <UimClockNine className="icon" style={{width: '5em', height: '5em'}}/>
                        <br/>
                        Clients Directory
                    </div>

                    <div className="icon-wrapper" onClick={handleJobManagementClick}>
                        <UimSchedule className="icon" style={{width: '5em', height: '5em'}}/>
                        <br/>
                        Job Management
                    </div>

                    <div className="icon-wrapper" onClick={handleTimesheetsClick}>
                        <UimClockNine className="icon" style={{width: '5em', height: '5em'}}/>
                        <br/>
                        Timesheets
                    </div>

                    <div className="icon-wrapper" onClick={handleTrashBinClick} title="Manage Deleted Items">
                        <div className="icon" style={{width: '5em', height: '5em', fontSize: '3em', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                            🗑️
                        </div>
                        <br/>
                        Trash Bin
                    </div>
                </div>
            </div>

        
        </div>
    );
};

export default ManagerProfile;