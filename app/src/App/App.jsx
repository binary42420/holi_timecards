// App.jsx
import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext';
import { GoogleAuthContextProvider } from '../contexts/GoogleAuthContext';
import ProtectedRoute from '../components/ProtectedRoute';
import ErrorBoundary from '../components/ErrorBoundary';
// Import credential fix to ensure correct admin password
import '../utils/fixUserCredentials';
import DashboardRouter from '../components/DashboardRouter';
import Home from '../components/Home';
import Login from '../components/Login';
import SignUp from '../components/SignUp';
import ManagerSchedule from '../components/ManagerSchedule/ManagerSchedule';
import ManagerProfile from '../components/ManagerProfile';
import ManagerSettings from '../components/ManagerSettings';
import ManagerJobDashboard from '../components/ManagerJobDashboard';
import ManagerShiftEditor from '../components/ManagerShiftEditor';
import ManagerClientCompaniesPage from '../components/ManagerClientCompaniesPage';
import EnhancedSettingsPage from '../components/EnhancedSettingsPage';
import ClientDirectory from '../components/clients/ClientDirectory';
import ClientDirectoryDebug from '../components/clients/ClientDirectoryDebug';
import DebugDashboard from '../components/DebugDashboard';
import WebSocketDebugger from '../components/WebSocketDebugger';
import WebSocketTest from '../components/WebSocketTest';
import EnhancedAuthTest from '../components/EnhancedAuthTest';
import SignUpManager from '../components/SignUpManager';
import SignUpEmployee from '../components/SignUpEmployee';
import SignUpClient from '../components/SignUpClient';
import EmployeeProfile from '../components/EmployeeProfile';
import SignInShifts from '../components/SignInShifts';
import ManagerViewShiftsRequests from '../components/ManagerViewShiftsRequests';
import ManagerWorkersList from '../components/ManagerWorkersList';
import ShiftsPage from '../components/ShiftsPage';
import EmployeeListPage from '../components/EmployeeListPage';
import CrewChiefDashboard from '../components/CrewChiefDashboard'; // Import the new component
import CrewShiftTimeEntry from '../components/CrewShiftTimeEntry'; // Import the new component
import ManagerTimesheets from '../components/ManagerTimesheets';
import EnhancedTimesheetManager from '../components/EnhancedTimesheetManager';
import EnhancedScheduleView from '../components/schedule/EnhancedScheduleView';
import ShiftTimecard from '../components/ShiftTimecard';
import ShiftTimesheetEntry from '../components/ShiftTimesheetEntry';
import ScheduleDebugPage from '../components/ScheduleDebugPage';
import GoogleOAuthSetup from '../components/GoogleOAuthSetup';
import TestGoogleSignup from '../components/TestGoogleSignup';
import TrashBin from '../components/TrashBin';
import Toolbar from '../components/Toolbar';
import './App.css';

// Removed problematic import and userSession logic for simplification

function App() {
  return (
    <ErrorBoundary>
      <GoogleAuthContextProvider>
        <AuthProvider>
          <Router>
          <div className="App">
            <Toolbar />
            <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<DashboardRouter />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<SignUp />} />
          <Route path="/manager-schedule" element={<ProtectedRoute requireManager={true}><ManagerSchedule /></ProtectedRoute>} />
          <Route path="/manager-profile" element={<ProtectedRoute requireManager={true}><ManagerProfile /></ProtectedRoute>} />
          <Route path="/manager-settings" element={<ProtectedRoute requireManager={true}><ManagerSettings /></ProtectedRoute>} />
          <Route path="/manager-advanced-settings" element={<ProtectedRoute requireManager={true}><EnhancedSettingsPage /></ProtectedRoute>} />
          <Route path="/manager-jobs" element={<ProtectedRoute requireManager={true}><ManagerJobDashboard /></ProtectedRoute>} />
          <Route path="/manager-jobs/:jobId/shifts" element={<ProtectedRoute requireManager={true}><ManagerShiftEditor /></ProtectedRoute>} />
          <Route path="/shift/:shiftId/timecard" element={<ProtectedRoute requireManager={true}><ShiftTimecard /></ProtectedRoute>} />
          <Route path="/shift/:shiftId/timesheet-entry" element={<ProtectedRoute requireManager={true}><ShiftTimesheetEntry /></ProtectedRoute>} />
          <Route path="/schedule-debug" element={<ProtectedRoute><ScheduleDebugPage /></ProtectedRoute>} />
          <Route path="/manager-clients" element={<ProtectedRoute requireManager={true}><ClientDirectory /></ProtectedRoute>} />
          <Route path="/manager-clients-debug" element={<ProtectedRoute requireManager={true}><ClientDirectoryDebug /></ProtectedRoute>} />
          <Route path="/manager-clients-legacy" element={<ProtectedRoute requireManager={true}><ManagerClientCompaniesPage /></ProtectedRoute>} />
          <Route path="/signupManager" element={<SignUpManager />} />
          <Route path="/signupEmployee" element={<SignUpEmployee />} />
          <Route path="/signupClient" element={<SignUpClient />} />
          <Route path="/employeeProfile" element={<ProtectedRoute><EmployeeProfile /></ProtectedRoute>} />
          <Route path="/employee-profile" element={<ProtectedRoute><EmployeeProfile /></ProtectedRoute>} />
          <Route path="/signInShifts" element={<ProtectedRoute><SignInShifts /></ProtectedRoute>} />
          <Route path="/managerViewShiftsRequests" element={<ProtectedRoute requireManager={true}><ManagerViewShiftsRequests /></ProtectedRoute>} />
          <Route path="/managerWorkersList" element={<ProtectedRoute requireManager={true}><ManagerWorkersList /></ProtectedRoute>} />
          <Route path="/shiftsPage" element={<ProtectedRoute><ShiftsPage /></ProtectedRoute>} />
          <Route path="/employeeListPage" element={<ProtectedRoute requireManager={true}><EmployeeListPage /></ProtectedRoute>} />
          <Route path="/crew-chief-dashboard" element={<ProtectedRoute><CrewChiefDashboard /></ProtectedRoute>} />
          <Route path="/crew-chief/shift/:shiftId/times" element={<ProtectedRoute><CrewShiftTimeEntry /></ProtectedRoute>} />
          <Route path="/manager-timesheets" element={<ProtectedRoute requireManager={true}><ManagerTimesheets /></ProtectedRoute>} />
          <Route path="/timesheet/:shiftId" element={<ProtectedRoute><EnhancedTimesheetManager /></ProtectedRoute>} />
          <Route path="/enhanced-schedule" element={<ProtectedRoute requireManager={true}><EnhancedScheduleView /></ProtectedRoute>} />
          <Route path="/trash-bin" element={<ProtectedRoute requireManager={true}><TrashBin /></ProtectedRoute>} />
          <Route path="/google-oauth-setup" element={<GoogleOAuthSetup />} />
          <Route path="/test-google-signup" element={<TestGoogleSignup />} />
          <Route path="/debug" element={<DebugDashboard />} />
          <Route path="/websocket-debug" element={<WebSocketDebugger />} />
          <Route path="/websocket-test" element={<WebSocketTest />} />
          <Route path="/enhanced-auth-test" element={<EnhancedAuthTest />} />
          <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          </div>
          </Router>
        </AuthProvider>
      </GoogleAuthContextProvider>
    </ErrorBoundary>
  );
}

export default App;
