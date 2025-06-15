import React, { useState, useEffect } from 'react';
import { useSocket } from '../../utils';
import './JobEditModal.css';

const JobEditModal = ({ job, isOpen, onClose, onSave }) => {
  const { socket } = useSocket();
  const [formData, setFormData] = useState({
    name: '',
    venue_name: '',
    venue_address: '',
    description: '',
    estimated_start_date: '',
    estimated_end_date: '',
    is_active: true
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (job) {
      setFormData({
        name: job.name || '',
        venue_name: job.venue_name || '',
        venue_address: job.venue_address || '',
        description: job.description || '',
        estimated_start_date: job.estimated_start_date ? job.estimated_start_date.split('T')[0] : '',
        estimated_end_date: job.estimated_end_date ? job.estimated_end_date.split('T')[0] : '',
        is_active: job.is_active !== undefined ? job.is_active : true
      });
    }
  }, [job]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError('Connection not available. Please try again.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const request = {
        request_id: 214, // UPDATE_JOB
        data: {
          job_id: job.id,
          ...formData
        }
      };

      socket.send(JSON.stringify(request));

      // Listen for response
      const handleResponse = (event) => {
        try {
          const response = JSON.parse(event.data);
          if (response.request_id === 214) {
            socket.removeEventListener('message', handleResponse);
            setIsLoading(false);
            
            if (response.success) {
              onSave(response.data);
            } else {
              setError(response.error || 'Failed to update job');
            }
          }
        } catch (err) {
          console.error('Error parsing response:', err);
        }
      };

      socket.addEventListener('message', handleResponse);

      // Timeout after 10 seconds
      setTimeout(() => {
        socket.removeEventListener('message', handleResponse);
        if (isLoading) {
          setIsLoading(false);
          setError('Request timed out. Please try again.');
        }
      }, 10000);

    } catch (err) {
      setIsLoading(false);
      setError('Failed to send request. Please try again.');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="job-edit-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Edit Job Details</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="edit-form">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="name">Job Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                disabled={isLoading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="venue_name">Venue Name</label>
              <input
                type="text"
                id="venue_name"
                name="venue_name"
                value={formData.venue_name}
                onChange={handleInputChange}
                disabled={isLoading}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="venue_address">Venue Address</label>
            <input
              type="text"
              id="venue_address"
              name="venue_address"
              value={formData.venue_address}
              onChange={handleInputChange}
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              rows="3"
              disabled={isLoading}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="estimated_start_date">Start Date</label>
              <input
                type="date"
                id="estimated_start_date"
                name="estimated_start_date"
                value={formData.estimated_start_date}
                onChange={handleInputChange}
                disabled={isLoading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="estimated_end_date">End Date</label>
              <input
                type="date"
                id="estimated_end_date"
                name="estimated_end_date"
                value={formData.estimated_end_date}
                onChange={handleInputChange}
                disabled={isLoading}
              />
            </div>
          </div>

          <div className="form-group checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="is_active"
                checked={formData.is_active}
                onChange={handleInputChange}
                disabled={isLoading}
              />
              <span className="checkbox-text">Active Job</span>
            </label>
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={onClose}
              className="cancel-button"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="save-button"
              disabled={isLoading}
            >
              {isLoading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default JobEditModal;
