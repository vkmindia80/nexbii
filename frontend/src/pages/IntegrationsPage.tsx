import React, { useState, useEffect } from 'react';
import { Mail, Send, Loader2, CheckCircle, XCircle, AlertCircle, Settings } from 'lucide-react';
import { integrationService } from '../services/integrationService';

interface EmailConfig {
  smtp_host: string;
  smtp_port: number;
  smtp_user: string;
  smtp_password: string;
  from_email: string;
  from_name: string;
  mock_email: boolean;
}

interface SlackConfig {
  slack_webhook_url: string;
  mock_slack: boolean;
}

const IntegrationsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'email' | 'slack'>('email');
  
  // Email state
  const [emailConfig, setEmailConfig] = useState<EmailConfig>({
    smtp_host: '',
    smtp_port: 587,
    smtp_user: '',
    smtp_password: '',
    from_email: '',
    from_name: '',
    mock_email: true,
  });
  const [testEmail, setTestEmail] = useState('');
  const [emailLoading, setEmailLoading] = useState(false);
  const [emailSaveLoading, setEmailSaveLoading] = useState(false);
  const [emailTestLoading, setEmailTestLoading] = useState(false);
  const [emailMessage, setEmailMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);
  
  // Slack state
  const [slackConfig, setSlackConfig] = useState<SlackConfig>({
    slack_webhook_url: '',
    mock_slack: true,
  });
  const [slackLoading, setSlackLoading] = useState(false);
  const [slackSaveLoading, setSlackSaveLoading] = useState(false);
  const [slackTestLoading, setSlackTestLoading] = useState(false);
  const [slackMessage, setSlackMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);

  useEffect(() => {
    loadConfigurations();
  }, []);

  const loadConfigurations = async () => {
    try {
      setEmailLoading(true);
      setSlackLoading(true);

      // Load email config
      const emailData = await integrationService.getEmailConfig();
      if (emailData) {
        setEmailConfig({
          smtp_host: emailData.smtp_host || '',
          smtp_port: emailData.smtp_port || 587,
          smtp_user: emailData.smtp_user || '',
          smtp_password: '', // Never populate password field
          from_email: emailData.from_email || '',
          from_name: emailData.from_name || '',
          mock_email: emailData.mock_email ?? true,
        });
      }

      // Load Slack config
      const slackData = await integrationService.getSlackConfig();
      if (slackData) {
        setSlackConfig({
          slack_webhook_url: slackData.slack_webhook_url || '',
          mock_slack: slackData.mock_slack ?? true,
        });
      }
    } catch (error: any) {
      console.error('Error loading configurations:', error);
      if (error.response?.status === 403) {
        setEmailMessage({ type: 'error', text: 'Access denied. Only administrators can manage integrations.' });
        setSlackMessage({ type: 'error', text: 'Access denied. Only administrators can manage integrations.' });
      }
    } finally {
      setEmailLoading(false);
      setSlackLoading(false);
    }
  };

  const handleSaveEmailConfig = async (e: React.FormEvent) => {
    e.preventDefault();
    setEmailMessage(null);
    setEmailSaveLoading(true);

    try {
      await integrationService.saveEmailConfig(emailConfig);
      setEmailMessage({ type: 'success', text: 'Email configuration saved successfully!' });
      
      // Clear password field after save
      setEmailConfig(prev => ({ ...prev, smtp_password: '' }));
    } catch (error: any) {
      console.error('Error saving email config:', error);
      setEmailMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to save email configuration' 
      });
    } finally {
      setEmailSaveLoading(false);
    }
  };

  const handleTestEmail = async () => {
    if (!testEmail) {
      setEmailMessage({ type: 'error', text: 'Please enter a test email address' });
      return;
    }

    setEmailMessage(null);
    setEmailTestLoading(true);

    try {
      const response = await integrationService.testEmail(testEmail);
      setEmailMessage({ 
        type: 'success', 
        text: response.message + (response.mock_mode ? ' (Check backend logs for mock email)' : '')
      });
    } catch (error: any) {
      console.error('Error testing email:', error);
      setEmailMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to send test email' 
      });
    } finally {
      setEmailTestLoading(false);
    }
  };

  const handleSaveSlackConfig = async (e: React.FormEvent) => {
    e.preventDefault();
    setSlackMessage(null);
    setSlackSaveLoading(true);

    try {
      await integrationService.saveSlackConfig(slackConfig);
      setSlackMessage({ type: 'success', text: 'Slack configuration saved successfully!' });
    } catch (error: any) {
      console.error('Error saving Slack config:', error);
      setSlackMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to save Slack configuration' 
      });
    } finally {
      setSlackSaveLoading(false);
    }
  };

  const handleTestSlack = async () => {
    if (!slackConfig.slack_webhook_url) {
      setSlackMessage({ type: 'error', text: 'Please enter a webhook URL first' });
      return;
    }

    setSlackMessage(null);
    setSlackTestLoading(true);

    try {
      const response = await integrationService.testSlack();
      setSlackMessage({ 
        type: 'success', 
        text: response.message + (response.mock_mode ? ' (Check backend logs for mock message)' : '')
      });
    } catch (error: any) {
      console.error('Error testing Slack:', error);
      setSlackMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to send test message' 
      });
    } finally {
      setSlackTestLoading(false);
    }
  };

  const MessageAlert = ({ message }: { message: { type: 'success' | 'error' | 'info'; text: string } }) => {
    const icons = {
      success: <CheckCircle className="w-5 h-5" />,
      error: <XCircle className="w-5 h-5" />,
      info: <AlertCircle className="w-5 h-5" />,
    };

    const colors = {
      success: 'bg-green-50 text-green-800 border-green-200',
      error: 'bg-red-50 text-red-800 border-red-200',
      info: 'bg-blue-50 text-blue-800 border-blue-200',
    };

    return (
      <div className={`flex items-start space-x-3 p-4 rounded-lg border ${colors[message.type]}`}>
        {icons[message.type]}
        <p className="flex-1">{message.text}</p>
      </div>
    );
  };

  return (
    <div className="max-w-5xl mx-auto" data-testid="integrations-page">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Integrations</h1>
        <p className="text-gray-600">
          Configure email and Slack integrations for notifications, alerts, and subscriptions.
        </p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-4 px-6" aria-label="Tabs">
            <button
              onClick={() => setActiveTab('email')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'email'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              data-testid="tab-email"
            >
              <div className="flex items-center space-x-2">
                <Mail className="w-5 h-5" />
                <span>Email Configuration</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('slack')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'slack'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              data-testid="tab-slack"
            >
              <div className="flex items-center space-x-2">
                <Send className="w-5 h-5" />
                <span>Slack Configuration</span>
              </div>
            </button>
          </nav>
        </div>

        <div className="p-6">
          {/* Email Configuration */}
          {activeTab === 'email' && (
            <div data-testid="email-config-section">
              {emailLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
                </div>
              ) : (
                <>
                  {emailMessage && (
                    <div className="mb-6">
                      <MessageAlert message={emailMessage} />
                    </div>
                  )}

                  <form onSubmit={handleSaveEmailConfig} className="space-y-6">
                    {/* Mock Mode Toggle */}
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <label className="flex items-center space-x-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={emailConfig.mock_email}
                          onChange={(e) => setEmailConfig({ ...emailConfig, mock_email: e.target.checked })}
                          className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                          data-testid="email-mock-toggle"
                        />
                        <div>
                          <span className="font-medium text-gray-900">Mock Mode (Development)</span>
                          <p className="text-sm text-gray-600">
                            When enabled, emails are logged to console instead of being sent
                          </p>
                        </div>
                      </label>
                    </div>

                    {/* SMTP Configuration */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          SMTP Host *
                        </label>
                        <input
                          type="text"
                          value={emailConfig.smtp_host}
                          onChange={(e) => setEmailConfig({ ...emailConfig, smtp_host: e.target.value })}
                          placeholder="smtp.gmail.com"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                          required
                          data-testid="email-smtp-host"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          SMTP Port *
                        </label>
                        <input
                          type="number"
                          value={emailConfig.smtp_port}
                          onChange={(e) => setEmailConfig({ ...emailConfig, smtp_port: parseInt(e.target.value) })}
                          placeholder="587"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                          required
                          data-testid="email-smtp-port"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          SMTP Username *
                        </label>
                        <input
                          type="text"
                          value={emailConfig.smtp_user}
                          onChange={(e) => setEmailConfig({ ...emailConfig, smtp_user: e.target.value })}
                          placeholder="your-email@gmail.com"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                          required
                          data-testid="email-smtp-user"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          SMTP Password *
                        </label>
                        <input
                          type="password"
                          value={emailConfig.smtp_password}
                          onChange={(e) => setEmailConfig({ ...emailConfig, smtp_password: e.target.value })}
                          placeholder="Enter password (leave empty to keep existing)"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                          data-testid="email-smtp-password"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Leave empty to keep existing password
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          From Email *
                        </label>
                        <input
                          type="email"
                          value={emailConfig.from_email}
                          onChange={(e) => setEmailConfig({ ...emailConfig, from_email: e.target.value })}
                          placeholder="noreply@nexbii.com"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                          required
                          data-testid="email-from-email"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          From Name
                        </label>
                        <input
                          type="text"
                          value={emailConfig.from_name}
                          onChange={(e) => setEmailConfig({ ...emailConfig, from_name: e.target.value })}
                          placeholder="NexBII Analytics"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                          data-testid="email-from-name"
                        />
                      </div>
                    </div>

                    {/* Save Button */}
                    <div className="flex justify-end">
                      <button
                        type="submit"
                        disabled={emailSaveLoading}
                        className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                        data-testid="email-save-button"
                      >
                        {emailSaveLoading ? (
                          <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            <span>Saving...</span>
                          </>
                        ) : (
                          <>
                            <Settings className="w-5 h-5" />
                            <span>Save Configuration</span>
                          </>
                        )}
                      </button>
                    </div>

                    {/* Test Email Section */}
                    <div className="border-t border-gray-200 pt-6 mt-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Test Email Configuration</h3>
                      <div className="flex space-x-4">
                        <input
                          type="email"
                          value={testEmail}
                          onChange={(e) => setTestEmail(e.target.value)}
                          placeholder="test@example.com"
                          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                          data-testid="email-test-input"
                        />
                        <button
                          type="button"
                          onClick={handleTestEmail}
                          disabled={emailTestLoading || !testEmail}
                          className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                          data-testid="email-test-button"
                        >
                          {emailTestLoading ? (
                            <>
                              <Loader2 className="w-5 h-5 animate-spin" />
                              <span>Sending...</span>
                            </>
                          ) : (
                            <>
                              <Mail className="w-5 h-5" />
                              <span>Send Test Email</span>
                            </>
                          )}
                        </button>
                      </div>
                      <p className="text-sm text-gray-500 mt-2">
                        💡 Make sure to save your configuration before testing
                      </p>
                    </div>
                  </form>
                </>
              )}
            </div>
          )}

          {/* Slack Configuration */}
          {activeTab === 'slack' && (
            <div data-testid="slack-config-section">
              {slackLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
                </div>
              ) : (
                <>
                  {slackMessage && (
                    <div className="mb-6">
                      <MessageAlert message={slackMessage} />
                    </div>
                  )}

                  <form onSubmit={handleSaveSlackConfig} className="space-y-6">
                    {/* Mock Mode Toggle */}
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <label className="flex items-center space-x-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={slackConfig.mock_slack}
                          onChange={(e) => setSlackConfig({ ...slackConfig, mock_slack: e.target.checked })}
                          className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                          data-testid="slack-mock-toggle"
                        />
                        <div>
                          <span className="font-medium text-gray-900">Mock Mode (Development)</span>
                          <p className="text-sm text-gray-600">
                            When enabled, Slack messages are logged to console instead of being sent
                          </p>
                        </div>
                      </label>
                    </div>

                    {/* Webhook URL */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Slack Webhook URL *
                      </label>
                      <input
                        type="url"
                        value={slackConfig.slack_webhook_url}
                        onChange={(e) => setSlackConfig({ ...slackConfig, slack_webhook_url: e.target.value })}
                        placeholder="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        required
                        data-testid="slack-webhook-url"
                      />
                      <p className="text-sm text-gray-500 mt-2">
                        📖 Get your webhook URL from{' '}
                        <a
                          href="https://api.slack.com/messaging/webhooks"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary-600 hover:underline"
                        >
                          Slack Incoming Webhooks
                        </a>
                      </p>
                    </div>

                    {/* Save and Test Buttons */}
                    <div className="flex justify-between items-center">
                      <button
                        type="button"
                        onClick={handleTestSlack}
                        disabled={slackTestLoading || !slackConfig.slack_webhook_url}
                        className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                        data-testid="slack-test-button"
                      >
                        {slackTestLoading ? (
                          <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            <span>Testing...</span>
                          </>
                        ) : (
                          <>
                            <Send className="w-5 h-5" />
                            <span>Send Test Message</span>
                          </>
                        )}
                      </button>

                      <button
                        type="submit"
                        disabled={slackSaveLoading}
                        className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                        data-testid="slack-save-button"
                      >
                        {slackSaveLoading ? (
                          <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            <span>Saving...</span>
                          </>
                        ) : (
                          <>
                            <Settings className="w-5 h-5" />
                            <span>Save Configuration</span>
                          </>
                        )}
                      </button>
                    </div>

                    <p className="text-sm text-gray-500">
                      💡 Make sure to save your configuration before testing
                    </p>

                    {/* Help Section */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-6">
                      <h4 className="font-medium text-blue-900 mb-2">How to set up Slack Webhooks:</h4>
                      <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
                        <li>Go to your Slack workspace settings</li>
                        <li>Navigate to "Apps" and search for "Incoming Webhooks"</li>
                        <li>Add the app to your workspace</li>
                        <li>Choose a channel for notifications</li>
                        <li>Copy the webhook URL and paste it above</li>
                      </ol>
                    </div>
                  </form>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default IntegrationsPage;
