import React from 'react';
import './EmployeeFilters.css';

const EmployeeFilters = ({
    searchTerm,
    onSearchChange,
    filters,
    onFiltersChange,
    sortBy,
    onSortByChange,
    sortOrder,
    onSortOrderChange,
    viewMode,
    onViewModeChange,
    employees
}) => {
    const handleFilterChange = (key, value) => {
        onFiltersChange(prev => ({
            ...prev,
            [key]: value
        }));
    };

    const clearAllFilters = () => {
        onSearchChange('');
        onFiltersChange({
            status: 'all',
            role: 'all',
            certification: 'all',
            availability: 'all'
        });
        onSortByChange('name');
        onSortOrderChange('asc');
    };

    const hasActiveFilters = searchTerm || Object.values(filters).some(f => f !== 'all') || sortBy !== 'name' || sortOrder !== 'asc';

    return (
        <div className="employee-filters">
            <div className="filters-row">
                <div className="search-section">
                    <div className="search-input-wrapper">
                        <span className="search-icon">🔍</span>
                        <input
                            type="text"
                            placeholder="Search employees by name, username, or certification..."
                            value={searchTerm}
                            onChange={(e) => onSearchChange(e.target.value)}
                            className="search-input"
                        />
                        {searchTerm && (
                            <button 
                                className="clear-search"
                                onClick={() => onSearchChange('')}
                                title="Clear search"
                            >
                                ✕
                            </button>
                        )}
                    </div>
                </div>

                <div className="view-controls">
                    <div className="view-mode-selector">
                        <button
                            className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
                            onClick={() => onViewModeChange('grid')}
                            title="Grid View"
                        >
                            ⊞
                        </button>
                        <button
                            className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
                            onClick={() => onViewModeChange('list')}
                            title="List View"
                        >
                            ☰
                        </button>
                        <button
                            className={`view-btn ${viewMode === 'table' ? 'active' : ''}`}
                            onClick={() => onViewModeChange('table')}
                            title="Table View"
                        >
                            ⊞
                        </button>
                    </div>
                </div>
            </div>

            <div className="filters-row">
                <div className="filter-group">
                    <label className="filter-label">Status:</label>
                    <select
                        value={filters.status}
                        onChange={(e) => handleFilterChange('status', e.target.value)}
                        className="filter-select"
                    >
                        <option value="all">All Status</option>
                        <option value="approved">Approved</option>
                        <option value="pending">Pending</option>
                    </select>
                </div>

                <div className="filter-group">
                    <label className="filter-label">Role:</label>
                    <select
                        value={filters.role}
                        onChange={(e) => handleFilterChange('role', e.target.value)}
                        className="filter-select"
                    >
                        <option value="all">All Roles</option>
                        <option value="stagehand">Stagehand</option>
                        <option value="crew_chief">Crew Chief</option>
                        <option value="fork_operator">Forklift Operator</option>
                        <option value="pickup_truck_driver">Truck Driver</option>
                    </select>
                </div>

                <div className="filter-group">
                    <label className="filter-label">Certification:</label>
                    <select
                        value={filters.certification}
                        onChange={(e) => handleFilterChange('certification', e.target.value)}
                        className="filter-select"
                    >
                        <option value="all">All Certifications</option>
                        <option value="crew_chief">Crew Chief</option>
                        <option value="forklift">Forklift</option>
                        <option value="truck">Truck Driver</option>
                    </select>
                </div>

                <div className="filter-group">
                    <label className="filter-label">Sort by:</label>
                    <select
                        value={sortBy}
                        onChange={(e) => onSortByChange(e.target.value)}
                        className="filter-select"
                    >
                        <option value="name">Name</option>
                        <option value="username">Username</option>
                        <option value="role">Role</option>
                        <option value="status">Status</option>
                    </select>
                </div>

                <div className="filter-group">
                    <button
                        className={`sort-order-btn ${sortOrder === 'desc' ? 'desc' : 'asc'}`}
                        onClick={() => onSortOrderChange(sortOrder === 'asc' ? 'desc' : 'asc')}
                        title={`Sort ${sortOrder === 'asc' ? 'Descending' : 'Ascending'}`}
                    >
                        {sortOrder === 'asc' ? '↑' : '↓'}
                    </button>
                </div>

                {hasActiveFilters && (
                    <div className="filter-group">
                        <button
                            className="clear-filters-btn"
                            onClick={clearAllFilters}
                            title="Clear all filters"
                        >
                            🗑️ Clear All
                        </button>
                    </div>
                )}
            </div>

            <div className="filters-summary">
                <span className="results-count">
                    Showing {employees.length} employee{employees.length !== 1 ? 's' : ''}
                    {hasActiveFilters && ' (filtered)'}
                </span>
                
                {hasActiveFilters && (
                    <div className="active-filters">
                        {searchTerm && (
                            <span className="filter-tag">
                                Search: "{searchTerm}"
                                <button onClick={() => onSearchChange('')}>✕</button>
                            </span>
                        )}
                        {filters.status !== 'all' && (
                            <span className="filter-tag">
                                Status: {filters.status}
                                <button onClick={() => handleFilterChange('status', 'all')}>✕</button>
                            </span>
                        )}
                        {filters.role !== 'all' && (
                            <span className="filter-tag">
                                Role: {filters.role.replace(/_/g, ' ')}
                                <button onClick={() => handleFilterChange('role', 'all')}>✕</button>
                            </span>
                        )}
                        {filters.certification !== 'all' && (
                            <span className="filter-tag">
                                Cert: {filters.certification}
                                <button onClick={() => handleFilterChange('certification', 'all')}>✕</button>
                            </span>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default EmployeeFilters;
