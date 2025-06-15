import React, { useState, useEffect } from 'react';
import { useSocket } from '../../utils';
import './ClientUsersList.css';

const ClientUsersList = ({ users, companyId, onRefresh }) => {
  const { socket } = useSocket();
  const [processingUsers, setProcessingUsers] = useState(new Set());

  const handleUserAction = (userId, action) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      setProcessingUsers(prev => new Set(prev).add(userId));
      
      const request = {
        request_id: 214, // UPDATE_CLIENT_USER_STATUS
        data: {
          user_id: userId,
          action: action
        }
      };
      socket.send(JSON.stringify(request));
    }
  };

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);

        if (response.request_id === 214) { // Update Client User Status
          if (response.success) {
            setProcessingUsers(prev => {
              const newSet = new Set(prev);
              newSet.delete(response.data.user_id);
              return newSet;
            });
            onRefresh(); // Refresh the parent component
          } else {
            setProcessingUsers(new Set()); // Clear all processing states on error
            console.error('Failed to update user status:', response.error);
          }
        }
      } catch (e) {
        console.error('WebSocket message error in ClientUsersList:', e);
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => {
      socket.removeEventListener('message', handleMessage);
    };
  }, [socket, onRefresh]);

  const formatLastLogin = (lastLogin) => {
    if (!lastLogin) return 'Never';
    const date = new Date(lastLogin);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
    return date.toLocaleDateString();
  };

  const getUserStatusClass = (user) => {
    if (!user.isActive) return 'inactive';
    if (!user.isApproval) return 'pending';
    return 'active';
  };

  const getUserStatusText = (user) => {
    if (!user.isActive) return 'Inactive';
    if (!user.isApproval) return 'Pending Approval';
    return 'Active';
  };

  if (users.length === 0) {
    return (
      <div className="no-users">
        <p>No users found for this company.</p>
      </div>
    );
  }

  return (
    <div className="client-users-list">
      {users.map((user) => (
        <div key={user.id} className={`user-item ${getUserStatusClass(user)}`}>
          <div className="user-avatar">
            {user.google_picture ? (
              <img src={user.google_picture} alt={user.name} className="avatar-image" />
            ) : (
              <div className="avatar-placeholder">
                {user.name.charAt(0).toUpperCase()}
              </div>
            )}
          </div>
          
          <div className="user-info">
            <div className="user-name">{user.name}</div>
            <div className="user-details">
              <span className="user-username">@{user.username}</span>
              {user.email && <span className="user-email">{user.email}</span>}
            </div>
            <div className="user-meta">
              <span className={`user-status ${getUserStatusClass(user)}`}>
                {getUserStatusText(user)}
              </span>
              <span className="user-last-login">
                Last login: {formatLastLogin(user.last_login)}
              </span>
            </div>
          </div>

          <div className="user-actions">
            {user.isActive ? (
              <button
                onClick={() => handleUserAction(user.id, 'deactivate')}
                disabled={processingUsers.has(user.id)}
                className="action-button deactivate"
                title="Deactivate user"
              >
                {processingUsers.has(user.id) ? '⟳' : '🚫'}
              </button>
            ) : (
              <button
                onClick={() => handleUserAction(user.id, 'activate')}
                disabled={processingUsers.has(user.id)}
                className="action-button activate"
                title="Activate user"
              >
                {processingUsers.has(user.id) ? '⟳' : '✅'}
              </button>
            )}

            {user.isApproval ? (
              <button
                onClick={() => handleUserAction(user.id, 'unapprove')}
                disabled={processingUsers.has(user.id)}
                className="action-button unapprove"
                title="Remove approval"
              >
                {processingUsers.has(user.id) ? '⟳' : '❌'}
              </button>
            ) : (
              <button
                onClick={() => handleUserAction(user.id, 'approve')}
                disabled={processingUsers.has(user.id)}
                className="action-button approve"
                title="Approve user"
              >
                {processingUsers.has(user.id) ? '⟳' : '✓'}
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ClientUsersList;
