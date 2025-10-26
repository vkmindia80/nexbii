/**
 * Data Governance Service
 * Phase 4.4: Data Governance
 * 
 * API calls for:
 * - Data Catalog
 * - Data Lineage  
 * - Data Classification
 * - Access Requests
 */
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: `${API_URL}/api/governance`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ==================== Data Catalog ====================

export const createCatalogEntry = async (entry: any) => {
  const response = await api.post('/catalog', entry);
  return response.data;
};

export const getCatalogEntries = async (params?: {
  datasource_id?: string;
  table_name?: string;
  classification_level?: string;
  is_pii?: boolean;
  search?: string;
  limit?: number;
  offset?: number;
}) => {
  const response = await api.get('/catalog', { params });
  return response.data;
};

export const getCatalogEntry = async (entryId: string) => {
  const response = await api.get(`/catalog/${entryId}`);
  return response.data;
};

export const updateCatalogEntry = async (entryId: string, entry: any) => {
  const response = await api.put(`/catalog/${entryId}`, entry);
  return response.data;
};

export const deleteCatalogEntry = async (entryId: string) => {
  const response = await api.delete(`/catalog/${entryId}`);
  return response.data;
};

export const getCatalogStatistics = async () => {
  const response = await api.get('/catalog/statistics');
  return response.data;
};

// ==================== Data Lineage ====================

export const createLineage = async (lineage: any) => {
  const response = await api.post('/lineage', lineage);
  return response.data;
};

export const getLineageGraph = async (resourceType: string, resourceId: string) => {
  const response = await api.get(`/lineage/graph/${resourceType}/${resourceId}`);
  return response.data;
};

export const analyzeImpact = async (request: {
  change_type: string;
  affected_resource_type: string;
  affected_resource_id: string;
  affected_resource_name?: string;
}) => {
  const response = await api.post('/lineage/impact-analysis', request);
  return response.data;
};

// ==================== Data Classification ====================

export const createClassificationRule = async (rule: any) => {
  const response = await api.post('/classification/rules', rule);
  return response.data;
};

export const getClassificationRules = async (isEnabled?: boolean) => {
  const params = isEnabled !== undefined ? { is_enabled: isEnabled } : {};
  const response = await api.get('/classification/rules', { params });
  return response.data;
};

export const scanForPII = async (datasourceId: string, tableName?: string) => {
  const response = await api.post('/classification/scan', {
    datasource_id: datasourceId,
    table_name: tableName,
  });
  return response.data;
};

// ==================== Access Requests ====================

export const createAccessRequest = async (request: {
  requester_justification: string;
  resource_type: string;
  resource_id: string;
  resource_name?: string;
  access_level?: string;
  duration_days?: number;
}) => {
  const response = await api.post('/access-requests', request);
  return response.data;
};

export const getAccessRequests = async (status?: string, requesterId?: string) => {
  const params: any = {};
  if (status) params.status = status;
  if (requesterId) params.requester_id = requesterId;
  const response = await api.get('/access-requests', { params });
  return response.data;
};

export const getPendingRequests = async () => {
  const response = await api.get('/access-requests/pending');
  return response.data;
};

export const approveAccessRequest = async (
  requestId: string,
  approvalNotes?: string,
  isComplianceApproval: boolean = false
) => {
  const response = await api.post(`/access-requests/${requestId}/approve`, null, {
    params: {
      approval_notes: approvalNotes,
      is_compliance_approval: isComplianceApproval,
    },
  });
  return response.data;
};

export const rejectAccessRequest = async (requestId: string, rejectionNotes: string) => {
  const response = await api.post(`/access-requests/${requestId}/reject`, null, {
    params: {
      rejection_notes: rejectionNotes,
    },
  });
  return response.data;
};

// ==================== Health Check ====================

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

const governanceService = {
  // Data Catalog
  createCatalogEntry,
  getCatalogEntries,
  getCatalogEntry,
  updateCatalogEntry,
  deleteCatalogEntry,
  getCatalogStatistics,
  
  // Data Lineage
  createLineage,
  getLineageGraph,
  analyzeImpact,
  
  // Data Classification
  createClassificationRule,
  getClassificationRules,
  scanForPII,
  
  // Access Requests
  createAccessRequest,
  getAccessRequests,
  getPendingRequests,
  approveAccessRequest,
  rejectAccessRequest,
  
  // Health
  healthCheck,
};

export default governanceService;
