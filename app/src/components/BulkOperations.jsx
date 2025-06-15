import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
import './BulkOperations.css';

const BulkOperations = ({ 
  items = [], 
  itemType = 'employees', 
  onSelectionChange, 
  onOperationComplete 
}) => {
  const { socket, connectionStatus } = useSocket();
  const [selectedItems, setSelectedItems] = useState(new Set());
  const [isProcessing, setIsProcessing] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [pendingOperation, setPendingOperation] = useState(null);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const operationConfigs = {
    employees: [
      { 
        id: 'assign_certification', 
        label: 'Assign Certification', 
        icon: '🏆', 
        color: '#28a745',
        requiresInput: true,
        inputType: 'select',
        inputOptions: [
          { value: 'crew_chief', label: 'Crew Chief' },
          { value: 'forklift_operator', label: 'Forklift Operator' },
          { value: 'truck_driver', label: 'Truck Driver' }
        ]
      },
      { 
        id: 'remove_certification', 
        label: 'Remove Certification', 
        icon: '❌', 
        color: '#dc3545',
        requiresInput: true,
        inputType: 'select',
        inputOptions: [
          { value: 'crew_chief', label: 'Crew Chief' },
          { value: 'forklift_operator', label: 'Forklift Operator' },
          { value: 'truck_driver', label: 'Truck Driver' }
        ]
      },
      { 
        id: 'send_notification', 
        label: 'Send Notification', 
        icon: '📧', 
        color: '#007bff',
        requiresInput: true,
        inputType: 'textarea',
        inputPlaceholder: 'Enter notification message...'
      },
      { 
        id: 'deactivate', 
        label: 'Deactivate Accounts', 
        icon: '🚫', 
        color: '#ffc107',
        dangerous: true
      },
      { 
        id: 'export', 
        label: 'Export Data', 
        icon: '📥', 
        color: '#17a2b8'
      }
    ],
    shifts: [
      { 
        id: 'cancel', 
        label: 'Cancel Shifts', 
        icon: '❌', 
        color: '#dc3545',
        dangerous: true
      },
      { 
        id: 'assign_workers', 
        label: 'Assign Workers', 
        icon: '👥', 
        color: '#28a745',
        requiresInput: true,
        inputType: 'multiselect'
      },
      { 
        id: 'update_status', 
        label: 'Update Status', 
        icon: '🔄', 
        color: '#007bff',
        requiresInput: true,
        inputType: 'select',
        inputOptions: [
          { value: 'scheduled', label: 'Scheduled' },
          { value: 'in_progress', label: 'In Progress' },
          { value: 'completed', label: 'Completed' },
          { value: 'cancelled', label: 'Cancelled' }
        ]
      },
      { 
        id: 'export', 
        label: 'Export Shifts', 
        icon: '📥', 
        color: '#17a2b8'
      }
    ],
    jobs: [
      { 
        id: 'update_status', 
        label: 'Update Status', 
        icon: '🔄', 
        color: '#007bff',
        requiresInput: true,
        inputType: 'select',
        inputOptions: [
          { value: 'active', label: 'Active' },
          { value: 'on_hold', label: 'On Hold' },
          { value: 'completed', label: 'Completed' },
          { value: 'cancelled', label: 'Cancelled' }
        ]
      },
      { 
        id: 'assign_manager', 
        label: 'Assign Manager', 
        icon: '👤', 
        color: '#6f42c1',
        requiresInput: true,
        inputType: 'select'
      },
      { 
        id: 'export', 
        label: 'Export Jobs', 
        icon: '📥', 
        color: '#17a2b8'
      }
    ]
  };

  const operations = operationConfigs[itemType] || [];

  useEffect(() => {
    if (onSelectionChange) {
      onSelectionChange(Array.from(selectedItems));
    }
  }, [selectedItems, onSelectionChange]);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        if (response.request_id === 1100) { // BULK_OPERATION
          setIsProcessing(false);
          if (response.success) {
            setSuccessMessage(`Operation completed successfully on ${selectedItems.size} items`);
            setSelectedItems(new Set());
            setError('');
            if (onOperationComplete) {
              onOperationComplete(response.data);
            }
          } else {
            setError(response.error || 'Operation failed');
            setSuccessMessage('');
          }
        }
      } catch (e) {
        console.error('Error parsing bulk operation response:', e);
        setIsProcessing(false);
        setError('Error processing operation');
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => socket.removeEventListener('message', handleMessage);
  }, [socket, selectedItems, onOperationComplete]);

  const handleSelectAll = () => {
    if (selectedItems.size === items.length) {
      setSelectedItems(new Set());
    } else {
      setSelectedItems(new Set(items.map(item => item.id)));
    }
  };

  const handleSelectItem = (itemId) => {
    const newSelection = new Set(selectedItems);
    if (newSelection.has(itemId)) {
      newSelection.delete(itemId);
    } else {
      newSelection.add(itemId);
    }
    setSelectedItems(newSelection);
  };

  const handleOperationClick = (operation) => {
    if (selectedItems.size === 0) {
      setError('Please select at least one item');
      return;
    }

    setPendingOperation(operation);
    setShowConfirmDialog(true);
    setError('');
    setSuccessMessage('');
  };

  const executeOperation = (operationData = {}) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError('Cannot perform operation: WebSocket is not connected');
      return;
    }

    setIsProcessing(true);
    setShowConfirmDialog(false);
    setError('');
    setSuccessMessage('');

    const request = {
      request_id: 1100, // BULK_OPERATION
      data: {
        operation: pendingOperation.id,
        item_type: itemType,
        item_ids: Array.from(selectedItems),
        operation_data: operationData
      }
    };

    socket.send(JSON.stringify(request));
  };

  const getSelectionSummary = () => {
    const total = items.length;
    const selected = selectedItems.size;
    
    if (selected === 0) return 'No items selected';
    if (selected === total) return `All ${total} items selected`;
    return `${selected} of ${total} items selected`;
  };

  const isAllSelected = selectedItems.size === items.length && items.length > 0;
  const isPartiallySelected = selectedItems.size > 0 && selectedItems.size < items.length;

  return (
    <div className="bulk-operations">
      <div className="bulk-header">
        <div className="selection-controls">
          <label className="select-all-checkbox">
            <input
              type="checkbox"
              checked={isAllSelected}
              ref={input => {
                if (input) input.indeterminate = isPartiallySelected;
              }}
              onChange={handleSelectAll}
              disabled={items.length === 0}
            />
            <span className="checkmark"></span>
            <span className="selection-summary">{getSelectionSummary()}</span>
          </label>
        </div>

        {selectedItems.size > 0 && (
          <div className="bulk-actions">
            {operations.map(operation => (
              <button
                key={operation.id}
                onClick={() => handleOperationClick(operation)}
                disabled={isProcessing || connectionStatus !== 'connected'}
                className={`bulk-action-btn ${operation.dangerous ? 'dangerous' : ''}`}
                style={{ backgroundColor: operation.color }}
                title={operation.label}
              >
                <span className="action-icon">{operation.icon}</span>
                <span className="action-label">{operation.label}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="success-message">
          {successMessage}
        </div>
      )}

      <div className="items-list">
        {items.map(item => (
          <div
            key={item.id}
            className={`item-row ${selectedItems.has(item.id) ? 'selected' : ''}`}
            onClick={() => handleSelectItem(item.id)}
          >
            <div className="item-checkbox">
              <input
                type="checkbox"
                checked={selectedItems.has(item.id)}
                onChange={() => handleSelectItem(item.id)}
                onClick={(e) => e.stopPropagation()}
              />
            </div>
            <div className="item-content">
              <div className="item-title">
                {item.name || item.title || `${itemType.slice(0, -1)} #${item.id}`}
              </div>
              <div className="item-subtitle">
                {item.email || item.description || item.status || ''}
              </div>
            </div>
            <div className="item-status">
              {item.status && (
                <span className={`status-badge status-${item.status}`}>
                  {item.status}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {showConfirmDialog && pendingOperation && (
        <ConfirmationDialog
          operation={pendingOperation}
          selectedCount={selectedItems.size}
          onConfirm={executeOperation}
          onCancel={() => {
            setShowConfirmDialog(false);
            setPendingOperation(null);
          }}
        />
      )}

      {isProcessing && (
        <div className="processing-overlay">
          <div className="processing-message">
            <div className="spinner"></div>
            <p>Processing operation...</p>
          </div>
        </div>
      )}
    </div>
  );
};

const ConfirmationDialog = ({ operation, selectedCount, onConfirm, onCancel }) => {
  const [inputValue, setInputValue] = useState('');
  const [selectedOptions, setSelectedOptions] = useState([]);

  const handleConfirm = () => {
    let operationData = {};
    
    if (operation.requiresInput) {
      if (operation.inputType === 'select' || operation.inputType === 'textarea') {
        operationData.value = inputValue;
      } else if (operation.inputType === 'multiselect') {
        operationData.values = selectedOptions;
      }
    }
    
    onConfirm(operationData);
  };

  const isValid = !operation.requiresInput || 
    (operation.inputType === 'multiselect' ? selectedOptions.length > 0 : inputValue.trim());

  return (
    <div className="confirmation-overlay">
      <div className="confirmation-dialog">
        <div className="dialog-header">
          <h3>Confirm Operation</h3>
          <button onClick={onCancel} className="close-btn">×</button>
        </div>
        
        <div className="dialog-content">
          <div className="operation-summary">
            <div className="operation-icon" style={{ color: operation.color }}>
              {operation.icon}
            </div>
            <div className="operation-details">
              <div className="operation-name">{operation.label}</div>
              <div className="operation-count">
                This will affect {selectedCount} selected item{selectedCount !== 1 ? 's' : ''}
              </div>
            </div>
          </div>

          {operation.dangerous && (
            <div className="warning-message">
              ⚠️ This action cannot be undone. Please confirm you want to proceed.
            </div>
          )}

          {operation.requiresInput && (
            <div className="input-section">
              {operation.inputType === 'select' && (
                <select
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  className="operation-input"
                >
                  <option value="">Select an option...</option>
                  {operation.inputOptions?.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              )}
              
              {operation.inputType === 'textarea' && (
                <textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder={operation.inputPlaceholder}
                  className="operation-input"
                  rows="4"
                />
              )}
            </div>
          )}
        </div>

        <div className="dialog-actions">
          <button onClick={onCancel} className="cancel-btn">
            Cancel
          </button>
          <button 
            onClick={handleConfirm} 
            disabled={!isValid}
            className={`confirm-btn ${operation.dangerous ? 'dangerous' : ''}`}
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
};

export default BulkOperations;
