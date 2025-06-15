import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
import './RoleRequirementBuilder.css';

const RoleRequirementBuilder = ({
  requiredCounts,
  onCountChange,
  disabled = false,
  showAvailableWorkers = true,
  shiftDateTime = null
}) => {
  const { socket } = useSocket();
  const [availableWorkers, setAvailableWorkers] = useState({});
  const [isLoadingAvailability, setIsLoadingAvailability] = useState(false);
  const roleTypes = [
    { 
      key: 'crew_chief', 
      label: 'Crew Chief', 
      icon: '👷‍♂️', 
      color: '#dc3545',
      description: 'Lead teams and coordinate operations'
    },
    { 
      key: 'stagehand', 
      label: 'Stagehand', 
      icon: '🔧', 
      color: '#28a745',
      description: 'General labor and equipment handling'
    },
    { 
      key: 'fork_operator', 
      label: 'Forklift Operator', 
      icon: '🚜', 
      color: '#ffc107',
      description: 'Operate forklifts and heavy equipment'
    },
    { 
      key: 'pickup_truck_driver', 
      label: 'Truck Driver', 
      icon: '🚛', 
      color: '#17a2b8',
      description: 'Drive trucks and transport materials'
    }
  ];

  const handleCountChange = (roleKey, value) => {
    const count = parseInt(value, 10);
    onCountChange(roleKey, Math.max(0, count || 0));
  };

  const getTotalWorkers = () => {
    return Object.values(requiredCounts).reduce((sum, count) => sum + (count || 0), 0);
  };

  // Fetch available workers when component mounts or shift time changes
  useEffect(() => {
    if (showAvailableWorkers && socket && socket.readyState === WebSocket.OPEN) {
      fetchAvailableWorkers();
    }
  }, [socket, showAvailableWorkers, shiftDateTime]);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        if (response.request_id === 400 && response.success) {
          setAvailableWorkers(response.data || {});
          setIsLoadingAvailability(false);
        }
      } catch (e) {
        console.error('Error parsing available workers response:', e);
        setIsLoadingAvailability(false);
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => socket.removeEventListener('message', handleMessage);
  }, [socket]);

  const fetchAvailableWorkers = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      setIsLoadingAvailability(true);
      const request = {
        request_id: 400, // GET_AVAILABLE_WORKERS_BY_ROLE
        data: { shift_datetime: shiftDateTime }
      };
      socket.send(JSON.stringify(request));
    }
  };

  const getAvailabilityStatus = (roleKey, required) => {
    if (!showAvailableWorkers || required === 0) return 'none';
    const available = availableWorkers[roleKey] || 0;
    if (available >= required) return 'sufficient';
    if (available > 0) return 'partial';
    return 'insufficient';
  };

  const getAvailabilityColor = (status) => {
    switch (status) {
      case 'sufficient': return '#28a745';
      case 'partial': return '#ffc107';
      case 'insufficient': return '#dc3545';
      default: return '#6c757d';
    }
  };

  return (
    <div className="role-requirement-builder">
      <div className="builder-header">
        <h4>Required Workers by Role</h4>
        <div className="total-count">
          Total Workers: <span className="count-badge">{getTotalWorkers()}</span>
        </div>
      </div>
      
      <div className="role-grid">
        {roleTypes.map(role => (
          <div 
            key={role.key} 
            className={`role-card ${(requiredCounts[role.key] || 0) > 0 ? 'active' : ''}`}
            style={{ '--role-color': role.color }}
          >
            <div className="role-header">
              <span className="role-icon">{role.icon}</span>
              <div className="role-info">
                <h5 className="role-title">{role.label}</h5>
                <p className="role-description">{role.description}</p>
              </div>
            </div>
            
            <div className="role-counter">
              <button
                type="button"
                className="counter-btn decrease"
                onClick={() => handleCountChange(role.key, (requiredCounts[role.key] || 0) - 1)}
                disabled={disabled || (requiredCounts[role.key] || 0) <= 0}
              >
                −
              </button>
              
              <input
                type="number"
                className="counter-input"
                min="0"
                max="99"
                value={requiredCounts[role.key] || 0}
                onChange={(e) => handleCountChange(role.key, e.target.value)}
                disabled={disabled}
              />
              
              <button
                type="button"
                className="counter-btn increase"
                onClick={() => handleCountChange(role.key, (requiredCounts[role.key] || 0) + 1)}
                disabled={disabled}
              >
                +
              </button>
            </div>
            
            {(requiredCounts[role.key] || 0) > 0 && (
              <div className="role-summary">
                {requiredCounts[role.key]} {role.label}{requiredCounts[role.key] > 1 ? 's' : ''} needed
              </div>
            )}

            {showAvailableWorkers && (
              <div className="availability-info">
                {isLoadingAvailability ? (
                  <div className="availability-loading">Loading...</div>
                ) : (
                  <div
                    className="availability-status"
                    style={{
                      color: getAvailabilityColor(getAvailabilityStatus(role.key, requiredCounts[role.key] || 0))
                    }}
                  >
                    {availableWorkers[role.key] || 0} available
                    {(requiredCounts[role.key] || 0) > 0 && (
                      <span className="availability-indicator">
                        {getAvailabilityStatus(role.key, requiredCounts[role.key]) === 'sufficient' && ' ✓'}
                        {getAvailabilityStatus(role.key, requiredCounts[role.key]) === 'partial' && ' ⚠'}
                        {getAvailabilityStatus(role.key, requiredCounts[role.key]) === 'insufficient' && ' ✗'}
                      </span>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
      
      {getTotalWorkers() === 0 && (
        <div className="no-workers-warning">
          ⚠️ No workers required. Add at least one worker to create the shift.
        </div>
      )}

      {showAvailableWorkers && (
        <div className="builder-footer">
          <button
            type="button"
            onClick={fetchAvailableWorkers}
            disabled={isLoadingAvailability}
            className="refresh-availability-btn"
          >
            {isLoadingAvailability ? 'Refreshing...' : '🔄 Refresh Availability'}
          </button>

          <div className="availability-legend">
            <div className="legend-item">
              <span style={{ color: '#28a745' }}>✓</span> Sufficient workers available
            </div>
            <div className="legend-item">
              <span style={{ color: '#ffc107' }}>⚠</span> Partially available
            </div>
            <div className="legend-item">
              <span style={{ color: '#dc3545' }}>✗</span> Insufficient workers
            </div>
          </div>

          {getTotalWorkers() > 0 && (
            <div className="total-availability-summary">
              <strong>Total Required:</strong> {getTotalWorkers()} workers
              {Object.keys(availableWorkers).length > 0 && (
                <span className="total-available">
                  | <strong>Total Available:</strong> {Object.values(availableWorkers).reduce((sum, count) => sum + count, 0)} workers
                </span>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default RoleRequirementBuilder;
