import api from './api';

export interface APIScope {
  scope: string;
  description: string;
  category: string;
}

export interface APIKey {
  id: string;
  name: string;
  description?: string;
  key_prefix: string;
  scopes: string[];
  rate_limit_per_minute: number;
  rate_limit_per_hour: number;
  rate_limit_per_day: number;
  is_active: boolean;
  expires_at?: string;
  last_used_at?: string;
  last_used_ip?: string;
  request_count: number;
  created_at: string;
  updated_at?: string;
}

export interface APIKeyCreate {
  name: string;
  description?: string;
  scopes: string[];
  rate_limit_per_minute?: number;
  rate_limit_per_hour?: number;
  rate_limit_per_day?: number;
  expires_at?: string;
}

export interface APIKeyCreated extends APIKey {
  api_key: string; // Full key - only shown once
}

export interface APIKeyUpdate {
  name?: string;
  description?: string;
  scopes?: string[];
  rate_limit_per_minute?: number;
  rate_limit_per_hour?: number;
  rate_limit_per_day?: number;
  is_active?: boolean;
}

export interface APIKeyUsageStats {
  api_key_id: string;
  total_requests: number;
  requests_last_24h: number;
  requests_last_7d: number;
  requests_last_30d: number;
  avg_response_time_ms?: number;
  error_rate?: number;
  most_used_endpoints: Array<{
    endpoint: string;
    method: string;
    count: number;
  }>;
}

class APIKeyService {
  async getAvailableScopes(): Promise<APIScope[]> {
    const response = await api.get('/api/api-keys/scopes');
    return response.data.scopes;
  }

  async createAPIKey(data: APIKeyCreate): Promise<APIKeyCreated> {
    const response = await api.post('/api/api-keys/', data);
    return response.data;
  }

  async listAPIKeys(includeInactive: boolean = false): Promise<APIKey[]> {
    const response = await api.get('/api/api-keys/', {
      params: { include_inactive: includeInactive }
    });
    return response.data;
  }

  async getAPIKey(apiKeyId: string): Promise<APIKey> {
    const response = await api.get(`/api/api-keys/${apiKeyId}`);
    return response.data;
  }

  async updateAPIKey(apiKeyId: string, data: APIKeyUpdate): Promise<APIKey> {
    const response = await api.put(`/api/api-keys/${apiKeyId}`, data);
    return response.data;
  }

  async deleteAPIKey(apiKeyId: string): Promise<void> {
    await api.delete(`/api/api-keys/${apiKeyId}`);
  }

  async rotateAPIKey(apiKeyId: string): Promise<{ id: string; api_key: string; message: string }> {
    const response = await api.post(`/api/api-keys/${apiKeyId}/rotate`);
    return response.data;
  }

  async getAPIKeyUsage(apiKeyId: string): Promise<APIKeyUsageStats> {
    const response = await api.get(`/api/api-keys/${apiKeyId}/usage`);
    return response.data;
  }

  async testAPIKey(): Promise<any> {
    const response = await api.post('/api/api-keys/test');
    return response.data;
  }
}

export default new APIKeyService();
