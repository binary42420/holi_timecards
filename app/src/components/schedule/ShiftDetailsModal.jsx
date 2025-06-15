import React, { useState, useEffect } from 'react';
import './ShiftDetailsModal.css';

const ShiftDetailsModal = ({
  shift,
  workers,
  jobs,
  clients,
  onClose,
  onSave,
  onDelete,
  onAssignWorker,
  onUnassignWorker
}) => {
  const [formData, setFormData] = useState({
    job_id: '',
    shift_start_datetime: '',
    shift_end_datetime: '',
    client_po_number: '',
    role_requirements: {
      stagehand: 0,
      crew_chief: 0,
      forklift_operator: 0,
      truck_driver: 0
    }
  });

  const [selectedWorker, setSelectedWorker] = useState('');
  const [selectedRole, setSelectedRole] = useState('stagehand');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (shift) {
      // Edit mode - populate form with existing shift data
      setFormData({
        job_id: shift.job_id || '',
        shift_start_datetime: shift.shift_start_datetime ? 
          new Date(shift.shift_start_datetime).toISOString().slice(0, 16) : '',
        shift_end_datetime: shift.shift_end_datetime ? 
          new Date(shift.shift_end_datetime).toISOString().slice(0, 16) : '',
        client_po_number: shift.client_po_number || '',
        role_requirements: shift.role_requirements || {
          stagehand: 0,
          crew_chief: 0,
          forklift_operator: 0,
          truck_driver: 0
        }
      });
    } else {
      // Create mode - set default values
      const now = new Date();
      const startTime = new Date(now);
      startTime.setHours(9, 0, 0, 0);
      const endTime = new Date(startTime);
      endTime.setHours(17, 0, 0, 0);

      setFormData({
        job_id: '',
        shift_start_datetime: startTime.toISOString().slice(0, 16),
        shift_end_datetime: endTime.toISOString().slice(0, 16),
        client_po_number: '',
        role_requirements: {
          stagehand: 1,
          crew_chief: 0,
          forklift_operator: 0,
          truck_driver: 0
        }
      });
    }
  }, [shift]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleRoleRequirementChange = (role, value) => {
    setFormData(prev => ({
      ...prev,
      role_requirements: {
        ...prev.role_requirements,
        [role]: Math.max(0, parseInt(value) || 0)
      }
    }));
  };

  const handleSave = async () => {
    setIsLoading(true);
    
    try {
      const saveData = {
        ...formData,
        shift_start_datetime: new Date(formData.shift_start_datetime).toISOString(),
        shift_end_datetime: new Date(formData.shift_end_datetime).toISOString()
      };

      if (shift) {
        await onSave(shift.id, saveData);
      } else {
        await onSave(saveData);
      }
      
      onClose();
    } catch (error) {
      console.error('Error saving shift:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this shift?')) {
      setIsLoading(true);
      try {
        await onDelete(shift.id);
        onClose();
      } catch (error) {
        console.error('Error deleting shift:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleAssignWorker = () => {
    if (selectedWorker && selectedRole) {
      onAssignWorker(shift.id, parseInt(selectedWorker), selectedRole);
      setSelectedWorker('');
    }
  };

  const handleUnassignWorker = (workerId, role) => {
    onUnassignWorker(shift.id, workerId, role);
  };

  const getAvailableWorkers = () => {
    const assignedWorkerIds = shift?.assigned_workers?.map(w => w.user_id) || [];
    return workers.filter(worker => !assignedWorkerIds.includes(worker.id));
  };

  const getSelectedJob = () => {
    return jobs.find(job => job.id === parseInt(formData.job_id));
  };

  const calculateDuration = () => {
    if (formData.shift_start_datetime && formData.shift_end_datetime) {
      const start = new Date(formData.shift_start_datetime);
      const end = new Date(formData.shift_end_datetime);
      const duration = (end - start) / (1000 * 60 * 60);
      return duration > 0 ? `${duration} hours` : 'Invalid duration';
    }
    return '';
  };

  const roleOptions = [
    { value: 'stagehand', label: 'Stagehand' },
    { value: 'crew_chief', label: 'Crew Chief' },
    { value: 'forklift_operator', label: 'Forklift Operator' },
    { value: 'truck_driver', label: 'Truck Driver' }
  ];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="shift-details-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{shift ? 'Edit Shift' : 'Create New Shift'}</h2>
          <button onClick={onClose} className="close-button">×</button>
        </div>

        <div className="modal-content">
          <div className="form-section">
            <h3>Shift Details</h3>
            
            <div className="form-row">
              <div className="form-group">
                <label>Job:</label>
                <select
                  value={formData.job_id}
                  onChange={(e) => handleInputChange('job_id', e.target.value)}
                  className="form-select"
                >
                  <option value="">Select a job</option>
                  {jobs.map(job => (
                    <option key={job.id} value={job.id}>
                      {job.jobName} {job.client_company_name && `(${job.client_company_name})`}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>PO Number:</label>
                <input
                  type="text"
                  value={formData.client_po_number}
                  onChange={(e) => handleInputChange('client_po_number', e.target.value)}
                  className="form-input"
                  placeholder="Client PO number"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Start Time:</label>
                <input
                  type="datetime-local"
                  value={formData.shift_start_datetime}
                  onChange={(e) => handleInputChange('shift_start_datetime', e.target.value)}
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label>End Time:</label>
                <input
                  type="datetime-local"
                  value={formData.shift_end_datetime}
                  onChange={(e) => handleInputChange('shift_end_datetime', e.target.value)}
                  className="form-input"
                />
              </div>
            </div>

            {calculateDuration() && (
              <div className="duration-display">
                Duration: {calculateDuration()}
              </div>
            )}
          </div>

          <div className="form-section">
            <h3>Role Requirements</h3>
            <div className="role-requirements">
              {roleOptions.map(role => (
                <div key={role.value} className="role-requirement">
                  <label>{role.label}:</label>
                  <input
                    type="number"
                    min="0"
                    value={formData.role_requirements[role.value]}
                    onChange={(e) => handleRoleRequirementChange(role.value, e.target.value)}
                    className="role-input"
                  />
                </div>
              ))}
            </div>
          </div>

          {shift && (
            <div className="form-section">
              <h3>Assigned Workers</h3>
              
              {shift.assigned_workers && shift.assigned_workers.length > 0 ? (
                <div className="assigned-workers-list">
                  {shift.assigned_workers.map(worker => (
                    <div key={`${worker.user_id}-${worker.role_assigned}`} className="assigned-worker">
                      <span className="worker-name">{worker.name}</span>
                      <span className="worker-role">({worker.role_assigned})</span>
                      <button
                        onClick={() => handleUnassignWorker(worker.user_id, worker.role_assigned)}
                        className="unassign-button"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="no-workers">No workers assigned</p>
              )}

              <div className="assign-worker-section">
                <h4>Assign Worker</h4>
                <div className="assign-controls">
                  <select
                    value={selectedWorker}
                    onChange={(e) => setSelectedWorker(e.target.value)}
                    className="worker-select"
                  >
                    <option value="">Select worker</option>
                    {getAvailableWorkers().map(worker => (
                      <option key={worker.id} value={worker.id}>
                        {worker.name} ({worker.employee_type})
                      </option>
                    ))}
                  </select>

                  <select
                    value={selectedRole}
                    onChange={(e) => setSelectedRole(e.target.value)}
                    className="role-select"
                  >
                    {roleOptions.map(role => (
                      <option key={role.value} value={role.value}>
                        {role.label}
                      </option>
                    ))}
                  </select>

                  <button
                    onClick={handleAssignWorker}
                    disabled={!selectedWorker}
                    className="assign-button"
                  >
                    Assign
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <div className="footer-left">
            {shift && onDelete && (
              <button
                onClick={handleDelete}
                disabled={isLoading}
                className="delete-button"
              >
                Delete Shift
              </button>
            )}
          </div>

          <div className="footer-right">
            <button
              onClick={onClose}
              disabled={isLoading}
              className="cancel-button"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isLoading}
              className="save-button"
            >
              {isLoading ? 'Saving...' : (shift ? 'Update Shift' : 'Create Shift')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ShiftDetailsModal;
