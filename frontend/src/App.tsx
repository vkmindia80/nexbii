import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import ProfilePage from './pages/ProfilePage';
import DashboardPage from './pages/DashboardPage';
import DataSourcesPage from './pages/DataSourcesPage';
import QueriesPage from './pages/QueriesPage';
import DashboardsPage from './pages/DashboardsPage';
import DashboardViewerPage from './pages/DashboardViewerPage';
import DashboardBuilderPage from './pages/DashboardBuilderPage';
import ChartsShowcasePage from './pages/ChartsShowcasePage';
import PublicDashboardPage from './pages/PublicDashboardPage';
import AlertsPage from './pages/AlertsPage';
import ActivityFeedPage from './pages/ActivityFeedPage';
import IntegrationsPage from './pages/IntegrationsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import TenantSettingsPage from './pages/TenantSettingsPage';
import Layout from './components/Layout';
import { useWebSocket } from './hooks/useWebSocket';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const { isConnected } = useWebSocket();

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
    setLoading(false);
  }, []);

  useEffect(() => {
    if (isConnected) {
      console.log('✅ WebSocket connected and ready');
    }
  }, [isConnected]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        <Route path="/login" element={!isAuthenticated ? <LoginPage /> : <Navigate to="/" />} />
        <Route path="/register" element={!isAuthenticated ? <RegisterPage /> : <Navigate to="/" />} />
        <Route path="/forgot-password" element={!isAuthenticated ? <ForgotPasswordPage /> : <Navigate to="/" />} />
        <Route path="/reset-password" element={!isAuthenticated ? <ResetPasswordPage /> : <Navigate to="/" />} />
        
        {/* Public routes (no authentication required) */}
        <Route path="/public/dashboard/:shareToken" element={<PublicDashboardPage />} />
        
        <Route element={isAuthenticated ? <Layout /> : <Navigate to="/login" />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/datasources" element={<DataSourcesPage />} />
          <Route path="/queries" element={<QueriesPage />} />
          <Route path="/dashboards" element={<DashboardsPage />} />
          <Route path="/dashboards/:id" element={<DashboardViewerPage />} />
          <Route path="/dashboards/:id/edit" element={<DashboardBuilderPage />} />
          <Route path="/charts-showcase" element={<ChartsShowcasePage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/activity" element={<ActivityFeedPage />} />
          <Route path="/integrations" element={<IntegrationsPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/tenant-settings" element={<TenantSettingsPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;