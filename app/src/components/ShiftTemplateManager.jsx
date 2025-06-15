import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
import RoleRequirementBuilder from './RoleRequirementBuilder';
import './ShiftTemplateManager.css';

const ShiftTemplateManager = ({ 
  onTemplateSelect, 
  onClose, 
  isModal = true 
}) => {
  const { socket, connectionStatus } = useSocket();
  const [templates, setTemplates] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const [newTemplate, setNewTemplate] = useState({
    name: '',
    description: '',
    duration_hours: 8,
    role_requirements: {
      stagehand: 1,
      crew_chief: 0,
      fork_operator: 0,
      pickup_truck_driver: 0
    },
    default_start_time: '09:00',
    is_public: true
  });

  // Predefined templates for common scenarios
  const predefinedTemplates = [
    {
      name: 'Standard Setup Crew',
      description: 'Basic stage setup with general labor',
      duration_hours: 8,
      role_requirements: { stagehand: 4, crew_chief: 1, fork_operator: 0, pickup_truck_driver: 0 },
      default_start_time: '07:00'
    },
    {
      name: 'Load-In Crew',
      description: 'Heavy equipment load-in with forklift support',
      duration_hours: 6,
      role_requirements: { stagehand: 6, crew_chief: 1, fork_operator: 2, pickup_truck_driver: 1 },
      default_start_time: '06:00'
    },
    {
      name: 'Event Maintenance',
      description: 'During-event maintenance and support',
      duration_hours: 12,
      role_requirements: { stagehand: 2, crew_chief: 1, fork_operator: 0, pickup_truck_driver: 0 },
      default_start_time: '10:00'
    },
    {
      name: 'Strike Crew',
      description: 'Post-event teardown and cleanup',
      duration_hours: 10,
      role_requirements: { stagehand: 8, crew_chief: 2, fork_operator: 2, pickup_truck_driver: 2 },
      default_start_time: '22:00'
    }
  ];

  useEffect(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      fetchTemplates();
    }
  }, [socket]);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        
        if (response.request_id === 500) { // GET_SHIFT_TEMPLATES
          setIsLoading(false);
          if (response.success) {
            setTemplates([...predefinedTemplates, ...(response.data || [])]);
          } else {
            setError(response.error || 'Failed to load templates');
            setTemplates(predefinedTemplates);
          }
        } else if (response.request_id === 501) { // CREATE_SHIFT_TEMPLATE
          if (response.success) {
            setSuccessMessage('Template created successfully!');
            setShowCreateForm(false);
            setNewTemplate({
              name: '',
              description: '',
              duration_hours: 8,
              role_requirements: { stagehand: 1, crew_chief: 0, fork_operator: 0, pickup_truck_driver: 0 },
              default_start_time: '09:00',
              is_public: true
            });
            fetchTemplates();
          } else {
            setError(response.error || 'Failed to create template');
          }
        } else if (response.request_id === 502) { // DELETE_SHIFT_TEMPLATE
          if (response.success) {
            setSuccessMessage('Template deleted successfully!');
            fetchTemplates();
          } else {
            setError(response.error || 'Failed to delete template');
          }
        }
      } catch (e) {
        console.error('Error parsing template response:', e);
        setIsLoading(false);
        setError('Error processing server response');
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => socket.removeEventListener('message', handleMessage);
  }, [socket]);

  const fetchTemplates = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      setIsLoading(true);
      const request = { request_id: 500 }; // GET_SHIFT_TEMPLATES
      socket.send(JSON.stringify(request));
    }
  };

  const handleCreateTemplate = () => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError('Cannot create template: WebSocket is not connected');
      return;
    }

    if (!newTemplate.name.trim()) {
      setError('Template name is required');
      return;
    }

    const request = {
      request_id: 501, // CREATE_SHIFT_TEMPLATE
      data: newTemplate
    };

    socket.send(JSON.stringify(request));
  };

  const handleDeleteTemplate = (templateId) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError('Cannot delete template: WebSocket is not connected');
      return;
    }

    if (window.confirm('Are you sure you want to delete this template?')) {
      const request = {
        request_id: 502, // DELETE_SHIFT_TEMPLATE
        data: { template_id: templateId }
      };
      socket.send(JSON.stringify(request));
    }
  };

  const handleTemplateSelect = (template) => {
    if (onTemplateSelect) {
      onTemplateSelect(template);
    }
    if (onClose) {
      onClose();
    }
  };

  const getTotalWorkers = (roleRequirements) => {
    return Object.values(roleRequirements).reduce((sum, count) => sum + (count || 0), 0);
  };

  const content = (
    <div className="shift-template-manager">
      <div className="template-header">
        <h2>Shift Templates</h2>
        <div className="header-actions">
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="btn btn-primary"
            disabled={connectionStatus !== 'connected'}
          >
            {showCreateForm ? 'Cancel' : '+ Create Template'}
          </button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}
      {successMessage && <div className="success-message">{successMessage}</div>}

      {showCreateForm && (
        <div className="create-template-form">
          <h3>Create New Template</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Template Name</label>
              <input
                type="text"
                value={newTemplate.name}
                onChange={(e) => setNewTemplate(prev => ({ ...prev, name: e.target.value }))}
                placeholder="e.g., Festival Setup Crew"
              />
            </div>
            <div className="form-group">
              <label>Duration (hours)</label>
              <input
                type="number"
                min="1"
                max="24"
                value={newTemplate.duration_hours}
                onChange={(e) => setNewTemplate(prev => ({ ...prev, duration_hours: parseInt(e.target.value) || 8 }))}
              />
            </div>
            <div className="form-group">
              <label>Default Start Time</label>
              <input
                type="time"
                value={newTemplate.default_start_time}
                onChange={(e) => setNewTemplate(prev => ({ ...prev, default_start_time: e.target.value }))}
              />
            </div>
            <div className="form-group full-width">
              <label>Description</label>
              <textarea
                value={newTemplate.description}
                onChange={(e) => setNewTemplate(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Describe when to use this template..."
                rows="2"
              />
            </div>
          </div>

          <RoleRequirementBuilder
            requiredCounts={newTemplate.role_requirements}
            onCountChange={(role, count) => 
              setNewTemplate(prev => ({
                ...prev,
                role_requirements: { ...prev.role_requirements, [role]: count }
              }))
            }
            showAvailableWorkers={false}
          />

          <div className="form-actions">
            <button
              onClick={() => setShowCreateForm(false)}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              onClick={handleCreateTemplate}
              className="btn btn-primary"
              disabled={!newTemplate.name.trim()}
            >
              Create Template
            </button>
          </div>
        </div>
      )}

      <div className="templates-grid">
        {isLoading ? (
          <div className="loading-message">Loading templates...</div>
        ) : (
          templates.map((template, index) => (
            <div key={template.id || index} className="template-card">
              <div className="template-info">
                <h4 className="template-name">{template.name}</h4>
                <p className="template-description">{template.description}</p>
                
                <div className="template-details">
                  <div className="detail-item">
                    <span className="detail-label">Duration:</span>
                    <span>{template.duration_hours} hours</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Start Time:</span>
                    <span>{template.default_start_time}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Total Workers:</span>
                    <span>{getTotalWorkers(template.role_requirements)}</span>
                  </div>
                </div>

                <div className="role-breakdown">
                  {Object.entries(template.role_requirements)
                    .filter(([_, count]) => count > 0)
                    .map(([role, count]) => (
                      <span key={role} className="role-tag">
                        {count} {role.replace('_', ' ')}
                      </span>
                    ))}
                </div>
              </div>

              <div className="template-actions">
                <button
                  onClick={() => handleTemplateSelect(template)}
                  className="btn btn-primary"
                >
                  Use Template
                </button>
                {template.id && (
                  <button
                    onClick={() => handleDeleteTemplate(template.id)}
                    className="btn btn-danger btn-small"
                  >
                    Delete
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );

  if (isModal) {
    return (
      <div className="template-modal-overlay">
        <div className="template-modal">
          <div className="modal-header">
            <h2>Select Shift Template</h2>
            <button onClick={onClose} className="modal-close-btn">×</button>
          </div>
          {content}
        </div>
      </div>
    );
  }

  return content;
};

export default ShiftTemplateManager;
