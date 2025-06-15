import React, { useState, useEffect } from 'react';
import { useSocket } from '../../utils';
import './ClientEditModal.css';

const ClientEditModal = ({ client, isOpen, onClose, onSave }) => {
  const { socket } = useSocket();
  const [formData, setFormData] = useState({
    name: '',
    contact_email: '',
    contact_phone: '',
    address: '',
    is_active: true
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (client) {
      setFormData({
        name: client.name || '',
        contact_email: client.contact_email || '',
        contact_phone: client.contact_phone || '',
        address: client.address || '',
        is_active: client.is_active !== undefined ? client.is_active : true
      });
    }
  }, [client]);

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
        request_id: 213, // UPDATE_CLIENT_COMPANY
        data: {
          client_id: client.id,
          ...formData
        }
      };

      socket.send(JSON.stringify(request));

      // Listen for response
      const handleResponse = (event) => {
        try {
          const response = JSON.parse(event.data);
          if (response.request_id === 213) {
            socket.removeEventListener('message', handleResponse);
            setIsLoading(false);
            
            if (response.success) {
              onSave(response.data);
            } else {
              setError(response.error || 'Failed to update client');
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
      <div className="client-edit-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Edit Client Details</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="edit-form">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="name">Company Name *</label>
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
            <label htmlFor="contact_email">Contact Email</label>
            <input
              type="email"
              id="contact_email"
              name="contact_email"
              value={formData.contact_email}
              onChange={handleInputChange}
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="contact_phone">Contact Phone</label>
            <input
              type="tel"
              id="contact_phone"
              name="contact_phone"
              value={formData.contact_phone}
              onChange={handleInputChange}
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="address">Address</label>
            <textarea
              id="address"
              name="address"
              value={formData.address}
              onChange={handleInputChange}
              rows="3"
              disabled={isLoading}
            />
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
              <span className="checkbox-text">Active Client</span>
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

export default ClientEditModal;
