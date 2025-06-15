// EmployeeProfile.js

import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
import { Link, useNavigate } from 'react-router-dom';
import '../css/EmployeeProfile.css'; // Import the CSS file

function EmployeeProfile() {
  const { socket, connectionStatus } = useSocket();
  const navigate = useNavigate();
  const [profileData, setProfileData] = useState(null);
  const [certifications, setCertifications] = useState(null);
  const [upcomingShifts, setUpcomingShifts] = useState([]);
  const [timesheetStatus, setTimesheetStatus] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      // Request profile data
      const getProfileRequest = { request_id: 70 };
      socket.send(JSON.stringify(getProfileRequest));

      // Request certifications
      const getCertificationsRequest = { request_id: 71 }; // GET_USER_CERTIFICATIONS
      socket.send(JSON.stringify(getCertificationsRequest));

      // Request upcoming shifts
      const getUpcomingShiftsRequest = { request_id: 72 }; // GET_UPCOMING_SHIFTS
      socket.send(JSON.stringify(getUpcomingShiftsRequest));

      // Request timesheet status
      const getTimesheetStatusRequest = { request_id: 73 }; // GET_TIMESHEET_STATUS
      socket.send(JSON.stringify(getTimesheetStatusRequest));

      const handleSocketMessage = (event) => {
        const response = JSON.parse(event.data);
        if (response && response.request_id === 70) {
          handleProfileResponse(response);
        } else if (response && response.request_id === 71) {
          handleCertificationsResponse(response);
        } else if (response && response.request_id === 72) {
          handleUpcomingShiftsResponse(response);
        } else if (response && response.request_id === 73) {
          handleTimesheetStatusResponse(response);
        }
      };

      socket.addEventListener('message', handleSocketMessage);

      return () => {
        socket.removeEventListener('message', handleSocketMessage);
      };
    }
  }, [socket]);

  const handleProfileResponse = (response) => {
    if (response.success) {
      setProfileData(response.data);
      setIsLoading(false);
    } else {
      console.error('Failed to retrieve profile data');
      setIsLoading(false);
    }
  };

  const handleCertificationsResponse = (response) => {
    if (response.success) {
      setCertifications(response.data);
    } else {
      console.error('Failed to retrieve certifications');
    }
  };

  const handleUpcomingShiftsResponse = (response) => {
    if (response.success) {
      setUpcomingShifts(response.data || []);
    } else {
      console.error('Failed to retrieve upcoming shifts');
    }
  };

  const handleTimesheetStatusResponse = (response) => {
    if (response.success) {
      setTimesheetStatus(response.data);
    } else {
      console.error('Failed to retrieve timesheet status');
    }
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return '#28a745';
      case 'connecting': case 'reconnecting': return '#ffc107';
      case 'disconnected': case 'failed': case 'error': return '#dc3545';
      default: return '#6c757d';
    }
  };

  if (isLoading) {
    return (
      <div className="EmployeeProfileContainer">
        <div className="loading-message">Loading your profile...</div>
      </div>
    );
  }

  return (
    <div className="EmployeeProfileContainer">
      <div className="ProfileHeader">
        <h2>Employee Dashboard</h2>
        <div className="connection-status" style={{ color: getConnectionStatusColor() }}>
          ● {connectionStatus === 'connected' ? 'Connected' : connectionStatus}
        </div>
      </div>

      {profileData ? (
        <div>
          {/* Profile Information */}
          <div className="profile-section">
            <h3>Profile Information</h3>
            <div className="profile-grid">
              <div className="profile-item">
                <strong>Name:</strong> {profileData.name}
              </div>
              <div className="profile-item">
                <strong>Username:</strong> {profileData.username}
              </div>
              <div className="profile-item">
                <strong>Workplace:</strong> {profileData.workplace_name}
              </div>
              {profileData.employee_type && (
                <div className="profile-item">
                  <strong>Role:</strong> {profileData.employee_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </div>
              )}
            </div>
          </div>

          {/* Certifications */}
          {certifications && (
            <div className="profile-section">
              <h3>Certifications</h3>
              <div className="certifications-grid">
                <div className={`cert-badge ${certifications.can_crew_chief ? 'certified' : 'not-certified'}`}>
                  👷‍♂️ Crew Chief {certifications.can_crew_chief ? '✓' : '✗'}
                </div>
                <div className={`cert-badge ${certifications.can_forklift ? 'certified' : 'not-certified'}`}>
                  🚜 Forklift Operator {certifications.can_forklift ? '✓' : '✗'}
                </div>
                <div className={`cert-badge ${certifications.can_truck ? 'certified' : 'not-certified'}`}>
                  🚛 Truck Driver {certifications.can_truck ? '✓' : '✗'}
                </div>
              </div>
            </div>
          )}

          {/* Upcoming Shifts */}
          <div className="profile-section">
            <h3>Upcoming Shifts</h3>
            {upcomingShifts.length > 0 ? (
              <div className="shifts-list">
                {upcomingShifts.slice(0, 3).map((shift, index) => (
                  <div key={index} className="shift-preview">
                    <div className="shift-date">
                      {new Date(shift.shift_start_datetime).toLocaleDateString()}
                    </div>
                    <div className="shift-time">
                      {new Date(shift.shift_start_datetime).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </div>
                    <div className="shift-role">{shift.role_assigned}</div>
                  </div>
                ))}
                {upcomingShifts.length > 3 && (
                  <div className="view-more">
                    <button onClick={() => navigate('/shiftsPage')}>
                      View all {upcomingShifts.length} shifts
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <p>No upcoming shifts scheduled.</p>
            )}
          </div>

          {/* Timesheet Status */}
          {timesheetStatus && (
            <div className="profile-section">
              <h3>Timesheet Status</h3>
              <div className="timesheet-summary">
                <div className="timesheet-item">
                  <strong>Hours This Week:</strong> {timesheetStatus.hoursThisWeek || 0}
                </div>
                <div className="timesheet-item">
                  <strong>Pending Submissions:</strong> {timesheetStatus.pendingSubmissions || 0}
                </div>
                <div className="timesheet-item">
                  <strong>Last Submitted:</strong> {timesheetStatus.lastSubmitted ?
                    new Date(timesheetStatus.lastSubmitted).toLocaleDateString() : 'Never'}
                </div>
              </div>
            </div>
          )}

          <div className="ButtonContainer">
            <button className="SignInShiftsButton">
              <Link to="/SignInShifts" aria-label="Sign In Shifts">
                <span className="ButtonIcon" role="img" aria-label="Note Icon"></span>
                <span className="ButtonText">Sign in shifts</span>
              </Link>
            </button>
            <button className="ViewShiftsButton">
              <Link to="/ShiftsPage" aria-label="View My Shifts">
                <span className="ButtonIcon" role="img" aria-label="Calendar Icon"></span>
                <span className="ButtonText">View my shifts</span>
              </Link>
            </button>
            {profileData.employee_type === 'crew_chief' && (
              <button className="ViewShiftsButton"> {/* You might want a different class/styling */}
                <Link to="/crew-chief-dashboard" aria-label="View Supervised Shifts">
                  <span className="ButtonIcon" role="img" aria-label="Team Icon"></span> {/* Consider a different icon */}
                  <span className="ButtonText">Supervised Shifts</span>
                </Link>
              </button>
            )}
          </div>
        </div>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
}

export default EmployeeProfile;
