import React, { useState } from 'react';
import JobDetailsModal from './JobDetailsModal';
import ClientEditModal from './ClientEditModal';
import JobEditModal from './JobEditModal';
import './ClientDetailsModal.css';

const ClientDetailsModal = ({ clientDetails, isOpen, onClose, onRefresh }) => {
  const [selectedJob, setSelectedJob] = useState(null);
  const [isJobModalOpen, setIsJobModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isJobEditModalOpen, setIsJobEditModalOpen] = useState(false);
  const [jobToEdit, setJobToEdit] = useState(null);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'jobs', 'users'

  if (!isOpen || !clientDetails) return null;

  const handleJobClick = (job) => {
    setSelectedJob(job);
    setIsJobModalOpen(true);
  };

  const handleCloseJobModal = () => {
    setIsJobModalOpen(false);
    setSelectedJob(null);
  };

  const handleEditJob = (e, job) => {
    e.stopPropagation(); // Prevent opening the job details modal
    setJobToEdit(job);
    setIsJobEditModalOpen(true);
  };

  const handleCloseJobEditModal = () => {
    setIsJobEditModalOpen(false);
    setJobToEdit(null);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const getNextUpcomingShift = (job) => {
    if (!job.shifts || job.shifts.length === 0) return null;
    const now = new Date();
    const upcomingShifts = job.shifts
      .filter(shift => new Date(shift.start_time) > now)
      .sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
    return upcomingShifts.length > 0 ? upcomingShifts[0] : null;
  };

  const getMostRecentCompletedShift = (job) => {
    if (!job.shifts || job.shifts.length === 0) return null;
    const now = new Date();
    const completedShifts = job.shifts
      .filter(shift => new Date(shift.end_time) < now)
      .sort((a, b) => new Date(b.end_time) - new Date(a.end_time));
    return completedShifts.length > 0 ? completedShifts[0] : null;
  };

  const getUnassignedShiftsForNextShift = (job) => {
    const nextShift = getNextUpcomingShift(job);
    if (!nextShift) return { cc: 0, sh: 0, fo: 0 };

    // Count unassigned positions for the next shift
    const unassigned = {
      cc: Math.max(0, (nextShift.crew_chief_needed || 0) - (nextShift.crew_chief_assigned || 0)),
      sh: Math.max(0, (nextShift.stage_hands_needed || 0) - (nextShift.stage_hands_assigned || 0)),
      fo: Math.max(0, (nextShift.forklift_operators_needed || 0) - (nextShift.forklift_operators_assigned || 0))
    };

    return unassigned;
  };



  const getJobStatusBadge = (job) => {
    if (job.is_active) {
      return <span className="status-badge active">Active</span>;
    } else {
      return <span className="status-badge completed">Completed</span>;
    }
  };

  const getUserStatusBadge = (user) => {
    if (user.isActive && user.isApproval) {
      return <span className="status-badge active">Active</span>;
    } else if (user.isActive && !user.isApproval) {
      return <span className="status-badge pending">Pending Approval</span>;
    } else {
      return <span className="status-badge inactive">Inactive</span>;
    }
  };

  return (
    <>
      <div className="modal-overlay" onClick={onClose}>
        <div className="client-details-modal" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <div className="header-content">
              <h2>{clientDetails.name}</h2>
              <p className="company-id">Client ID: {clientDetails.id}</p>
            </div>
            <div className="header-actions">
              <button
                className="edit-button"
                onClick={() => setIsEditModalOpen(true)}
                title="Edit Client Details"
              >
                ✏️ Edit
              </button>
              <button className="close-button" onClick={onClose}>×</button>
            </div>
          </div>

          <div className="modal-tabs">
            <button 
              className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              📊 Overview
            </button>
            <button 
              className={`tab-button ${activeTab === 'jobs' ? 'active' : ''}`}
              onClick={() => setActiveTab('jobs')}
            >
              💼 Jobs ({clientDetails.jobs?.length || 0})
            </button>
            <button 
              className={`tab-button ${activeTab === 'users' ? 'active' : ''}`}
              onClick={() => setActiveTab('users')}
            >
              👥 Users ({clientDetails.users?.length || 0})
            </button>
          </div>

          <div className="modal-content">
            {activeTab === 'overview' && (
              <div className="overview-tab">
                <div className="company-info-section">
                  <h3>Company Information</h3>
                  <div className="info-grid">
                    <div className="info-item">
                      <label>Email:</label>
                      <span>{clientDetails.contact_email || 'Not provided'}</span>
                    </div>
                    <div className="info-item">
                      <label>Phone:</label>
                      <span>{clientDetails.contact_phone || 'Not provided'}</span>
                    </div>
                    <div className="info-item">
                      <label>Address:</label>
                      <span>{clientDetails.address || 'Not provided'}</span>
                    </div>
                    <div className="info-item">
                      <label>Status:</label>
                      <span className={`status-badge ${clientDetails.is_active ? 'active' : 'inactive'}`}>
                        {clientDetails.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="statistics-section">
                  <h3>Statistics</h3>
                  <div className="stats-grid">
                    <div className="stat-card">
                      <div className="stat-number">{clientDetails.statistics?.total_jobs || 0}</div>
                      <div className="stat-label">Total Jobs</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-number">{clientDetails.statistics?.active_jobs || 0}</div>
                      <div className="stat-label">Active Jobs</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-number">{clientDetails.statistics?.completed_jobs || 0}</div>
                      <div className="stat-label">Completed Jobs</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-number">{clientDetails.statistics?.total_users || 0}</div>
                      <div className="stat-label">Total Users</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-number">{clientDetails.statistics?.active_users || 0}</div>
                      <div className="stat-label">Active Users</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-number">{clientDetails.statistics?.recent_jobs_30_days || 0}</div>
                      <div className="stat-label">Recent Jobs (30 days)</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'jobs' && (
              <div className="jobs-tab">
                <div className="jobs-header">
                  <h3>All Jobs</h3>
                  <p>Click on any job to view details and assigned workers</p>
                </div>
                
                {clientDetails.jobs && clientDetails.jobs.length > 0 ? (
                  <div className="jobs-list">
                    {clientDetails.jobs.map((job) => (
                      <div 
                        key={job.id} 
                        className="job-item"
                        onClick={() => handleJobClick(job)}
                      >
                        <div className="job-header">
                          <div className="job-info">
                            <h4 className="job-name">{job.name}</h4>
                            <p className="job-venue">{job.venue_name}</p>
                          </div>
                          <div className="job-actions">
                            <button
                              className="edit-job-button"
                              onClick={(e) => handleEditJob(e, job)}
                              title="Edit Job"
                            >
                              ✏️
                            </button>
                            <div className="job-status">
                              {getJobStatusBadge(job)}
                            </div>
                          </div>
                        </div>
                        
                        <div className="job-details">
                          <div className="job-meta">
                            <span className="job-address">{job.venue_address}</span>
                            <span className="job-dates">
                              {formatDate(job.estimated_start_date)} - {formatDate(job.estimated_end_date)}
                            </span>
                          </div>
                          
                          {job.description && (
                            <p className="job-description">{job.description}</p>
                          )}
                          
                          <div className="job-stats">
                            <span className="shift-count">
                              # of shifts: {job.shift_count || 0}
                            </span>
                            <span className="created-date">
                              Created: {formatDate(job.created_at)}
                            </span>
                          </div>

                          <div className="job-shift-details">
                            {(() => {
                              const nextShift = getNextUpcomingShift(job);
                              const recentShift = getMostRecentCompletedShift(job);
                              const unassigned = getUnassignedShiftsForNextShift(job);

                              return (
                                <>
                                  <div className="shift-info">
                                    <span className="next-shift">
                                      Next Upcoming Shift: {nextShift ? formatDateTime(nextShift.start_time) : 'None scheduled'}
                                    </span>
                                    <span className="recent-shift">
                                      Most Recent Completed Shift: {recentShift ? formatDateTime(recentShift.end_time) : 'None completed'}
                                    </span>
                                  </div>

                                  {nextShift && (unassigned.cc > 0 || unassigned.sh > 0 || unassigned.fo > 0) && (
                                    <div className="unassigned-positions">
                                      <span className="unassigned-label">Unassigned positions to fill:</span>
                                      <span className="unassigned-counts">
                                        {unassigned.cc > 0 && `${unassigned.cc} CC`}
                                        {unassigned.cc > 0 && (unassigned.sh > 0 || unassigned.fo > 0) && ', '}
                                        {unassigned.sh > 0 && `${unassigned.sh} SH`}
                                        {unassigned.sh > 0 && unassigned.fo > 0 && ', '}
                                        {unassigned.fo > 0 && `${unassigned.fo} FO`}
                                      </span>
                                    </div>
                                  )}
                                </>
                              );
                            })()}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">
                    <p>No jobs found for this client.</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'users' && (
              <div className="users-tab">
                <div className="users-header">
                  <h3>Client Users</h3>
                  <p>All users associated with this client company</p>
                </div>
                
                {clientDetails.users && clientDetails.users.length > 0 ? (
                  <div className="users-list">
                    {clientDetails.users.map((user) => (
                      <div key={user.id} className="user-item">
                        <div className="user-info">
                          <div className="user-details">
                            <h4 className="user-name">{user.name}</h4>
                            <p className="user-email">{user.email}</p>
                            <p className="user-username">@{user.username}</p>
                          </div>
                          <div className="user-status">
                            {getUserStatusBadge(user)}
                          </div>
                        </div>
                        
                        <div className="user-meta">
                          <div className="user-stats">
                            <span className="last-login">
                              Last login: {formatDateTime(user.last_login)}
                            </span>
                            <span className="created-date">
                              Joined: {formatDate(user.created_at)}
                            </span>
                          </div>
                          
                          {user.google_id && (
                            <div className="google-integration">
                              <span className="google-badge">🔗 Google Account</span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">
                    <p>No users found for this client.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {isJobModalOpen && selectedJob && (
        <JobDetailsModal
          job={selectedJob}
          isOpen={isJobModalOpen}
          onClose={handleCloseJobModal}
        />
      )}

      {isEditModalOpen && (
        <ClientEditModal
          client={clientDetails}
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          onSave={() => {
            setIsEditModalOpen(false);
            if (onRefresh) onRefresh();
          }}
        />
      )}

      {isJobEditModalOpen && jobToEdit && (
        <JobEditModal
          job={jobToEdit}
          isOpen={isJobEditModalOpen}
          onClose={handleCloseJobEditModal}
          onSave={() => {
            handleCloseJobEditModal();
            if (onRefresh) onRefresh();
          }}
        />
      )}
    </>
  );
};

export default ClientDetailsModal;
