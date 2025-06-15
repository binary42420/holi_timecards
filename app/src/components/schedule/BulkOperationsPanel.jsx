import React, { useState } from 'react';
import { logDebug, logError, logInfo } from '../../utils';
import './BulkOperationsPanel.css';

const BulkOperationsPanel = ({
  selectedShifts,
  onClearSelection,
  onBulkAssign,
  onBulkUnassign,
  onBulkDelete,
  onBulkCopy,
  onBulkMove,
  onCreateTemplate,
  workers,
  isVisible
}) => {
  const [selectedWorker, setSelectedWorker] = useState('');
  const [copyDate, setCopyDate] = useState('');
  const [moveDate, setMoveDate] = useState('');
  const [templateName, setTemplateName] = useState('');
  const [showConfirmDelete, setShowConfirmDelete] = useState(false);

  if (!isVisible || selectedShifts.length === 0) {
    return null;
  }

  const handleBulkAssign = () => {
    if (!selectedWorker) {
      alert('Please select a worker to assign');
      return;
    }
    
    const worker = workers.find(w => w.id === parseInt(selectedWorker));
    if (!worker) {
      alert('Selected worker not found');
      return;
    }

    logInfo('BulkOperationsPanel', 'Bulk assigning worker to shifts', {
      workerId: worker.id,
      workerName: worker.name,
      shiftCount: selectedShifts.length
    });

    onBulkAssign(selectedShifts, worker);
    setSelectedWorker('');
  };

  const handleBulkCopy = () => {
    if (!copyDate) {
      alert('Please select a date to copy shifts to');
      return;
    }

    const targetDate = new Date(copyDate);
    logInfo('BulkOperationsPanel', 'Bulk copying shifts', {
      shiftCount: selectedShifts.length,
      targetDate: targetDate.toISOString()
    });

    onBulkCopy(selectedShifts, targetDate);
    setCopyDate('');
  };

  const handleBulkMove = () => {
    if (!moveDate) {
      alert('Please select a date to move shifts to');
      return;
    }

    const targetDate = new Date(moveDate);
    logInfo('BulkOperationsPanel', 'Bulk moving shifts', {
      shiftCount: selectedShifts.length,
      targetDate: targetDate.toISOString()
    });

    onBulkMove(selectedShifts, targetDate);
    setMoveDate('');
  };

  const handleCreateTemplate = () => {
    if (!templateName.trim()) {
      alert('Please enter a template name');
      return;
    }

    logInfo('BulkOperationsPanel', 'Creating shift template', {
      templateName,
      shiftCount: selectedShifts.length
    });

    onCreateTemplate(selectedShifts, templateName.trim());
    setTemplateName('');
  };

  const handleBulkDelete = () => {
    if (!showConfirmDelete) {
      setShowConfirmDelete(true);
      return;
    }

    logInfo('BulkOperationsPanel', 'Bulk deleting shifts', {
      shiftCount: selectedShifts.length
    });

    onBulkDelete(selectedShifts);
    setShowConfirmDelete(false);
  };

  const getShiftSummary = () => {
    const totalWorkers = selectedShifts.reduce((sum, shift) => 
      sum + (shift.assigned_workers?.length || 0), 0
    );
    const totalHours = selectedShifts.reduce((sum, shift) => 
      sum + (shift.duration_hours || 0), 0
    );

    return { totalWorkers, totalHours };
  };

  const { totalWorkers, totalHours } = getShiftSummary();

  return (
    <div className="bulk-operations-panel">
      <div className="bulk-header">
        <h3>Bulk Operations</h3>
        <button 
          className="clear-selection-btn"
          onClick={onClearSelection}
          title="Clear selection"
        >
          ✕
        </button>
      </div>

      <div className="selection-summary">
        <div className="summary-item">
          <span className="summary-label">Selected:</span>
          <span className="summary-value">{selectedShifts.length} shifts</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Workers:</span>
          <span className="summary-value">{totalWorkers}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Total Hours:</span>
          <span className="summary-value">{totalHours}h</span>
        </div>
      </div>

      <div className="bulk-operations">
        {/* Worker Assignment */}
        <div className="operation-group">
          <h4>Worker Assignment</h4>
          <div className="operation-row">
            <select 
              value={selectedWorker} 
              onChange={(e) => setSelectedWorker(e.target.value)}
              className="worker-select"
            >
              <option value="">Select worker...</option>
              {workers.map(worker => (
                <option key={worker.id} value={worker.id}>
                  {worker.name} - {worker.role}
                </option>
              ))}
            </select>
            <button 
              onClick={handleBulkAssign}
              disabled={!selectedWorker}
              className="operation-btn assign-btn"
            >
              Assign
            </button>
            <button 
              onClick={() => onBulkUnassign(selectedShifts)}
              className="operation-btn unassign-btn"
            >
              Unassign All
            </button>
          </div>
        </div>

        {/* Copy/Move Operations */}
        <div className="operation-group">
          <h4>Copy/Move Shifts</h4>
          <div className="operation-row">
            <input
              type="date"
              value={copyDate}
              onChange={(e) => setCopyDate(e.target.value)}
              className="date-input"
            />
            <button 
              onClick={handleBulkCopy}
              disabled={!copyDate}
              className="operation-btn copy-btn"
            >
              Copy to Date
            </button>
          </div>
          <div className="operation-row">
            <input
              type="date"
              value={moveDate}
              onChange={(e) => setMoveDate(e.target.value)}
              className="date-input"
            />
            <button 
              onClick={handleBulkMove}
              disabled={!moveDate}
              className="operation-btn move-btn"
            >
              Move to Date
            </button>
          </div>
        </div>

        {/* Template Creation */}
        <div className="operation-group">
          <h4>Create Template</h4>
          <div className="operation-row">
            <input
              type="text"
              value={templateName}
              onChange={(e) => setTemplateName(e.target.value)}
              placeholder="Template name..."
              className="template-name-input"
            />
            <button 
              onClick={handleCreateTemplate}
              disabled={!templateName.trim()}
              className="operation-btn template-btn"
            >
              Create Template
            </button>
          </div>
        </div>

        {/* Delete Operation */}
        <div className="operation-group danger-group">
          <h4>Delete Shifts</h4>
          <div className="operation-row">
            <button 
              onClick={handleBulkDelete}
              className={`operation-btn delete-btn ${showConfirmDelete ? 'confirm-delete' : ''}`}
            >
              {showConfirmDelete ? 'Confirm Delete' : 'Delete Selected'}
            </button>
            {showConfirmDelete && (
              <button 
                onClick={() => setShowConfirmDelete(false)}
                className="operation-btn cancel-btn"
              >
                Cancel
              </button>
            )}
          </div>
          {showConfirmDelete && (
            <div className="delete-warning">
              ⚠️ This action cannot be undone. {selectedShifts.length} shifts will be permanently deleted.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BulkOperationsPanel;
