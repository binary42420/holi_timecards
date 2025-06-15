import React, { useMemo } from 'react';
import ShiftCard from '../ShiftCard';
import TimeSlot from '../TimeSlot';
import './DayView.css';

const DayView = ({
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
  // Generate time slots (24-hour format)
  const timeSlots = useMemo(() => {
    const slots = [];
    for (let hour = 0; hour < 24; hour++) {
      slots.push({
        hour,
        display: workplaceSettings?.use_24_hour_format 
          ? `${hour.toString().padStart(2, '0')}:00`
          : `${hour === 0 ? 12 : hour > 12 ? hour - 12 : hour}:00 ${hour < 12 ? 'AM' : 'PM'}`
      });
    }
    return slots;
  }, [workplaceSettings]);

  // Filter shifts for current day
  const dayShifts = useMemo(() => {
    const dayKey = currentDate.toDateString();
    return shifts.filter(shift => {
      const shiftDate = new Date(shift.shift_start_datetime || shift.shiftDate);
      return shiftDate.toDateString() === dayKey;
    });
  }, [shifts, currentDate]);

  // Group shifts by hour
  const shiftsByHour = useMemo(() => {
    const grouped = {};
    
    dayShifts.forEach(shift => {
      const shiftDate = new Date(shift.shift_start_datetime || shift.shiftDate);
      const hour = shiftDate.getHours();
      
      if (!grouped[hour]) {
        grouped[hour] = [];
      }
      grouped[hour].push(shift);
    });
    
    return grouped;
  }, [dayShifts]);

  const handleTimeSlotClick = (hour) => {
    const shiftStart = new Date(currentDate);
    shiftStart.setHours(hour, 0, 0, 0);
    
    const shiftEnd = new Date(shiftStart);
    shiftEnd.setHours(hour + 4, 0, 0, 0); // Default 4-hour shift
    
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

  const handleShiftDrop = (hour, worker) => {
    const shiftsAtTime = shiftsByHour[hour] || [];
    
    if (shiftsAtTime.length > 0) {
      // Drop on existing shift
      onShiftDrop(shiftsAtTime[0].id, worker);
    } else {
      // Create new shift and assign worker
      const shiftStart = new Date(currentDate);
      shiftStart.setHours(hour, 0, 0, 0);
      
      const shiftEnd = new Date(shiftStart);
      shiftEnd.setHours(hour + 4, 0, 0, 0);
      
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

  const getShiftDuration = (shift) => {
    if (shift.shift_start_datetime && shift.shift_end_datetime) {
      const start = new Date(shift.shift_start_datetime);
      const end = new Date(shift.shift_end_datetime);
      return (end - start) / (1000 * 60 * 60); // Hours
    }
    return 4; // Default duration
  };

  const getShiftPosition = (shift) => {
    const duration = getShiftDuration(shift);
    return {
      height: `${duration * 80}px`, // 80px per hour for day view
      minHeight: '60px'
    };
  };

  return (
    <div className="day-view">
      <div className="day-header">
        <h2 className="day-title">
          {currentDate.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          })}
        </h2>
        
        <div className="day-stats">
          <div className="stat-item">
            <span className="stat-value">{dayShifts.length}</span>
            <span className="stat-label">Shifts</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">
              {dayShifts.reduce((total, shift) => total + (shift.assigned_workers?.length || 0), 0)}
            </span>
            <span className="stat-label">Workers</span>
          </div>
        </div>
      </div>

      <div className="day-grid">
        <div className="time-column">
          {timeSlots.map(slot => (
            <div key={slot.hour} className="time-slot-label">
              {slot.display}
            </div>
          ))}
        </div>

        <div className="shifts-column">
          {timeSlots.map(slot => {
            const shiftsAtTime = shiftsByHour[slot.hour] || [];
            
            return (
              <TimeSlot
                key={slot.hour}
                date={currentDate}
                hour={slot.hour}
                shifts={shiftsAtTime}
                draggedWorker={draggedWorker}
                onClick={() => handleTimeSlotClick(slot.hour)}
                onDrop={(worker) => handleShiftDrop(slot.hour, worker)}
                className="day-time-slot"
              >
                {shiftsAtTime.map(shift => (
                  <ShiftCard
                    key={shift.id}
                    shift={shift}
                    workers={workers}
                    style={getShiftPosition(shift)}
                    onClick={() => onShiftClick(shift)}
                    onDoubleClick={() => onShiftDoubleClick(shift)}
                    compact={false}
                  />
                ))}
              </TimeSlot>
            );
          })}
        </div>
      </div>

      <div className="day-summary">
        <h3>Day Summary</h3>
        <div className="summary-stats">
          <div className="summary-item">
            <span className="summary-label">Total Shifts:</span>
            <span className="summary-value">{dayShifts.length}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Total Workers:</span>
            <span className="summary-value">
              {dayShifts.reduce((total, shift) => total + (shift.assigned_workers?.length || 0), 0)}
            </span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Understaffed Shifts:</span>
            <span className="summary-value">
              {dayShifts.filter(shift => {
                const required = Object.values(shift.role_requirements || {}).reduce((sum, count) => sum + count, 0);
                const assigned = shift.assigned_workers?.length || 0;
                return assigned < required;
              }).length}
            </span>
          </div>
        </div>
      </div>

      <div className="day-instructions">
        <p><strong>💡 Day View Tips:</strong></p>
        <ul>
          <li>Click on time slots to create new shifts</li>
          <li>Drag workers to assign them to specific times</li>
          <li>Shifts show detailed information and staffing status</li>
          <li>Double-click shifts to open timesheet management</li>
        </ul>
      </div>
    </div>
  );
};

export default DayView;
