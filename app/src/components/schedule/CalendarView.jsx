import React from 'react';
import DayView from './views/DayView';
import WeekView from './views/WeekView';
import MonthView from './views/MonthView';
import './CalendarView.css';

const CalendarView = ({
  view,
  currentDate,
  shifts,
  workers,
  workplaceSettings,
  draggedWorker,
  onShiftClick,
  onShiftDoubleClick,
  onShiftDrop,
  onCreateShift,
  isLoading
}) => {
  if (isLoading) {
    return (
      <div className="calendar-loading">
        <div className="loading-spinner"></div>
        <p>Loading schedule...</p>
      </div>
    );
  }

  const commonProps = {
    currentDate,
    shifts,
    workers,
    workplaceSettings,
    draggedWorker,
    onShiftClick,
    onShiftDoubleClick,
    onShiftDrop,
    onCreateShift
  };

  switch (view) {
    case 'day':
      return <DayView {...commonProps} />;
    case 'week':
      return <WeekView {...commonProps} />;
    case 'month':
      return <MonthView {...commonProps} />;
    default:
      return <WeekView {...commonProps} />;
  }
};

export default CalendarView;
