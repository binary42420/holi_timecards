import React, { useMemo } from 'react';
import './MonthView.css';

const MonthView = ({
  currentDate,
  shifts,
  workers,
  workplaceSettings,
  draggedWorker,
  onShiftClick,
  onShiftDoubleClick,
  onShiftDrop,
  onCreateShift
}) => {
  // Generate calendar days for the month
  const calendarDays = useMemo(() => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    // First day of the month
    const firstDay = new Date(year, month, 1);
    // Last day of the month
    const lastDay = new Date(year, month + 1, 0);
    
    // Start from Sunday of the week containing the first day
    const startDate = new Date(firstDay);
    startDate.setDate(firstDay.getDate() - firstDay.getDay());
    
    // End on Saturday of the week containing the last day
    const endDate = new Date(lastDay);
    endDate.setDate(lastDay.getDate() + (6 - lastDay.getDay()));
    
    const days = [];
    const currentDay = new Date(startDate);
    
    while (currentDay <= endDate) {
      days.push(new Date(currentDay));
      currentDay.setDate(currentDay.getDate() + 1);
    }
    
    return days;
  }, [currentDate]);

  // Group shifts by date
  const shiftsByDate = useMemo(() => {
    const grouped = {};
    
    shifts.forEach(shift => {
      const shiftDate = new Date(shift.shift_start_datetime || shift.shiftDate);
      const dateKey = shiftDate.toDateString();
      
      if (!grouped[dateKey]) {
        grouped[dateKey] = [];
      }
      grouped[dateKey].push(shift);
    });
    
    return grouped;
  }, [shifts]);

  const handleDayClick = (date) => {
    const shiftStart = new Date(date);
    shiftStart.setHours(9, 0, 0, 0); // Default to 9 AM
    
    const shiftEnd = new Date(shiftStart);
    shiftEnd.setHours(17, 0, 0, 0); // Default to 5 PM (8-hour shift)
    
    onCreateShift({
      shift_start_datetime: shiftStart.toISOString(),
      shift_end_datetime: shiftEnd.toISOString(),
      job_id: null,
      role_requirements: {
        stagehand: 1,
        crew_chief: 0,
        forklift_operator: 0,
        truck_driver: 0
      }
    });
  };

  const handleDayDrop = (date, worker) => {
    const dateKey = date.toDateString();
    const dayShifts = shiftsByDate[dateKey] || [];
    
    if (dayShifts.length > 0) {
      // Drop on existing shift (use first shift of the day)
      onShiftDrop(dayShifts[0].id, worker);
    } else {
      // Create new shift and assign worker
      const shiftStart = new Date(date);
      shiftStart.setHours(9, 0, 0, 0);
      
      const shiftEnd = new Date(shiftStart);
      shiftEnd.setHours(17, 0, 0, 0);
      
      onCreateShift({
        shift_start_datetime: shiftStart.toISOString(),
        shift_end_datetime: shiftEnd.toISOString(),
        job_id: null,
        role_requirements: {
          [worker.employee_type || 'stagehand']: 1
        },
        auto_assign_worker: {
          worker_id: worker.id,
          role: worker.employee_type || 'stagehand'
        }
      });
    }
  };

  const getDayStats = (date) => {
    const dateKey = date.toDateString();
    const dayShifts = shiftsByDate[dateKey] || [];
    
    const totalShifts = dayShifts.length;
    const totalWorkers = dayShifts.reduce((total, shift) => total + (shift.assigned_workers?.length || 0), 0);
    
    const understaffed = dayShifts.filter(shift => {
      const required = Object.values(shift.role_requirements || {}).reduce((sum, count) => sum + count, 0);
      const assigned = shift.assigned_workers?.length || 0;
      return assigned < required;
    }).length;
    
    const unassigned = dayShifts.filter(shift => (shift.assigned_workers?.length || 0) === 0).length;
    
    return { totalShifts, totalWorkers, understaffed, unassigned };
  };

  const getDayClass = (date) => {
    const today = new Date();
    const isToday = date.toDateString() === today.toDateString();
    const isCurrentMonth = date.getMonth() === currentDate.getMonth();
    const stats = getDayStats(date);
    
    let classes = ['calendar-day'];
    
    if (isToday) classes.push('today');
    if (!isCurrentMonth) classes.push('other-month');
    if (stats.totalShifts > 0) classes.push('has-shifts');
    if (stats.understaffed > 0) classes.push('has-understaffed');
    if (stats.unassigned > 0) classes.push('has-unassigned');
    
    return classes.join(' ');
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e, date) => {
    e.preventDefault();
    if (draggedWorker) {
      handleDayDrop(date, draggedWorker);
    }
  };

  const monthName = currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <div className="month-view">
      <div className="month-header">
        <h2 className="month-title">{monthName}</h2>
        
        <div className="month-stats">
          <div className="stat-item">
            <span className="stat-value">{shifts.length}</span>
            <span className="stat-label">Total Shifts</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">
              {shifts.reduce((total, shift) => total + (shift.assigned_workers?.length || 0), 0)}
            </span>
            <span className="stat-label">Total Workers</span>
          </div>
        </div>
      </div>

      <div className="calendar-grid">
        <div className="calendar-header">
          {dayNames.map(dayName => (
            <div key={dayName} className="day-name-header">
              {dayName}
            </div>
          ))}
        </div>

        <div className="calendar-body">
          {calendarDays.map(date => {
            const stats = getDayStats(date);
            const dateKey = date.toDateString();
            const dayShifts = shiftsByDate[dateKey] || [];
            
            return (
              <div
                key={dateKey}
                className={getDayClass(date)}
                onClick={() => handleDayClick(date)}
                onDragOver={handleDragOver}
                onDrop={(e) => handleDrop(e, date)}
              >
                <div className="day-number">
                  {date.getDate()}
                </div>
                
                {stats.totalShifts > 0 && (
                  <div className="day-content">
                    <div className="shift-indicators">
                      {dayShifts.slice(0, 3).map((shift, index) => (
                        <div
                          key={shift.id}
                          className={`shift-indicator ${getShiftStatusClass(shift)}`}
                          onClick={(e) => {
                            e.stopPropagation();
                            onShiftClick(shift);
                          }}
                          title={`${shift.job_name || 'No Job'} - ${shift.assigned_workers?.length || 0} workers`}
                        >
                          {shift.job_name ? shift.job_name.substring(0, 3) : 'Job'}
                        </div>
                      ))}
                      {dayShifts.length > 3 && (
                        <div className="more-shifts">
                          +{dayShifts.length - 3}
                        </div>
                      )}
                    </div>
                    
                    <div className="day-stats">
                      <span className="shifts-count">{stats.totalShifts} shift{stats.totalShifts !== 1 ? 's' : ''}</span>
                      <span className="workers-count">{stats.totalWorkers} worker{stats.totalWorkers !== 1 ? 's' : ''}</span>
                    </div>
                  </div>
                )}
                
                {draggedWorker && (
                  <div className="drop-zone">
                    Drop to assign
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <div className="month-legend">
        <h4>Legend:</h4>
        <div className="legend-items">
          <div className="legend-item">
            <div className="legend-indicator has-shifts"></div>
            <span>Has Shifts</span>
          </div>
          <div className="legend-item">
            <div className="legend-indicator has-understaffed"></div>
            <span>Understaffed</span>
          </div>
          <div className="legend-item">
            <div className="legend-indicator has-unassigned"></div>
            <span>Unassigned</span>
          </div>
          <div className="legend-item">
            <div className="legend-indicator today"></div>
            <span>Today</span>
          </div>
        </div>
      </div>

      <div className="month-instructions">
        <p><strong>💡 Month View Tips:</strong></p>
        <ul>
          <li>Click on days to create new shifts</li>
          <li>Drag workers to days to assign them</li>
          <li>Click on shift indicators to view details</li>
          <li>Color coding shows staffing status</li>
        </ul>
      </div>
    </div>
  );
};

// Helper function to get shift status class
const getShiftStatusClass = (shift) => {
  const required = Object.values(shift.role_requirements || {}).reduce((sum, count) => sum + count, 0);
  const assigned = shift.assigned_workers?.length || 0;
  
  if (assigned === 0) return 'no-workers';
  if (assigned < required) return 'understaffed';
  if (assigned === required) return 'fully-staffed';
  return 'overstaffed';
};

export default MonthView;
