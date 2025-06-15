import React, { useState } from 'react';
import './ScheduleFilters.css';

const ScheduleFilters = ({
  filters,
  onFiltersChange,
  jobs,
  clients,
  workers
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleFilterChange = (filterType, value, isMultiple = false) => {
    const newFilters = { ...filters };
    
    if (isMultiple) {
      if (newFilters[filterType].includes(value)) {
        newFilters[filterType] = newFilters[filterType].filter(item => item !== value);
      } else {
        newFilters[filterType] = [...newFilters[filterType], value];
      }
    } else {
      newFilters[filterType] = value;
    }
    
    onFiltersChange(newFilters);
  };

  const clearAllFilters = () => {
    onFiltersChange({
      jobs: [],
      clients: [],
      workers: [],
      roles: [],
      status: 'all',
      showOnlyMyShifts: false
    });
  };

  const getActiveFilterCount = () => {
    let count = 0;
    if (filters.jobs.length > 0) count++;
    if (filters.clients.length > 0) count++;
    if (filters.workers.length > 0) count++;
    if (filters.roles.length > 0) count++;
    if (filters.status !== 'all') count++;
    if (filters.showOnlyMyShifts) count++;
    return count;
  };

  const activeFilterCount = getActiveFilterCount();

  const roleOptions = [
    { value: 'stagehand', label: 'Stagehand' },
    { value: 'crew_chief', label: 'Crew Chief' },
    { value: 'fork_operator', label: 'Forklift Operator' },
    { value: 'pickup_truck_driver', label: 'Truck Driver' }
  ];

  const statusOptions = [
    { value: 'all', label: 'All Shifts' },
    { value: 'assigned', label: 'Fully Assigned' },
    { value: 'understaffed', label: 'Understaffed' },
    { value: 'unassigned', label: 'No Workers' },
    { value: 'overstaffed', label: 'Overstaffed' }
  ];

  return (
    <div className={`schedule-filters ${isExpanded ? 'expanded' : ''}`}>
      <div className="filters-header">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="filters-toggle"
        >
          <span className="toggle-icon">🔍</span>
          <span className="toggle-text">Filters</span>
          {activeFilterCount > 0 && (
            <span className="filter-count">{activeFilterCount}</span>
          )}
          <span className={`expand-arrow ${isExpanded ? 'expanded' : ''}`}>▼</span>
        </button>

        {activeFilterCount > 0 && (
          <button
            onClick={clearAllFilters}
            className="clear-filters-button"
          >
            Clear All
          </button>
        )}
      </div>

      {isExpanded && (
        <div className="filters-content">
          <div className="filter-row">
            <div className="filter-group">
              <label className="filter-label">Status:</label>
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="filter-select"
              >
                {statusOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label className="filter-label">
                <input
                  type="checkbox"
                  checked={filters.showOnlyMyShifts}
                  onChange={(e) => handleFilterChange('showOnlyMyShifts', e.target.checked)}
                  className="filter-checkbox"
                />
                Show only my shifts
              </label>
            </div>
          </div>

          <div className="filter-row">
            <div className="filter-group">
              <label className="filter-label">Jobs:</label>
              <div className="multi-select">
                {jobs.slice(0, 5).map(job => (
                  <label key={job.id} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={filters.jobs.includes(job.id)}
                      onChange={() => handleFilterChange('jobs', job.id, true)}
                      className="filter-checkbox"
                    />
                    {job.jobName}
                  </label>
                ))}
                {jobs.length > 5 && (
                  <span className="more-items">+{jobs.length - 5} more</span>
                )}
              </div>
            </div>

            <div className="filter-group">
              <label className="filter-label">Clients:</label>
              <div className="multi-select">
                {clients.slice(0, 5).map(client => (
                  <label key={client.id} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={filters.clients.includes(client.id)}
                      onChange={() => handleFilterChange('clients', client.id, true)}
                      className="filter-checkbox"
                    />
                    {client.companyName}
                  </label>
                ))}
                {clients.length > 5 && (
                  <span className="more-items">+{clients.length - 5} more</span>
                )}
              </div>
            </div>
          </div>

          <div className="filter-row">
            <div className="filter-group">
              <label className="filter-label">Roles:</label>
              <div className="multi-select">
                {roleOptions.map(role => (
                  <label key={role.value} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={filters.roles.includes(role.value)}
                      onChange={() => handleFilterChange('roles', role.value, true)}
                      className="filter-checkbox"
                    />
                    {role.label}
                  </label>
                ))}
              </div>
            </div>

            <div className="filter-group">
              <label className="filter-label">Workers:</label>
              <div className="multi-select">
                {workers.slice(0, 5).map(worker => (
                  <label key={worker.id} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={filters.workers.includes(worker.id)}
                      onChange={() => handleFilterChange('workers', worker.id, true)}
                      className="filter-checkbox"
                    />
                    {worker.name}
                  </label>
                ))}
                {workers.length > 5 && (
                  <span className="more-items">+{workers.length - 5} more</span>
                )}
              </div>
            </div>
          </div>

          <div className="filter-summary">
            <p className="summary-text">
              {activeFilterCount === 0 
                ? 'No filters applied - showing all shifts'
                : `${activeFilterCount} filter(s) applied`
              }
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScheduleFilters;
