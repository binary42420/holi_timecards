import React from 'react';
import './WorkerCard.css';

const WorkerCard = ({
  worker,
  onDragStart,
  onDragEnd
}) => {
  const handleDragStart = (e) => {
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', worker.id);
    
    if (onDragStart) {
      onDragStart(worker);
    }
  };

  const handleDragEnd = (e) => {
    if (onDragEnd) {
      onDragEnd();
    }
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'crew_chief':
        return '👷‍♂️';
      case 'fork_operator':
        return '🚜';
      case 'pickup_truck_driver':
        return '🚚';
      case 'stagehand':
      default:
        return '👤';
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'crew_chief':
        return '#e74c3c';
      case 'fork_operator':
        return '#f39c12';
      case 'pickup_truck_driver':
        return '#9b59b6';
      case 'stagehand':
      default:
        return '#3498db';
    }
  };

  const getCertificationBadges = () => {
    const badges = [];
    
    if (worker.certifications) {
      if (worker.certifications.can_crew_chief) {
        badges.push({ key: 'cc', label: 'CC', title: 'Crew Chief Certified' });
      }
      if (worker.certifications.can_forklift) {
        badges.push({ key: 'fo', label: 'FO', title: 'Forklift Operator Certified' });
      }
      if (worker.certifications.can_truck) {
        badges.push({ key: 'tr', label: 'TR', title: 'Truck Driver Certified' });
      }
    }
    
    return badges;
  };

  const getAvailabilityStatus = () => {
    if (worker.is_available === false) {
      return { status: 'unavailable', text: 'Unavailable', color: '#e74c3c' };
    }
    
    if (worker.current_shifts_count > 0) {
      return { 
        status: 'assigned', 
        text: `${worker.current_shifts_count} shift${worker.current_shifts_count !== 1 ? 's' : ''}`, 
        color: '#f39c12' 
      };
    }
    
    return { status: 'available', text: 'Available', color: '#27ae60' };
  };

  const certificationBadges = getCertificationBadges();
  const availability = getAvailabilityStatus();
  const roleColor = getRoleColor(worker.employee_type);

  return (
    <div
      className={`worker-card ${availability.status}`}
      draggable={availability.status !== 'unavailable'}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="worker-header">
        <div className="worker-avatar" style={{ backgroundColor: roleColor }}>
          <span className="worker-icon">{getRoleIcon(worker.employee_type)}</span>
        </div>
        
        <div className="worker-info">
          <div className="worker-name" title={worker.name}>
            {worker.name}
          </div>
          <div className="worker-role">
            {worker.employee_type?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Stagehand'}
          </div>
        </div>
        
        <div className="worker-status">
          <div 
            className={`status-indicator ${availability.status}`}
            style={{ backgroundColor: availability.color }}
            title={availability.text}
          ></div>
        </div>
      </div>

      <div className="worker-details">
        <div className="availability-text" style={{ color: availability.color }}>
          {availability.text}
        </div>
        
        {certificationBadges.length > 0 && (
          <div className="certification-badges">
            {certificationBadges.map(badge => (
              <span
                key={badge.key}
                className="cert-badge"
                title={badge.title}
              >
                {badge.label}
              </span>
            ))}
          </div>
        )}
      </div>

      {worker.availability_score && (
        <div className="availability-score">
          <div className="score-bar">
            <div 
              className="score-fill"
              style={{ width: `${worker.availability_score}%` }}
            ></div>
          </div>
          <span className="score-text">{worker.availability_score}% available</span>
        </div>
      )}

      <div className="worker-actions">
        {availability.status !== 'unavailable' && (
          <div className="drag-hint">
            <span className="drag-icon">🖱️</span>
            <span className="drag-text">Drag to assign</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkerCard;
