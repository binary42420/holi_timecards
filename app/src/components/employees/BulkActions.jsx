import React, { useState } from 'react';
import './BulkActions.css';

const BulkActions = ({
    selectedEmployees,
    onApproveSelected,
    onRejectSelected,
    onClearSelection
}) => {
    const [showConfirmation, setShowConfirmation] = useState(null);

    const handleBulkAction = (action) => {
        setShowConfirmation(action);
    };

    const confirmAction = () => {
        if (showConfirmation === 'approve') {
            onApproveSelected();
        } else if (showConfirmation === 'reject') {
            onRejectSelected();
        }
        setShowConfirmation(null);
    };

    const cancelAction = () => {
        setShowConfirmation(null);
    };

    return (
        <div className="bulk-actions">
            <div className="bulk-actions-bar">
                <div className="selection-info">
                    <span className="selection-count">
                        {selectedEmployees.length} employee{selectedEmployees.length !== 1 ? 's' : ''} selected
                    </span>
                </div>

                <div className="bulk-buttons">
                    <button
                        className="bulk-btn approve"
                        onClick={() => handleBulkAction('approve')}
                        disabled={selectedEmployees.length === 0}
                    >
                        ✓ Approve Selected ({selectedEmployees.length})
                    </button>
                    
                    <button
                        className="bulk-btn reject"
                        onClick={() => handleBulkAction('reject')}
                        disabled={selectedEmployees.length === 0}
                    >
                        ✗ Reject Selected ({selectedEmployees.length})
                    </button>

                    <button
                        className="bulk-btn clear"
                        onClick={onClearSelection}
                    >
                        Clear Selection
                    </button>
                </div>
            </div>

            {showConfirmation && (
                <div className="confirmation-overlay">
                    <div className="confirmation-modal">
                        <div className="confirmation-header">
                            <h3>Confirm Bulk Action</h3>
                        </div>
                        
                        <div className="confirmation-content">
                            <p>
                                Are you sure you want to <strong>{showConfirmation}</strong> the following {selectedEmployees.length} employee{selectedEmployees.length !== 1 ? 's' : ''}?
                            </p>
                            
                            <div className="selected-employees-list">
                                {selectedEmployees.slice(0, 5).map(employeeId => (
                                    <div key={employeeId} className="selected-employee-item">
                                        @{employeeId}
                                    </div>
                                ))}
                                {selectedEmployees.length > 5 && (
                                    <div className="more-employees">
                                        ... and {selectedEmployees.length - 5} more
                                    </div>
                                )}
                            </div>

                            <div className="warning-message">
                                <span className="warning-icon">⚠️</span>
                                This action cannot be undone.
                            </div>
                        </div>

                        <div className="confirmation-actions">
                            <button
                                className="btn btn-secondary"
                                onClick={cancelAction}
                            >
                                Cancel
                            </button>
                            <button
                                className={`btn ${showConfirmation === 'approve' ? 'btn-success' : 'btn-danger'}`}
                                onClick={confirmAction}
                            >
                                {showConfirmation === 'approve' ? '✓ Approve All' : '✗ Reject All'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default BulkActions;
