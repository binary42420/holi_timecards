import React, { useState } from 'react';
import './AddEmployeeModal.css';

const AddEmployeeModal = ({ isOpen, onClose, onSubmit }) => {
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        confirmPassword: '',
        name: '',
        email: '',
        phone: '',
        employee_type: 'stagehand',
        // Certifications
        can_crew_chief: false,
        can_forklift: false,
        can_truck: false,
        // Auto-approve by default since manager is creating
        auto_approve: true
    });
    const [errors, setErrors] = useState({});
    const [isSubmitting, setIsSubmitting] = useState(false);

    if (!isOpen) return null;

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
        
        // Clear error when user starts typing
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }
    };

    const validateForm = () => {
        const newErrors = {};

        // Required fields
        if (!formData.username.trim()) {
            newErrors.username = 'Username is required';
        } else if (formData.username.length < 3) {
            newErrors.username = 'Username must be at least 3 characters';
        }

        if (!formData.password) {
            newErrors.password = 'Password is required';
        } else if (formData.password.length < 6) {
            newErrors.password = 'Password must be at least 6 characters';
        }

        if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = 'Passwords do not match';
        }

        if (!formData.name.trim()) {
            newErrors.name = 'Full name is required';
        }

        if (formData.email && !/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Please enter a valid email address';
        }

        if (formData.phone && !/^\+?[\d\s\-\(\)]+$/.test(formData.phone)) {
            newErrors.phone = 'Please enter a valid phone number';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }

        setIsSubmitting(true);

        try {
            const employeeData = {
                username: formData.username.trim(),
                password: formData.password,
                name: formData.name.trim(),
                email: formData.email.trim() || null,
                phone: formData.phone.trim() || null,
                employee_type: formData.employee_type,
                isManager: false,
                isActive: true,
                isApproval: formData.auto_approve, // Auto-approve if checked
                certifications: {
                    can_crew_chief: formData.can_crew_chief,
                    can_forklift: formData.can_forklift,
                    can_truck: formData.can_truck
                }
            };

            await onSubmit(employeeData);
            
            // Reset form on success
            setFormData({
                username: '',
                password: '',
                confirmPassword: '',
                name: '',
                email: '',
                phone: '',
                employee_type: 'stagehand',
                can_crew_chief: false,
                can_forklift: false,
                can_truck: false,
                auto_approve: true
            });
            setErrors({});
        } catch (error) {
            console.error('Error creating employee:', error);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleOverlayClick = (e) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    return (
        <div className="modal-overlay" onClick={handleOverlayClick}>
            <div className="add-employee-modal">
                <div className="modal-header">
                    <h2>Add New Employee</h2>
                    <button className="modal-close" onClick={onClose}>
                        ✕
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="employee-form">
                    <div className="form-section">
                        <h3>Account Information</h3>
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="username">Username *</label>
                                <input
                                    type="text"
                                    id="username"
                                    name="username"
                                    value={formData.username}
                                    onChange={handleChange}
                                    className={errors.username ? 'error' : ''}
                                    placeholder="Enter username"
                                    disabled={isSubmitting}
                                />
                                {errors.username && <span className="error-text">{errors.username}</span>}
                            </div>

                            <div className="form-group">
                                <label htmlFor="name">Full Name *</label>
                                <input
                                    type="text"
                                    id="name"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    className={errors.name ? 'error' : ''}
                                    placeholder="Enter full name"
                                    disabled={isSubmitting}
                                />
                                {errors.name && <span className="error-text">{errors.name}</span>}
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="password">Password *</label>
                                <input
                                    type="password"
                                    id="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    className={errors.password ? 'error' : ''}
                                    placeholder="Enter password"
                                    disabled={isSubmitting}
                                />
                                {errors.password && <span className="error-text">{errors.password}</span>}
                            </div>

                            <div className="form-group">
                                <label htmlFor="confirmPassword">Confirm Password *</label>
                                <input
                                    type="password"
                                    id="confirmPassword"
                                    name="confirmPassword"
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                    className={errors.confirmPassword ? 'error' : ''}
                                    placeholder="Confirm password"
                                    disabled={isSubmitting}
                                />
                                {errors.confirmPassword && <span className="error-text">{errors.confirmPassword}</span>}
                            </div>
                        </div>
                    </div>

                    <div className="form-section">
                        <h3>Contact Information</h3>
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="email">Email</label>
                                <input
                                    type="email"
                                    id="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    className={errors.email ? 'error' : ''}
                                    placeholder="Enter email address"
                                    disabled={isSubmitting}
                                />
                                {errors.email && <span className="error-text">{errors.email}</span>}
                            </div>

                            <div className="form-group">
                                <label htmlFor="phone">Phone</label>
                                <input
                                    type="tel"
                                    id="phone"
                                    name="phone"
                                    value={formData.phone}
                                    onChange={handleChange}
                                    className={errors.phone ? 'error' : ''}
                                    placeholder="Enter phone number"
                                    disabled={isSubmitting}
                                />
                                {errors.phone && <span className="error-text">{errors.phone}</span>}
                            </div>
                        </div>
                    </div>

                    <div className="form-section">
                        <h3>Role & Certifications</h3>
                        <div className="form-group">
                            <label htmlFor="employee_type">Primary Role</label>
                            <select
                                id="employee_type"
                                name="employee_type"
                                value={formData.employee_type}
                                onChange={handleChange}
                                disabled={isSubmitting}
                            >
                                <option value="stagehand">Stagehand</option>
                                <option value="crew_chief">Crew Chief</option>
                                <option value="fork_operator">Forklift Operator</option>
                                <option value="pickup_truck_driver">Truck Driver</option>
                            </select>
                        </div>

                        <div className="certifications-group">
                            <label className="section-label">Additional Certifications</label>
                            <div className="checkbox-group">
                                <label className="checkbox-label">
                                    <input
                                        type="checkbox"
                                        name="can_crew_chief"
                                        checked={formData.can_crew_chief}
                                        onChange={handleChange}
                                        disabled={isSubmitting}
                                    />
                                    <span className="checkmark"></span>
                                    Crew Chief Certified
                                </label>

                                <label className="checkbox-label">
                                    <input
                                        type="checkbox"
                                        name="can_forklift"
                                        checked={formData.can_forklift}
                                        onChange={handleChange}
                                        disabled={isSubmitting}
                                    />
                                    <span className="checkmark"></span>
                                    Forklift Operator Certified
                                </label>

                                <label className="checkbox-label">
                                    <input
                                        type="checkbox"
                                        name="can_truck"
                                        checked={formData.can_truck}
                                        onChange={handleChange}
                                        disabled={isSubmitting}
                                    />
                                    <span className="checkmark"></span>
                                    Truck Driver Certified
                                </label>
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="checkbox-label">
                                <input
                                    type="checkbox"
                                    name="auto_approve"
                                    checked={formData.auto_approve}
                                    onChange={handleChange}
                                    disabled={isSubmitting}
                                />
                                <span className="checkmark"></span>
                                Auto-approve this employee
                            </label>
                        </div>
                    </div>

                    <div className="modal-actions">
                        <button
                            type="button"
                            className="btn btn-secondary"
                            onClick={onClose}
                            disabled={isSubmitting}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="btn btn-success"
                            disabled={isSubmitting}
                        >
                            {isSubmitting ? 'Creating...' : 'Create Employee'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AddEmployeeModal;
