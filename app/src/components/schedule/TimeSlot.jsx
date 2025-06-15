import React, { useState } from 'react';
import './TimeSlot.css';

const TimeSlot = ({
  date,
  hour,
  shifts,
  draggedWorker,
  onClick,
  onDrop,
  className = '',
  children
}) => {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleClick = () => {
    if (onClick) {
      onClick();
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    if (draggedWorker) {
      setIsDragOver(true);
    }
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    
    if (draggedWorker && onDrop) {
      onDrop(draggedWorker);
    }
  };

  const getSlotClass = () => {
    let classes = ['time-slot'];
    
    if (className) {
      classes.push(className);
    }
    
    if (shifts && shifts.length > 0) {
      classes.push('has-shifts');
    } else {
      classes.push('empty-slot');
    }
    
    if (isDragOver) {
      classes.push('drag-over');
    }
    
    if (draggedWorker) {
      classes.push('drop-target');
    }
    
    return classes.join(' ');
  };

  const formatTime = () => {
    if (typeof hour === 'number') {
      const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
      const period = hour < 12 ? 'AM' : 'PM';
      return `${displayHour}:00 ${period}`;
    }
    return '';
  };

  return (
    <div
      className={getSlotClass()}
      onClick={handleClick}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Time label for mobile/compact views */}
      {hour !== undefined && (
        <div className="slot-time-label">
          {formatTime()}
        </div>
      )}
      
      {/* Shift content */}
      <div className="slot-content">
        {children}
      </div>
      
      {/* Empty slot indicator */}
      {(!shifts || shifts.length === 0) && (
        <div className="empty-slot-content">
          {draggedWorker ? (
            <div className="drop-hint">
              <span className="drop-icon">📥</span>
              <span className="drop-text">Drop to assign</span>
            </div>
          ) : (
            <div className="create-hint">
              <span className="create-icon">➕</span>
              <span className="create-text">Click to create shift</span>
            </div>
          )}
        </div>
      )}
      
      {/* Drag overlay */}
      {isDragOver && (
        <div className="drag-overlay">
          <div className="drag-indicator">
            <span className="drag-icon">📥</span>
            <span className="drag-text">Drop here to assign {draggedWorker?.name}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default TimeSlot;
