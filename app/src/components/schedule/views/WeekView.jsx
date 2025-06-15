import React, { useState, useMemo } from 'react';
import ShiftCard from '../ShiftCard';
import TimeSlot from '../TimeSlot';
import './WeekView.css';

const WeekView = ({
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
  const [selectedTimeSlot, setSelectedTimeSlot] = useState(null);

  // Generate week dates
  const weekDates = useMemo(() => {
    const dates = [];
    const startOfWeek = new Date(currentDate);
    const dayOfWeek = startOfWeek.getDay();
    startOfWeek.setDate(startOfWeek.getDate() - dayOfWeek);

    for (let i = 0; i < 7; i++) {
      const date = new Date(startOfWeek);
      date.setDate(startOfWeek.getDate() + i);
      dates.push(date);
    }
    return dates;
  }, [currentDate]);

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

  // Group shifts by date and time
  const shiftsByDateTime = useMemo(() => {
    const grouped = {};
    
    shifts.forEach(shift => {
      const shiftDate = new Date(shift.shift_start_datetime || shift.shiftDate);
      const dateKey = shiftDate.toDateString();
      const hour = shiftDate.getHours();
      
      if (!grouped[dateKey]) {
        grouped[dateKey] = {};
      }
      if (!grouped[dateKey][hour]) {
        grouped[dateKey][hour] = [];
      }
      
      grouped[dateKey][hour].push(shift);
    });
    
    return grouped;
  }, [shifts]);

  const handleTimeSlotClick = (date, hour) => {
    const clickedSlot = { date, hour };
    setSelectedTimeSlot(clickedSlot);
    
    // Create new shift at this time
    const shiftStart = new Date(date);
    shiftStart.setHours(hour, 0, 0, 0);
    
    const shiftEnd = new Date(shiftStart);
    shiftEnd.setHours(hour + 4, 0, 0, 0); // Default 4-hour shift
    
    onCreateShift({
      shift_start_datetime: shiftStart.toISOString(),
      shift_end_datetime: shiftEnd.toISOString(),
      job_id: null, // Will be set in modal
      role_requirements: {
        stagehand: 1,
        crew_chief: 0,
        forklift_operator: 0,
        truck_driver: 0
      }
    });
  };

  const handleShiftDrop = (date, hour, worker) => {
    // Find shift at this time slot
    const dateKey = date.toDateString();
    const shiftsAtTime = shiftsByDateTime[dateKey]?.[hour] || [];
    
    if (shiftsAtTime.length > 0) {
      // Drop on existing shift
      onShiftDrop(shiftsAtTime[0].id, worker);
    } else {
      // Create new shift and assign worker
      const shiftStart = new Date(date);
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
      height: `${duration * 60}px`, // 60px per hour
      minHeight: '40px'
    };
  };

  const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  return (
    <div className="week-view">
      <div className="week-header">
        <div className="time-column-header">Time</div>
        {weekDates.map((date, index) => (
          <div key={date.toDateString()} className="day-header">
            <div className="day-name">{dayNames[index]}</div>
            <div className="day-date">
              {date.getDate()}/{date.getMonth() + 1}
            </div>
          </div>
        ))}
      </div>

      <div className="week-grid">
        <div className="time-column">
          {timeSlots.map(slot => (
            <div key={slot.hour} className="time-slot-label">
              {slot.display}
            </div>
          ))}
        </div>

        {weekDates.map(date => (
          <div key={date.toDateString()} className="day-column">
            {timeSlots.map(slot => {
              const dateKey = date.toDateString();
              const shiftsAtTime = shiftsByDateTime[dateKey]?.[slot.hour] || [];
              
              return (
                <TimeSlot
                  key={`${dateKey}-${slot.hour}`}
                  date={date}
                  hour={slot.hour}
                  shifts={shiftsAtTime}
                  draggedWorker={draggedWorker}
                  onClick={() => handleTimeSlotClick(date, slot.hour)}
                  onDrop={(worker) => handleShiftDrop(date, slot.hour, worker)}
                  className={`time-slot ${selectedTimeSlot?.date?.toDateString() === dateKey && selectedTimeSlot?.hour === slot.hour ? 'selected' : ''}`}
                >
                  {shiftsAtTime.map(shift => (
                    <ShiftCard
                      key={shift.id}
                      shift={shift}
                      workers={workers}
                      style={getShiftPosition(shift)}
                      onClick={() => onShiftClick(shift)}
                      onDoubleClick={() => onShiftDoubleClick(shift)}
                      compact={true}
                    />
                  ))}
                </TimeSlot>
              );
            })}
          </div>
        ))}
      </div>

      <div className="week-view-legend">
        <div className="legend-item">
          <div className="legend-color understaffed"></div>
          <span>Understaffed</span>
        </div>
        <div className="legend-item">
          <div className="legend-color fully-staffed"></div>
          <span>Fully Staffed</span>
        </div>
        <div className="legend-item">
          <div className="legend-color overstaffed"></div>
          <span>Overstaffed</span>
        </div>
        <div className="legend-item">
          <div className="legend-color no-workers"></div>
          <span>No Workers</span>
        </div>
      </div>

      <div className="week-view-instructions">
        <p><strong>💡 Tips:</strong></p>
        <ul>
          <li>Click on empty time slots to create new shifts</li>
          <li>Drag workers from the panel to assign them to shifts</li>
          <li>Click on shifts to view details and manage assignments</li>
          <li>Double-click shifts to open timesheet management</li>
        </ul>
      </div>
    </div>
  );
};

export default WeekView;
