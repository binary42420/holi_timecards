import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
import './NotificationCenter.css';

const NotificationCenter = ({ isOpen, onClose, onMarkAllRead }) => {
  const { socket, connectionStatus } = useSocket();
  const [notifications, setNotifications] = useState([]);
  const [filter, setFilter] = useState('all'); // all, unread, read
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const notificationTypes = {
    shift_assignment: { icon: '📅', color: '#007bff', label: 'Shift Assignment' },
    shift_change: { icon: '🔄', color: '#ffc107', label: 'Schedule Change' },
    timesheet_reminder: { icon: '⏰', color: '#28a745', label: 'Timesheet Reminder' },
    shift_request: { icon: '✋', color: '#17a2b8', label: 'Shift Request' },
    system_alert: { icon: '⚠️', color: '#dc3545', label: 'System Alert' },
    approval_needed: { icon: '✅', color: '#6f42c1', label: 'Approval Needed' },
    message: { icon: '💬', color: '#fd7e14', label: 'Message' },
    reminder: { icon: '🔔', color: '#20c997', label: 'Reminder' }
  };

  useEffect(() => {
    if (isOpen && socket && socket.readyState === WebSocket.OPEN) {
      fetchNotifications();
    }
  }, [isOpen, socket]);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        
        if (response.request_id === 600) { // GET_NOTIFICATIONS
          setIsLoading(false);
          if (response.success) {
            setNotifications(response.data || []);
            setError('');
          } else {
            setError(response.error || 'Failed to load notifications');
          }
        } else if (response.request_id === 601) { // MARK_NOTIFICATION_READ
          if (response.success) {
            setNotifications(prev => 
              prev.map(notif => 
                notif.id === response.data.notification_id 
                  ? { ...notif, is_read: true, read_at: new Date().toISOString() }
                  : notif
              )
            );
          }
        } else if (response.request_id === 602) { // MARK_ALL_READ
          if (response.success) {
            setNotifications(prev => 
              prev.map(notif => ({ 
                ...notif, 
                is_read: true, 
                read_at: new Date().toISOString() 
              }))
            );
            if (onMarkAllRead) onMarkAllRead();
          }
        } else if (response.request_id === 603) { // DELETE_NOTIFICATION
          if (response.success) {
            setNotifications(prev => 
              prev.filter(notif => notif.id !== response.data.notification_id)
            );
          }
        } else if (response.type === 'new_notification') {
          // Real-time notification received
          setNotifications(prev => [response.data, ...prev]);
        }
      } catch (e) {
        console.error('Error parsing notification response:', e);
        setIsLoading(false);
        setError('Error processing notifications');
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => socket.removeEventListener('message', handleMessage);
  }, [socket, onMarkAllRead]);

  const fetchNotifications = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      setIsLoading(true);
      setError('');
      const request = { request_id: 600 }; // GET_NOTIFICATIONS
      socket.send(JSON.stringify(request));
    }
  };

  const markAsRead = (notificationId) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      const request = {
        request_id: 601, // MARK_NOTIFICATION_READ
        data: { notification_id: notificationId }
      };
      socket.send(JSON.stringify(request));
    }
  };

  const markAllAsRead = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      const request = { request_id: 602 }; // MARK_ALL_READ
      socket.send(JSON.stringify(request));
    }
  };

  const deleteNotification = (notificationId) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      const request = {
        request_id: 603, // DELETE_NOTIFICATION
        data: { notification_id: notificationId }
      };
      socket.send(JSON.stringify(request));
    }
  };

  const filteredNotifications = notifications.filter(notif => {
    if (filter === 'unread') return !notif.is_read;
    if (filter === 'read') return notif.is_read;
    return true;
  });

  const unreadCount = notifications.filter(n => !n.is_read).length;

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now - time;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return time.toLocaleDateString();
  };

  const getNotificationConfig = (type) => {
    return notificationTypes[type] || notificationTypes.message;
  };

  if (!isOpen) return null;

  return (
    <div className="notification-center-overlay">
      <div className="notification-center">
        <div className="notification-header">
          <div className="header-left">
            <h2>Notifications</h2>
            {unreadCount > 0 && (
              <span className="unread-badge">{unreadCount}</span>
            )}
          </div>
          <div className="header-actions">
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="mark-all-read-btn"
                disabled={connectionStatus !== 'connected'}
              >
                Mark All Read
              </button>
            )}
            <button onClick={onClose} className="close-btn">×</button>
          </div>
        </div>

        <div className="notification-filters">
          <button
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All ({notifications.length})
          </button>
          <button
            className={`filter-btn ${filter === 'unread' ? 'active' : ''}`}
            onClick={() => setFilter('unread')}
          >
            Unread ({unreadCount})
          </button>
          <button
            className={`filter-btn ${filter === 'read' ? 'active' : ''}`}
            onClick={() => setFilter('read')}
          >
            Read ({notifications.length - unreadCount})
          </button>
        </div>

        <div className="notification-content">
          {error && (
            <div className="error-message">
              {error}
              <button onClick={fetchNotifications} className="retry-btn">
                Retry
              </button>
            </div>
          )}

          {isLoading ? (
            <div className="loading-message">Loading notifications...</div>
          ) : filteredNotifications.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🔔</div>
              <h3>No notifications</h3>
              <p>
                {filter === 'unread' 
                  ? "You're all caught up! No unread notifications."
                  : filter === 'read'
                  ? "No read notifications to show."
                  : "You don't have any notifications yet."
                }
              </p>
            </div>
          ) : (
            <div className="notifications-list">
              {filteredNotifications.map((notification) => {
                const config = getNotificationConfig(notification.type);
                return (
                  <div
                    key={notification.id}
                    className={`notification-item ${!notification.is_read ? 'unread' : ''}`}
                    onClick={() => !notification.is_read && markAsRead(notification.id)}
                  >
                    <div className="notification-icon" style={{ color: config.color }}>
                      {config.icon}
                    </div>
                    <div className="notification-body">
                      <div className="notification-title">
                        {notification.title}
                      </div>
                      <div className="notification-message">
                        {notification.message}
                      </div>
                      <div className="notification-meta">
                        <span className="notification-type">{config.label}</span>
                        <span className="notification-time">
                          {formatTimeAgo(notification.created_at)}
                        </span>
                      </div>
                    </div>
                    <div className="notification-actions">
                      {!notification.is_read && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            markAsRead(notification.id);
                          }}
                          className="mark-read-btn"
                          title="Mark as read"
                        >
                          ✓
                        </button>
                      )}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteNotification(notification.id);
                        }}
                        className="delete-btn"
                        title="Delete notification"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {connectionStatus !== 'connected' && (
          <div className="connection-warning">
            ⚠️ Not connected. Notifications may not be up to date.
          </div>
        )}
      </div>
    </div>
  );
};

export default NotificationCenter;
