import api from './api';

export interface WebhookEvent {
  event: string;
  description: string;
  category: string;
}

export interface Webhook {
  id: string;
  name: string;
  description?: string;
  url: string;
  events: string[];
  is_active: boolean;
  max_retries: number;
  retry_backoff_seconds: number;
  total_deliveries: number;
  successful_deliveries: number;
  failed_deliveries: number;
  last_triggered_at?: string;
  last_success_at?: string;
  last_failure_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface WebhookCreate {
  name: string;
  description?: string;
  url: string;
  events: string[];
  secret?: string;
  max_retries?: number;
  retry_backoff_seconds?: number;
}

export interface WebhookUpdate {
  name?: string;
  description?: string;
  url?: string;
  events?: string[];
  is_active?: boolean;
  max_retries?: number;
  retry_backoff_seconds?: number;
}

export interface WebhookDelivery {
  id: string;
  webhook_id: string;
  event_type: string;
  status: string;
  attempt_count: number;
  max_attempts: number;
  response_status_code?: number;
  response_time_ms?: number;
  error_message?: string;
  next_retry_at?: string;
  created_at: string;
  delivered_at?: string;
}

export interface WebhookStats {
  webhook_id: string;
  webhook_name: string;
  total_deliveries: number;
  successful_deliveries: number;
  failed_deliveries: number;
  success_rate: number;
  avg_response_time_ms?: number;
  deliveries_last_24h: number;
  deliveries_last_7d: number;
  deliveries_last_30d: number;
  recent_deliveries: WebhookDelivery[];
}

class WebhookService {
  async getAvailableEvents(): Promise<WebhookEvent[]> {
    const response = await api.get('/api/webhooks/events');
    return response.data.events;
  }

  async createWebhook(data: WebhookCreate): Promise<Webhook> {
    const response = await api.post('/api/webhooks/', data);
    return response.data;
  }

  async listWebhooks(includeInactive: boolean = false): Promise<Webhook[]> {
    const response = await api.get('/api/webhooks/', {
      params: { include_inactive: includeInactive }
    });
    return response.data;
  }

  async getWebhook(webhookId: string): Promise<Webhook> {
    const response = await api.get(`/api/webhooks/${webhookId}`);
    return response.data;
  }

  async updateWebhook(webhookId: string, data: WebhookUpdate): Promise<Webhook> {
    const response = await api.put(`/api/webhooks/${webhookId}`, data);
    return response.data;
  }

  async deleteWebhook(webhookId: string): Promise<void> {
    await api.delete(`/api/webhooks/${webhookId}`);
  }

  async testWebhook(webhookId: string, eventType: string = 'test.webhook', testData?: any): Promise<{
    success: boolean;
    status_code?: number;
    response_time_ms?: number;
    response_body?: string;
    error_message?: string;
  }> {
    const response = await api.post(`/api/webhooks/${webhookId}/test`, {
      event_type: eventType,
      test_data: testData
    });
    return response.data;
  }

  async getWebhookDeliveries(
    webhookId: string,
    statusFilter?: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<WebhookDelivery[]> {
    const response = await api.get(`/api/webhooks/${webhookId}/deliveries`, {
      params: { status_filter: statusFilter, skip, limit }
    });
    return response.data;
  }

  async getWebhookStats(webhookId: string): Promise<WebhookStats> {
    const response = await api.get(`/api/webhooks/${webhookId}/stats`);
    return response.data;
  }
}

export default new WebhookService();
