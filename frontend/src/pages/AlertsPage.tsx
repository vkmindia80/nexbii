import React, { useState, useEffect } from 'react';
import { Bell, Plus, Play, Pause, Trash2, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import alertService, { Alert, CreateAlertRequest } from '../services/alertService';
import { queryService } from '../services/queryService';
import { Query } from '../types';

const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [queries, setQueries] = useState<Query[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [alertsData, queriesData] = await Promise.all([
        alertService.getAlerts(),
        queryService.getQueries()
      ]);
      setAlerts(alertsData);
      setQueries(queriesData);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAlert = async (alertId: string) => {
    if (!window.confirm('Are you sure you want to delete this alert?')) return;
    
    try {
      await alertService.deleteAlert(alertId);
      setAlerts(alerts.filter(a => a.id !== alertId));
    } catch (error) {
      console.error('Failed to delete alert:', error);
      alert('Failed to delete alert');
    }
  };

  const handleToggleActive = async (alert: Alert) => {
    try {
      const updated = await alertService.updateAlert(alert.id, {
        is_active: !alert.is_active
      });
      setAlerts(alerts.map(a => a.id === alert.id ? updated : a));
    } catch (error) {
      console.error('Failed to update alert:', error);
    }
  };

  const handleTestAlert = async (alertId: string) => {
    try {
      await alertService.evaluateAlert(alertId);
      alert('Alert evaluated successfully!');
    } catch (error) {
      console.error('Failed to evaluate alert:', error);
      alert('Failed to evaluate alert');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'triggered': return 'bg-red-100 text-red-800';
      case 'paused': return 'bg-gray-100 text-gray-800';
      case 'snoozed': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getConditionLabel = (type: string) => {
    const labels: Record<string, string> = {
      'greater_than': '>',
      'less_than': '<',
      'equals': '=',
      'not_equals': '≠',
      'between': 'between'
    };
    return labels[type] || type;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div data-testid="alerts-page">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Alerts</h1>
          <p className="mt-1 text-sm text-gray-600">
            Monitor your queries and get notified when conditions are met
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
          data-testid="create-alert-btn"
        >
          <Plus className="h-5 w-5 mr-2" />
          Create Alert
        </button>
      </div>

      {alerts.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border-2 border-dashed border-gray-300">
          <Bell className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No alerts</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating a new alert to monitor your queries.
          </p>
          <div className="mt-6">
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              <Plus className="h-5 w-5 mr-2" />
              Create Alert
            </button>
          </div>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
              data-testid={`alert-card-${alert.id}`}
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold text-gray-900 flex-1">
                  {alert.name}
                </h3>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(alert.status)}`}>
                  {alert.status}
                </span>
              </div>

              {alert.description && (
                <p className="text-sm text-gray-600 mb-4">{alert.description}</p>
              )}

              <div className="space-y-2 mb-4 text-sm">
                <div className="flex items-center text-gray-700">
                  <span className="font-medium mr-2">Condition:</span>
                  <span className="font-mono bg-gray-100 px-2 py-1 rounded">
                    {alert.metric_column} {getConditionLabel(alert.condition_type)} {alert.threshold_value}
                  </span>
                </div>
                <div className="flex items-center text-gray-700">
                  <Clock className="h-4 w-4 mr-2" />
                  <span>Check {alert.frequency}</span>
                </div>
                {alert.last_triggered_at && (
                  <div className="flex items-center text-red-600">
                    <AlertCircle className="h-4 w-4 mr-2" />
                    <span className="text-xs">
                      Last triggered: {new Date(alert.last_triggered_at).toLocaleString()}
                    </span>
                  </div>
                )}
              </div>

              <div className="flex justify-between items-center pt-4 border-t">
                <button
                  onClick={() => handleToggleActive(alert)}
                  className="text-sm text-gray-600 hover:text-gray-900 flex items-center"
                  title={alert.is_active ? 'Pause' : 'Activate'}
                >
                  {alert.is_active ? (
                    <Pause className="h-4 w-4 mr-1" />
                  ) : (
                    <Play className="h-4 w-4 mr-1" />
                  )}
                </button>
                <button
                  onClick={() => handleTestAlert(alert.id)}
                  className="text-sm text-indigo-600 hover:text-indigo-900"
                >
                  Test
                </button>
                <button
                  onClick={() => handleDeleteAlert(alert.id)}
                  className="text-sm text-red-600 hover:text-red-900"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreateModal && (
        <AlertBuilderModal
          queries={queries}
          onClose={() => setShowCreateModal(false)}
          onSave={() => {
            setShowCreateModal(false);
            fetchData();
          }}
        />
      )}
    </div>
  );
};

// Alert Builder Modal Component
interface AlertBuilderModalProps {
  queries: Query[];
  onClose: () => void;
  onSave: () => void;
}

const AlertBuilderModal: React.FC<AlertBuilderModalProps> = ({ queries, onClose, onSave }) => {
  const [formData, setFormData] = useState<CreateAlertRequest>({
    name: '',
    description: '',
    query_id: '',
    condition_type: 'greater_than',
    metric_column: '',
    threshold_value: 0,
    frequency: 'once',
    notify_emails: [],
    notify_slack: false,
    slack_webhook: ''
  });
  const [emailInput, setEmailInput] = useState('');
  const [testingWebhook, setTestingWebhook] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await alertService.createAlert(formData);
      onSave();
    } catch (error) {
      console.error('Failed to create alert:', error);
      alert('Failed to create alert');
    }
  };

  const addEmail = () => {
    if (emailInput && emailInput.includes('@')) {
      setFormData({
        ...formData,
        notify_emails: [...(formData.notify_emails || []), emailInput]
      });
      setEmailInput('');
    }
  };

  const removeEmail = (email: string) => {
    setFormData({
      ...formData,
      notify_emails: formData.notify_emails?.filter(e => e !== email) || []
    });
  };

  const testSlackWebhook = async () => {
    if (!formData.slack_webhook) {
      alert('Please enter a Slack webhook URL first');
      return;
    }

    try {
      setTestingWebhook(true);
      await alertService.testSlackWebhook(formData.slack_webhook);
      alert('✅ Test message sent successfully! Check your Slack channel.');
    } catch (error) {
      console.error('Failed to test webhook:', error);
      alert('❌ Failed to send test message. Please check your webhook URL.');
    } finally {
      setTestingWebhook(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">Create Alert</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Alert Name *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="e.g., High Revenue Alert"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              rows={2}
              placeholder="Optional description"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Query *
            </label>
            <select
              required
              value={formData.query_id}
              onChange={(e) => setFormData({ ...formData, query_id: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Select a query</option>
              {queries.map((query) => (
                <option key={query.id} value={query.id}>
                  {query.name}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Metric Column *
              </label>
              <input
                type="text"
                required
                value={formData.metric_column}
                onChange={(e) => setFormData({ ...formData, metric_column: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="e.g., total_revenue"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Condition *
              </label>
              <select
                value={formData.condition_type}
                onChange={(e) => setFormData({ ...formData, condition_type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="greater_than">Greater than (&gt;)</option>
                <option value="less_than">Less than (&lt;)</option>
                <option value="equals">Equals (=)</option>
                <option value="not_equals">Not equals (≠)</option>
                <option value="between">Between</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Threshold Value *
            </label>
            <input
              type="number"
              step="any"
              required
              value={formData.threshold_value}
              onChange={(e) => setFormData({ ...formData, threshold_value: parseFloat(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Check Frequency
            </label>
            <select
              value={formData.frequency}
              onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="once">Once</option>
              <option value="hourly">Hourly</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notification Emails
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="email"
                value={emailInput}
                onChange={(e) => setEmailInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addEmail())}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Enter email address"
              />
              <button
                type="button"
                onClick={addEmail}
                className="px-4 py-2 bg-gray-200 rounded-md hover:bg-gray-300"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.notify_emails?.map((email, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-indigo-100 text-indigo-800"
                >
                  {email}
                  <button
                    type="button"
                    onClick={() => removeEmail(email)}
                    className="ml-2 text-indigo-600 hover:text-indigo-900"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Slack Notifications Section */}
          <div className="border-t pt-4">
            <div className="flex items-center mb-4">
              <input
                type="checkbox"
                id="notify_slack"
                checked={formData.notify_slack}
                onChange={(e) => setFormData({ ...formData, notify_slack: e.target.checked })}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label htmlFor="notify_slack" className="ml-2 block text-sm font-medium text-gray-700">
                Send notifications to Slack
              </label>
            </div>

            {formData.notify_slack && (
              <div className="space-y-3 pl-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Slack Webhook URL *
                  </label>
                  <input
                    type="url"
                    required={formData.notify_slack}
                    value={formData.slack_webhook}
                    onChange={(e) => setFormData({ ...formData, slack_webhook: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="https://hooks.slack.com/services/..."
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Get your webhook URL from Slack's Incoming Webhooks app
                  </p>
                </div>
                <button
                  type="button"
                  onClick={testSlackWebhook}
                  disabled={testingWebhook || !formData.slack_webhook}
                  className="text-sm px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 disabled:opacity-50"
                >
                  {testingWebhook ? 'Testing...' : 'Test Webhook'}
                </button>
              </div>
            )}
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700"
            >
              Create Alert
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AlertsPage;
