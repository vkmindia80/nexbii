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
import APIKeysPage from './pages/APIKeysPage';
import WebhooksPage from './pages/WebhooksPage';
import PluginsPage from './pages/PluginsPage';
import SecurityPoliciesPage from './pages/SecurityPoliciesPage';
import SSOConfigPage from './pages/SSOConfigPage';
import MFAManagementPage from './pages/MFAManagementPage';
import AuditLogsPage from './pages/AuditLogsPage';
import CompliancePage from './pages/CompliancePage';
import DataCatalogPage from './pages/DataCatalogPage';
import DataLineagePage from './pages/DataLineagePage';
import DataClassificationPage from './pages/DataClassificationPage';
import AccessRequestsPage from './pages/AccessRequestsPage';
import SystemMonitoringPage from './pages/SystemMonitoringPage';
import PerformanceAnalyticsPage from './pages/PerformanceAnalyticsPage';
import UsageAnalyticsPage from './pages/UsageAnalyticsPage';
import UserManagementPage from './pages/UserManagementPage';
import BackupManagementPage from './pages/BackupManagementPage';
import ConfigurationManagementPage from './pages/ConfigurationManagementPage';
import Layout from './components/Layout';
import { useWebSocket } from './hooks/useWebSocket';
import { useTenantBranding } from './hooks/useTenantBranding';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const { isConnected } = useWebSocket();
  const { branding, loading: brandingLoading } = useTenantBranding();

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

  useEffect(() => {
    if (branding) {
      console.log('✅ Tenant branding applied:', branding);
    }
  }, [branding]);

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
          <Route path="/settings/api-keys" element={<APIKeysPage />} />
          <Route path="/settings/webhooks" element={<WebhooksPage />} />
          <Route path="/settings/plugins" element={<PluginsPage />} />
          <Route path="/security/policies" element={<SecurityPoliciesPage />} />
          <Route path="/security/sso" element={<SSOConfigPage />} />
          <Route path="/security/mfa" element={<MFAManagementPage />} />
          <Route path="/security/audit-logs" element={<AuditLogsPage />} />
          <Route path="/security/compliance" element={<CompliancePage />} />
          <Route path="/governance/catalog" element={<DataCatalogPage />} />
          <Route path="/governance/lineage" element={<DataLineagePage />} />
          <Route path="/governance/classification" element={<DataClassificationPage />} />
          <Route path="/governance/access-requests" element={<AccessRequestsPage />} />
          
          {/* Admin Routes - Phase 4.5 */}
          <Route path="/admin/monitoring" element={<SystemMonitoringPage />} />
          <Route path="/admin/performance" element={<PerformanceAnalyticsPage />} />
          <Route path="/admin/usage" element={<UsageAnalyticsPage />} />
          <Route path="/admin/users" element={<UserManagementPage />} />
          <Route path="/admin/backups" element={<BackupManagementPage />} />
          <Route path="/admin/config" element={<ConfigurationManagementPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;