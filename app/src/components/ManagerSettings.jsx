import React, { useState, useEffect, useCallback } from "react";
import SettingsForm from "./SettingsForm";
import "../css/ManagerSetting.css";
import DateTime from 'react-datetime';
import 'react-datetime/css/react-datetime.css';
import { useSocket } from "../utils";
import ToggleSwitch from "./ToggleSwitch";

export default function ManagerSettings() {
    const { socket } = useSocket();

    // State for active tab
    const [activeTab, setActiveTab] = useState('basic');

    // State for Schedule Window
    const [startTime, setStartTime] = useState(new Date());
    const [endTime, setEndTime] = useState(new Date());
    const [isLoadingWindow, setIsLoadingWindow] = useState(false);
    const [windowSuccessMessage, setWindowSuccessMessage] = useState('');
    const [windowErrorMessage, setWindowErrorMessage] = useState('');

    // State for extended settings
    const [extendedSettings, setExtendedSettings] = useState({
        // User Management
        auto_approve_employees: false,
        require_manager_approval: true,
        allow_employee_self_registration: true,
        require_email_verification: true,
        employee_probation_period_days: 90,
        managers_can_create_employees: true,
        managers_can_edit_all_timesheets: true,
        managers_can_approve_overtime: true,
        managers_can_modify_rates: false,

        // Timesheet Settings
        require_photo_clock_in: false,
        require_location_verification: true,
        location_verification_radius_feet: 100,
        allow_early_clock_in_minutes: 15,
        allow_late_clock_out_minutes: 15,
        auto_clock_out_hours: 12,
        max_clock_pairs_per_shift: 3,
        require_break_documentation: true,
        auto_deduct_unpaid_breaks: true,

        // Notifications
        email_notifications_enabled: true,
        notify_on_shift_requests: true,
        notify_on_worker_assignments: true,
        notify_on_timesheet_submissions: true,
        notify_on_schedule_changes: true,
        sms_notifications_enabled: false,

        // Role Premiums
        crew_chief_premium_rate: 5.00,
        forklift_operators_premium_rate: 2.00,
        truck_drivers_premium_rate: 3.00,

        // Security
        password_min_length: 8,
        require_password_complexity: true,
        session_timeout_minutes: 480,
        max_login_attempts: 5,

        // Client Management
        clients_can_view_timesheets: true,
        clients_can_edit_timesheets: false,
        clients_can_request_workers: true,
        clients_can_modify_jobs: true,
        require_client_verification: true,
    });

    const [isLoadingSettings, setIsLoadingSettings] = useState(false);
    const [settingsSuccessMessage, setSettingsSuccessMessage] = useState('');
    const [settingsErrorMessage, setSettingsErrorMessage] = useState('');
    const [connectionStatus, setConnectionStatus] = useState('connecting');

    // Tab configuration
    const tabs = [
        { id: 'basic', label: 'Basic Settings', icon: '⚙️' },
        { id: 'schedule', label: 'Schedule Window', icon: '📅' },
        { id: 'users', label: 'User Management', icon: '👥' },
        { id: 'timesheets', label: 'Timesheet Settings', icon: '⏰' },
        { id: 'notifications', label: 'Notifications', icon: '🔔' },
        { id: 'roles', label: 'Role Premiums', icon: '💰' },
        { id: 'security', label: 'Security', icon: '🔒' },
        { id: 'clients', label: 'Client Settings', icon: '🏢' }
    ];

    const fetchRequestWindowTimes = useCallback(() => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            setIsLoadingWindow(true);
            setWindowErrorMessage('');
            setWindowSuccessMessage('');
            const request = { request_id: 42 }; // GET_REQUEST_WINDOW_TIMES
            socket.send(JSON.stringify(request));
        } else {
            setWindowErrorMessage("WebSocket is not connected. Cannot fetch window times.");
        }
    }, [socket]);

    // Fetch extended settings
    const fetchExtendedSettings = useCallback(() => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            setIsLoadingSettings(true);
            const request = { request_id: 1111 }; // GET_ALL_EXTENDED_SETTINGS
            socket.send(JSON.stringify(request));
        }
    }, [socket]);

    // Retry connection function
    const retryConnection = () => {
        setSettingsErrorMessage('');
        setConnectionStatus('connecting');
        // Force a page reload to reinitialize the WebSocket
        window.location.reload();
    };

    // Monitor connection status
    useEffect(() => {
        if (socket) {
            if (socket.readyState === WebSocket.CONNECTING) {
                setConnectionStatus('connecting');
            } else if (socket.readyState === WebSocket.OPEN) {
                setConnectionStatus('connected');
                fetchRequestWindowTimes();
                fetchExtendedSettings();
            } else if (socket.readyState === WebSocket.CLOSING) {
                setConnectionStatus('disconnecting');
            } else if (socket.readyState === WebSocket.CLOSED) {
                setConnectionStatus('disconnected');
            }

            // Add event listeners for connection state changes
            const handleOpen = () => {
                setConnectionStatus('connected');
                setSettingsErrorMessage('');
                fetchRequestWindowTimes();
                fetchExtendedSettings();
            };

            const handleClose = () => {
                setConnectionStatus('disconnected');
                setSettingsErrorMessage('Connection lost. Please refresh the page.');
            };

            const handleError = () => {
                setConnectionStatus('error');
                setSettingsErrorMessage('WebSocket connection error. Please check your internet connection.');
            };

            socket.addEventListener('open', handleOpen);
            socket.addEventListener('close', handleClose);
            socket.addEventListener('error', handleError);

            return () => {
                socket.removeEventListener('open', handleOpen);
                socket.removeEventListener('close', handleClose);
                socket.removeEventListener('error', handleError);
            };
        } else {
            setConnectionStatus('no-socket');
            setSettingsErrorMessage('WebSocket not available. Please refresh the page.');
        }
    }, [socket, fetchRequestWindowTimes, fetchExtendedSettings]);

    useEffect(() => {
        if (!socket) return;

        const handleMessage = (event) => {
            try {
                const response = JSON.parse(event.data);
                if (response.request_id === 42) { // Response for GET_REQUEST_WINDOW_TIMES
                    setIsLoadingWindow(false);
                    if (response.success && response.data) {
                        if (response.data.requests_window_start) {
                            setStartTime(new Date(response.data.requests_window_start));
                        }
                        if (response.data.requests_window_end) {
                            setEndTime(new Date(response.data.requests_window_end));
                        }
                    } else {
                        setWindowErrorMessage(response.error || "Failed to fetch request window times.");
                    }
                } else if (response.request_id === 992) { // Response for SAVE_SCHEDULE_WINDOW
                    setIsLoadingWindow(false);
                    if (response.success) {
                        setWindowSuccessMessage(response.message || "Schedule window saved successfully!");
                        setWindowErrorMessage('');
                    } else {
                        setWindowErrorMessage(response.error || "Failed to save schedule window.");
                        setWindowSuccessMessage('');
                    }
                } else if (response.request_id === 1111) { // Response for GET_ALL_EXTENDED_SETTINGS
                    setIsLoadingSettings(false);
                    if (response.success && response.data) {
                        setExtendedSettings(prev => ({
                            ...prev,
                            ...response.data.user_management,
                            ...response.data.timesheet_advanced,
                            ...response.data.notifications,
                            ...response.data.security,
                            ...response.data.client_management
                        }));
                    } else {
                        setSettingsErrorMessage(response.error || "Failed to fetch extended settings.");
                    }
                } else if ([1100, 1101, 1102, 1103, 1105, 1108].includes(response.request_id)) {
                    // Responses for various settings updates
                    setIsLoadingSettings(false);
                    if (response.success) {
                        setSettingsSuccessMessage("Settings saved successfully!");
                        setSettingsErrorMessage('');
                    } else {
                        setSettingsErrorMessage(response.error || "Failed to save settings.");
                        setSettingsSuccessMessage('');
                    }
                }
            } catch (e) {
                setIsLoadingWindow(false);
                setIsLoadingSettings(false);
                setWindowErrorMessage("Error processing server response.");
                console.error('WebSocket message error in ManagerSettings:', e);
            }
        };

        socket.addEventListener('message', handleMessage);
        return () => {
            socket.removeEventListener('message', handleMessage);
        };
    }, [socket, fetchRequestWindowTimes]);

    // Settings update handlers
    const handleSettingChange = (field, value) => {
        setExtendedSettings(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleToggle = (field) => {
        setExtendedSettings(prev => ({
            ...prev,
            [field]: !prev[field]
        }));
    };

    const saveSettings = (category, requestId) => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            setIsLoadingSettings(true);
            setSettingsSuccessMessage('');
            setSettingsErrorMessage('');

            const request = {
                request_id: requestId,
                data: extendedSettings
            };

            try {
                socket.send(JSON.stringify(request));
                console.log(`Sending ${category} settings:`, request);
            } catch (error) {
                setIsLoadingSettings(false);
                setSettingsErrorMessage(`Failed to send settings: ${error.message}`);
            }
        } else {
            const statusMessage = connectionStatus === 'connecting'
                ? "Still connecting to server. Please wait..."
                : connectionStatus === 'disconnected'
                ? "Connection lost. Please refresh the page."
                : "Socket not connected. Cannot save settings.";
            setSettingsErrorMessage(statusMessage);
        }
    };

    function handleWindowSubmit(event) {
        event.preventDefault();
        setWindowSuccessMessage('');
        setWindowErrorMessage('');

        if (!(startTime instanceof Date && !isNaN(startTime)) || !(endTime instanceof Date && !isNaN(endTime))) {
            setWindowErrorMessage("Invalid date selected for start or end time.");
            return;
        }

        if (endTime <= startTime) {
            setWindowErrorMessage("End time must be after start time.");
            return;
        }

        if (socket && socket.readyState === WebSocket.OPEN) {
            setIsLoadingWindow(true);
            const request = {
                request_id: 992, // SAVE_SCHEDULE_WINDOW
                data: {
                    requests_window_start: startTime.toISOString(),
                    requests_window_end: endTime.toISOString(),
                },
            };
            socket.send(JSON.stringify(request));
            console.log("Sent schedule window to server: ", request);
        } else {
            setWindowErrorMessage("Socket not connected. Cannot save schedule window.");
            console.error("Socket is not open");
        }
    }

    // Render functions for different tabs
    const renderBasicSettings = () => (
        <div className="settings-content-section">
            <div className="settings-card">
                <div className="settings-card-header">
                    <span className="settings-card-icon">⚙️</span>
                    <h3 className="settings-card-title">Basic Preferences</h3>
                </div>
                <div className="settings-card-content">
                    <SettingsForm />
                </div>
            </div>
        </div>
    );

    const renderScheduleWindow = () => (
        <div className="settings-content-section">
            <div className="settings-card">
                <div className="settings-card-header">
                    <span className="settings-card-icon">📅</span>
                    <h3 className="settings-card-title">Schedule Request Window</h3>
                </div>
                <div className="settings-card-content">
                    {windowSuccessMessage && <div className="success-message">{windowSuccessMessage}</div>}
                    {windowErrorMessage && <div className="error-message">{windowErrorMessage}</div>}
                    {isLoadingWindow && <div className="loading-message">Loading/Saving window times...</div>}

                    <form onSubmit={handleWindowSubmit} className="settings-form">
                        <div className="form-group">
                            <label htmlFor="startTime" className="form-label">Start Time:</label>
                            <DateTime
                                inputId="startTime"
                                inputProps={{ className: "datetime form-input" }}
                                value={startTime}
                                onChange={date => setStartTime(date instanceof Date || typeof date === 'string' ? new Date(date) : new Date())}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="endTime" className="form-label">End Time:</label>
                            <DateTime
                                inputId="endTime"
                                inputProps={{ className: "datetime form-input" }}
                                value={endTime}
                                onChange={date => setEndTime(date instanceof Date || typeof date === 'string' ? new Date(date) : new Date())}
                            />
                        </div>

                        <div className="settings-actions">
                            <button type="submit" className="btn btn-primary" disabled={isLoadingWindow}>
                                {isLoadingWindow ? 'Saving...' : 'Save Window Times'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );

    const renderUserManagement = () => (
        <div className="settings-content-section">
            <div className="settings-card">
                <div className="settings-card-header">
                    <span className="settings-card-icon">👥</span>
                    <h3 className="settings-card-title">Employee Management</h3>
                </div>
                <div className="settings-card-content">
                    <div className="form-grid">
                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Auto-approve Employees</div>
                                    <div className="toggle-description">Automatically approve new employee registrations</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.auto_approve_employees}
                                    onChange={() => handleToggle('auto_approve_employees')}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Require Manager Approval</div>
                                    <div className="toggle-description">Require manager approval for employee actions</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.require_manager_approval}
                                    onChange={() => handleToggle('require_manager_approval')}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Allow Employee Self-Registration</div>
                                    <div className="toggle-description">Allow employees to register themselves</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.allow_employee_self_registration}
                                    onChange={() => handleToggle('allow_employee_self_registration')}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Employee Probation Period (days)</label>
                            <input
                                type="number"
                                min="0"
                                max="365"
                                className="form-input"
                                value={extendedSettings.employee_probation_period_days}
                                onChange={(e) => handleSettingChange('employee_probation_period_days', parseInt(e.target.value))}
                            />
                        </div>
                    </div>
                </div>
            </div>

            <div className="settings-card">
                <div className="settings-card-header">
                    <span className="settings-card-icon">🔑</span>
                    <h3 className="settings-card-title">Manager Permissions</h3>
                </div>
                <div className="settings-card-content">
                    <div className="form-grid">
                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Can Create Employees</div>
                                    <div className="toggle-description">Managers can create new employee accounts</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.managers_can_create_employees}
                                    onChange={() => handleToggle('managers_can_create_employees')}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Can Edit All Timesheets</div>
                                    <div className="toggle-description">Managers can edit any employee's timesheet</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.managers_can_edit_all_timesheets}
                                    onChange={() => handleToggle('managers_can_edit_all_timesheets')}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Can Approve Overtime</div>
                                    <div className="toggle-description">Managers can approve overtime requests</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.managers_can_approve_overtime}
                                    onChange={() => handleToggle('managers_can_approve_overtime')}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Can Modify Rates</div>
                                    <div className="toggle-description">Managers can modify employee pay rates</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.managers_can_modify_rates}
                                    onChange={() => handleToggle('managers_can_modify_rates')}
                                />
                            </div>
                        </div>
                    </div>

                    <div className="settings-actions">
                        <button
                            onClick={() => saveSettings('user-management', 1101)}
                            className="btn btn-primary"
                            disabled={isLoadingSettings}
                        >
                            {isLoadingSettings ? 'Saving...' : 'Save User Management Settings'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );

    const renderTimesheetSettings = () => (
        <div className="settings-content-section">
            <div className="settings-card">
                <div className="settings-card-header">
                    <span className="settings-card-icon">⏰</span>
                    <h3 className="settings-card-title">Clock In/Out Rules</h3>
                </div>
                <div className="settings-card-content">
                    <div className="form-grid">
                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Require Photo Clock In</div>
                                    <div className="toggle-description">Employees must take a photo when clocking in</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.require_photo_clock_in}
                                    onChange={() => handleToggle('require_photo_clock_in')}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Require Location Verification</div>
                                    <div className="toggle-description">Verify employee location when clocking in</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.require_location_verification}
                                    onChange={() => handleToggle('require_location_verification')}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Location Verification Radius (feet)</label>
                            <input
                                type="number"
                                min="10"
                                max="1000"
                                className="form-input"
                                value={extendedSettings.location_verification_radius_feet}
                                onChange={(e) => handleSettingChange('location_verification_radius_feet', parseInt(e.target.value))}
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">Allow Early Clock In (minutes)</label>
                            <input
                                type="number"
                                min="0"
                                max="60"
                                className="form-input"
                                value={extendedSettings.allow_early_clock_in_minutes}
                                onChange={(e) => handleSettingChange('allow_early_clock_in_minutes', parseInt(e.target.value))}
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">Allow Late Clock Out (minutes)</label>
                            <input
                                type="number"
                                min="0"
                                max="60"
                                className="form-input"
                                value={extendedSettings.allow_late_clock_out_minutes}
                                onChange={(e) => handleSettingChange('allow_late_clock_out_minutes', parseInt(e.target.value))}
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">Auto Clock Out After (hours)</label>
                            <input
                                type="number"
                                min="8"
                                max="24"
                                className="form-input"
                                value={extendedSettings.auto_clock_out_hours}
                                onChange={(e) => handleSettingChange('auto_clock_out_hours', parseInt(e.target.value))}
                            />
                        </div>
                    </div>
                </div>
            </div>

            <div className="settings-card">
                <div className="settings-card-header">
                    <span className="settings-card-icon">🔄</span>
                    <h3 className="settings-card-title">Break Management</h3>
                </div>
                <div className="settings-card-content">
                    <div className="form-grid">
                        <div className="form-group">
                            <label className="form-label">Max Clock Pairs Per Shift</label>
                            <input
                                type="number"
                                min="1"
                                max="10"
                                className="form-input"
                                value={extendedSettings.max_clock_pairs_per_shift}
                                onChange={(e) => handleSettingChange('max_clock_pairs_per_shift', parseInt(e.target.value))}
                            />
                        </div>

                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Require Break Documentation</div>
                                    <div className="toggle-description">Require documentation for breaks</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.require_break_documentation}
                                    onChange={() => handleToggle('require_break_documentation')}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Auto-deduct Unpaid Breaks</div>
                                    <div className="toggle-description">Automatically deduct unpaid break time</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.auto_deduct_unpaid_breaks}
                                    onChange={() => handleToggle('auto_deduct_unpaid_breaks')}
                                />
                            </div>
                        </div>
                    </div>

                    <div className="settings-actions">
                        <button
                            onClick={() => saveSettings('timesheet-advanced', 1105)}
                            className="btn btn-primary"
                            disabled={isLoadingSettings}
                        >
                            {isLoadingSettings ? 'Saving...' : 'Save Timesheet Settings'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );

    const renderNotifications = () => (
        <div className="settings-content-section">
            <div className="settings-card">
                <div className="settings-card-header">
                    <span className="settings-card-icon">🔔</span>
                    <h3 className="settings-card-title">Notification Preferences</h3>
                </div>
                <div className="settings-card-content">
                    <div className="form-grid">
                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Email Notifications</div>
                                    <div className="toggle-description">Receive notifications via email</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.email_notifications_enabled}
                                    onChange={() => handleToggle('email_notifications_enabled')}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Shift Request Notifications</div>
                                    <div className="toggle-description">Notify when employees request shifts</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.notify_on_shift_requests}
                                    onChange={() => handleToggle('notify_on_shift_requests')}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Worker Assignment Notifications</div>
                                    <div className="toggle-description">Notify when workers are assigned to shifts</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.notify_on_worker_assignments}
                                    onChange={() => handleToggle('notify_on_worker_assignments')}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Timesheet Submission Notifications</div>
                                    <div className="toggle-description">Notify when timesheets are submitted</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.notify_on_timesheet_submissions}
                                    onChange={() => handleToggle('notify_on_timesheet_submissions')}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Schedule Change Notifications</div>
                                    <div className="toggle-description">Notify when schedules are modified</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.notify_on_schedule_changes}
                                    onChange={() => handleToggle('notify_on_schedule_changes')}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">SMS Notifications</div>
                                    <div className="toggle-description">Receive notifications via SMS</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.sms_notifications_enabled}
                                    onChange={() => handleToggle('sms_notifications_enabled')}
                                />
                            </div>
                        </div>
                    </div>

                    <div className="settings-actions">
                        <button
                            onClick={() => saveSettings('notifications', 1100)}
                            className="btn btn-primary"
                            disabled={isLoadingSettings}
                        >
                            {isLoadingSettings ? 'Saving...' : 'Save Notification Settings'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );

    const renderRolePremiums = () => (
        <div className="settings-content-section">
            <div className="settings-card">
                <div className="settings-card-header">
                    <span className="settings-card-icon">💰</span>
                    <h3 className="settings-card-title">Role Premium Rates</h3>
                </div>
                <div className="settings-card-content">
                    <div className="form-grid">
                        <div className="form-group">
                            <label className="form-label">Crew Chief Premium ($/hour)</label>
                            <input
                                type="number"
                                step="0.25"
                                min="0"
                                className="form-input"
                                value={extendedSettings.crew_chief_premium_rate}
                                onChange={(e) => handleSettingChange('crew_chief_premium_rate', parseFloat(e.target.value))}
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">Forklift Operator Premium ($/hour)</label>
                            <input
                                type="number"
                                step="0.25"
                                min="0"
                                className="form-input"
                                value={extendedSettings.forklift_operators_premium_rate}
                                onChange={(e) => handleSettingChange('forklift_operators_premium_rate', parseFloat(e.target.value))}
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">Truck Driver Premium ($/hour)</label>
                            <input
                                type="number"
                                step="0.25"
                                min="0"
                                className="form-input"
                                value={extendedSettings.truck_drivers_premium_rate}
                                onChange={(e) => handleSettingChange('truck_drivers_premium_rate', parseFloat(e.target.value))}
                            />
                        </div>
                    </div>

                    <div className="settings-actions">
                        <button
                            onClick={() => saveSettings('role-premiums', 1101)}
                            className="btn btn-primary"
                            disabled={isLoadingSettings}
                        >
                            {isLoadingSettings ? 'Saving...' : 'Save Role Premium Settings'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );

    const renderSecurity = () => (
        <div className="settings-content-section">
            <div className="settings-card">
                <div className="settings-card-header">
                    <span className="settings-card-icon">🔒</span>
                    <h3 className="settings-card-title">Security Settings</h3>
                </div>
                <div className="settings-card-content">
                    <div className="form-grid">
                        <div className="form-group">
                            <label className="form-label">Minimum Password Length</label>
                            <input
                                type="number"
                                min="6"
                                max="20"
                                className="form-input"
                                value={extendedSettings.password_min_length}
                                onChange={(e) => handleSettingChange('password_min_length', parseInt(e.target.value))}
                            />
                        </div>

                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Require Password Complexity</div>
                                    <div className="toggle-description">Require uppercase, lowercase, numbers, and symbols</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.require_password_complexity}
                                    onChange={() => handleToggle('require_password_complexity')}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Session Timeout (minutes)</label>
                            <input
                                type="number"
                                min="30"
                                max="1440"
                                className="form-input"
                                value={extendedSettings.session_timeout_minutes}
                                onChange={(e) => handleSettingChange('session_timeout_minutes', parseInt(e.target.value))}
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">Max Login Attempts</label>
                            <input
                                type="number"
                                min="3"
                                max="10"
                                className="form-input"
                                value={extendedSettings.max_login_attempts}
                                onChange={(e) => handleSettingChange('max_login_attempts', parseInt(e.target.value))}
                            />
                        </div>
                    </div>

                    <div className="settings-actions">
                        <button
                            onClick={() => saveSettings('security', 1108)}
                            className="btn btn-primary"
                            disabled={isLoadingSettings}
                        >
                            {isLoadingSettings ? 'Saving...' : 'Save Security Settings'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );

    const renderClientSettings = () => (
        <div className="settings-content-section">
            <div className="settings-card">
                <div className="settings-card-header">
                    <span className="settings-card-icon">🏢</span>
                    <h3 className="settings-card-title">Client Permissions</h3>
                </div>
                <div className="settings-card-content">
                    <div className="form-grid">
                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Clients Can View Timesheets</div>
                                    <div className="toggle-description">Allow clients to view employee timesheets</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.clients_can_view_timesheets}
                                    onChange={() => handleToggle('clients_can_view_timesheets')}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Clients Can Edit Timesheets</div>
                                    <div className="toggle-description">Allow clients to edit employee timesheets</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.clients_can_edit_timesheets}
                                    onChange={() => handleToggle('clients_can_edit_timesheets')}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Clients Can Request Workers</div>
                                    <div className="toggle-description">Allow clients to request specific workers</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.clients_can_request_workers}
                                    onChange={() => handleToggle('clients_can_request_workers')}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Clients Can Modify Jobs</div>
                                    <div className="toggle-description">Allow clients to modify job details</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.clients_can_modify_jobs}
                                    onChange={() => handleToggle('clients_can_modify_jobs')}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <div className="toggle-setting">
                                <div className="toggle-info">
                                    <div className="toggle-title">Require Client Verification</div>
                                    <div className="toggle-description">Require verification for new client accounts</div>
                                </div>
                                <ToggleSwitch
                                    checked={extendedSettings.require_client_verification}
                                    onChange={() => handleToggle('require_client_verification')}
                                />
                            </div>
                        </div>
                    </div>

                    <div className="settings-actions">
                        <button
                            onClick={() => saveSettings('client-management', 1103)}
                            className="btn btn-primary"
                            disabled={isLoadingSettings}
                        >
                            {isLoadingSettings ? 'Saving...' : 'Save Client Settings'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );

    // Render tab content based on active tab
    const renderTabContent = () => {
        switch (activeTab) {
            case 'basic':
                return renderBasicSettings();
            case 'schedule':
                return renderScheduleWindow();
            case 'users':
                return renderUserManagement();
            case 'timesheets':
                return renderTimesheetSettings();
            case 'notifications':
                return renderNotifications();
            case 'roles':
                return renderRolePremiums();
            case 'security':
                return renderSecurity();
            case 'clients':
                return renderClientSettings();
            default:
                return renderBasicSettings();
        }
    };

    return (
        <div className="enhanced-settings-page">
            <div className="settings-header">
                <h1 className="settings-title">Manager Settings</h1>
                <p className="settings-subtitle">Configure your workspace preferences and permissions</p>

                {/* Connection Status Indicator */}
                <div className={`connection-status ${connectionStatus}`}>
                    <span className="connection-icon">
                        {connectionStatus === 'connected' && '🟢'}
                        {connectionStatus === 'connecting' && '🟡'}
                        {connectionStatus === 'disconnected' && '🔴'}
                        {connectionStatus === 'error' && '⚠️'}
                        {connectionStatus === 'no-socket' && '❌'}
                    </span>
                    <span className="connection-text">
                        {connectionStatus === 'connected' && 'Connected'}
                        {connectionStatus === 'connecting' && 'Connecting...'}
                        {connectionStatus === 'disconnected' && 'Disconnected'}
                        {connectionStatus === 'error' && 'Connection Error'}
                        {connectionStatus === 'no-socket' && 'No Connection'}
                    </span>
                </div>

                {settingsSuccessMessage && (
                    <div className="success-banner">
                        <span className="success-icon">✅</span>
                        {settingsSuccessMessage}
                    </div>
                )}

                {settingsErrorMessage && (
                    <div className="error-banner">
                        <span className="error-icon">❌</span>
                        {settingsErrorMessage}
                        {(connectionStatus === 'disconnected' || connectionStatus === 'error' || connectionStatus === 'no-socket') && (
                            <button
                                onClick={retryConnection}
                                className="btn btn-secondary retry-btn"
                                style={{ marginLeft: '15px', padding: '6px 12px', fontSize: '12px' }}
                            >
                                Retry Connection
                            </button>
                        )}
                    </div>
                )}
            </div>

            <div className="settings-container">
                <div className="settings-sidebar">
                    <nav className="settings-nav">
                        {tabs.map(tab => (
                            <button
                                key={tab.id}
                                className={`nav-item ${activeTab === tab.id ? 'active' : ''}`}
                                onClick={() => setActiveTab(tab.id)}
                                disabled={isLoadingSettings || isLoadingWindow}
                            >
                                <span className="nav-icon">{tab.icon}</span>
                                <div className="nav-content">
                                    <span className="nav-label">{tab.label}</span>
                                </div>
                            </button>
                        ))}
                    </nav>
                </div>

                <div className="settings-content">
                    {renderTabContent()}
                </div>
            </div>
        </div>
    );
}
