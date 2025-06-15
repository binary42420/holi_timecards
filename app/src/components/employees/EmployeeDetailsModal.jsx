import React, { useState } from 'react';
import './EmployeeDetailsModal.css';

const EmployeeDetailsModal = ({
    employee,
    isOpen,
    onClose,
    onApprove,
    onReject
}) => {
    const [activeTab, setActiveTab] = useState('overview');

    if (!isOpen || !employee) return null;

    const formatRole = (role) => {
        if (!role) return 'Stagehand';
        return role.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    };

    const getCertificationBadges = (certifications) => {
        if (!certifications || !Array.isArray(certifications)) return [];
        
        const badgeMap = {
            'crew_chief': { label: 'Crew Chief', color: '#e74c3c', icon: '👑' },
            'forklift': { label: 'Forklift Operator', color: '#f39c12', icon: '🚜' },
            'truck': { label: 'Truck Driver', color: '#27ae60', icon: '🚛' }
        };

        return certifications.map(cert => badgeMap[cert]).filter(Boolean);
    };

    const handleOverlayClick = (e) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    return (
        <div className="modal-overlay" onClick={handleOverlayClick}>
            <div className="employee-modal">
                <div className="modal-header">
                    <div className="employee-header-info">
                        <div className="employee-avatar large">
                            {employee.name.charAt(0).toUpperCase()}
                        </div>
                        <div className="employee-title-info">
                            <h2 className="employee-name">{employee.name}</h2>
                            <p className="employee-username">@{employee.userName}</p>
                            <span className={`status-badge ${employee.approved ? 'approved' : 'pending'}`}>
                                {employee.approved ? '✓ Approved' : '⏳ Pending Approval'}
                            </span>
                        </div>
                    </div>
                    <button className="modal-close" onClick={onClose}>
                        ✕
                    </button>
                </div>

                <div className="modal-tabs">
                    <button 
                        className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
                        onClick={() => setActiveTab('overview')}
                    >
                        📋 Overview
                    </button>
                    <button 
                        className={`tab ${activeTab === 'certifications' ? 'active' : ''}`}
                        onClick={() => setActiveTab('certifications')}
                    >
                        🏆 Certifications
                    </button>
                    <button 
                        className={`tab ${activeTab === 'history' ? 'active' : ''}`}
                        onClick={() => setActiveTab('history')}
                    >
                        📊 History
                    </button>
                </div>

                <div className="modal-content">
                    {activeTab === 'overview' && (
                        <div className="tab-content">
                            <div className="info-grid">
                                <div className="info-card">
                                    <h4>Basic Information</h4>
                                    <div className="info-item">
                                        <span className="label">Full Name:</span>
                                        <span className="value">{employee.name}</span>
                                    </div>
                                    <div className="info-item">
                                        <span className="label">Username:</span>
                                        <span className="value">@{employee.userName}</span>
                                    </div>
                                    <div className="info-item">
                                        <span className="label">Primary Role:</span>
                                        <span className="value">{formatRole(employee.employee_type)}</span>
                                    </div>
                                    <div className="info-item">
                                        <span className="label">Status:</span>
                                        <span className={`value status ${employee.approved ? 'approved' : 'pending'}`}>
                                            {employee.approved ? 'Approved' : 'Pending Approval'}
                                        </span>
                                    </div>
                                </div>

                                <div className="info-card">
                                    <h4>Account Details</h4>
                                    <div className="info-item">
                                        <span className="label">Account Created:</span>
                                        <span className="value">
                                            {employee.created_at ? new Date(employee.created_at).toLocaleDateString() : 'N/A'}
                                        </span>
                                    </div>
                                    <div className="info-item">
                                        <span className="label">Last Updated:</span>
                                        <span className="value">
                                            {employee.updated_at ? new Date(employee.updated_at).toLocaleDateString() : 'N/A'}
                                        </span>
                                    </div>
                                    <div className="info-item">
                                        <span className="label">Account Active:</span>
                                        <span className="value">
                                            {employee.isActive !== false ? '✅ Yes' : '❌ No'}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'certifications' && (
                        <div className="tab-content">
                            <div className="certifications-section">
                                <h4>Current Certifications</h4>
                                <div className="certification-list">
                                    <div className="cert-item base">
                                        <span className="cert-icon">🎭</span>
                                        <div className="cert-info">
                                            <span className="cert-name">Stagehand</span>
                                            <span className="cert-desc">Base certification - All employees</span>
                                        </div>
                                        <span className="cert-status active">✓ Active</span>
                                    </div>
                                    
                                    {getCertificationBadges(employee.certifications).map((cert, index) => (
                                        <div key={index} className="cert-item">
                                            <span className="cert-icon">{cert.icon}</span>
                                            <div className="cert-info">
                                                <span className="cert-name">{cert.label}</span>
                                                <span className="cert-desc">Additional certification</span>
                                            </div>
                                            <span className="cert-status active">✓ Active</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'history' && (
                        <div className="tab-content">
                            <div className="history-section">
                                <h4>Recent Activity</h4>
                                <div className="history-list">
                                    <div className="history-item">
                                        <span className="history-icon">👤</span>
                                        <div className="history-info">
                                            <span className="history-action">Account created</span>
                                            <span className="history-date">
                                                {employee.created_at ? new Date(employee.created_at).toLocaleDateString() : 'N/A'}
                                            </span>
                                        </div>
                                    </div>
                                    {employee.approved && (
                                        <div className="history-item">
                                            <span className="history-icon">✅</span>
                                            <div className="history-info">
                                                <span className="history-action">Account approved</span>
                                                <span className="history-date">
                                                    {employee.updated_at ? new Date(employee.updated_at).toLocaleDateString() : 'N/A'}
                                                </span>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {!employee.approved && (
                    <div className="modal-actions">
                        <button className="btn btn-approve" onClick={onApprove}>
                            ✓ Approve Employee
                        </button>
                        <button className="btn btn-reject" onClick={onReject}>
                            ✗ Reject Employee
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default EmployeeDetailsModal;
