import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
import './ShiftRequirementsEditor.css';

const ShiftRequirementsEditor = ({ 
  shift, 
  onUpdate, 
  onClose, 
  isModal = true 
}) => {
  const { socket, connectionStatus } = useSocket();
  const [requirements, setRequirements] = useState({
    stagehand: 0,
    crew_chief: 0,
    forklift_operator: 0,
    truck_driver: 0,
    ...shift.required_employee_counts
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const roleConfig = {
    stagehand: {
      label: 'Stagehands',
      icon: '👷',
      color: '#3498db',
      description: 'General stage workers'
    },
    crew_chief: {
      label: 'Crew Chiefs',
      icon: '👨‍💼',
      color: '#e74c3c',
      description: 'Team leaders and supervisors'
    },
    forklift_operator: {
      label: 'Forklift Operators',
      icon: '🚜',
      color: '#f39c12',
      description: 'Certified forklift operators'
    },
    truck_driver: {
      label: 'Truck Drivers',
      icon: '🚛',
      color: '#27ae60',
      description: 'Licensed truck drivers'
    }
  };

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        
        if (response.request_id === 232) { // UPDATE_SHIFT_REQUIREMENTS
          setIsLoading(false);
          
          if (response.success) {
            setSuccessMessage('Shift requirements updated successfully!');
            setError('');
            
            if (onUpdate) {
              onUpdate(response.data);
            }
            
            // Auto-close modal after success
            setTimeout(() => {
              if (onClose) onClose();
            }, 1500);
          } else {
            setError(response.error || 'Failed to update shift requirements');
            setSuccessMessage('');
          }
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
        setIsLoading(false);
        setError('Communication error occurred');
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => socket.removeEventListener('message', handleMessage);
  }, [socket, onUpdate, onClose]);

  const handleRequirementChange = (role, value) => {
    const numValue = Math.max(0, parseInt(value) || 0);
    setRequirements(prev => ({
      ...prev,
      [role]: numValue
    }));
    setError('');
    setSuccessMessage('');
  };

  const handleSave = () => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError('Cannot save: WebSocket is not connected');
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccessMessage('');

    const request = {
      request_id: 232, // UPDATE_SHIFT_REQUIREMENTS
      data: {
        shift_id: shift.id,
        required_employee_counts: requirements
      }
    };

    socket.send(JSON.stringify(request));
  };

  const handleReset = () => {
    setRequirements({
      stagehand: 0,
      crew_chief: 0,
      forklift_operator: 0,
      truck_driver: 0,
      ...shift.required_employee_counts
    });
    setError('');
    setSuccessMessage('');
  };

  const hasChanges = () => {
    const original = shift.required_employee_counts || {};
    return Object.keys(requirements).some(role => 
      requirements[role] !== (original[role] || 0)
    );
  };

  const getTotalWorkers = () => {
    return Object.values(requirements).reduce((sum, count) => sum + count, 0);
  };

  const isConnected = connectionStatus === 'connected';

  if (isModal) {
    return (
      <div className="modal-overlay">
        <div className="modal-content shift-requirements-editor">
          <div className="modal-header">
            <h2>Edit Shift Requirements</h2>
            <button 
              className="modal-close-btn" 
              onClick={onClose}
              disabled={isLoading}
            >
              ×
            </button>
          </div>
          
          <div className="modal-body">
            <ShiftRequirementsContent />
          </div>
        </div>
      </div>
    );
  }

  function ShiftRequirementsContent() {
    return (
      <>
        <div className="shift-info">
          <h3>Shift Details</h3>
          <p><strong>Date:</strong> {shift.shift_start_datetime ? new Date(shift.shift_start_datetime).toLocaleDateString() : 'N/A'}</p>
          <p><strong>Time:</strong> {shift.shift_start_datetime ? new Date(shift.shift_start_datetime).toLocaleTimeString() : 'N/A'} - {shift.shift_end_datetime ? new Date(shift.shift_end_datetime).toLocaleTimeString() : 'N/A'}</p>
          <p><strong>Current Total Workers:</strong> {getTotalWorkers()}</p>
        </div>

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        {successMessage && (
          <div className="success-message">
            ✅ {successMessage}
          </div>
        )}

        <div className="requirements-grid">
          {Object.entries(roleConfig).map(([roleKey, config]) => (
            <div key={roleKey} className="requirement-card">
              <div className="requirement-header">
                <div className="role-icon" style={{ color: config.color }}>
                  {config.icon}
                </div>
                <div className="role-info">
                  <h4 className="role-title">{config.label}</h4>
                  <p className="role-description">{config.description}</p>
                </div>
              </div>
              
              <div className="requirement-input">
                <label htmlFor={`${roleKey}-count`}>Required Count:</label>
                <input
                  id={`${roleKey}-count`}
                  type="number"
                  min="0"
                  max="50"
                  value={requirements[roleKey]}
                  onChange={(e) => handleRequirementChange(roleKey, e.target.value)}
                  disabled={isLoading || !isConnected}
                  className="count-input"
                />
              </div>
            </div>
          ))}
        </div>

        <div className="requirements-actions">
          <button
            onClick={handleReset}
            disabled={isLoading || !hasChanges()}
            className="btn btn-secondary"
          >
            Reset
          </button>
          <button
            onClick={handleSave}
            disabled={isLoading || !hasChanges() || !isConnected}
            className="btn btn-primary"
          >
            {isLoading ? 'Saving...' : 'Save Requirements'}
          </button>
          {isModal && (
            <button
              onClick={onClose}
              disabled={isLoading}
              className="btn btn-outline"
            >
              Cancel
            </button>
          )}
        </div>

        {!isConnected && (
          <div className="connection-warning">
            ⚠️ Not connected to server. Changes cannot be saved.
          </div>
        )}
      </>
    );
  }

  return <ShiftRequirementsContent />;
};

export default ShiftRequirementsEditor;
