import React, { useState, useEffect, useMemo } from 'react';
import { logDebug, logError, logInfo } from '../../utils';
import './ScheduleAnalytics.css';

const ScheduleAnalytics = ({
  shifts,
  workers,
  jobs,
  dateRange,
  isOpen,
  onClose
}) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedMetric, setSelectedMetric] = useState('utilization');

  // Calculate analytics data
  const analytics = useMemo(() => {
    if (!shifts || shifts.length === 0) {
      return {
        overview: {},
        utilization: {},
        costs: {},
        performance: {},
        trends: {}
      };
    }

    // Overview metrics
    const totalShifts = shifts.length;
    const assignedShifts = shifts.filter(s => s.assigned_workers?.length > 0).length;
    const totalHours = shifts.reduce((sum, s) => sum + (s.duration_hours || 0), 0);
    const totalWorkers = new Set(
      shifts.flatMap(s => s.assigned_workers?.map(w => w.id) || [])
    ).size;

    // Utilization metrics
    const workerUtilization = workers.map(worker => {
      const workerShifts = shifts.filter(s => 
        s.assigned_workers?.some(w => w.id === worker.id)
      );
      const workerHours = workerShifts.reduce((sum, s) => sum + (s.duration_hours || 0), 0);
      const maxPossibleHours = dateRange ? 
        Math.ceil((dateRange.end - dateRange.start) / (1000 * 60 * 60 * 24)) * 8 : 40;
      
      return {
        ...worker,
        assignedShifts: workerShifts.length,
        totalHours: workerHours,
        utilization: maxPossibleHours > 0 ? (workerHours / maxPossibleHours) * 100 : 0
      };
    });

    // Job distribution
    const jobDistribution = jobs.map(job => {
      const jobShifts = shifts.filter(s => s.job_id === job.id);
      const jobHours = jobShifts.reduce((sum, s) => sum + (s.duration_hours || 0), 0);
      
      return {
        ...job,
        shiftCount: jobShifts.length,
        totalHours: jobHours,
        percentage: totalHours > 0 ? (jobHours / totalHours) * 100 : 0
      };
    }).sort((a, b) => b.totalHours - a.totalHours);

    // Cost analysis (estimated)
    const estimatedCosts = shifts.reduce((costs, shift) => {
      const shiftCost = (shift.assigned_workers?.length || 0) * (shift.duration_hours || 0) * 25; // $25/hour estimate
      return costs + shiftCost;
    }, 0);

    // Understaffed/Overstaffed analysis
    const staffingAnalysis = shifts.map(shift => {
      const required = shift.required_workers || 1;
      const assigned = shift.assigned_workers?.length || 0;
      const status = assigned < required ? 'understaffed' : 
                    assigned > required ? 'overstaffed' : 'optimal';
      
      return {
        ...shift,
        staffingStatus: status,
        staffingDifference: assigned - required
      };
    });

    const understaffedShifts = staffingAnalysis.filter(s => s.staffingStatus === 'understaffed');
    const overstaffedShifts = staffingAnalysis.filter(s => s.staffingStatus === 'overstaffed');

    return {
      overview: {
        totalShifts,
        assignedShifts,
        unassignedShifts: totalShifts - assignedShifts,
        totalHours,
        totalWorkers,
        averageShiftLength: totalShifts > 0 ? totalHours / totalShifts : 0,
        assignmentRate: totalShifts > 0 ? (assignedShifts / totalShifts) * 100 : 0
      },
      utilization: {
        workerUtilization: workerUtilization.sort((a, b) => b.utilization - a.utilization),
        averageUtilization: workerUtilization.length > 0 ? 
          workerUtilization.reduce((sum, w) => sum + w.utilization, 0) / workerUtilization.length : 0
      },
      distribution: {
        jobDistribution,
        staffingAnalysis: {
          understaffedShifts,
          overstaffedShifts,
          optimalShifts: staffingAnalysis.filter(s => s.staffingStatus === 'optimal')
        }
      },
      costs: {
        estimatedTotal: estimatedCosts,
        averagePerShift: totalShifts > 0 ? estimatedCosts / totalShifts : 0,
        averagePerHour: totalHours > 0 ? estimatedCosts / totalHours : 0
      }
    };
  }, [shifts, workers, jobs, dateRange]);

  const renderOverview = () => (
    <div className="analytics-section">
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-value">{analytics.overview.totalShifts}</div>
          <div className="metric-label">Total Shifts</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{analytics.overview.assignedShifts}</div>
          <div className="metric-label">Assigned Shifts</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{analytics.overview.totalHours.toFixed(1)}h</div>
          <div className="metric-label">Total Hours</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{analytics.overview.totalWorkers}</div>
          <div className="metric-label">Active Workers</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{analytics.overview.assignmentRate.toFixed(1)}%</div>
          <div className="metric-label">Assignment Rate</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{analytics.overview.averageShiftLength.toFixed(1)}h</div>
          <div className="metric-label">Avg Shift Length</div>
        </div>
      </div>

      <div className="charts-section">
        <div className="chart-container">
          <h4>Shift Status Distribution</h4>
          <div className="pie-chart-placeholder">
            <div className="chart-segment assigned" 
                 style={{width: `${analytics.overview.assignmentRate}%`}}>
              Assigned ({analytics.overview.assignedShifts})
            </div>
            <div className="chart-segment unassigned" 
                 style={{width: `${100 - analytics.overview.assignmentRate}%`}}>
              Unassigned ({analytics.overview.unassignedShifts})
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderUtilization = () => (
    <div className="analytics-section">
      <div className="section-header">
        <h4>Worker Utilization</h4>
        <div className="avg-utilization">
          Average: {analytics.utilization.averageUtilization.toFixed(1)}%
        </div>
      </div>

      <div className="utilization-list">
        {analytics.utilization.workerUtilization.map(worker => (
          <div key={worker.id} className="utilization-item">
            <div className="worker-info">
              <span className="worker-name">{worker.name}</span>
              <span className="worker-role">{worker.role}</span>
            </div>
            <div className="utilization-bar">
              <div 
                className="utilization-fill"
                style={{
                  width: `${Math.min(worker.utilization, 100)}%`,
                  backgroundColor: worker.utilization > 80 ? '#28a745' : 
                                  worker.utilization > 50 ? '#ffc107' : '#dc3545'
                }}
              />
              <span className="utilization-text">
                {worker.utilization.toFixed(1)}% ({worker.totalHours}h)
              </span>
            </div>
            <div className="shift-count">
              {worker.assignedShifts} shifts
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderDistribution = () => (
    <div className="analytics-section">
      <div className="distribution-grid">
        <div className="distribution-section">
          <h4>Job Distribution</h4>
          <div className="job-list">
            {analytics.distribution.jobDistribution.slice(0, 10).map(job => (
              <div key={job.id} className="job-item">
                <div className="job-info">
                  <span className="job-title">{job.title}</span>
                  <span className="job-client">{job.client_company}</span>
                </div>
                <div className="job-stats">
                  <span className="job-hours">{job.totalHours}h</span>
                  <span className="job-percentage">({job.percentage.toFixed(1)}%)</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="distribution-section">
          <h4>Staffing Analysis</h4>
          <div className="staffing-summary">
            <div className="staffing-item optimal">
              <span className="staffing-label">Optimal</span>
              <span className="staffing-count">
                {analytics.distribution.staffingAnalysis.optimalShifts.length}
              </span>
            </div>
            <div className="staffing-item understaffed">
              <span className="staffing-label">Understaffed</span>
              <span className="staffing-count">
                {analytics.distribution.staffingAnalysis.understaffedShifts.length}
              </span>
            </div>
            <div className="staffing-item overstaffed">
              <span className="staffing-label">Overstaffed</span>
              <span className="staffing-count">
                {analytics.distribution.staffingAnalysis.overstaffedShifts.length}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCosts = () => (
    <div className="analytics-section">
      <div className="cost-metrics">
        <div className="cost-card">
          <div className="cost-value">${analytics.costs.estimatedTotal.toLocaleString()}</div>
          <div className="cost-label">Estimated Total Cost</div>
        </div>
        <div className="cost-card">
          <div className="cost-value">${analytics.costs.averagePerShift.toFixed(2)}</div>
          <div className="cost-label">Average per Shift</div>
        </div>
        <div className="cost-card">
          <div className="cost-value">${analytics.costs.averagePerHour.toFixed(2)}</div>
          <div className="cost-label">Average per Hour</div>
        </div>
      </div>

      <div className="cost-note">
        <p>* Cost estimates based on $25/hour average rate. Actual costs may vary based on worker rates, overtime, and other factors.</p>
      </div>
    </div>
  );

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="schedule-analytics-modal">
        <div className="modal-header">
          <h2>Schedule Analytics</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="analytics-tabs">
          <button 
            className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button 
            className={`tab-btn ${activeTab === 'utilization' ? 'active' : ''}`}
            onClick={() => setActiveTab('utilization')}
          >
            Utilization
          </button>
          <button 
            className={`tab-btn ${activeTab === 'distribution' ? 'active' : ''}`}
            onClick={() => setActiveTab('distribution')}
          >
            Distribution
          </button>
          <button 
            className={`tab-btn ${activeTab === 'costs' ? 'active' : ''}`}
            onClick={() => setActiveTab('costs')}
          >
            Costs
          </button>
        </div>

        <div className="analytics-content">
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'utilization' && renderUtilization()}
          {activeTab === 'distribution' && renderDistribution()}
          {activeTab === 'costs' && renderCosts()}
        </div>
      </div>
    </div>
  );
};

export default ScheduleAnalytics;
