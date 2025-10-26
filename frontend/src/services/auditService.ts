import api from './api';

export interface AuditLog {
  id: string;
  event_type: string;
  event_category: string;
  user_id: string;
  username: string;
  action: string;
  status: 'success' | 'failure' | 'denied';
  resource_type: string;
  resource_id: string;
  resource_name: string;
  ip_address: string;
  user_agent: string;
  details: any;
  tenant_id: string;
  created_at: string;
}

export interface AuditStats {
  total_events: number;
  by_status: {
    success: number;
    failure: number;
    denied: number;
  };
  by_category: {
    [key: string]: number;
  };
  recent_events: AuditLog[];
}

export interface AuditFilters {
  event_category?: string;
  status?: string;
  user_id?: string;
  start_date?: string;
  end_date?: string;
  limit?: number;
  offset?: number;
}

class AuditService {
  async getLogs(filters?: AuditFilters): Promise<AuditLog[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    const response = await api.get(`/api/audit/logs?${params.toString()}`);
    return response.data;
  }

  async getLog(id: string): Promise<AuditLog> {
    const response = await api.get(`/api/audit/logs/${id}`);
    return response.data;
  }

  async getStats(): Promise<AuditStats> {
    const response = await api.get('/api/audit/stats');
    return response.data;
  }

  async exportLogs(filters?: AuditFilters): Promise<Blob> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    const response = await api.post(`/api/audit/logs/export?${params.toString()}`, {}, {
      responseType: 'blob'
    });
    return response.data;
  }

  async getEventTypes(): Promise<string[]> {
    const response = await api.get('/api/audit/events');
    return response.data;
  }
}

export default new AuditService();
