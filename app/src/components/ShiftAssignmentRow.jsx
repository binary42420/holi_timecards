import React, { useState, useMemo } from 'react';
import Select from 'react-select';
import './ShiftAssignmentRow.css';

const ShiftAssignmentRow = ({
  shiftId,
  role, // The key for the role, e.g., 'crew_chief'
  roleLabel, // The display name, e.g., 'Crew Chief'
  requiredCount,
  assignedWorkers, // Array of worker objects { id, name } currently assigned to this role on this shift
  availableWorkers, // Array of all worker objects { id, name, employee_type } for the manager
  onAssignWorker, // Callback: (shiftId, userId, role) => void
  onUnassignWorker, // Callback: (shiftId, userId, role) => void
  isLoading // Boolean to disable controls during operations
}) => {
  const [selectedWorkerToAssign, setSelectedWorkerToAssign] = useState(null);

  const numAssigned = assignedWorkers.length;

  // Role mapping for certification checking
  const roleMapping = {
    'crew_chief': 'crew chief',
    'stagehand': 'stagehand',
    'fork_operator': 'forklift',
    'pickup_truck_driver': 'truck',
    'general_employee': 'stagehand'
  };

  // Filter available workers based on certifications and current assignments
  const assignableWorkerOptions = useMemo(() => {
    return availableWorkers
      .filter(worker => {
        // Don't show workers already assigned to this role on this shift
        if (assignedWorkers.some(sw => sw.id === worker.id)) {
          return false;
        }

        // Check if worker is certified for this role
        const requiredRole = roleMapping[role] || role;
        if (worker.certifications) {
          // Everyone can be a stagehand
          if (requiredRole === 'stagehand') return true;

          // Check specific certifications
          if (requiredRole === 'crew chief' && !worker.certifications.can_crew_chief) return false;
          if (requiredRole === 'forklift' && !worker.certifications.can_forklift) return false;
          if (requiredRole === 'truck' && !worker.certifications.can_truck) return false;
        }

        return true;
      })
      .map(worker => ({
        value: worker.id,
        label: `${worker.name}`,
        worker: worker,
        isCertified: worker.certifications ?
          (roleMapping[role] === 'stagehand' ||
           worker.certifications[`can_${roleMapping[role]?.replace(' ', '_')}`] ||
           worker.available_roles?.includes(roleLabel)) : false
      }));
  }, [availableWorkers, assignedWorkers, role, roleLabel, roleMapping]);

  const handleAssignClick = () => {
    if (selectedWorkerToAssign && selectedWorkerToAssign.value) {
      onAssignWorker(shiftId, selectedWorkerToAssign.value, role);
      setSelectedWorkerToAssign(null); // Reset dropdown after assignment
    }
  };

  // Get status color based on fulfillment
  const getStatusColor = () => {
    if (numAssigned === 0) return '#dc3545'; // Red - empty
    if (numAssigned < requiredCount) return '#ffc107'; // Yellow - partial
    return '#28a745'; // Green - full
  };

  // Custom styles for react-select
  const selectStyles = {
    control: (base, state) => ({
      ...base,
      borderColor: state.isFocused ? '#80bdff' : '#ced4da',
      boxShadow: state.isFocused ? '0 0 0 2px rgba(0, 123, 255, 0.25)' : 'none',
      '&:hover': {
        borderColor: '#adb5bd'
      }
    }),
    option: (base, state) => ({
      ...base,
      backgroundColor: state.isSelected ? '#007bff' :
                      state.isFocused ? '#f8f9fa' : 'white',
      color: state.isSelected ? 'white' : '#495057',
      '&:before': {
        content: state.data.isCertified ? '"✓ "' : '"⚠ "',
        color: state.data.isCertified ? '#28a745' : '#ffc107',
        fontWeight: 'bold'
      }
    }),
    menuPortal: base => ({ ...base, zIndex: 9999 })
  };

  return (
    <div className="shift-assignment-row">
      <div className="role-status">
        <div className="role-header">
          <span className="role-label">{roleLabel}</span>
          <span
            className="status-badge"
            style={{ backgroundColor: getStatusColor() }}
          >
            {numAssigned}/{requiredCount}
          </span>
        </div>
      </div>

      <div className="assigned-workers">
        {assignedWorkers.map(worker => (
          <div key={worker.id} className="assigned-worker">
            <span className="worker-name">{worker.name}</span>
            <button
              onClick={() => onUnassignWorker(shiftId, worker.id, role)}
              disabled={isLoading}
              className="unassign-btn"
            >
              Remove
            </button>
          </div>
        ))}
      </div>

      <div className="assignment-controls">
        {numAssigned < requiredCount ? (
          <div className="assign-section">
            <Select
              options={assignableWorkerOptions}
              value={selectedWorkerToAssign}
              onChange={setSelectedWorkerToAssign}
              placeholder={`Select ${roleLabel.toLowerCase()}...`}
              isClearable
              isDisabled={isLoading}
              isSearchable
              menuPortalTarget={document.body}
              styles={selectStyles}
              noOptionsMessage={() => `No certified ${roleLabel.toLowerCase()}s available`}
            />
            <button
              onClick={handleAssignClick}
              disabled={!selectedWorkerToAssign || isLoading}
              className="assign-btn"
            >
              Assign
            </button>
          </div>
        ) : (
          <div className="fully-staffed">
            <span className="status-text">✓ Fully Staffed</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default ShiftAssignmentRow;
