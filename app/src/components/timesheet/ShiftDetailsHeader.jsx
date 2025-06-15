import React from 'react';
import './ShiftDetailsHeader.css';

const ShiftDetailsHeader = ({ shiftDetails, userPermissions }) => {
  const formatDateTime = (dateTimeString) => {
    if (!dateTimeString) return 'Not specified';
    return new Date(dateTimeString).toLocaleString();
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not specified';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="shift-details-header">
      <div className="shift-info-card">
        <div className="card-header">
          <h2>Shift Details</h2>
          <div className="shift-id">Shift #{shiftDetails.shift_id}</div>
        </div>
        
        <div className="shift-info-grid">
          <div className="info-section">
            <h3>📅 Schedule</h3>
            <div className="info-items">
              {shiftDetails.shift_start_datetime ? (
                <>
                  <div className="info-item">
                    <span className="label">Start:</span>
                    <span className="value">{formatDateTime(shiftDetails.shift_start_datetime)}</span>
                  </div>
                  {shiftDetails.shift_end_datetime && (
                    <div className="info-item">
                      <span className="label">End:</span>
                      <span className="value">{formatDateTime(shiftDetails.shift_end_datetime)}</span>
                    </div>
                  )}
                </>
              ) : (
                <>
                  <div className="info-item">
                    <span className="label">Date:</span>
                    <span className="value">{formatDate(shiftDetails.shift_date)}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Part:</span>
                    <span className="value">{shiftDetails.shift_part || 'Not specified'}</span>
                  </div>
                </>
              )}
            </div>
          </div>

          <div className="info-section">
            <h3>🏢 Job Information</h3>
            <div className="info-items">
              <div className="info-item">
                <span className="label">Job:</span>
                <span className="value">{shiftDetails.job_name}</span>
              </div>
              <div className="info-item">
                <span className="label">Client:</span>
                <span className="value">{shiftDetails.client_company_name}</span>
              </div>
              {shiftDetails.client_po_number && (
                <div className="info-item">
                  <span className="label">PO Number:</span>
                  <span className="value">{shiftDetails.client_po_number}</span>
                </div>
              )}
            </div>
          </div>

          <div className="info-section">
            <h3>👤 Your Access</h3>
            <div className="info-items">
              <div className="access-badges">
                {userPermissions.is_manager && (
                  <span className="access-badge manager">Manager</span>
                )}
                {userPermissions.is_crew_chief && (
                  <span className="access-badge crew-chief">Crew Chief</span>
                )}
                {userPermissions.is_client && (
                  <span className="access-badge client">Client</span>
                )}
                {!userPermissions.is_manager && !userPermissions.is_crew_chief && !userPermissions.is_client && (
                  <span className="access-badge employee">Employee</span>
                )}
              </div>
              <div className="permissions-list">
                {userPermissions.can_edit_others && (
                  <div className="permission-item">
                    <span className="permission-icon">✏️</span>
                    <span>Can edit all timesheets</span>
                  </div>
                )}
                {userPermissions.can_approve && (
                  <div className="permission-item">
                    <span className="permission-icon">✅</span>
                    <span>Can approve timesheets</span>
                  </div>
                )}
                {userPermissions.is_client && (
                  <div className="permission-item">
                    <span className="permission-icon">👁️</span>
                    <span>View-only access</span>
                  </div>
                )}
                {!userPermissions.can_edit_others && !userPermissions.can_approve && !userPermissions.is_client && (
                  <div className="permission-item">
                    <span className="permission-icon">📝</span>
                    <span>Can edit own timesheet</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ShiftDetailsHeader;
