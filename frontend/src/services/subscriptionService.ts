import api from './api';

export interface EmailSubscription {
  id: string;
  user_id: string;
  dashboard_id: string;
  frequency: 'daily' | 'weekly' | 'monthly';
  is_active: boolean;
  next_send_date?: string;
  last_sent_date?: string;
  created_at: string;
  updated_at?: string;
}

export interface CreateSubscriptionRequest {
  dashboard_id: string;
  frequency: 'daily' | 'weekly' | 'monthly';
}

export interface UpdateSubscriptionRequest {
  frequency?: 'daily' | 'weekly' | 'monthly';
  is_active?: boolean;
}

class SubscriptionService {
  async createSubscription(data: CreateSubscriptionRequest): Promise<EmailSubscription> {
    const response = await api.post('/api/subscriptions/', data);
    return response.data;
  }

  async getSubscriptions(dashboardId?: string): Promise<EmailSubscription[]> {
    const params = dashboardId ? { dashboard_id: dashboardId } : {};
    const response = await api.get('/api/subscriptions/', { params });
    return response.data;
  }

  async updateSubscription(
    subscriptionId: string,
    data: UpdateSubscriptionRequest
  ): Promise<EmailSubscription> {
    const response = await api.put(`/api/subscriptions/${subscriptionId}`, data);
    return response.data;
  }

  async deleteSubscription(subscriptionId: string): Promise<void> {
    await api.delete(`/api/subscriptions/${subscriptionId}`);
  }
}

export default new SubscriptionService();