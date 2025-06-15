import React, { useState, useEffect } from 'react';
import { logDebug, logError, logInfo } from '../../utils';
import './ShiftTemplateModal.css';

const ShiftTemplateModal = ({
  isOpen,
  onClose,
  onSave,
  onApplyTemplate,
  templates,
  jobs,
  workers,
  mode = 'create' // 'create', 'apply'
}) => {
  const [templateData, setTemplateData] = useState({
    name: '',
    description: '',
    shifts: [],
    recurrence: {
      type: 'none', // 'none', 'daily', 'weekly', 'monthly'
      interval: 1,
      daysOfWeek: [],
      endDate: null
    }
  });

  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [applyDate, setApplyDate] = useState('');
  const [applyWeeks, setApplyWeeks] = useState(1);

  useEffect(() => {
    if (!isOpen) {
      resetForm();
    }
  }, [isOpen]);

  const resetForm = () => {
    setTemplateData({
      name: '',
      description: '',
      shifts: [],
      recurrence: {
        type: 'none',
        interval: 1,
        daysOfWeek: [],
        endDate: null
      }
    });
    setSelectedTemplate('');
    setApplyDate('');
    setApplyWeeks(1);
  };

  const handleInputChange = (field, value) => {
    setTemplateData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleRecurrenceChange = (field, value) => {
    setTemplateData(prev => ({
      ...prev,
      recurrence: {
        ...prev.recurrence,
        [field]: value
      }
    }));
  };

  const addShiftToTemplate = () => {
    const newShift = {
      id: Date.now(),
      job_id: '',
      start_time: '09:00',
      end_time: '17:00',
      required_workers: 1,
      required_roles: [],
      day_offset: 0, // Days from template start date
      notes: ''
    };

    setTemplateData(prev => ({
      ...prev,
      shifts: [...prev.shifts, newShift]
    }));
  };

  const updateShift = (shiftId, field, value) => {
    setTemplateData(prev => ({
      ...prev,
      shifts: prev.shifts.map(shift =>
        shift.id === shiftId ? { ...shift, [field]: value } : shift
      )
    }));
  };

  const removeShift = (shiftId) => {
    setTemplateData(prev => ({
      ...prev,
      shifts: prev.shifts.filter(shift => shift.id !== shiftId)
    }));
  };

  const handleSave = () => {
    if (!templateData.name.trim()) {
      alert('Please enter a template name');
      return;
    }

    if (templateData.shifts.length === 0) {
      alert('Please add at least one shift to the template');
      return;
    }

    logInfo('ShiftTemplateModal', 'Saving shift template', {
      name: templateData.name,
      shiftCount: templateData.shifts.length,
      recurrence: templateData.recurrence
    });

    onSave(templateData);
    onClose();
  };

  const handleApplyTemplate = () => {
    if (!selectedTemplate) {
      alert('Please select a template');
      return;
    }

    if (!applyDate) {
      alert('Please select a start date');
      return;
    }

    const template = templates.find(t => t.id === selectedTemplate);
    if (!template) {
      alert('Selected template not found');
      return;
    }

    logInfo('ShiftTemplateModal', 'Applying shift template', {
      templateId: selectedTemplate,
      templateName: template.name,
      startDate: applyDate,
      weeks: applyWeeks
    });

    onApplyTemplate(template, new Date(applyDate), applyWeeks);
    onClose();
  };

  const getDayName = (dayOffset) => {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[dayOffset] || `Day +${dayOffset}`;
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="shift-template-modal">
        <div className="modal-header">
          <h2>
            {mode === 'create' ? 'Create Shift Template' : 'Apply Shift Template'}
          </h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="modal-content">
          {mode === 'create' ? (
            <>
              {/* Template Basic Info */}
              <div className="form-section">
                <h3>Template Information</h3>
                <div className="form-group">
                  <label>Template Name *</label>
                  <input
                    type="text"
                    value={templateData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    placeholder="e.g., Weekly Standard Schedule"
                  />
                </div>
                <div className="form-group">
                  <label>Description</label>
                  <textarea
                    value={templateData.description}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    placeholder="Optional description of this template"
                    rows="3"
                  />
                </div>
              </div>

              {/* Shifts */}
              <div className="form-section">
                <div className="section-header">
                  <h3>Shifts</h3>
                  <button 
                    type="button" 
                    className="add-shift-btn"
                    onClick={addShiftToTemplate}
                  >
                    + Add Shift
                  </button>
                </div>

                {templateData.shifts.map(shift => (
                  <div key={shift.id} className="shift-template-item">
                    <div className="shift-header">
                      <span className="shift-day">{getDayName(shift.day_offset)}</span>
                      <button 
                        className="remove-shift-btn"
                        onClick={() => removeShift(shift.id)}
                      >
                        ✕
                      </button>
                    </div>

                    <div className="shift-details">
                      <div className="form-row">
                        <div className="form-group">
                          <label>Job</label>
                          <select
                            value={shift.job_id}
                            onChange={(e) => updateShift(shift.id, 'job_id', e.target.value)}
                          >
                            <option value="">Select job...</option>
                            {jobs.map(job => (
                              <option key={job.id} value={job.id}>
                                {job.title} - {job.client_company}
                              </option>
                            ))}
                          </select>
                        </div>

                        <div className="form-group">
                          <label>Day</label>
                          <select
                            value={shift.day_offset}
                            onChange={(e) => updateShift(shift.id, 'day_offset', parseInt(e.target.value))}
                          >
                            {[0, 1, 2, 3, 4, 5, 6].map(day => (
                              <option key={day} value={day}>
                                {getDayName(day)}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>

                      <div className="form-row">
                        <div className="form-group">
                          <label>Start Time</label>
                          <input
                            type="time"
                            value={shift.start_time}
                            onChange={(e) => updateShift(shift.id, 'start_time', e.target.value)}
                          />
                        </div>

                        <div className="form-group">
                          <label>End Time</label>
                          <input
                            type="time"
                            value={shift.end_time}
                            onChange={(e) => updateShift(shift.id, 'end_time', e.target.value)}
                          />
                        </div>

                        <div className="form-group">
                          <label>Workers Needed</label>
                          <input
                            type="number"
                            min="1"
                            value={shift.required_workers}
                            onChange={(e) => updateShift(shift.id, 'required_workers', parseInt(e.target.value))}
                          />
                        </div>
                      </div>

                      <div className="form-group">
                        <label>Notes</label>
                        <input
                          type="text"
                          value={shift.notes}
                          onChange={(e) => updateShift(shift.id, 'notes', e.target.value)}
                          placeholder="Optional shift notes"
                        />
                      </div>
                    </div>
                  </div>
                ))}

                {templateData.shifts.length === 0 && (
                  <div className="no-shifts-message">
                    No shifts added yet. Click "Add Shift" to create your first shift.
                  </div>
                )}
              </div>

              {/* Recurrence Settings */}
              <div className="form-section">
                <h3>Recurrence (Optional)</h3>
                <div className="form-group">
                  <label>Repeat Pattern</label>
                  <select
                    value={templateData.recurrence.type}
                    onChange={(e) => handleRecurrenceChange('type', e.target.value)}
                  >
                    <option value="none">No Repeat</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>

                {templateData.recurrence.type !== 'none' && (
                  <div className="form-group">
                    <label>Repeat Every</label>
                    <div className="interval-input">
                      <input
                        type="number"
                        min="1"
                        value={templateData.recurrence.interval}
                        onChange={(e) => handleRecurrenceChange('interval', parseInt(e.target.value))}
                      />
                      <span>{templateData.recurrence.type === 'weekly' ? 'week(s)' : 'month(s)'}</span>
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : (
            <>
              {/* Apply Template Mode */}
              <div className="form-section">
                <h3>Select Template</h3>
                <div className="form-group">
                  <label>Available Templates</label>
                  <select
                    value={selectedTemplate}
                    onChange={(e) => setSelectedTemplate(e.target.value)}
                  >
                    <option value="">Choose a template...</option>
                    {templates.map(template => (
                      <option key={template.id} value={template.id}>
                        {template.name} ({template.shifts?.length || 0} shifts)
                      </option>
                    ))}
                  </select>
                </div>

                {selectedTemplate && (
                  <div className="template-preview">
                    {(() => {
                      const template = templates.find(t => t.id === selectedTemplate);
                      return template ? (
                        <div>
                          <h4>Template Preview: {template.name}</h4>
                          <p>{template.description}</p>
                          <div className="shifts-preview">
                            {template.shifts?.map((shift, index) => (
                              <div key={index} className="shift-preview-item">
                                {getDayName(shift.day_offset)}: {shift.start_time} - {shift.end_time}
                                ({shift.required_workers} workers)
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : null;
                    })()}
                  </div>
                )}
              </div>

              <div className="form-section">
                <h3>Application Settings</h3>
                <div className="form-row">
                  <div className="form-group">
                    <label>Start Date *</label>
                    <input
                      type="date"
                      value={applyDate}
                      onChange={(e) => setApplyDate(e.target.value)}
                    />
                  </div>

                  <div className="form-group">
                    <label>Apply for Weeks</label>
                    <input
                      type="number"
                      min="1"
                      max="52"
                      value={applyWeeks}
                      onChange={(e) => setApplyWeeks(parseInt(e.target.value))}
                    />
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        <div className="modal-footer">
          <button className="cancel-btn" onClick={onClose}>
            Cancel
          </button>
          <button 
            className="save-btn"
            onClick={mode === 'create' ? handleSave : handleApplyTemplate}
          >
            {mode === 'create' ? 'Save Template' : 'Apply Template'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ShiftTemplateModal;
