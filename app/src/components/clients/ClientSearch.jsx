import React from 'react';
import './ClientSearch.css';

const ClientSearch = ({
  searchTerm,
  onSearchChange,
  filterStatus,
  onFilterChange,
  sortBy,
  onSortChange
}) => {
  return (
    <div className="client-search-container">
      <div className="search-section">
        <div className="search-input-container">
          <input
            type="text"
            placeholder="Search companies, users, or emails..."
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            className="search-input"
          />
          <span className="search-icon">🔍</span>
        </div>
        
        {searchTerm && (
          <button
            onClick={() => onSearchChange('')}
            className="clear-search-button"
            title="Clear search"
          >
            ✕
          </button>
        )}
      </div>

      <div className="filters-section">
        <div className="filter-group">
          <label htmlFor="status-filter">Status:</label>
          <select
            id="status-filter"
            value={filterStatus}
            onChange={(e) => onFilterChange(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Companies</option>
            <option value="active">Active Users</option>
            <option value="inactive">No Active Users</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="sort-select">Sort by:</label>
          <select
            id="sort-select"
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value)}
            className="filter-select"
          >
            <option value="name">Company Name</option>
            <option value="jobs">Total Jobs</option>
            <option value="users">User Count</option>
            <option value="recent">Recent Activity</option>
          </select>
        </div>
      </div>
    </div>
  );
};

export default ClientSearch;
