import api from './api';

export interface CreateShareRequest {
  dashboard_id: string;
  password?: string;
  expires_in_days?: number;
  allow_interactions?: boolean;
}

export interface ShareResponse {
  share_token: string;
  share_url: string;
  expires_at?: string;
  password_protected: boolean;
  allow_interactions: boolean;
}

export interface SharedDashboard {
  id: number;
  dashboard_id: string;
  dashboard_name: string;
  share_token: string;
  share_url: string;
  password_protected: boolean;
  expires_at?: string;
  allow_interactions: boolean;
  created_at: string;
}

class SharingService {
  async createShareLink(data: CreateShareRequest): Promise<ShareResponse> {
    const response = await api.post('/api/sharing/create', data);
    return response.data;
  }

  async getSharedDashboard(shareToken: string) {
    const response = await api.get(`/api/sharing/dashboard/${shareToken}`);
    return response.data;
  }

  async accessSharedDashboard(shareToken: string, password?: string) {
    const response = await api.post(`/api/sharing/dashboard/${shareToken}/access`, {
      password
    });
    return response.data;
  }

  async getMyShares(): Promise<SharedDashboard[]> {
    const response = await api.get('/api/sharing/my-shares');
    return response.data;
  }

  async deleteShare(shareId: number): Promise<void> {
    await api.delete(`/api/sharing/share/${shareId}`);
  }
}

export default new SharingService();