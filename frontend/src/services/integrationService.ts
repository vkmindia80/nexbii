import api from './api';

export interface EmailConfig {
  smtp_host?: string;
  smtp_port?: number;
  smtp_user?: string;
  smtp_password?: string;
  from_email?: string;
  from_name?: string;
  mock_email: boolean;
}

export interface SlackConfig {
  slack_webhook_url?: string;
  mock_slack: boolean;
}

export interface TestEmailRequest {
  test_email: string;
}

export interface TestSlackRequest {
  test_message?: string;
}

export interface TestResponse {
  success: boolean;
  message: string;
  mock_mode: boolean;
}

export const integrationService = {
  // Email Configuration
  async getEmailConfig(): Promise<EmailConfig> {
    const response = await api.get('/integrations/email');
    return response.data;
  },

  async saveEmailConfig(config: EmailConfig): Promise<EmailConfig> {
    const response = await api.post('/integrations/email', config);
    return response.data;
  },

  async testEmail(testEmail: string): Promise<TestResponse> {
    const response = await api.post('/integrations/email/test', { test_email: testEmail });
    return response.data;
  },

  // Slack Configuration
  async getSlackConfig(): Promise<SlackConfig> {
    const response = await api.get('/integrations/slack');
    return response.data;
  },

  async saveSlackConfig(config: SlackConfig): Promise<SlackConfig> {
    const response = await api.post('/integrations/slack', config);
    return response.data;
  },

  async testSlack(testMessage?: string): Promise<TestResponse> {
    const response = await api.post('/integrations/slack/test', { test_message: testMessage });
    return response.data;
  },
};
