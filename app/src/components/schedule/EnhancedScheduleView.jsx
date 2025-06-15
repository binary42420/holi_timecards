import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { useSocket, logDebug, logError, logInfo } from '../../utils';
import { createAuthenticatedRequest } from '../../utils/sessionUtils';
import CalendarView from './CalendarView';
import ScheduleToolbar from './ScheduleToolbar';
import WorkerPanel from './WorkerPanel';
import ShiftDetailsModal from './ShiftDetailsModal';
import ScheduleFilters from './ScheduleFilters';
import BulkOperationsPanel from './BulkOperationsPanel';
import './EnhancedScheduleView.css';

const EnhancedScheduleView = () => {
  const { socket } = useSocket();
  const scheduleRef = useRef(null);
  const lastUpdateRef = useRef(Date.now());

  // View state
  const [currentView, setCurrentView] = useState('week'); // 'day', 'week', 'month', 'timeline'
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedShift, setSelectedShift] = useState(null);
  const [selectedShifts, setSelectedShifts] = useState([]); // For bulk operations
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalType, setModalType] = useState('create'); // 'create', 'edit', 'template', 'conflict'

  // Data state
  const [shifts, setShifts] = useState([]);
  const [workers, setWorkers] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [clientCompanies, setClientCompanies] = useState([]);
  const [workplaceSettings, setWorkplaceSettings] = useState(null);
  const [shiftTemplates, setShiftTemplates] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [conflicts, setConflicts] = useState([]);

  // Filter state
  const [filters, setFilters] = useState({
    jobs: [],
    clients: [],
    workers: [],
    roles: [],
    status: 'all', // 'all', 'assigned', 'unassigned', 'understaffed', 'overstaffed'
    showOnlyMyShifts: false,
    dateRange: null,
    searchTerm: '',
    showConflicts: false,
    showAvailableOnly: false
  });

  // UI state
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [draggedWorker, setDraggedWorker] = useState(null);
  const [draggedShift, setDraggedShift] = useState(null);
  const [isWorkerPanelOpen, setIsWorkerPanelOpen] = useState(true);
  const [isBulkMode, setIsBulkMode] = useState(false);
  const [isAnalyticsOpen, setIsAnalyticsOpen] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30 seconds

  // Load initial data
  useEffect(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      loadScheduleData();
    }
  }, [socket, currentDate, currentView]);

  // WebSocket message handler
  useEffect(() => {
    if (socket) {
      const handleMessage = (event) => {
        const response = JSON.parse(event.data);
        
        switch (response.request_id) {
          case 2001: // Get schedule data
            handleScheduleDataResponse(response);
            break;
          case 2002: // Assign worker to shift
            handleWorkerAssignmentResponse(response);
            break;
          case 2003: // Unassign worker from shift
            handleWorkerUnassignmentResponse(response);
            break;
          case 2004: // Create new shift
            handleShiftCreationResponse(response);
            break;
          case 2005: // Update shift
            handleShiftUpdateResponse(response);
            break;
          case 2006: // Delete shift
            handleShiftDeletionResponse(response);
            break;
          default:
            break;
        }
      };

      socket.addEventListener('message', handleMessage);
      return () => socket.removeEventListener('message', handleMessage);
    }
  }, [socket]);

  const loadScheduleData = useCallback(() => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    
    setIsLoading(true);
    setError('');
    
    const startDate = getViewStartDate(currentDate, currentView);
    const endDate = getViewEndDate(currentDate, currentView);
    
    const request = createAuthenticatedRequest(2001, {
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString(),
      view_type: currentView,
      include_workers: true,
      include_jobs: true,
      include_clients: true,
      filters: filters
    });

    socket.send(JSON.stringify(request));
  }, [socket, currentDate, currentView, filters]);

  const handleScheduleDataResponse = (response) => {
    setIsLoading(false);
    if (response.success) {
      setShifts(response.data.shifts || []);
      setWorkers(response.data.workers || []);
      setJobs(response.data.jobs || []);
      setClientCompanies(response.data.clients || []);
      setWorkplaceSettings(response.data.workplace_settings || null);
    } else {
      setError(response.error || 'Failed to load schedule data');
    }
  };

  const handleWorkerAssignmentResponse = (response) => {
    if (response.success) {
      // Update local state
      loadScheduleData();
    } else {
      setError(response.error || 'Failed to assign worker');
    }
  };

  const handleWorkerUnassignmentResponse = (response) => {
    if (response.success) {
      // Update local state
      loadScheduleData();
    } else {
      setError(response.error || 'Failed to unassign worker');
    }
  };

  const handleShiftCreationResponse = (response) => {
    if (response.success) {
      loadScheduleData();
      setSelectedShift(response.data);
      setIsModalOpen(true);
    } else {
      setError(response.error || 'Failed to create shift');
    }
  };

  const handleShiftUpdateResponse = (response) => {
    if (response.success) {
      loadScheduleData();
      if (selectedShift && selectedShift.id === response.data.id) {
        setSelectedShift(response.data);
      }
    } else {
      setError(response.error || 'Failed to update shift');
    }
  };

  const handleShiftDeletionResponse = (response) => {
    if (response.success) {
      loadScheduleData();
      setIsModalOpen(false);
      setSelectedShift(null);
    } else {
      setError(response.error || 'Failed to delete shift');
    }
  };

  // Navigation functions
  const navigateDate = (direction) => {
    const newDate = new Date(currentDate);
    
    switch (currentView) {
      case 'day':
        newDate.setDate(newDate.getDate() + (direction === 'next' ? 1 : -1));
        break;
      case 'week':
        newDate.setDate(newDate.getDate() + (direction === 'next' ? 7 : -7));
        break;
      case 'month':
        newDate.setMonth(newDate.getMonth() + (direction === 'next' ? 1 : -1));
        break;
      default:
        break;
    }
    
    setCurrentDate(newDate);
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  // Drag and drop handlers
  const handleWorkerDragStart = (worker) => {
    setDraggedWorker(worker);
  };

  const handleWorkerDragEnd = () => {
    setDraggedWorker(null);
  };

  const handleShiftDrop = (shiftId, worker) => {
    if (!worker || !shiftId) return;
    
    assignWorkerToShift(shiftId, worker.id, worker.role_assigned || 'stagehand');
  };

  // API functions
  const assignWorkerToShift = (shiftId, workerId, role) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;

    const request = createAuthenticatedRequest(2002, {
      shift_id: shiftId,
      worker_id: workerId,
      role_assigned: role
    });

    socket.send(JSON.stringify(request));
  };

  const unassignWorkerFromShift = (shiftId, workerId, role) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;

    const request = createAuthenticatedRequest(2003, {
      shift_id: shiftId,
      worker_id: workerId,
      role_assigned: role
    });

    socket.send(JSON.stringify(request));
  };

  const createShift = (shiftData) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    
    const request = {
      request_id: 2004,
      data: shiftData
    };
    
    socket.send(JSON.stringify(request));
  };

  const updateShift = (shiftId, updateData) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    
    const request = {
      request_id: 2005,
      data: {
        shift_id: shiftId,
        ...updateData
      }
    };
    
    socket.send(JSON.stringify(request));
  };

  const deleteShift = (shiftId) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    
    if (!window.confirm('Are you sure you want to delete this shift?')) return;
    
    const request = {
      request_id: 2006,
      data: { shift_id: shiftId }
    };
    
    socket.send(JSON.stringify(request));
  };

  // Utility functions
  const getViewStartDate = (date, view) => {
    const start = new Date(date);
    
    switch (view) {
      case 'day':
        start.setHours(0, 0, 0, 0);
        break;
      case 'week':
        const dayOfWeek = start.getDay();
        start.setDate(start.getDate() - dayOfWeek);
        start.setHours(0, 0, 0, 0);
        break;
      case 'month':
        start.setDate(1);
        start.setHours(0, 0, 0, 0);
        break;
      default:
        break;
    }
    
    return start;
  };

  const getViewEndDate = (date, view) => {
    const end = new Date(date);
    
    switch (view) {
      case 'day':
        end.setHours(23, 59, 59, 999);
        break;
      case 'week':
        const dayOfWeek = end.getDay();
        end.setDate(end.getDate() + (6 - dayOfWeek));
        end.setHours(23, 59, 59, 999);
        break;
      case 'month':
        end.setMonth(end.getMonth() + 1, 0);
        end.setHours(23, 59, 59, 999);
        break;
      default:
        break;
    }
    
    return end;
  };

  const handleShiftClick = (shift) => {
    setSelectedShift(shift);
    setIsModalOpen(true);
  };

  const handleShiftDoubleClick = (shift) => {
    // Quick edit mode or navigate to timesheet
    window.open(`/timesheet/${shift.id}`, '_blank');
  };

  // Bulk operation handlers
  const handleBulkAssign = (shifts, worker) => {
    logInfo('EnhancedScheduleView', 'Bulk assigning worker to shifts', {
      workerId: worker.id,
      shiftCount: shifts.length
    });

    shifts.forEach(shift => {
      assignWorkerToShift(shift.id, worker);
    });

    setSelectedShifts([]);
  };

  const handleBulkUnassign = (shifts) => {
    logInfo('EnhancedScheduleView', 'Bulk unassigning workers from shifts', {
      shiftCount: shifts.length
    });

    shifts.forEach(shift => {
      if (shift.assigned_workers) {
        shift.assigned_workers.forEach(worker => {
          unassignWorkerFromShift(shift.id, worker.id);
        });
      }
    });

    setSelectedShifts([]);
  };

  const handleBulkDelete = (shifts) => {
    logInfo('EnhancedScheduleView', 'Bulk deleting shifts', {
      shiftCount: shifts.length
    });

    shifts.forEach(shift => {
      deleteShift(shift.id);
    });

    setSelectedShifts([]);
  };

  const handleBulkCopy = (shifts, targetDate) => {
    logInfo('EnhancedScheduleView', 'Bulk copying shifts', {
      shiftCount: shifts.length,
      targetDate: targetDate.toISOString()
    });

    // Implementation would copy shifts to target date
    setSelectedShifts([]);
  };

  const handleBulkMove = (shifts, targetDate) => {
    logInfo('EnhancedScheduleView', 'Bulk moving shifts', {
      shiftCount: shifts.length,
      targetDate: targetDate.toISOString()
    });

    // Implementation would move shifts to target date
    setSelectedShifts([]);
  };

  const handleCreateTemplate = (shifts, templateName) => {
    logInfo('EnhancedScheduleView', 'Creating template from shifts', {
      templateName,
      shiftCount: shifts.length
    });

    // Implementation would create a reusable template from selected shifts
    setSelectedShifts([]);
  };

  return (
    <div className="enhanced-schedule-view">
      <ScheduleToolbar
        currentView={currentView}
        currentDate={currentDate}
        onViewChange={setCurrentView}
        onNavigate={navigateDate}
        onToday={goToToday}
        onCreateShift={() => setIsModalOpen(true)}
        onToggleWorkerPanel={() => setIsWorkerPanelOpen(!isWorkerPanelOpen)}
        isWorkerPanelOpen={isWorkerPanelOpen}
      />

      <ScheduleFilters
        filters={filters}
        onFiltersChange={setFilters}
        jobs={jobs}
        clients={clientCompanies}
        workers={workers}
      />

      {error && (
        <div className="schedule-error">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      <div className="schedule-content">
        {isWorkerPanelOpen && (
          <WorkerPanel
            workers={workers}
            onWorkerDragStart={handleWorkerDragStart}
            onWorkerDragEnd={handleWorkerDragEnd}
            filters={filters}
          />
        )}

        <div className="calendar-container">
          <CalendarView
            view={currentView}
            currentDate={currentDate}
            shifts={shifts}
            workers={workers}
            workplaceSettings={workplaceSettings}
            draggedWorker={draggedWorker}
            onShiftClick={handleShiftClick}
            onShiftDoubleClick={handleShiftDoubleClick}
            onShiftDrop={handleShiftDrop}
            onCreateShift={createShift}
            isLoading={isLoading}
          />
        </div>
      </div>

      {/* Bulk Operations Panel */}
      <BulkOperationsPanel
        selectedShifts={selectedShifts}
        onClearSelection={() => setSelectedShifts([])}
        onBulkAssign={handleBulkAssign}
        onBulkUnassign={handleBulkUnassign}
        onBulkDelete={handleBulkDelete}
        onBulkCopy={handleBulkCopy}
        onBulkMove={handleBulkMove}
        onCreateTemplate={handleCreateTemplate}
        workers={workers}
        isVisible={isBulkMode && selectedShifts.length > 0}
      />

      {isModalOpen && (
        <ShiftDetailsModal
          shift={selectedShift}
          workers={workers}
          jobs={jobs}
          clients={clientCompanies}
          onClose={() => {
            setIsModalOpen(false);
            setSelectedShift(null);
          }}
          onSave={selectedShift ? updateShift : createShift}
          onDelete={selectedShift ? deleteShift : null}
          onAssignWorker={assignWorkerToShift}
          onUnassignWorker={unassignWorkerFromShift}
        />
      )}
    </div>
  );
};

export default EnhancedScheduleView;
