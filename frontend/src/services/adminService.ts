/**
 * Admin Service for Phase 4.5 - Enterprise Admin
 * Handles all admin-related API calls
 */
import api from './api';

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

export interface SystemMetrics {
  id: string;
  metric_type: string;
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
  active_connections: number;
  query_count: number;
  avg_query_time: number;
  timestamp: string;
}

export interface SystemHealth {
  id: string;
  timestamp: string;
  database_status: string;
  redis_status: string;
  api_status: string;
  email_service_status?: string;
  slack_service_status?: string;
  database_response_time?: number;
  redis_response_time?: number;
  api_response_time?: number;
  overall_status: string;
  alerts_triggered?: Array<{ type: string; message: string }>;
  additional_data?: any;
  created_at: string;
}

export interface UserActivity {
  id: string;
  user_id: string;
  username: string;
  action: string;
  resource_type: string;
  resource_id: string;
  ip_address: string;
  user_agent: string;
  created_at: string;
}

export interface UserSession {
  id: string;
  user_id: string;
  username: string;
  ip_address: string;
  user_agent: string;
  created_at: string;
  last_activity: string;
  is_active: boolean;
}

export interface UserManagementStats {
  total_users: number;
  active_users: number;
  inactive_users: number;
  locked_users: number;
  users_by_role: {
    [key: string]: number;
  };
  recent_signups: number;
  active_sessions: number;
}

export interface TenantUsageMetrics {
  tenant_id: string;
  tenant_name: string;
  date: string;
  active_users: number;
  total_queries: number;
  total_dashboards: number;
  storage_used_mb: number;
  api_calls: number;
}

export interface UsageAnalyticsSummary {
  tenant_id: string;
  period_start: string;
  period_end: string;
  total_active_users: number;
  total_queries_executed: number;
  total_dashboards_created: number;
  total_api_calls: number;
  storage_used_mb: number;
  top_users: Array<{
    user_id: string;
    username: string;
    query_count: number;
  }>;
  top_dashboards: Array<{
    dashboard_id: string;
    dashboard_name: string;
    view_count: number;
  }>;
}

export interface BackupJob {
  id: string;
  tenant_id: string;
  backup_type: string;
  status: string;
  file_path: string;
  file_size_mb: number;
  metadata: any;
  created_by: string;
  created_at: string;
  completed_at?: string;
  error_message?: string;
}

export interface BackupJobCreate {
  tenant_id?: string;
  backup_type: 'full' | 'incremental' | 'tenant_only';
  include_data: boolean;
  include_files: boolean;
  compression: boolean;
}

export interface BackupRestoreRequest {
  backup_id: string;
  target_tenant_id?: string;
  restore_data: boolean;
  restore_files: boolean;
  overwrite_existing: boolean;
}

export interface ConfigurationVersion {
  id: string;
  tenant_id: string;
  version: number;
  config_data: any;
  created_by: string;
  created_at: string;
  description?: string;
}

export interface ConfigurationExportRequest {
  tenant_id?: string;
  include_secrets: boolean;
  sections: string[];
}

export interface ConfigurationImportRequest {
  tenant_id?: string;
  config_data: any;
  merge_strategy: 'replace' | 'merge' | 'skip_existing';
  validate_only: boolean;
}

export interface QueryPerformanceStats {
  query_id: string;
  query_name: string;
  avg_execution_time: number;
  max_execution_time: number;
  min_execution_time: number;
  execution_count: number;
  error_count: number;
  last_executed: string;
}

export interface APIEndpointPerformance {
  endpoint: string;
  method: string;
  avg_response_time: number;
  max_response_time: number;
  request_count: number;
  error_count: number;
  error_rate: number;
}

// ============================================================================
// ADMIN SERVICE
// ============================================================================

class AdminService {
  // ------------------------------------------------------------------------
  // SYSTEM MONITORING & HEALTH
  // ------------------------------------------------------------------------

  async getSystemHealth(
    checkDatabase: boolean = true,
    checkRedis: boolean = true,
    checkIntegrations: boolean = false
  ): Promise<SystemHealth> {
    const params = new URLSearchParams({
      check_database: String(checkDatabase),
      check_redis: String(checkRedis),
      check_integrations: String(checkIntegrations),
    });
    const response = await api.get(`/api/admin/health?${params.toString()}`);
    return response.data;
  }

  async getSystemMetrics(
    startTime?: string,
    endTime?: string,
    metricType: string = 'database',
    limit: number = 100
  ): Promise<SystemMetrics[]> {
    const params = new URLSearchParams({ metric_type: metricType, limit: String(limit) });
    if (startTime) params.append('start_time', startTime);
    if (endTime) params.append('end_time', endTime);
    
    const response = await api.get(`/api/admin/metrics/system?${params.toString()}`);
    return response.data;
  }

  async collectMetricsNow(): Promise<any> {
    const response = await api.post('/api/admin/metrics/collect');
    return response.data;
  }

  async cleanupOldMetrics(days: number = 90): Promise<any> {
    const response = await api.delete(`/api/admin/metrics/cleanup?days=${days}`);
    return response.data;
  }

  // ------------------------------------------------------------------------
  // USER MANAGEMENT
  // ------------------------------------------------------------------------

  async getUserStats(tenantId?: string): Promise<UserManagementStats> {
    const params = tenantId ? `?tenant_id=${tenantId}` : '';
    const response = await api.get(`/api/admin/users/stats${params}`);
    return response.data;
  }

  async getUserActivity(
    userId: string,
    limit: number = 100,
    action?: string
  ): Promise<UserActivity[]> {
    const params = new URLSearchParams({ limit: String(limit) });
    if (action) params.append('action', action);
    
    const response = await api.get(`/api/admin/users/${userId}/activity?${params.toString()}`);
    return response.data;
  }

  async getUserSessions(userId: string): Promise<UserSession[]> {
    const response = await api.get(`/api/admin/users/${userId}/sessions`);
    return response.data;
  }

  async terminateUserSession(userId: string, sessionId: string): Promise<any> {
    const response = await api.post(`/api/admin/users/${userId}/sessions/${sessionId}/terminate`);
    return response.data;
  }

  async bulkImportUsers(data: any): Promise<any> {
    const response = await api.post('/api/admin/users/bulk-import', data);
    return response.data;
  }

  async offboardUser(userId: string, data: any): Promise<any> {
    const response = await api.post(`/api/admin/users/${userId}/offboard`, data);
    return response.data;
  }

  async lockUserAccount(userId: string, reason: string): Promise<any> {
    const response = await api.post(`/api/admin/users/${userId}/lock?reason=${encodeURIComponent(reason)}`);
    return response.data;
  }

  async unlockUserAccount(userId: string): Promise<any> {
    const response = await api.post(`/api/admin/users/${userId}/unlock`);
    return response.data;
  }

  async cleanupExpiredSessions(): Promise<any> {
    const response = await api.post('/api/admin/sessions/cleanup');
    return response.data;
  }

  // ------------------------------------------------------------------------
  // USAGE ANALYTICS
  // ------------------------------------------------------------------------

  async getTenantUsageSummary(
    tenantId: string,
    startDate?: string,
    endDate?: string
  ): Promise<UsageAnalyticsSummary> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await api.get(`/api/admin/usage/tenant/${tenantId}?${params.toString()}`);
    return response.data;
  }

  async getUsageMetrics(
    tenantId?: string,
    startDate?: string,
    endDate?: string,
    limit: number = 30
  ): Promise<TenantUsageMetrics[]> {
    const params = new URLSearchParams({ limit: String(limit) });
    if (tenantId) params.append('tenant_id', tenantId);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await api.get(`/api/admin/usage/metrics?${params.toString()}`);
    return response.data;
  }

  async aggregateUsage(tenantId?: string, date?: string): Promise<any> {
    const params = new URLSearchParams();
    if (tenantId) params.append('tenant_id', tenantId);
    if (date) params.append('date', date);
    
    const response = await api.post(`/api/admin/usage/aggregate?${params.toString()}`);
    return response.data;
  }

  async getBillingReport(tenantId: string, startDate?: string, endDate?: string): Promise<any> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await api.get(`/api/admin/usage/billing/${tenantId}?${params.toString()}`);
    return response.data;
  }

  // ------------------------------------------------------------------------
  // BACKUP & RESTORE
  // ------------------------------------------------------------------------

  async createBackup(data: BackupJobCreate): Promise<BackupJob> {
    const response = await api.post('/api/admin/backups', data);
    return response.data;
  }

  async listBackups(tenantId?: string, limit: number = 50): Promise<BackupJob[]> {
    const params = new URLSearchParams({ limit: String(limit) });
    if (tenantId) params.append('tenant_id', tenantId);
    
    const response = await api.get(`/api/admin/backups?${params.toString()}`);
    return response.data;
  }

  async restoreBackup(backupId: string, data: BackupRestoreRequest): Promise<any> {
    const response = await api.post(`/api/admin/backups/${backupId}/restore`, data);
    return response.data;
  }

  async cleanupOldBackups(retentionDays: number = 30): Promise<any> {
    const response = await api.delete(`/api/admin/backups/cleanup?retention_days=${retentionDays}`);
    return response.data;
  }

  // ------------------------------------------------------------------------
  // CONFIGURATION MANAGEMENT
  // ------------------------------------------------------------------------

  async exportConfiguration(data: ConfigurationExportRequest): Promise<any> {
    const response = await api.post('/api/admin/config/export', data);
    return response.data;
  }

  async importConfiguration(data: ConfigurationImportRequest): Promise<any> {
    const response = await api.post('/api/admin/config/import', data);
    return response.data;
  }

  async getConfigurationVersions(tenantId: string, limit: number = 20): Promise<ConfigurationVersion[]> {
    const response = await api.get(`/api/admin/config/versions/${tenantId}?limit=${limit}`);
    return response.data;
  }

  async rollbackConfiguration(tenantId: string, versionId: string): Promise<any> {
    const response = await api.post(`/api/admin/config/rollback/${tenantId}/${versionId}`);
    return response.data;
  }

  // ------------------------------------------------------------------------
  // PERFORMANCE ANALYTICS (Using existing endpoints)
  // ------------------------------------------------------------------------

  async getQueryPerformanceStats(): Promise<QueryPerformanceStats[]> {
    // This would typically come from audit logs or a dedicated performance table
    const response = await api.get('/api/audit/logs?event_category=query_execution&limit=100');
    return response.data;
  }

  async getAPIPerformanceStats(): Promise<APIEndpointPerformance[]> {
    // This would typically come from audit logs or a dedicated performance table
    const response = await api.get('/api/audit/logs?event_category=api_call&limit=100');
    return response.data;
  }
}

export default new AdminService();
