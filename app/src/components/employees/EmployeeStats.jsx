import React from 'react';
import './EmployeeStats.css';

const EmployeeStats = ({ employees, filteredEmployees }) => {
    const totalEmployees = employees.length;
    const approvedEmployees = employees.filter(emp => emp.approved).length;
    const pendingEmployees = employees.filter(emp => !emp.approved).length;
    
    // Calculate certification stats
    const certificationStats = employees.reduce((stats, emp) => {
        if (emp.certifications && Array.isArray(emp.certifications)) {
            emp.certifications.forEach(cert => {
                stats[cert] = (stats[cert] || 0) + 1;
            });
        }
        return stats;
    }, {});

    // Calculate role distribution
    const roleStats = employees.reduce((stats, emp) => {
        const role = emp.employee_type || 'stagehand';
        stats[role] = (stats[role] || 0) + 1;
        return stats;
    }, {});

    const formatRole = (role) => {
        return role.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    };

    const getPercentage = (value, total) => {
        return total > 0 ? Math.round((value / total) * 100) : 0;
    };

    return (
        <div className="employee-stats">
            <div className="stats-grid">
                <div className="stat-card primary">
                    <div className="stat-icon">👥</div>
                    <div className="stat-content">
                        <h3 className="stat-number">{totalEmployees}</h3>
                        <p className="stat-label">Total Employees</p>
                        {filteredEmployees.length !== totalEmployees && (
                            <span className="stat-filtered">({filteredEmployees.length} shown)</span>
                        )}
                    </div>
                </div>

                <div className="stat-card success">
                    <div className="stat-icon">✅</div>
                    <div className="stat-content">
                        <h3 className="stat-number">{approvedEmployees}</h3>
                        <p className="stat-label">Approved</p>
                        <div className="stat-progress">
                            <div 
                                className="progress-bar approved"
                                style={{ width: `${getPercentage(approvedEmployees, totalEmployees)}%` }}
                            ></div>
                        </div>
                        <span className="stat-percentage">
                            {getPercentage(approvedEmployees, totalEmployees)}%
                        </span>
                    </div>
                </div>

                <div className="stat-card warning">
                    <div className="stat-icon">⏳</div>
                    <div className="stat-content">
                        <h3 className="stat-number">{pendingEmployees}</h3>
                        <p className="stat-label">Pending Approval</p>
                        <div className="stat-progress">
                            <div 
                                className="progress-bar pending"
                                style={{ width: `${getPercentage(pendingEmployees, totalEmployees)}%` }}
                            ></div>
                        </div>
                        <span className="stat-percentage">
                            {getPercentage(pendingEmployees, totalEmployees)}%
                        </span>
                    </div>
                </div>

                <div className="stat-card info">
                    <div className="stat-icon">🏆</div>
                    <div className="stat-content">
                        <h3 className="stat-number">
                            {Object.values(certificationStats).reduce((sum, count) => sum + count, 0)}
                        </h3>
                        <p className="stat-label">Total Certifications</p>
                        <div className="certification-breakdown">
                            {Object.entries(certificationStats).map(([cert, count]) => (
                                <span key={cert} className="cert-stat">
                                    {cert.toUpperCase()}: {count}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            <div className="detailed-stats">
                <div className="stats-section">
                    <h4 className="section-title">Role Distribution</h4>
                    <div className="role-stats">
                        {Object.entries(roleStats).map(([role, count]) => (
                            <div key={role} className="role-stat-item">
                                <div className="role-info">
                                    <span className="role-name">{formatRole(role)}</span>
                                    <span className="role-count">{count}</span>
                                </div>
                                <div className="role-progress">
                                    <div 
                                        className="progress-bar role"
                                        style={{ 
                                            width: `${getPercentage(count, totalEmployees)}%`,
                                            backgroundColor: getRoleColor(role)
                                        }}
                                    ></div>
                                </div>
                                <span className="role-percentage">
                                    {getPercentage(count, totalEmployees)}%
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="stats-section">
                    <h4 className="section-title">Certification Breakdown</h4>
                    <div className="cert-stats">
                        {Object.entries(certificationStats).length > 0 ? (
                            Object.entries(certificationStats).map(([cert, count]) => (
                                <div key={cert} className="cert-stat-item">
                                    <div className="cert-info">
                                        <span className="cert-icon">{getCertIcon(cert)}</span>
                                        <span className="cert-name">{formatCertification(cert)}</span>
                                        <span className="cert-count">{count}</span>
                                    </div>
                                    <div className="cert-progress">
                                        <div 
                                            className="progress-bar cert"
                                            style={{ 
                                                width: `${getPercentage(count, totalEmployees)}%`,
                                                backgroundColor: getCertColor(cert)
                                            }}
                                        ></div>
                                    </div>
                                    <span className="cert-percentage">
                                        {getPercentage(count, totalEmployees)}%
                                    </span>
                                </div>
                            ))
                        ) : (
                            <p className="no-certs">No additional certifications recorded</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

const getRoleColor = (role) => {
    const colors = {
        'crew_chief': '#e74c3c',
        'stagehand': '#3498db',
        'fork_operator': '#f39c12',
        'pickup_truck_driver': '#27ae60'
    };
    return colors[role] || '#95a5a6';
};

const getCertColor = (cert) => {
    const colors = {
        'crew_chief': '#e74c3c',
        'forklift': '#f39c12',
        'truck': '#27ae60'
    };
    return colors[cert] || '#95a5a6';
};

const getCertIcon = (cert) => {
    const icons = {
        'crew_chief': '👑',
        'forklift': '🚜',
        'truck': '🚛'
    };
    return icons[cert] || '🏆';
};

const formatCertification = (cert) => {
    const names = {
        'crew_chief': 'Crew Chief',
        'forklift': 'Forklift Operator',
        'truck': 'Truck Driver'
    };
    return names[cert] || cert.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

export default EmployeeStats;
