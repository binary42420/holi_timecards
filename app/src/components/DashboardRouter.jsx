import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const DashboardRouter = () => {
  const { isAuthenticated, isManager, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px',
        color: '#666'
      }}>
        Loading...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Redirect to appropriate dashboard based on user role
  if (isManager) {
    return <Navigate to="/manager-profile" replace />;
  } else {
    return <Navigate to="/employee-profile" replace />;
  }
};

export default DashboardRouter;
