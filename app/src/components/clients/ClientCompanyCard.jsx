import React, { useState, useEffect } from 'react';
import { useSocket } from '../../utils';
import ClientUsersList from './ClientUsersList';
import ClientDetailsModal from './ClientDetailsModal';
import './ClientCompanyCard.css';

const ClientCompanyCard = ({ client, onRefresh }) => {
  const { socket } = useSocket();
  const [isExpanded, setIsExpanded] = useState(false);
  const [showUsers, setShowUsers] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [clientDetails, setClientDetails] = useState(null);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);

        if (response.request_id === 216) { // GET_CLIENT_COMPANY_DETAILS response
          setIsLoading(false);
          if (response.success) {
            setClientDetails(response.data);
            setIsDetailsModalOpen(true);
          } else {
            console.error('Failed to fetch client details:', response.error);
          }
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => socket.removeEventListener('message', handleMessage);
  }, [socket]);

  const handleToggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  const handleShowUsers = () => {
    setShowUsers(!showUsers);
  };

  const handleViewDetails = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      setIsLoading(true);
      const request = {
        request_id: 216, // GET_CLIENT_COMPANY_DETAILS
        data: { company_id: client.id }
      };
      socket.send(JSON.stringify(request));
    }
  };

  const handleCloseDetailsModal = () => {
    setIsDetailsModalOpen(false);
    setClientDetails(null);
  };

  const getStatusColor = (client) => {
    const activeUsers = client.statistics.active_users;
    const totalUsers = client.statistics.total_users;
    
    if (totalUsers === 0) return 'gray';
    if (activeUsers === totalUsers) return 'green';
    if (activeUsers > 0) return 'orange';
    return 'red';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <>
      <div className={`client-company-card ${isExpanded ? 'expanded' : ''}`}>
      <div className="card-header" onClick={handleToggleExpand}>
        <div className="company-info">
          <h3 className="company-name">{client.name}</h3>
          <span className="company-id">ID: {client.id}</span>
        </div>
        <div className="company-status">
          <div className={`status-indicator ${getStatusColor(client)}`}></div>
          <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
        </div>
      </div>

      <div className="card-stats">
        <div className="stat-grid">
          <div className="stat-item">
            <span className="stat-number">{client.statistics.total_jobs}</span>
            <span className="stat-label">Total Jobs</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{client.statistics.active_jobs}</span>
            <span className="stat-label">Active Jobs</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{client.statistics.total_users}</span>
            <span className="stat-label">Users</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{client.statistics.recent_jobs_count}</span>
            <span className="stat-label">Recent Jobs</span>
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="card-details">
          <div className="details-section">
            <h4>Recent Activity</h4>
            {client.recent_activity.length > 0 ? (
              <div className="recent-activity-list">
                {client.recent_activity.map((activity, index) => (
                  <div key={index} className="activity-item">
                    <div className="activity-info">
                      <span className="activity-title">{activity.job_title}</span>
                      <span className="activity-venue">{activity.venue_name}</span>
                    </div>
                    <span className="activity-date">
                      {formatDate(activity.created_at)}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-activity">No recent activity</p>
            )}
          </div>

          <div className="details-section">
            <div className="section-header">
              <h4>Users ({client.users.length})</h4>
              <button
                onClick={handleShowUsers}
                className="toggle-users-button"
              >
                {showUsers ? 'Hide' : 'Show'} Users
              </button>
            </div>
            
            {showUsers && (
              <ClientUsersList 
                users={client.users} 
                companyId={client.id}
                onRefresh={onRefresh}
              />
            )}
          </div>

          <div className="card-actions">
            <button
              onClick={handleViewDetails}
              disabled={isLoading}
              className="details-button"
            >
              {isLoading ? 'Loading...' : 'View Full Details'}
            </button>
          </div>
        </div>
      )}
      </div>

      <ClientDetailsModal
        clientDetails={clientDetails}
        isOpen={isDetailsModalOpen}
        onClose={handleCloseDetailsModal}
        onRefresh={onRefresh}
      />
    </>
  );
};

export default ClientCompanyCard;
