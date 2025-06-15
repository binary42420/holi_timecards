import React, { useState } from 'react';
import './ScheduleToolbar.css';

const ScheduleToolbar = ({
  currentView,
  currentDate,
  onViewChange,
  onNavigate,
  onToday,
  onCreateShift,
  onToggleWorkerPanel,
  isWorkerPanelOpen,
  onBulkMode,
  isBulkMode,
  onShowAnalytics,
  onShowTemplates,
  onAutoRefresh,
  autoRefresh,
  onExport,
  onImport,
  selectedShiftsCount = 0
}) => {
  const [showExportMenu, setShowExportMenu] = useState(false);
  const formatDateRange = () => {
    switch (currentView) {
      case 'day':
        return currentDate.toLocaleDateString('en-US', {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        });
      
      case 'week':
        const startOfWeek = new Date(currentDate);
        const dayOfWeek = startOfWeek.getDay();
        startOfWeek.setDate(startOfWeek.getDate() - dayOfWeek);
        
        const endOfWeek = new Date(startOfWeek);
        endOfWeek.setDate(startOfWeek.getDate() + 6);
        
        if (startOfWeek.getMonth() === endOfWeek.getMonth()) {
          return `${startOfWeek.toLocaleDateString('en-US', { month: 'long' })} ${startOfWeek.getDate()} - ${endOfWeek.getDate()}, ${startOfWeek.getFullYear()}`;
        } else {
          return `${startOfWeek.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${endOfWeek.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}, ${startOfWeek.getFullYear()}`;
        }
      
      case 'month':
        return currentDate.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long'
        });
      
      default:
        return '';
    }
  };

  const viewButtons = [
    { key: 'day', label: 'Day', icon: '📅' },
    { key: 'week', label: 'Week', icon: '📊' },
    { key: 'month', label: 'Month', icon: '🗓️' }
  ];

  return (
    <div className="schedule-toolbar">
      <div className="toolbar-section toolbar-left">
        <button
          onClick={onToday}
          className="today-button"
        >
          📍 Today
        </button>
        
        <div className="navigation-controls">
          <button
            onClick={() => onNavigate('prev')}
            className="nav-button prev-button"
            title="Previous"
          >
            ◀
          </button>
          
          <div className="date-display">
            {formatDateRange()}
          </div>
          
          <button
            onClick={() => onNavigate('next')}
            className="nav-button next-button"
            title="Next"
          >
            ▶
          </button>
        </div>
      </div>

      <div className="toolbar-section toolbar-center">
        <div className="view-selector">
          {viewButtons.map(button => (
            <button
              key={button.key}
              onClick={() => onViewChange(button.key)}
              className={`view-button ${currentView === button.key ? 'active' : ''}`}
            >
              <span className="view-icon">{button.icon}</span>
              <span className="view-label">{button.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="toolbar-section toolbar-right">
        {/* Bulk Mode Toggle */}
        <button
          onClick={onBulkMode}
          className={`bulk-mode-button ${isBulkMode ? 'active' : ''}`}
          title={isBulkMode ? 'Exit Bulk Mode' : 'Enter Bulk Mode'}
        >
          <span className="bulk-icon">☑️</span>
          <span className="bulk-label">
            {isBulkMode ? `Bulk (${selectedShiftsCount})` : 'Bulk'}
          </span>
        </button>

        {/* Auto Refresh Toggle */}
        <button
          onClick={onAutoRefresh}
          className={`auto-refresh-button ${autoRefresh ? 'active' : ''}`}
          title={autoRefresh ? 'Disable Auto Refresh' : 'Enable Auto Refresh'}
        >
          <span className="refresh-icon">🔄</span>
        </button>

        {/* Analytics Button */}
        <button
          onClick={onShowAnalytics}
          className="analytics-button"
          title="Show Analytics"
        >
          <span className="analytics-icon">📊</span>
          <span className="analytics-label">Analytics</span>
        </button>

        {/* Templates Button */}
        <button
          onClick={onShowTemplates}
          className="templates-button"
          title="Shift Templates"
        >
          <span className="templates-icon">📋</span>
          <span className="templates-label">Templates</span>
        </button>

        {/* Export/Import Menu */}
        <div className="export-menu-container">
          <button
            onClick={() => setShowExportMenu(!showExportMenu)}
            className="export-button"
            title="Export/Import"
          >
            <span className="export-icon">📤</span>
            <span className="export-label">Export</span>
          </button>

          {showExportMenu && (
            <div className="export-dropdown">
              <button onClick={() => { onExport('csv'); setShowExportMenu(false); }}>
                Export CSV
              </button>
              <button onClick={() => { onExport('excel'); setShowExportMenu(false); }}>
                Export Excel
              </button>
              <button onClick={() => { onExport('pdf'); setShowExportMenu(false); }}>
                Export PDF
              </button>
              <hr />
              <button onClick={() => { onImport(); setShowExportMenu(false); }}>
                Import Schedule
              </button>
            </div>
          )}
        </div>

        {/* Worker Panel Toggle */}
        <button
          onClick={onToggleWorkerPanel}
          className={`panel-toggle-button ${isWorkerPanelOpen ? 'active' : ''}`}
          title={isWorkerPanelOpen ? 'Hide Worker Panel' : 'Show Worker Panel'}
        >
          <span className="panel-icon">👥</span>
          <span className="panel-label">
            {isWorkerPanelOpen ? 'Hide Workers' : 'Show Workers'}
          </span>
        </button>

        {/* Create Shift Button */}
        <button
          onClick={onCreateShift}
          className="create-shift-button primary"
        >
          <span className="create-icon">➕</span>
          <span className="create-label">New Shift</span>
        </button>
      </div>
    </div>
  );
};

export default ScheduleToolbar;
