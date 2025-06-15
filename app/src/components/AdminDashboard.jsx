import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
import { logDebug, logError, logInfo } from '../utils/logger';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const socket = useSocket();
  const [adminData, setAdminData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedUser, setSelectedUser] = useState(null);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        logDebug('AdminDashboard', 'Received WebSocket message', { response });

        if (response.request_id === 950) { // Admin Get All Data
          if (response.success && response.data) {
            setAdminData(response.data);
            setIsLoading(false);
            setError('');
            logInfo('AdminDashboard', 'Admin data loaded successfully');
          } else {
            setError(response.error || 'Failed to load admin data');
            setIsLoading(false);
            logError('AdminDashboard', 'Failed to load admin data', { response });
          }
        } else if (response.request_id === 951) { // Admin User Management
          if (response.success) {
            logInfo('AdminDashboard', 'User management action completed', { response });
            // Refresh data after user management action
            fetchAdminData();
          } else {
            setError(response.error || 'User management action failed');
            logError('AdminDashboard', 'User management failed', { response });
          }
        }
      } catch (e) {
        logError('AdminDashboard', 'Error parsing admin response', { error: e });
        setError('Error processing admin data');
        setIsLoading(false);
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => socket.removeEventListener('message', handleMessage);
  }, [socket]);

  const fetchAdminData = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      setIsLoading(true);
      setError('');
      
      const request = {
        request_id: 950
      };
      
      socket.send(JSON.stringify(request));
      logDebug('AdminDashboard', 'Sent admin data request');
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, [socket]);

  const handleUserAction = (userId, action) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;

    const request = {
      request_id: 951,
      data: {
        user_id: userId,
        action: action
      }
    };

    socket.send(JSON.stringify(request));
    logDebug('AdminDashboard', 'Sent user management request', { userId, action });
  };

  const renderOverview = () => {
    if (!adminData) return null;

    const { statistics, admin_privileges } = adminData;

    return (
      <div className="admin-overview">
        <div className="stats-grid">
          <div className="stat-card">
            <h3>Total Users</h3>
            <div className="stat-number">{statistics.total_users}</div>
            <div className="stat-breakdown">
              <span>Admins: {statistics.total_admins}</span>
              <span>Managers: {statistics.total_managers}</span>
              <span>Employees: {statistics.total_employees}</span>
            </div>
          </div>

          <div className="stat-card">
            <h3>User Status</h3>
            <div className="stat-number">{statistics.active_users}</div>
            <div className="stat-breakdown">
              <span>Active: {statistics.active_users}</span>
              <span>Approved: {statistics.approved_users}</span>
            </div>
          </div>

          <div className="stat-card">
            <h3>Jobs & Shifts</h3>
            <div className="stat-number">{statistics.total_jobs}</div>
            <div className="stat-breakdown">
              <span>Jobs: {statistics.total_jobs}</span>
              <span>Active Jobs: {statistics.active_jobs}</span>
              <span>Shifts: {statistics.total_shifts}</span>
            </div>
          </div>

          <div className="stat-card">
            <h3>Clients</h3>
            <div className="stat-number">{statistics.total_clients}</div>
            <div className="stat-breakdown">
              <span>Total Clients: {statistics.total_clients}</span>
            </div>
          </div>
        </div>

        <div className="admin-privileges">
          <h3>Admin Privileges</h3>
          <div className="privileges-list">
            {admin_privileges.can_create_users && <span className="privilege">✅ Create Users</span>}
            {admin_privileges.can_delete_users && <span className="privilege">✅ Delete Users</span>}
            {admin_privileges.can_modify_all_data && <span className="privilege">✅ Modify All Data</span>}
            {admin_privileges.can_view_system_logs && <span className="privilege">✅ View System Logs</span>}
            {admin_privileges.can_manage_settings && <span className="privilege">✅ Manage Settings</span>}
          </div>
        </div>
      </div>
    );
  };

  const renderUsers = () => {
    if (!adminData || !adminData.users) return null;

    return (
      <div className="admin-users">
        <div className="users-header">
          <h3>User Management</h3>
          <button onClick={fetchAdminData} className="refresh-btn">🔄 Refresh</button>
        </div>

        <div className="users-table">
          <table>
            <thead>
              <tr>
                <th>Username</th>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {adminData.users.map(user => (
                <tr key={user.id} className={!user.isActive ? 'inactive-user' : ''}>
                  <td>{user.username}</td>
                  <td>{user.name}</td>
                  <td>{user.email}</td>
                  <td>
                    <span className={`role-badge ${user.isAdmin ? 'admin' : user.isManager ? 'manager' : 'employee'}`}>
                      {user.isAdmin ? 'Admin' : user.isManager ? 'Manager' : 'Employee'}
                    </span>
                  </td>
                  <td>
                    <span className={`status-badge ${user.isActive ? 'active' : 'inactive'}`}>
                      {user.isActive ? 'Active' : 'Inactive'}
                    </span>
                    {user.isApproval && <span className="approval-badge">Approved</span>}
                  </td>
                  <td>
                    <div className="user-actions">
                      {!user.isAdmin && (
                        <button 
                          onClick={() => handleUserAction(user.id, 'promote_to_admin')}
                          className="action-btn promote"
                          title="Promote to Admin"
                        >
                          👑
                        </button>
                      )}
                      {user.isAdmin && (
                        <button 
                          onClick={() => handleUserAction(user.id, 'demote_from_admin')}
                          className="action-btn demote"
                          title="Demote from Admin"
                        >
                          👤
                        </button>
                      )}
                      {user.isActive ? (
                        <button 
                          onClick={() => handleUserAction(user.id, 'deactivate')}
                          className="action-btn deactivate"
                          title="Deactivate User"
                        >
                          🚫
                        </button>
                      ) : (
                        <button 
                          onClick={() => handleUserAction(user.id, 'activate')}
                          className="action-btn activate"
                          title="Activate User"
                        >
                          ✅
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderJobs = () => {
    if (!adminData || !adminData.jobs) return null;

    return (
      <div className="admin-jobs">
        <h3>Jobs Management</h3>
        <div className="jobs-table">
          <table>
            <thead>
              <tr>
                <th>Job Name</th>
                <th>Client</th>
                <th>Venue</th>
                <th>Status</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {adminData.jobs.map(job => (
                <tr key={job.id}>
                  <td>{job.name}</td>
                  <td>{job.client_company_name || 'N/A'}</td>
                  <td>{job.venue_name}</td>
                  <td>
                    <span className={`status-badge ${job.is_active ? 'active' : 'inactive'}`}>
                      {job.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td>{job.created_at ? new Date(job.created_at).toLocaleDateString() : 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderClients = () => {
    if (!adminData || !adminData.clients) return null;

    return (
      <div className="admin-clients">
        <h3>Client Management</h3>
        <div className="clients-table">
          <table>
            <thead>
              <tr>
                <th>Company Name</th>
                <th>Contact Person</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Jobs Count</th>
              </tr>
            </thead>
            <tbody>
              {adminData.clients.map(client => (
                <tr key={client.id}>
                  <td>{client.name}</td>
                  <td>{client.contact_person || 'N/A'}</td>
                  <td>{client.contact_email || 'N/A'}</td>
                  <td>{client.contact_phone || 'N/A'}</td>
                  <td>{client.jobs_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'overview': return renderOverview();
      case 'users': return renderUsers();
      case 'jobs': return renderJobs();
      case 'clients': return renderClients();
      default: return renderOverview();
    }
  };

  if (isLoading) {
    return (
      <div className="admin-dashboard loading">
        <div className="loading-message">Loading admin data...</div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="dashboard-header">
        <h1>🛡️ Admin Dashboard</h1>
        <div className="header-actions">
          <button onClick={fetchAdminData} className="refresh-btn">🔄 Refresh All</button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={fetchAdminData} className="retry-btn">Retry</button>
        </div>
      )}

      <div className="dashboard-navigation">
        <button 
          className={`nav-tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={`nav-tab ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          👥 Users
        </button>
        <button 
          className={`nav-tab ${activeTab === 'jobs' ? 'active' : ''}`}
          onClick={() => setActiveTab('jobs')}
        >
          💼 Jobs
        </button>
        <button 
          className={`nav-tab ${activeTab === 'clients' ? 'active' : ''}`}
          onClick={() => setActiveTab('clients')}
        >
          🏢 Clients
        </button>
      </div>

      <div className="dashboard-content">
        {renderContent()}
      </div>
    </div>
  );
};

export default AdminDashboard;
