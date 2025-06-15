import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
import './JobEditModal.css';

const JobEditModal = ({ job, isOpen, onClose, onJobUpdated, clientCompanies = [] }) => {
  const { socket } = useSocket();
  const [formData, setFormData] = useState({
    name: '',
    client_company_id: '',
    venue_name: '',
    venue_address: '',
    venue_contact_info: '',
    description: '',
    is_active: true
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Initialize form data when job changes
  useEffect(() => {
    if (job) {
      setFormData({
        name: job.name || '',
        client_company_id: job.client_company_id || '',
        venue_name: job.venue_name || '',
        venue_address: job.venue_address || '',
        venue_contact_info: job.venue_contact_info || '',
        description: job.description || '',
        is_active: job.is_active !== undefined ? job.is_active : true
      });
    }
  }, [job]);

  // Handle WebSocket responses
  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        
        if (response.request_id === 213) { // UPDATE_JOB
          setIsLoading(false);
          
          if (response.success) {
            setSuccessMessage('Job updated successfully!');
            setError('');
            
            if (onJobUpdated) {
              onJobUpdated(response.data);
            }
            
            // Auto-close modal after success
            setTimeout(() => {
              onClose();
            }, 1500);
          } else {
            setError(response.error || 'Failed to update job');
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
  }, [socket, onJobUpdated, onClose]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    setError('');
    setSuccessMessage('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError('Cannot save: WebSocket is not connected');
      return;
    }

    if (!formData.name.trim() || !formData.venue_name.trim() || !formData.venue_address.trim()) {
      setError('Job name, venue name, and venue address are required.');
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccessMessage('');

    const request = {
      request_id: 213, // UPDATE_JOB
      data: {
        job_id: job.id,
        name: formData.name.trim(),
        client_company_id: parseInt(formData.client_company_id, 10),
        venue_name: formData.venue_name.trim(),
        venue_address: formData.venue_address.trim(),
        venue_contact_info: formData.venue_contact_info.trim(),
        description: formData.description.trim(),
        is_active: formData.is_active
      }
    };

    socket.send(JSON.stringify(request));
  };

  const getCompanyNameById = (id) => {
    const company = clientCompanies.find(c => c.id === parseInt(id, 10));
    return company ? company.name : 'Unknown Company';
  };

  if (!isOpen || !job) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="job-edit-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Edit Job</h2>
          <button className="close-button" onClick={onClose} disabled={isLoading}>×</button>
        </div>

        <div className="modal-content">
          {error && <div className="error-message">{error}</div>}
          {successMessage && <div className="success-message">{successMessage}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="jobName">Job Name *</label>
                <input
                  type="text"
                  id="jobName"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="e.g., CRSSD Festival Setup"
                  required
                  disabled={isLoading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="clientCompany">Client Company *</label>
                <select
                  id="clientCompany"
                  value={formData.client_company_id}
                  onChange={(e) => handleInputChange('client_company_id', e.target.value)}
                  required
                  disabled={isLoading}
                >
                  <option value="">Select a client company</option>
                  {clientCompanies.map((company) => (
                    <option key={company.id} value={company.id}>
                      {company.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="venueName">Venue Name *</label>
                <input
                  type="text"
                  id="venueName"
                  value={formData.venue_name}
                  onChange={(e) => handleInputChange('venue_name', e.target.value)}
                  placeholder="e.g., Waterfront Park"
                  required
                  disabled={isLoading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="venueContact">Venue Contact</label>
                <input
                  type="text"
                  id="venueContact"
                  value={formData.venue_contact_info}
                  onChange={(e) => handleInputChange('venue_contact_info', e.target.value)}
                  placeholder="e.g., John Doe - (555) 123-4567"
                  disabled={isLoading}
                />
              </div>

              <div className="form-group full-width">
                <label htmlFor="venueAddress">Venue Address *</label>
                <input
                  type="text"
                  id="venueAddress"
                  value={formData.venue_address}
                  onChange={(e) => handleInputChange('venue_address', e.target.value)}
                  placeholder="e.g., 1600 Pacific Hwy, San Diego, CA 92101"
                  required
                  disabled={isLoading}
                />
              </div>

              <div className="form-group full-width">
                <label htmlFor="jobDescription">Job Description</label>
                <textarea
                  id="jobDescription"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="e.g., Stage setup and teardown for 3-day music festival"
                  rows="3"
                  disabled={isLoading}
                />
              </div>

              <div className="form-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => handleInputChange('is_active', e.target.checked)}
                    disabled={isLoading}
                  />
                  Job is active
                </label>
              </div>
            </div>

            <div className="modal-actions">
              <button
                type="button"
                onClick={onClose}
                disabled={isLoading}
                className="cancel-button"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading || !formData.name.trim() || !formData.venue_name.trim() || !formData.venue_address.trim()}
                className="save-button"
              >
                {isLoading ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default JobEditModal;
