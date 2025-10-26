import api from './api';

// Security Policy Types
export interface SecurityPolicy {
  id: string;
  name: string;
  description: string;
  policy_type: 'row_level' | 'column_level';
  rules: any;
  is_active: boolean;
  priority: number;
  applies_to: string[];
  tenant_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface DataMaskingRule {
  id: string;
  name: string;
  description: string;
  data_type: string;
  masking_pattern: string;
  is_active: boolean;
  tenant_id: string;
  created_at: string;
}

export interface CreatePolicyRequest {
  name: string;
  description: string;
  policy_type: 'row_level' | 'column_level';
  rules: any;
  priority?: number;
  applies_to?: string[];
}

export interface CreateMaskingRuleRequest {
  name: string;
  description: string;
  data_type: string;
  masking_pattern: string;
}

class SecurityService {
  // Security Policies
  async getPolicies(): Promise<SecurityPolicy[]> {
    const response = await api.get('/api/security/policies');
    return response.data;
  }

  async getPolicy(id: string): Promise<SecurityPolicy> {
    const response = await api.get(`/api/security/policies/${id}`);
    return response.data;
  }

  async createPolicy(data: CreatePolicyRequest): Promise<SecurityPolicy> {
    const response = await api.post('/api/security/policies', data);
    return response.data;
  }

  async updatePolicy(id: string, data: Partial<SecurityPolicy>): Promise<SecurityPolicy> {
    const response = await api.put(`/api/security/policies/${id}`, data);
    return response.data;
  }

  async deletePolicy(id: string): Promise<void> {
    await api.delete(`/api/security/policies/${id}`);
  }

  async testPolicy(id: string, testData: any): Promise<any> {
    const response = await api.post(`/api/security/policies/${id}/test`, testData);
    return response.data;
  }

  // Data Masking Rules
  async getMaskingRules(): Promise<DataMaskingRule[]> {
    const response = await api.get('/api/security/data-masking/rules');
    return response.data;
  }

  async createMaskingRule(data: CreateMaskingRuleRequest): Promise<DataMaskingRule> {
    const response = await api.post('/api/security/data-masking/rules', data);
    return response.data;
  }

  async updateMaskingRule(id: string, data: Partial<DataMaskingRule>): Promise<DataMaskingRule> {
    const response = await api.put(`/api/security/data-masking/rules/${id}`, data);
    return response.data;
  }

  async deleteMaskingRule(id: string): Promise<void> {
    await api.delete(`/api/security/data-masking/rules/${id}`);
  }
}

export default new SecurityService();
