import api from './api';

export interface GDPRExportData {
  user_data: any;
  queries: any[];
  dashboards: any[];
  export_date: string;
}

export interface ConsentRecord {
  id: string;
  user_id: string;
  consent_type: string;
  version: string;
  is_granted: boolean;
  granted_at: string;
  revoked_at: string | null;
}

export interface DataClassification {
  id: string;
  table_name: string;
  column_name: string;
  classification: 'PII' | 'PHI' | 'SENSITIVE' | 'PUBLIC';
  masking_rule_id: string | null;
  tenant_id: string;
}

export interface ComplianceReport {
  report_type: 'soc2' | 'gdpr' | 'hipaa';
  generated_at: string;
  status: string;
  details: any;
}

class ComplianceService {
  // GDPR
  async exportUserData(): Promise<GDPRExportData> {
    const response = await api.get('/api/compliance/gdpr/export');
    return response.data;
  }

  async deleteUserData(confirmation: string): Promise<void> {
    await api.post('/api/compliance/gdpr/delete', { confirmation });
  }

  async getConsents(): Promise<ConsentRecord[]> {
    const response = await api.get('/api/compliance/consents');
    return response.data;
  }

  async recordConsent(consentType: string, isGranted: boolean): Promise<ConsentRecord> {
    const response = await api.post('/api/compliance/consents', {
      consent_type: consentType,
      is_granted: isGranted
    });
    return response.data;
  }

  async updateConsent(id: string, isGranted: boolean): Promise<ConsentRecord> {
    const response = await api.put(`/api/compliance/consents/${id}`, {
      is_granted: isGranted
    });
    return response.data;
  }

  // HIPAA
  async getDataClassifications(): Promise<DataClassification[]> {
    const response = await api.get('/api/compliance/hipaa/classifications');
    return response.data;
  }

  async classifyData(data: {
    table_name: string;
    column_name: string;
    classification: 'PII' | 'PHI' | 'SENSITIVE' | 'PUBLIC';
  }): Promise<DataClassification> {
    const response = await api.post('/api/compliance/hipaa/classify', data);
    return response.data;
  }

  // Compliance Reports
  async generateSOC2Report(): Promise<ComplianceReport> {
    const response = await api.get('/api/compliance/reports/soc2');
    return response.data;
  }

  async generateGDPRReport(): Promise<ComplianceReport> {
    const response = await api.get('/api/compliance/reports/gdpr');
    return response.data;
  }

  async generateHIPAAReport(): Promise<ComplianceReport> {
    const response = await api.get('/api/compliance/reports/hipaa');
    return response.data;
  }
}

export default new ComplianceService();
