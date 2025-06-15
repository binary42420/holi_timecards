import React, { useState, useMemo } from 'react';
import WorkerCard from './WorkerCard';
import './WorkerPanel.css';

const WorkerPanel = ({
  workers,
  onWorkerDragStart,
  onWorkerDragEnd,
  filters
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState('all');
  const [sortBy, setSortBy] = useState('name'); // 'name', 'role', 'availability'
  const [groupBy, setGroupBy] = useState('none'); // 'none', 'role', 'certification'

  // Filter and sort workers
  const filteredWorkers = useMemo(() => {
    let filtered = workers.filter(worker => {
      // Search filter
      if (searchTerm && !worker.name.toLowerCase().includes(searchTerm.toLowerCase())) {
        return false;
      }
      
      // Role filter
      if (selectedRole !== 'all' && worker.employee_type !== selectedRole) {
        return false;
      }
      
      // Additional filters from parent component
      if (filters.workers.length > 0 && !filters.workers.includes(worker.id)) {
        return false;
      }
      
      if (filters.roles.length > 0 && !filters.roles.includes(worker.employee_type)) {
        return false;
      }
      
      return true;
    });

    // Sort workers
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'role':
          return (a.employee_type || '').localeCompare(b.employee_type || '');
        case 'availability':
          // Sort by number of available hours or shifts
          return (b.availability_score || 0) - (a.availability_score || 0);
        default:
          return 0;
      }
    });

    return filtered;
  }, [workers, searchTerm, selectedRole, sortBy, filters]);

  // Group workers if needed
  const groupedWorkers = useMemo(() => {
    if (groupBy === 'none') {
      return { 'All Workers': filteredWorkers };
    }

    const groups = {};
    
    filteredWorkers.forEach(worker => {
      let groupKey;
      
      switch (groupBy) {
        case 'role':
          groupKey = worker.employee_type || 'Unassigned';
          break;
        case 'certification':
          if (worker.certifications) {
            const certs = [];
            if (worker.certifications.can_crew_chief) certs.push('Crew Chief');
            if (worker.certifications.can_forklift) certs.push('Forklift');
            if (worker.certifications.can_truck) certs.push('Truck');
            groupKey = certs.length > 0 ? certs.join(', ') : 'Basic';
          } else {
            groupKey = 'Basic';
          }
          break;
        default:
          groupKey = 'All Workers';
      }
      
      if (!groups[groupKey]) {
        groups[groupKey] = [];
      }
      groups[groupKey].push(worker);
    });

    return groups;
  }, [filteredWorkers, groupBy]);

  const roleOptions = [
    { value: 'all', label: 'All Roles' },
    { value: 'stagehand', label: 'Stagehand' },
    { value: 'crew_chief', label: 'Crew Chief' },
    { value: 'fork_operator', label: 'Forklift Operator' },
    { value: 'pickup_truck_driver', label: 'Truck Driver' }
  ];

  const getWorkerStats = () => {
    const total = filteredWorkers.length;
    const available = filteredWorkers.filter(w => w.is_available !== false).length;
    const assigned = filteredWorkers.filter(w => w.current_shifts_count > 0).length;
    
    return { total, available, assigned };
  };

  const stats = getWorkerStats();

  return (
    <div className="worker-panel">
      <div className="panel-header">
        <h3 className="panel-title">
          <span className="panel-icon">👥</span>
          Workers
        </h3>
        
        <div className="worker-stats">
          <div className="stat-item">
            <span className="stat-value">{stats.total}</span>
            <span className="stat-label">Total</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{stats.available}</span>
            <span className="stat-label">Available</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{stats.assigned}</span>
            <span className="stat-label">Assigned</span>
          </div>
        </div>
      </div>

      <div className="panel-controls">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search workers..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <span className="search-icon">🔍</span>
        </div>

        <div className="filter-controls">
          <select
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value)}
            className="role-filter"
          >
            {roleOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="sort-select"
          >
            <option value="name">Sort by Name</option>
            <option value="role">Sort by Role</option>
            <option value="availability">Sort by Availability</option>
          </select>

          <select
            value={groupBy}
            onChange={(e) => setGroupBy(e.target.value)}
            className="group-select"
          >
            <option value="none">No Grouping</option>
            <option value="role">Group by Role</option>
            <option value="certification">Group by Certification</option>
          </select>
        </div>
      </div>

      <div className="workers-container">
        {Object.entries(groupedWorkers).map(([groupName, groupWorkers]) => (
          <div key={groupName} className="worker-group">
            {groupBy !== 'none' && (
              <div className="group-header">
                <h4 className="group-title">{groupName}</h4>
                <span className="group-count">({groupWorkers.length})</span>
              </div>
            )}
            
            <div className="workers-list">
              {groupWorkers.map(worker => (
                <WorkerCard
                  key={worker.id}
                  worker={worker}
                  onDragStart={() => onWorkerDragStart(worker)}
                  onDragEnd={onWorkerDragEnd}
                />
              ))}
            </div>
          </div>
        ))}
      </div>

      {filteredWorkers.length === 0 && (
        <div className="no-workers">
          <div className="no-workers-icon">👤</div>
          <p className="no-workers-text">
            {searchTerm || selectedRole !== 'all' 
              ? 'No workers match your filters'
              : 'No workers available'
            }
          </p>
          {(searchTerm || selectedRole !== 'all') && (
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedRole('all');
              }}
              className="clear-filters-button"
            >
              Clear Filters
            </button>
          )}
        </div>
      )}

      <div className="panel-footer">
        <div className="drag-instructions">
          <p><strong>💡 Drag & Drop:</strong></p>
          <p>Drag workers to time slots to assign them to shifts</p>
        </div>
      </div>
    </div>
  );
};

export default WorkerPanel;
