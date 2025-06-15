import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSocket } from '../../utils';
import './JobDetailsModal.css';

const JobDetailsModal = ({ job, isOpen, onClose }) => {
  const { socket } = useSocket();
  const navigate = useNavigate();
  const [shifts, setShifts] = useState([]);
  const [selectedShift, setSelectedShift] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('details'); // 'details', 'shifts'

  useEffect(() => {
    if (isOpen && job && socket && socket.readyState === WebSocket.OPEN) {
      // Fetch shifts for this job
      setIsLoading(true);
      const request = {
        request_id: 221, // GET_SHIFTS_BY_JOB
        data: { job_id: job.id }
      };
      socket.send(JSON.stringify(request));
    }
  }, [isOpen, job, socket]);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        
        if (response.request_id === 221) { // GET_SHIFTS_BY_JOB response
          setIsLoading(false);
          if (response.success) {
            setShifts(response.data || []);
          } else {
            console.error('Failed to fetch shifts:', response.error);
            setShifts([]);
          }
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => socket.removeEventListener('message', handleMessage);
  }, [socket]);

  if (!isOpen || !job) return null;

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatTime = (dateString) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getShiftStatusBadge = (shift) => {
    const now = new Date();
    const shiftStart = new Date(shift.shift_start_datetime);
    const shiftEnd = new Date(shift.shift_end_datetime);

    if (now < shiftStart) {
      return <span className="status-badge upcoming">Upcoming</span>;
    } else if (now >= shiftStart && now <= shiftEnd) {
      return <span className="status-badge active">In Progress</span>;
    } else {
      return <span className="status-badge completed">Completed</span>;
    }
  };

  const handleShiftClick = (shift) => {
    setSelectedShift(selectedShift?.id === shift.id ? null : shift);
  };

  const handleAssignWorkersClick = (shift) => {
    // Navigate to the enhanced schedule page with the specific job and shift
    navigate('/enhanced-schedule', {
      state: {
        jobId: job.id,
        shiftId: shift.id,
        jobName: job.name,
        shiftDescription: shift.shift_description || `Shift ${shift.id}`
      }
    });
  };

  const getRequiredWorkersText = (requiredCounts) => {
    if (!requiredCounts) return 'No requirements specified';
    
    const requirements = [];
    if (requiredCounts.stagehand > 0) requirements.push(`${requiredCounts.stagehand} Stagehand${requiredCounts.stagehand > 1 ? 's' : ''}`);
    if (requiredCounts.crew_chief > 0) requirements.push(`${requiredCounts.crew_chief} Crew Chief${requiredCounts.crew_chief > 1 ? 's' : ''}`);
    if (requiredCounts.forklift_operator > 0) requirements.push(`${requiredCounts.forklift_operator} Forklift Operator${requiredCounts.forklift_operator > 1 ? 's' : ''}`);
    if (requiredCounts.truck_driver > 0) requirements.push(`${requiredCounts.truck_driver} Truck Driver${requiredCounts.truck_driver > 1 ? 's' : ''}`);
    
    return requirements.length > 0 ? requirements.join(', ') : 'No specific requirements';
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="job-details-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="header-content">
            <h2>{job.name}</h2>
            <p className="job-venue">{job.venue_name}</p>
            <p className="job-address">{job.venue_address}</p>
          </div>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-tabs">
          <button 
            className={`tab-button ${activeTab === 'details' ? 'active' : ''}`}
            onClick={() => setActiveTab('details')}
          >
            📋 Job Details
          </button>
          <button 
            className={`tab-button ${activeTab === 'shifts' ? 'active' : ''}`}
            onClick={() => setActiveTab('shifts')}
          >
            🕐 Shifts ({shifts.length})
          </button>
        </div>

        <div className="modal-content">
          {activeTab === 'details' && (
            <div className="details-tab">
              <div className="job-info-section">
                <h3>Job Information</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <label>Job ID:</label>
                    <span>{job.id}</span>
                  </div>
                  <div className="info-item">
                    <label>Status:</label>
                    <span className={`status-badge ${job.is_active ? 'active' : 'completed'}`}>
                      {job.is_active ? 'Active' : 'Completed'}
                    </span>
                  </div>
                  <div className="info-item">
                    <label>Estimated Start:</label>
                    <span>{formatDate(job.estimated_start_date)}</span>
                  </div>
                  <div className="info-item">
                    <label>Estimated End:</label>
                    <span>{formatDate(job.estimated_end_date)}</span>
                  </div>
                  <div className="info-item">
                    <label>Created:</label>
                    <span>{formatDateTime(job.created_at)}</span>
                  </div>
                  <div className="info-item">
                    <label>Created By:</label>
                    <span>Manager ID: {job.created_by}</span>
                  </div>
                </div>
              </div>

              <div className="venue-info-section">
                <h3>Venue Information</h3>
                <div className="info-grid">
                  <div className="info-item full-width">
                    <label>Venue Name:</label>
                    <span>{job.venue_name}</span>
                  </div>
                  <div className="info-item full-width">
                    <label>Address:</label>
                    <span>{job.venue_address}</span>
                  </div>
                  {job.venue_contact_info && (
                    <div className="info-item full-width">
                      <label>Contact Info:</label>
                      <span>{job.venue_contact_info}</span>
                    </div>
                  )}
                </div>
              </div>

              {job.description && (
                <div className="description-section">
                  <h3>Description</h3>
                  <p className="job-description">{job.description}</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'shifts' && (
            <div className="shifts-tab">
              <div className="shifts-header">
                <h3>All Shifts</h3>
                {isLoading ? (
                  <p>Loading shifts...</p>
                ) : (
                  <p>Click on any shift to view assigned workers</p>
                )}
              </div>
              
              {isLoading ? (
                <div className="loading-state">
                  <p>Loading shifts...</p>
                </div>
              ) : shifts.length > 0 ? (
                <div className="shifts-list">
                  {shifts.map((shift) => (
                    <div key={shift.id} className="shift-item">
                      <div 
                        className="shift-header"
                        onClick={() => handleShiftClick(shift)}
                      >
                        <div className="shift-info">
                          <h4 className="shift-title">
                            {shift.shift_description || `Shift ${shift.id}`}
                          </h4>
                          <div className="shift-time">
                            {formatDateTime(shift.shift_start_datetime)} - {formatTime(shift.shift_end_datetime)}
                          </div>
                        </div>
                        <div className="shift-status">
                          {getShiftStatusBadge(shift)}
                          <span className="expand-icon">
                            {selectedShift?.id === shift.id ? '▼' : '▶'}
                          </span>
                        </div>
                      </div>

                      <div className="shift-requirements">
                        <span className="requirements-text">
                          Required: {getRequiredWorkersText(shift.required_employee_counts)}
                        </span>
                      </div>

                      {selectedShift?.id === shift.id && (
                        <div className="shift-details">
                          <div className="shift-workers">
                            <div className="workers-header">
                              <h5>Assigned Workers</h5>
                              <button
                                className="assign-workers-button"
                                onClick={() => handleAssignWorkersClick(shift)}
                                title="Assign workers to this shift"
                              >
                                👥 Assign Workers
                              </button>
                            </div>
                            {shift.workers && shift.workers.length > 0 ? (
                              <div className="workers-list">
                                {shift.workers.map((worker) => (
                                  <div key={worker.id} className="worker-item">
                                    <div className="worker-info">
                                      <span className="worker-name">{worker.name}</span>
                                      <span className="worker-role">{worker.employee_type || 'Stagehand'}</span>
                                    </div>
                                    <div className="worker-status">
                                      <span className={`status-badge ${worker.isActive ? 'active' : 'inactive'}`}>
                                        {worker.isActive ? 'Active' : 'Inactive'}
                                      </span>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <div className="no-workers-section">
                                <p className="no-workers">No workers assigned to this shift</p>
                                <p className="assign-suggestion">Click "Assign Workers" to add workers to this shift.</p>
                              </div>
                            )}
                          </div>

                          {shift.special_instructions && (
                            <div className="shift-instructions">
                              <h5>Special Instructions</h5>
                              <p>{shift.special_instructions}</p>
                            </div>
                          )}

                          {shift.client_po_number && (
                            <div className="shift-po">
                              <h5>PO Number</h5>
                              <p>{shift.client_po_number}</p>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <p>No shifts found for this job.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default JobDetailsModal;
