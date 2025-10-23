import api from './api';

export interface Alert {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  query_id: string;
  condition_type: string;
  threshold_value?: number;
  threshold_value_2?: number;
  metric_column: string;
  frequency: string;
  notify_emails: string[];
  notify_slack: boolean;
  slack_webhook?: string;
  status: string;
  is_active: boolean;
  last_checked_at?: string;
  last_triggered_at?: string;
  next_check_at?: string;
  snooze_until?: string;
  created_at: string;
  updated_at?: string;
}

export interface AlertHistory {
  id: string;
  alert_id: string;
  triggered_at: string;
  condition_met: boolean;
  actual_value?: number;
  threshold_value?: number;
  notification_sent: boolean;
  notification_error?: string;
}

export interface CreateAlertRequest {
  name: string;
  description?: string;
  query_id: string;
  condition_type: string;
  threshold_value?: number;
  threshold_value_2?: number;
  metric_column: string;
  frequency?: string;
  notify_emails?: string[];
  notify_slack?: boolean;
  slack_webhook?: string;
}

export interface UpdateAlertRequest {
  name?: string;
  description?: string;
  condition_type?: string;
  threshold_value?: number;
  threshold_value_2?: number;
  metric_column?: string;
  frequency?: string;
  notify_emails?: string[];
  notify_slack?: boolean;
  slack_webhook?: string;
  status?: string;
  is_active?: boolean;
}

class AlertService {
  async createAlert(data: CreateAlertRequest): Promise<Alert> {
    const response = await api.post('/api/alerts/', data);
    return response.data;
  }

  async getAlerts(status?: string): Promise<Alert[]> {
    const params = status ? { status } : {};
    const response = await api.get('/api/alerts/', { params });
    return response.data;
  }

  async getAlert(alertId: string): Promise<Alert> {
    const response = await api.get(`/api/alerts/${alertId}`);
    return response.data;
  }

  async updateAlert(alertId: string, data: UpdateAlertRequest): Promise<Alert> {
    const response = await api.put(`/api/alerts/${alertId}`, data);
    return response.data;
  }

  async deleteAlert(alertId: string): Promise<void> {
    await api.delete(`/api/alerts/${alertId}`);
  }

  async evaluateAlert(alertId: string): Promise<any> {
    const response = await api.post(`/api/alerts/${alertId}/evaluate`);
    return response.data;
  }

  async snoozeAlert(alertId: string, hours: number = 24): Promise<Alert> {
    const response = await api.post(`/api/alerts/${alertId}/snooze`, null, {
      params: { hours }
    });
    return response.data;
  }

  async getAlertHistory(alertId: string, limit: number = 50): Promise<AlertHistory[]> {
    const response = await api.get(`/api/alerts/${alertId}/history`, {
      params: { limit }
    });
    return response.data;
  }

  async testSlackWebhook(webhookUrl: string): Promise<any> {
    const response = await api.post('/api/alerts/test-slack-webhook', null, {
      params: { webhook_url: webhookUrl }
    });
    return response.data;
  }
}

export default new AlertService();