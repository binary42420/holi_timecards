import React, { useState, useEffect, useCallback } from 'react';
import { useSocket } from '../utils';
import '../css/ManagerClientCompanies.css';

const ManagerClientCompaniesPage = () => {
  const { socket, connectionStatus, reconnect } = useSocket();
  const [clientCompanies, setClientCompanies] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Form state for creating new client company
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newCompanyName, setNewCompanyName] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  // Edit state
  const [editingCompany, setEditingCompany] = useState(null);
  const [editCompanyName, setEditCompanyName] = useState('');

  const fetchClientCompanies = useCallback(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      setIsLoading(true);
      setError('');
      setSuccessMessage('');
      const request = { request_id: 200 }; // GET_ALL_CLIENT_COMPANIES
      socket.send(JSON.stringify(request));
    } else {
      setError('Cannot fetch client companies: WebSocket is not connected.');
    }
  }, [socket]);

  const getConnectionStatusDisplay = () => {
    switch (connectionStatus) {
      case 'connecting':
        return { text: 'Connecting...', color: '#ffa500', showReconnect: false };
      case 'connected':
        return { text: 'Connected', color: '#28a745', showReconnect: false };
      case 'disconnected':
        return { text: 'Disconnected', color: '#dc3545', showReconnect: true };
      case 'reconnecting':
        return { text: 'Reconnecting...', color: '#ffa500', showReconnect: false };
      case 'failed':
        return { text: 'Connection Failed', color: '#dc3545', showReconnect: true };
      case 'error':
        return { text: 'Connection Error', color: '#dc3545', showReconnect: true };
      default:
        return { text: 'Unknown', color: '#6c757d', showReconnect: true };
    }
  };

  const isConnected = connectionStatus === 'connected';

  const handleCreateCompany = () => {
    if (!newCompanyName.trim()) {
      setError('Company name is required.');
      return;
    }

    if (socket && socket.readyState === WebSocket.OPEN) {
      setIsCreating(true);
      setError('');
      setSuccessMessage('');
      const request = {
        request_id: 201, // CREATE_CLIENT_COMPANY
        data: { name: newCompanyName.trim() }
      };
      socket.send(JSON.stringify(request));
    } else {
      setError('Cannot create company: WebSocket is not connected.');
    }
  };

  const handleUpdateCompany = () => {
    if (!editCompanyName.trim()) {
      setError('Company name is required.');
      return;
    }

    if (socket && socket.readyState === WebSocket.OPEN) {
      setError('');
      setSuccessMessage('');
      const request = {
        request_id: 202, // UPDATE_CLIENT_COMPANY
        data: {
          id: editingCompany.id,
          name: editCompanyName.trim()
        }
      };
      socket.send(JSON.stringify(request));
    } else {
      setError('Cannot update company: WebSocket is not connected.');
    }
  };

  const handleDeleteCompany = (companyId) => {
    if (window.confirm('Are you sure you want to delete this client company? This action cannot be undone.')) {
      if (socket && socket.readyState === WebSocket.OPEN) {
        setError('');
        setSuccessMessage('');
        const request = {
          request_id: 203, // DELETE_CLIENT_COMPANY
          data: { id: companyId }
        };
        socket.send(JSON.stringify(request));
      } else {
        setError('Cannot delete company: WebSocket is not connected.');
      }
    }
  };

  useEffect(() => {
    if (socket) {
      fetchClientCompanies();
    }
  }, [socket, fetchClientCompanies]);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        setIsLoading(false);
        setIsCreating(false);

        if (response.request_id === 200) { // Get All Client Companies
          if (response.success && Array.isArray(response.data)) {
            setClientCompanies(response.data);
          } else {
            setError(response.error || 'Failed to fetch client companies.');
            setClientCompanies([]);
          }
        } else if (response.request_id === 201) { // Create Client Company
          if (response.success) {
            setSuccessMessage('Client company created successfully!');
            setNewCompanyName('');
            setShowCreateForm(false);
            fetchClientCompanies(); // Refresh the list
          } else {
            setError(response.error || 'Failed to create client company.');
          }
        } else if (response.request_id === 202) { // Update Client Company
          if (response.success) {
            setSuccessMessage('Client company updated successfully!');
            setEditingCompany(null);
            setEditCompanyName('');
            fetchClientCompanies(); // Refresh the list
          } else {
            setError(response.error || 'Failed to update client company.');
          }
        } else if (response.request_id === 203) { // Delete Client Company
          if (response.success) {
            setSuccessMessage('Client company deleted successfully!');
            fetchClientCompanies(); // Refresh the list
          } else {
            setError(response.error || 'Failed to delete client company.');
          }
        }
      } catch (e) {
        setIsLoading(false);
        setIsCreating(false);
        setError('Error processing server response for client companies.');
        console.error('WebSocket message error in ManagerClientCompaniesPage:', e);
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => {
      socket.removeEventListener('message', handleMessage);
    };
  }, [socket, fetchClientCompanies]);

  return (
    <div className="client-companies-container">
      <div className="header-section">
        <h2>Client Companies Directory</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{
              color: getConnectionStatusDisplay().color,
              fontWeight: 'bold',
              fontSize: '14px'
            }}>
              ● {getConnectionStatusDisplay().text}
            </span>
            {getConnectionStatusDisplay().showReconnect && (
              <button
                onClick={reconnect}
                style={{
                  padding: '4px 8px',
                  fontSize: '12px',
                  backgroundColor: '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Reconnect
              </button>
            )}
          </div>
          <button
            className="create-button"
            onClick={() => setShowCreateForm(!showCreateForm)}
            disabled={isLoading || !isConnected}
          >
            {showCreateForm ? 'Cancel' : 'Add New Client'}
          </button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}
      {successMessage && <div className="success-message">{successMessage}</div>}

      {/* Create Form */}
      {showCreateForm && (
        <div className="create-form">
          <h3>Add New Client Company</h3>
          <div className="form-group">
            <input
              type="text"
              placeholder="Company Name"
              value={newCompanyName}
              onChange={(e) => setNewCompanyName(e.target.value)}
              disabled={isCreating}
              className="form-input"
            />
          </div>
          <div className="form-actions">
            <button
              onClick={handleCreateCompany}
              disabled={isCreating || !newCompanyName.trim() || !isConnected}
              className="submit-button"
            >
              {isCreating ? 'Creating...' : 'Create Company'}
            </button>
            <button
              onClick={() => {
                setShowCreateForm(false);
                setNewCompanyName('');
                setError('');
              }}
              className="cancel-button"
              disabled={isCreating}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {isLoading && <div className="loading-message">Loading client companies...</div>}

      {!isLoading && clientCompanies.length === 0 && !error && (
        <div className="empty-state">
          <p>No client companies found.</p>
          <p>Click "Add New Client" to create your first client company.</p>
        </div>
      )}

      {clientCompanies.length > 0 && (
        <div className="companies-list">
          {clientCompanies.map((company) => (
            <div key={company.id} className="company-card">
              {editingCompany && editingCompany.id === company.id ? (
                <div className="edit-form">
                  <input
                    type="text"
                    value={editCompanyName}
                    onChange={(e) => setEditCompanyName(e.target.value)}
                    className="form-input"
                  />
                  <div className="form-actions">
                    <button
                      onClick={handleUpdateCompany}
                      disabled={!editCompanyName.trim() || !isConnected}
                      className="submit-button"
                    >
                      Save
                    </button>
                    <button
                      onClick={() => {
                        setEditingCompany(null);
                        setEditCompanyName('');
                        setError('');
                      }}
                      className="cancel-button"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="company-info">
                  <h4 className="company-name">{company.name}</h4>
                  <div className="company-actions">
                    <button
                      onClick={() => {
                        setEditingCompany(company);
                        setEditCompanyName(company.name);
                        setError('');
                        setSuccessMessage('');
                      }}
                      className="edit-button"
                      disabled={!isConnected}
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteCompany(company.id)}
                      className="delete-button"
                      disabled={!isConnected}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ManagerClientCompaniesPage;
