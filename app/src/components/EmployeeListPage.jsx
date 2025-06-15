import React, { useState, useEffect, useCallback, useMemo } from 'react'; // Added useCallback
import { useSocket } from '../utils';
import { useNavigate } from 'react-router-dom';
import { createAuthenticatedRequest } from '../utils/sessionUtils';
import EmployeeCard from './employees/EmployeeCard';
import EmployeeDetailsModal from './employees/EmployeeDetailsModal';
import EmployeeFilters from './employees/EmployeeFilters';
import EmployeeStats from './employees/EmployeeStats';
import BulkActions from './employees/BulkActions';
import AddEmployeeModal from './employees/AddEmployeeModal';
import './../css/EmployeeListPage.css';

const EmployeeListPage = () => {
    const navigate = useNavigate();
    const [employees, setEmployees] = useState([]);
    const [filteredEmployees, setFilteredEmployees] = useState([]);
    const [selectedEmployees, setSelectedEmployees] = useState([]);
    const [selectedEmployee, setSelectedEmployee] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isAddEmployeeModalOpen, setIsAddEmployeeModalOpen] = useState(false);
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [filters, setFilters] = useState({
        status: 'all', // all, approved, pending
        role: 'all', // all, stagehand, crew_chief, forklift, truck
        certification: 'all', // all, crew_chief, forklift, truck
        availability: 'all' // all, available, unavailable
    });
    const [sortBy, setSortBy] = useState('name'); // name, username, role, status
    const [sortOrder, setSortOrder] = useState('asc'); // asc, desc
    const [viewMode, setViewMode] = useState('grid'); // grid, list, table
    const { socket, connectionStatus, reconnect } = useSocket();

    const fetchEmployees = useCallback(() => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            setIsLoading(true);
            setError('');
            setSuccessMessage('');
            const request = createAuthenticatedRequest(60); // FETCH_EMPLOYEES
            console.log('🔍 Sending employees request:', request);
            socket.send(JSON.stringify(request));
        } else {
            console.error('WebSocket connection not open when trying to fetch employees.');
            setError('Cannot fetch employees: WebSocket is not connected.');
            setIsLoading(false);
        }
    }, [socket]);



    const handleApprove = (userName) => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            setError('');
            setSuccessMessage('');
            const request = createAuthenticatedRequest(62, { userName }); // APPROVE_EMPLOYEE
            socket.send(JSON.stringify(request));
        } else {
            console.error('WebSocket connection not open when trying to approve employee.');
            setError('Cannot approve employee: WebSocket is not connected.');
        }
    };

    const handleReject = (userName) => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            setError('');
            setSuccessMessage('');
            const request = createAuthenticatedRequest(64, { userName }); // REJECT_EMPLOYEE
            socket.send(JSON.stringify(request));
        } else {
            console.error('WebSocket connection not open when trying to reject employee.');
            setError('Cannot reject employee: WebSocket is not connected.');
        }
    };

    // Handle employee selection for bulk operations
    const handleEmployeeSelect = (employeeId, isSelected) => {
        if (isSelected) {
            setSelectedEmployees(prev => [...prev, employeeId]);
        } else {
            setSelectedEmployees(prev => prev.filter(id => id !== employeeId));
        }
    };

    const handleSelectAll = (isSelected) => {
        if (isSelected) {
            setSelectedEmployees(filteredEmployees.map(emp => emp.userName));
        } else {
            setSelectedEmployees([]);
        }
    };

    const handleEmployeeClick = (employee) => {
        setSelectedEmployee(employee);
        setIsModalOpen(true);
    };

    const handleCreateEmployee = (employeeData) => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            setError('');
            setSuccessMessage('');
            const request = createAuthenticatedRequest(65, employeeData); // CREATE_EMPLOYEE_BY_MANAGER
            socket.send(JSON.stringify(request));
        } else {
            setError('Cannot create employee: WebSocket is not connected.');
        }
    };

    const handleCertificationUpdate = (employeeId, updatedData) => {
        // Update the employee in the local state with new certification data
        setEmployees(prevEmployees =>
            prevEmployees.map(emp =>
                emp.id === employeeId
                    ? {
                        ...emp,
                        certifications: updatedData.certifications,
                        available_roles: updatedData.available_roles
                    }
                    : emp
            )
        );
        setSuccessMessage(`Certifications updated for ${updatedData.employee_name}`);
    };

    // Filter and sort employees
    const processedEmployees = useMemo(() => {
        let filtered = employees.filter(employee => {
            // Search filter
            if (searchTerm) {
                const searchLower = searchTerm.toLowerCase();
                const matchesSearch =
                    employee.name.toLowerCase().includes(searchLower) ||
                    employee.userName.toLowerCase().includes(searchLower) ||
                    (employee.certifications && employee.certifications.some(cert =>
                        cert.toLowerCase().includes(searchLower)
                    ));
                if (!matchesSearch) return false;
            }

            // Status filter
            if (filters.status !== 'all') {
                if (filters.status === 'approved' && !employee.approved) return false;
                if (filters.status === 'pending' && employee.approved) return false;
            }

            // Role filter
            if (filters.role !== 'all') {
                if (!employee.employee_type || employee.employee_type !== filters.role) return false;
            }

            // Certification filter
            if (filters.certification !== 'all') {
                if (!employee.certifications || !employee.certifications.includes(filters.certification)) return false;
            }

            return true;
        });

        // Sort employees
        filtered.sort((a, b) => {
            let aValue, bValue;

            switch (sortBy) {
                case 'name':
                    aValue = a.name.toLowerCase();
                    bValue = b.name.toLowerCase();
                    break;
                case 'username':
                    aValue = a.userName.toLowerCase();
                    bValue = b.userName.toLowerCase();
                    break;
                case 'role':
                    aValue = a.employee_type || '';
                    bValue = b.employee_type || '';
                    break;
                case 'status':
                    aValue = a.approved ? 'approved' : 'pending';
                    bValue = b.approved ? 'approved' : 'pending';
                    break;
                default:
                    aValue = a.name.toLowerCase();
                    bValue = b.name.toLowerCase();
            }

            if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
            if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
            return 0;
        });

        return filtered;
    }, [employees, searchTerm, filters, sortBy, sortOrder]);

    useEffect(() => {
        setFilteredEmployees(processedEmployees);
    }, [processedEmployees]);

    useEffect(() => {
        if (socket) {
            fetchEmployees(); // Initial fetch when socket is ready

            const handleMessage = (event) => {
                try {
                    const response = JSON.parse(event.data);

                    if (response.request_id === 60) { // Fetch employees response
                        setIsLoading(false);
                        if (response.success && Array.isArray(response.data)) {
                            setEmployees(response.data);
                        } else {
                            setError(response.error || 'Error fetching employees list.');
                            setEmployees([]); // Clear employees on error
                        }
                    } else if (response.request_id === 61) { // Fetch employee details with certifications
                        if (response.success && Array.isArray(response.data)) {
                            // Merge certification data with existing employees
                            setEmployees(prevEmployees => {
                                return prevEmployees.map(emp => {
                                    const detailedEmp = response.data.find(d => d.userName === emp.userName);
                                    return detailedEmp ? { ...emp, ...detailedEmp } : emp;
                                });
                            });
                        }
                    } else if (response.request_id === 62) { // Approve employee response
                        if (response.success) {
                            setSuccessMessage(response.message || 'Employee approved successfully.');
                            fetchEmployees(); // Re-fetch the list
                        } else {
                            setError(response.error || 'Failed to approve employee.');
                        }
                    } else if (response.request_id === 64) { // Reject employee response
                        if (response.success) {
                            setSuccessMessage(response.message || 'Employee rejected successfully.');
                            fetchEmployees(); // Re-fetch the list
                        } else {
                            setError(response.error || 'Failed to reject employee.');
                        }
                    } else if (response.request_id === 65) { // Create employee response
                        if (response.success) {
                            setSuccessMessage(response.message || 'Employee created successfully.');
                            setIsAddEmployeeModalOpen(false);
                            fetchEmployees(); // Re-fetch the list
                        } else {
                            setError(response.error || 'Failed to create employee.');
                        }
                    }
                } catch (e) {
                    console.error('Error parsing WebSocket message in EmployeeListPage:', e);
                    setError('Error processing server response.');
                }
            };

            socket.addEventListener('message', handleMessage);

            return () => {
                socket.removeEventListener('message', handleMessage);
            };
        }
    }, [socket, fetchEmployees]); // fetchEmployees is now a stable useCallback dependency

    return (
        <div className="employee-directory">
            <div className="employee-header">
                <div className="header-top">
                    <h1 className="employee-title">
                        <span className="title-icon">👥</span>
                        Employee Directory
                    </h1>
                    <div className="header-actions">
                        <button
                            className="btn btn-success"
                            onClick={() => setIsAddEmployeeModalOpen(true)}
                        >
                            ➕ Add Employee
                        </button>
                        <button
                            className="btn btn-primary"
                            onClick={() => navigate('/enhanced-schedule')}
                        >
                            📅 Schedule View
                        </button>
                        <button
                            className="btn btn-secondary"
                            onClick={() => navigate('/manager-timesheets')}
                        >
                            ⏰ Timesheets
                        </button>
                    </div>
                </div>

                {error && (
                    <div className="alert alert-error">
                        <span className="alert-icon">⚠️</span>
                        <div className="alert-content">
                            <strong>Error:</strong> {error}
                            {error.includes("Workplace for user") && (
                                <div className="error-help">
                                    <p><strong>Possible Solution:</strong> This error typically occurs when the manager account doesn't have a workplace setup. Please contact your system administrator to initialize your workplace data.</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {successMessage && (
                    <div className="alert alert-success">
                        <span className="alert-icon">✅</span>
                        {successMessage}
                    </div>
                )}

                {connectionStatus !== 'connected' && (
                    <div className={`alert ${connectionStatus === 'error' || connectionStatus === 'failed' ? 'alert-error' : 'alert-warning'}`}>
                        <span className="alert-icon">
                            {connectionStatus === 'connecting' && '🔄'}
                            {connectionStatus === 'reconnecting' && '🔄'}
                            {connectionStatus === 'disconnected' && '⚠️'}
                            {connectionStatus === 'error' && '❌'}
                            {connectionStatus === 'failed' && '❌'}
                        </span>
                        <div className="alert-content">
                            <strong>Connection Status:</strong>
                            {connectionStatus === 'connecting' && ' Connecting to server...'}
                            {connectionStatus === 'reconnecting' && ' Reconnecting to server...'}
                            {connectionStatus === 'disconnected' && ' Connection lost. Attempting to reconnect...'}
                            {connectionStatus === 'error' && ' Connection error occurred.'}
                            {connectionStatus === 'failed' && ' Connection failed after multiple attempts.'}
                            {(connectionStatus === 'error' || connectionStatus === 'failed' || connectionStatus === 'disconnected') && (
                                <button
                                    className="btn btn-sm btn-primary"
                                    onClick={reconnect}
                                    style={{ marginLeft: '10px' }}
                                >
                                    🔄 Retry Connection
                                </button>
                            )}
                        </div>
                    </div>
                )}
            </div>

            <EmployeeStats
                employees={employees}
                filteredEmployees={filteredEmployees}
            />

            <EmployeeFilters
                searchTerm={searchTerm}
                onSearchChange={setSearchTerm}
                filters={filters}
                onFiltersChange={setFilters}
                sortBy={sortBy}
                onSortByChange={setSortBy}
                sortOrder={sortOrder}
                onSortOrderChange={setSortOrder}
                viewMode={viewMode}
                onViewModeChange={setViewMode}
                employees={employees}
            />

            {selectedEmployees.length > 0 && (
                <BulkActions
                    selectedEmployees={selectedEmployees}
                    onApproveSelected={() => {
                        selectedEmployees.forEach(userName => handleApprove(userName));
                        setSelectedEmployees([]);
                    }}
                    onRejectSelected={() => {
                        selectedEmployees.forEach(userName => handleReject(userName));
                        setSelectedEmployees([]);
                    }}
                    onClearSelection={() => setSelectedEmployees([])}
                />
            )}

            <div className="employee-content">
                {isLoading ? (
                    <div className="loading-state">
                        <div className="loading-spinner"></div>
                        <p>Loading employees...</p>
                    </div>
                ) : filteredEmployees.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-icon">👥</div>
                        <h3>No employees found</h3>
                        <p>
                            {searchTerm || Object.values(filters).some(f => f !== 'all')
                                ? 'Try adjusting your search or filters'
                                : 'No employees have been added yet'
                            }
                        </p>
                    </div>
                ) : (
                    <div className={`employee-list ${viewMode}`}>
                        {viewMode === 'table' && (
                            <div className="table-header">
                                <div className="table-cell checkbox-cell">
                                    <input
                                        type="checkbox"
                                        checked={selectedEmployees.length === filteredEmployees.length}
                                        onChange={(e) => handleSelectAll(e.target.checked)}
                                    />
                                </div>
                                <div className="table-cell">Name</div>
                                <div className="table-cell">Username</div>
                                <div className="table-cell">Status</div>
                                <div className="table-cell">Certifications</div>
                                <div className="table-cell">Actions</div>
                            </div>
                        )}

                        {filteredEmployees.map(employee => (
                            <EmployeeCard
                                key={employee.userName}
                                employee={employee}
                                viewMode={viewMode}
                                isSelected={selectedEmployees.includes(employee.userName)}
                                onSelect={(isSelected) => handleEmployeeSelect(employee.userName, isSelected)}
                                onClick={() => handleEmployeeClick(employee)}
                                onApprove={() => handleApprove(employee.userName)}
                                onReject={() => handleReject(employee.userName)}
                                isManager={true}
                                onCertificationUpdate={handleCertificationUpdate}
                            />
                        ))}
                    </div>
                )}
            </div>

            {isModalOpen && selectedEmployee && (
                <EmployeeDetailsModal
                    employee={selectedEmployee}
                    isOpen={isModalOpen}
                    onClose={() => {
                        setIsModalOpen(false);
                        setSelectedEmployee(null);
                    }}
                    onApprove={() => {
                        handleApprove(selectedEmployee.userName);
                        setIsModalOpen(false);
                        setSelectedEmployee(null);
                    }}
                    onReject={() => {
                        handleReject(selectedEmployee.userName);
                        setIsModalOpen(false);
                        setSelectedEmployee(null);
                    }}
                />
            )}

            {isAddEmployeeModalOpen && (
                <AddEmployeeModal
                    isOpen={isAddEmployeeModalOpen}
                    onClose={() => setIsAddEmployeeModalOpen(false)}
                    onSubmit={handleCreateEmployee}
                />
            )}
        </div>
    );
};

export default EmployeeListPage;
