import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
import './EmployeeCertificationManager.css';

const EmployeeCertificationManager = ({ 
  employeeId, 
  employeeName, 
  currentCertifications = {}, 
  onUpdate,
  isModal = false,
  onClose 
}) => {
  const { socket, connectionStatus } = useSocket();
  const [certifications, setCertifications] = useState({
    can_crew_chief: false,
    can_forklift: false,
    can_truck: false,
    ...currentCertifications
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const certificationConfig = {
    can_crew_chief: {
      label: 'Crew Chief',
      icon: '👷‍♂️',
      color: '#28a745',
      description: 'Can supervise teams and coordinate operations',
      requirements: 'Leadership experience and safety training required'
    },
    can_forklift: {
      label: 'Forklift Operator',
      icon: '🚜',
      color: '#ffc107',
      description: 'Certified to operate forklifts and heavy equipment',
      requirements: 'Valid forklift certification and safety training'
    },
    can_truck: {
      label: 'Truck Driver',
      icon: '🚛',
      color: '#dc3545',
      description: 'Licensed to drive trucks and transport materials',
      requirements: 'Valid commercial driver\'s license (CDL)'
    }
  };

  useEffect(() => {
    setCertifications({
      can_crew_chief: false,
      can_forklift: false,
      can_truck: false,
      ...currentCertifications
    });
  }, [currentCertifications]);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        if (response.request_id === 410) { // UPDATE_EMPLOYEE_CERTIFICATIONS
          setIsSaving(false);
          if (response.success) {
            setSuccessMessage('Certifications updated successfully!');
            setError('');
            if (onUpdate) {
              onUpdate(certifications);
            }
            // Auto-close modal after successful update
            if (isModal && onClose) {
              setTimeout(() => {
                onClose();
              }, 1500);
            }
          } else {
            setError(response.error || 'Failed to update certifications');
            setSuccessMessage('');
          }
        }
      } catch (e) {
        console.error('Error parsing certification response:', e);
        setIsSaving(false);
        setError('Error processing server response');
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => socket.removeEventListener('message', handleMessage);
  }, [socket, certifications, onUpdate, isModal, onClose]);

  const handleCertificationChange = (certType, isChecked) => {
    setCertifications(prev => ({
      ...prev,
      [certType]: isChecked
    }));
    setError('');
    setSuccessMessage('');
  };

  const handleSave = () => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError('Cannot save: WebSocket is not connected');
      return;
    }

    setIsSaving(true);
    setError('');
    setSuccessMessage('');

    const request = {
      request_id: 410, // UPDATE_EMPLOYEE_CERTIFICATIONS
      data: {
        employee_id: employeeId,
        certifications: certifications
      }
    };

    socket.send(JSON.stringify(request));
  };

  const handleReset = () => {
    setCertifications({
      can_crew_chief: false,
      can_forklift: false,
      can_truck: false,
      ...currentCertifications
    });
    setError('');
    setSuccessMessage('');
  };

  const hasChanges = () => {
    return Object.keys(certifications).some(key => 
      certifications[key] !== (currentCertifications[key] || false)
    );
  };

  const getActiveCertificationsCount = () => {
    return Object.values(certifications).filter(Boolean).length;
  };

  const isConnected = connectionStatus === 'connected';

  const content = (
    <div className="certification-manager-content">
      <div className="certification-header">
        <h3>Employee Certifications</h3>
        {employeeName && (
          <div className="employee-info">
            <strong>{employeeName}</strong>
            <span className="cert-count">
              {getActiveCertificationsCount()} certification{getActiveCertificationsCount() !== 1 ? 's' : ''}
            </span>
          </div>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}
      {successMessage && <div className="success-message">{successMessage}</div>}

      <div className="certifications-grid">
        {Object.entries(certificationConfig).map(([certType, config]) => (
          <div 
            key={certType} 
            className={`certification-card ${certifications[certType] ? 'certified' : 'not-certified'}`}
          >
            <div className="cert-header">
              <div className="cert-icon" style={{ color: config.color }}>
                {config.icon}
              </div>
              <div className="cert-info">
                <h4 className="cert-title">{config.label}</h4>
                <p className="cert-description">{config.description}</p>
              </div>
              <div className="cert-toggle">
                <label className="toggle-switch">
                  <input
                    type="checkbox"
                    checked={certifications[certType]}
                    onChange={(e) => handleCertificationChange(certType, e.target.checked)}
                    disabled={isSaving || !isConnected}
                  />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>
            
            <div className="cert-requirements">
              <small>{config.requirements}</small>
            </div>

            {certifications[certType] && (
              <div className="cert-status certified-status">
                ✓ Certified
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="certification-actions">
        <button
          onClick={handleReset}
          disabled={isSaving || !hasChanges()}
          className="btn btn-secondary"
        >
          Reset
        </button>
        <button
          onClick={handleSave}
          disabled={isSaving || !hasChanges() || !isConnected}
          className="btn btn-primary"
        >
          {isSaving ? 'Saving...' : 'Save Certifications'}
        </button>
        {isModal && (
          <button
            onClick={onClose}
            disabled={isSaving}
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
    </div>
  );

  if (isModal) {
    return (
      <div className="certification-modal-overlay">
        <div className="certification-modal">
          <div className="modal-header">
            <h2>Manage Certifications</h2>
            <button onClick={onClose} className="modal-close-btn">×</button>
          </div>
          {content}
        </div>
      </div>
    );
  }

  return (
    <div className="employee-certification-manager">
      {content}
    </div>
  );
};

export default EmployeeCertificationManager;
