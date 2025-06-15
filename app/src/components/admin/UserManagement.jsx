import React, { useState, useEffect } from 'react';
import { useSocket } from '../../contexts/SocketContext';
import { useAuth } from '../../contexts/AuthContext';
import './UserManagement.css';

const UserManagement = () => {
    const { socket } = useSocket();
    const { user } = useAuth();
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [createType, setCreateType] = useState('manager'); // 'manager' or 'admin'
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        name: '',
        email: ''
    });

    // Check if current user is admin
    const isAdmin = user?.isAdmin || false;

    useEffect(() => {
        if (!isAdmin) {
            setError('Access denied. Admin privileges required.');
            setLoading(false);
            return;
        }
        fetchUsers();
    }, [isAdmin]);

    const fetchUsers = () => {
        if (!socket) return;

        setLoading(true);
        setError('');

        const requestData = {
            request_id: 302 // Get All Users
        };

        socket.send(JSON.stringify(requestData));

        const handleResponse = (event) => {
            try {
                const response = JSON.parse(event.data);
                if (response.request_id === 302) {
                    if (response.success) {
                        setUsers(response.data.users || []);
                    } else {
                        setError(response.error || 'Failed to fetch users');
                    }
                    setLoading(false);
                    socket.removeEventListener('message', handleResponse);
                }
            } catch (err) {
                console.error('Error parsing response:', err);
                setError('Failed to parse server response');
                setLoading(false);
                socket.removeEventListener('message', handleResponse);
            }
        };

        socket.addEventListener('message', handleResponse);
    };

    const handleCreateUser = (e) => {
        e.preventDefault();
        if (!socket) return;

        setError('');
        setSuccessMessage('');

        // Validate form
        if (!formData.username || !formData.password || !formData.name || !formData.email) {
            setError('All fields are required');
            return;
        }

        const requestId = createType === 'admin' ? 301 : 300;
        const requestData = {
            request_id: requestId,
            data: formData
        };

        socket.send(JSON.stringify(requestData));

        const handleResponse = (event) => {
            try {
                const response = JSON.parse(event.data);
                if (response.request_id === requestId) {
                    if (response.success) {
                        setSuccessMessage(response.message);
                        setShowCreateForm(false);
                        setFormData({ username: '', password: '', name: '', email: '' });
                        fetchUsers(); // Refresh the user list
                    } else {
                        setError(response.error || 'Failed to create user');
                    }
                    socket.removeEventListener('message', handleResponse);
                }
            } catch (err) {
                console.error('Error parsing response:', err);
                setError('Failed to parse server response');
                socket.removeEventListener('message', handleResponse);
            }
        };

        socket.addEventListener('message', handleResponse);
    };

    const handleUpdateRole = (userId, newRole) => {
        if (!socket) return;

        setError('');
        setSuccessMessage('');

        const requestData = {
            request_id: 303, // Update User Role
            data: {
                user_id: userId,
                new_role: newRole
            }
        };

        socket.send(JSON.stringify(requestData));

        const handleResponse = (event) => {
            try {
                const response = JSON.parse(event.data);
                if (response.request_id === 303) {
                    if (response.success) {
                        setSuccessMessage(response.message);
                        fetchUsers(); // Refresh the user list
                    } else {
                        setError(response.error || 'Failed to update user role');
                    }
                    socket.removeEventListener('message', handleResponse);
                }
            } catch (err) {
                console.error('Error parsing response:', err);
                setError('Failed to parse server response');
                socket.removeEventListener('message', handleResponse);
            }
        };

        socket.addEventListener('message', handleResponse);
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    if (!isAdmin) {
        return (
            <div className="user-management">
                <div className="access-denied">
                    <h2>Access Denied</h2>
                    <p>You need admin privileges to access user management.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="user-management">
            <div className="user-management-header">
                <h1>User Management</h1>
                <button 
                    className="btn btn-primary"
                    onClick={() => setShowCreateForm(true)}
                >
                    Add New User
                </button>
            </div>

            {error && (
                <div className="alert alert-error">
                    <span className="alert-icon">⚠️</span>
                    {error}
                </div>
            )}

            {successMessage && (
                <div className="alert alert-success">
                    <span className="alert-icon">✅</span>
                    {successMessage}
                </div>
            )}

            {showCreateForm && (
                <div className="modal-overlay">
                    <div className="modal">
                        <div className="modal-header">
                            <h2>Create New User</h2>
                            <button 
                                className="close-btn"
                                onClick={() => setShowCreateForm(false)}
                            >
                                ×
                            </button>
                        </div>
                        <form onSubmit={handleCreateUser}>
                            <div className="form-group">
                                <label>User Type:</label>
                                <select 
                                    value={createType} 
                                    onChange={(e) => setCreateType(e.target.value)}
                                >
                                    <option value="manager">Manager</option>
                                    <option value="admin">Admin</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label>Username:</label>
                                <input
                                    type="text"
                                    name="username"
                                    value={formData.username}
                                    onChange={handleInputChange}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>Password:</label>
                                <input
                                    type="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleInputChange}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>Full Name:</label>
                                <input
                                    type="text"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleInputChange}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>Email:</label>
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleInputChange}
                                    required
                                />
                            </div>
                            <div className="form-actions">
                                <button type="submit" className="btn btn-primary">
                                    Create {createType === 'admin' ? 'Admin' : 'Manager'}
                                </button>
                                <button 
                                    type="button" 
                                    className="btn btn-secondary"
                                    onClick={() => setShowCreateForm(false)}
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {loading ? (
                <div className="loading">Loading users...</div>
            ) : (
                <div className="users-table">
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Username</th>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Role</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(user => (
                                <tr key={user.id}>
                                    <td>{user.id}</td>
                                    <td>{user.username}</td>
                                    <td>{user.name}</td>
                                    <td>{user.email || 'N/A'}</td>
                                    <td>
                                        <span className={`role-badge role-${user.role.toLowerCase()}`}>
                                            {user.role}
                                        </span>
                                    </td>
                                    <td>
                                        <span className={`status-badge ${user.isActive ? 'active' : 'inactive'}`}>
                                            {user.isActive ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td>
                                        {user.role !== 'Admin' && (
                                            <select 
                                                onChange={(e) => handleUpdateRole(user.id, e.target.value)}
                                                defaultValue=""
                                            >
                                                <option value="" disabled>Change Role</option>
                                                <option value="employee">Employee</option>
                                                <option value="manager">Manager</option>
                                                <option value="admin">Admin</option>
                                            </select>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default UserManagement;
