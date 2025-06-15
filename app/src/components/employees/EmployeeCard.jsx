import React, { useState } from 'react';
import './EmployeeCard.css';
import EmployeeCertificationManager from '../EmployeeCertificationManager';

const EmployeeCard = ({
    employee,
    viewMode,
    isSelected,
    onSelect,
    onClick,
    onApprove,
    onReject,
    isManager = false,
    onCertificationUpdate
}) => {
    const [showCertificationModal, setShowCertificationModal] = useState(false);
    const getRoleColor = (role) => {
        const colors = {
            'crew_chief': '#e74c3c',
            'stagehand': '#3498db',
            'fork_operator': '#f39c12',
            'pickup_truck_driver': '#27ae60'
        };
        return colors[role] || '#95a5a6';
    };

    const formatRole = (role) => {
        if (!role) return 'Stagehand';
        return role.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    };

    const getCertificationBadges = (certifications) => {
        if (!certifications || !Array.isArray(certifications)) return [];
        
        const badgeMap = {
            'crew_chief': { label: 'CC', color: '#e74c3c', title: 'Crew Chief' },
            'forklift': { label: 'FO', color: '#f39c12', title: 'Forklift Operator' },
            'truck': { label: 'TD', color: '#27ae60', title: 'Truck Driver' }
        };

        return certifications.map(cert => badgeMap[cert]).filter(Boolean);
    };

    if (viewMode === 'table') {
        return (
            <div className={`employee-table-row ${employee.approved ? 'approved' : 'pending'} ${isSelected ? 'selected' : ''}`}>
                <div className="table-cell checkbox-cell">
                    <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => onSelect(e.target.checked)}
                        onClick={(e) => e.stopPropagation()}
                    />
                </div>
                <div className="table-cell name-cell" onClick={onClick}>
                    <div className="employee-avatar">
                        {employee.name.charAt(0).toUpperCase()}
                    </div>
                    <div className="employee-name-info">
                        <span className="employee-name">{employee.name}</span>
                        <span className="employee-role" style={{ color: getRoleColor(employee.employee_type) }}>
                            {formatRole(employee.employee_type)}
                        </span>
                    </div>
                </div>
                <div className="table-cell username-cell">
                    @{employee.userName}
                </div>
                <div className="table-cell status-cell">
                    <span className={`status-badge ${employee.approved ? 'approved' : 'pending'}`}>
                        {employee.approved ? '✓ Approved' : '⏳ Pending'}
                    </span>
                </div>
                <div className="table-cell certifications-cell">
                    <div className="certification-badges">
                        {getCertificationBadges(employee.certifications).map((badge, index) => (
                            <span
                                key={index}
                                className="cert-badge"
                                style={{ backgroundColor: badge.color }}
                                title={badge.title}
                            >
                                {badge.label}
                            </span>
                        ))}
                    </div>
                </div>
                <div className="table-cell actions-cell">
                    <div className="employee-actions">
                        {!employee.approved && (
                            <>
                                <button
                                    className="btn btn-approve"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        onApprove();
                                    }}
                                    title="Approve Employee"
                                >
                                    ✓
                                </button>
                                <button
                                    className="btn btn-reject"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        onReject();
                                    }}
                                    title="Reject Employee"
                                >
                                    ✗
                                </button>
                            </>
                        )}
                        {isManager && employee.approved && (
                            <button
                                className="btn btn-secondary btn-sm"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    setShowCertificationModal(true);
                                }}
                                title="Manage Certifications"
                            >
                                🏆
                            </button>
                        )}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className={`employee-card ${viewMode} ${employee.approved ? 'approved' : 'pending'} ${isSelected ? 'selected' : ''}`}>
            <div className="card-header">
                <div className="card-checkbox">
                    <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => onSelect(e.target.checked)}
                        onClick={(e) => e.stopPropagation()}
                    />
                </div>
                <div className="employee-avatar">
                    {employee.name.charAt(0).toUpperCase()}
                </div>
                <div className="card-status">
                    <span className={`status-badge ${employee.approved ? 'approved' : 'pending'}`}>
                        {employee.approved ? '✓' : '⏳'}
                    </span>
                </div>
            </div>

            <div className="card-content" onClick={onClick}>
                <h3 className="employee-name">{employee.name}</h3>
                <p className="employee-username">@{employee.userName}</p>
                
                <div className="employee-role-info">
                    <span 
                        className="employee-role"
                        style={{ color: getRoleColor(employee.employee_type) }}
                    >
                        {formatRole(employee.employee_type)}
                    </span>
                </div>

                {employee.certifications && employee.certifications.length > 0 && (
                    <div className="certification-badges">
                        {getCertificationBadges(employee.certifications).map((badge, index) => (
                            <span
                                key={index}
                                className="cert-badge"
                                style={{ backgroundColor: badge.color }}
                                title={badge.title}
                            >
                                {badge.label}
                            </span>
                        ))}
                    </div>
                )}

                <div className="employee-meta">
                    <span className="meta-item">
                        📅 Joined: {employee.created_at ? new Date(employee.created_at).toLocaleDateString() : 'N/A'}
                    </span>
                    {employee.approved && (
                        <div className="quick-actions">
                            <button
                                className="quick-action-btn"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    window.open('/enhanced-schedule', '_blank');
                                }}
                                title="View in Schedule"
                            >
                                📅
                            </button>
                            <button
                                className="quick-action-btn"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    window.open('/manager-timesheets', '_blank');
                                }}
                                title="View Timesheets"
                            >
                                ⏰
                            </button>
                            {isManager && (
                                <button
                                    className="quick-action-btn"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setShowCertificationModal(true);
                                    }}
                                    title="Manage Certifications"
                                >
                                    🏆
                                </button>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {!employee.approved && (
                <div className="card-actions">
                    <button
                        className="btn btn-approve"
                        onClick={(e) => {
                            e.stopPropagation();
                            onApprove();
                        }}
                        title="Approve Employee"
                    >
                        ✓ Approve
                    </button>
                    <button
                        className="btn btn-reject"
                        onClick={(e) => {
                            e.stopPropagation();
                            onReject();
                        }}
                        title="Reject Employee"
                    >
                        ✗ Reject
                    </button>
                </div>
            )}

            {/* Certification Management Modal */}
            {showCertificationModal && (
                <EmployeeCertificationManager
                    employeeId={employee.id}
                    employeeName={employee.name}
                    currentCertifications={employee.certifications || {}}
                    onUpdate={(updatedData) => {
                        if (onCertificationUpdate) {
                            onCertificationUpdate(employee.id, updatedData);
                        }
                        setShowCertificationModal(false);
                    }}
                    isModal={true}
                    onClose={() => setShowCertificationModal(false)}
                />
            )}
        </div>
    );
};

export default EmployeeCard;
