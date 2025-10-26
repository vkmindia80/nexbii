/**
 * Webhooks Management Page
 * Comprehensive webhook CRUD with delivery logs and testing
 */

import React, { useState, useEffect } from 'react';
import {
  Webhook as WebhookIcon, Plus, Trash2, Play, CheckCircle, XCircle,
  AlertCircle, Check, Clock, TrendingUp, Activity, Globe, Settings,
  Search, RefreshCw, ExternalLink, Filter, ChevronDown, ChevronUp
} from 'lucide-react';
import webhookService, {
  Webhook,
  WebhookCreate,
  WebhookEvent,
  WebhookDelivery,
  WebhookStats
} from '../services/webhookService';

const WebhooksPage: React.FC = () => {
  const [webhooks, setWebhooks] = useState<Webhook[]>([]);
  const [events, setEvents] = useState<WebhookEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDeliveriesModal, setShowDeliveriesModal] = useState(false);
  const [showStatsModal, setShowStatsModal] = useState(false);
  const [selectedWebhookId, setSelectedWebhookId] = useState<string | null>(null);
  const [deliveries, setDeliveries] = useState<WebhookDelivery[]>([]);
  const [stats, setStats] = useState<WebhookStats | null>(null);
  const [testResult, setTestResult] = useState<any>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [includeInactive, setIncludeInactive] = useState(false);
  const [expandedWebhook, setExpandedWebhook] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState<WebhookCreate>({
    name: '',
    description: '',
    url: '',
    events: [],
    secret: '',
    max_retries: 3,
    retry_backoff_seconds: 60
  });

  useEffect(() => {
    loadData();
  }, [includeInactive]);

  const loadData = async () => {
    try {
      const [webhooksData, eventsData] = await Promise.all([
        webhookService.listWebhooks(includeInactive),
        webhookService.getAvailableEvents()
      ]);
      setWebhooks(webhooksData);
      setEvents(eventsData);
    } catch (error) {
      showMessage('error', 'Failed to load webhooks');
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const handleCreateWebhook = async () => {
    try {
      await webhookService.createWebhook(formData);
      setShowCreateModal(false);
      await loadData();
      resetForm();
      showMessage('success', 'Webhook created successfully!');
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to create webhook');
    }
  };

  const handleToggleActive = async (webhook: Webhook) => {
    try {
      await webhookService.updateWebhook(webhook.id, { is_active: !webhook.is_active });
      await loadData();
      showMessage('success', `Webhook ${webhook.is_active ? 'deactivated' : 'activated'} successfully!`);
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to update webhook');
    }
  };

  const handleDeleteWebhook = async (webhookId: string) => {
    if (!confirm('Are you sure you want to delete this webhook? This action cannot be undone.')) {
      return;
    }
    try {
      await webhookService.deleteWebhook(webhookId);
      await loadData();
      showMessage('success', 'Webhook deleted successfully!');
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to delete webhook');
    }
  };

  const handleTestWebhook = async (webhookId: string) => {
    try {
      const result = await webhookService.testWebhook(webhookId);
      setTestResult(result);
      showMessage(
        result.success ? 'success' : 'error',
        result.success ? 'Webhook test successful!' : `Test failed: ${result.error_message}`
      );
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to test webhook');
    }
  };

  const handleViewDeliveries = async (webhookId: string) => {
    try {
      const deliveriesData = await webhookService.getWebhookDeliveries(webhookId);
      setDeliveries(deliveriesData);
      setSelectedWebhookId(webhookId);
      setShowDeliveriesModal(true);
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to load deliveries');
    }
  };

  const handleViewStats = async (webhookId: string) => {
    try {
      const statsData = await webhookService.getWebhookStats(webhookId);
      setStats(statsData);
      setSelectedWebhookId(webhookId);
      setShowStatsModal(true);
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to load statistics');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      url: '',
      events: [],
      secret: '',
      max_retries: 3,
      retry_backoff_seconds: 60
    });
  };

  const toggleEvent = (event: string) => {
    setFormData({
      ...formData,
      events: formData.events.includes(event)
        ? formData.events.filter(e => e !== event)
        : [...formData.events, event]
    });
  };

  const selectAllEventsInCategory = (category: string) => {
    const categoryEvents = events.filter(e => e.category === category).map(e => e.event);
    const allSelected = categoryEvents.every(e => formData.events.includes(e));
    
    if (allSelected) {
      setFormData({
        ...formData,
        events: formData.events.filter(e => !categoryEvents.includes(e))
      });
    } else {
      setFormData({
        ...formData,
        events: [...new Set([...formData.events, ...categoryEvents])]
      });
    }
  };

  const generateSecret = () => {
    const secret = Array.from(crypto.getRandomValues(new Uint8Array(32)))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
    setFormData({ ...formData, secret });
  };

  const filteredWebhooks = webhooks.filter(webhook =>
    webhook.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    webhook.url.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const eventsByCategory = events.reduce((acc, event) => {
    if (!acc[event.category]) acc[event.category] = [];
    acc[event.category].push(event);
    return acc;
  }, {} as Record<string, WebhookEvent[]>);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2" data-testid="page-title">
            Webhooks Management
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Configure webhooks to receive real-time notifications about events in your platform
          </p>
        </div>

        {/* Message */}
        {message && (
          <div
            className={`mb-6 p-4 rounded-lg flex items-start space-x-3 ${
              message.type === 'success'
                ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200'
                : 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200'
            }`}
            data-testid="notification-message"
          >
            {message.type === 'success' ? (
              <Check className="w-5 h-5 flex-shrink-0 mt-0.5" />
            ) : (
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            )}
            <p>{message.text}</p>
          </div>
        )}

        {/* Actions Bar */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 mb-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
            <div className="flex-1 max-w-md">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search webhooks..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                  data-testid="search-input"
                />
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <label className="flex items-center space-x-2 text-sm text-gray-700 dark:text-gray-300">
                <input
                  type="checkbox"
                  checked={includeInactive}
                  onChange={(e) => setIncludeInactive(e.target.checked)}
                  className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                  data-testid="include-inactive-checkbox"
                />
                <span>Show inactive</span>
              </label>
              <button
                onClick={() => setShowCreateModal(true)}
                className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                data-testid="create-webhook-button"
              >
                <Plus className="w-5 h-5" />
                <span>Create Webhook</span>
              </button>
            </div>
          </div>
        </div>

        {/* Webhooks List */}
        <div className="space-y-4">
          {filteredWebhooks.length === 0 ? (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 text-center py-12">
              <WebhookIcon className="w-12 h-12 mx-auto mb-3 opacity-50 text-gray-400" />
              <p className="text-gray-500 dark:text-gray-400">No webhooks found</p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="mt-4 text-purple-600 hover:text-purple-700 font-medium"
              >
                Create your first webhook
              </button>
            </div>
          ) : (
            filteredWebhooks.map((webhook) => (
              <div
                key={webhook.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700"
                data-testid={`webhook-card-${webhook.id}`}
              >
                <div className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                          {webhook.name}
                        </h3>
                        {webhook.is_active ? (
                          <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs rounded-full flex items-center space-x-1">
                            <Check className="w-3 h-3" />
                            <span>Active</span>
                          </span>
                        ) : (
                          <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-xs rounded-full">
                            Inactive
                          </span>
                        )}
                      </div>
                      {webhook.description && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{webhook.description}</p>
                      )}
                      <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
                        <Globe className="w-4 h-4" />
                        <code className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">{webhook.url}</code>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleTestWebhook(webhook.id)}
                        className="p-2 text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                        title="Test webhook"
                        data-testid={`test-webhook-button-${webhook.id}`}
                      >
                        <Play className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => handleToggleActive(webhook)}
                        className="p-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200"
                        title="Toggle active"
                        data-testid={`toggle-webhook-button-${webhook.id}`}
                      >
                        <Settings className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => handleDeleteWebhook(webhook.id)}
                        className="p-2 text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                        title="Delete webhook"
                        data-testid={`delete-webhook-button-${webhook.id}`}
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => setExpandedWebhook(expandedWebhook === webhook.id ? null : webhook.id)}
                        className="p-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200"
                        data-testid={`expand-webhook-button-${webhook.id}`}
                      >
                        {expandedWebhook === webhook.id ? (
                          <ChevronUp className="w-5 h-5" />
                        ) : (
                          <ChevronDown className="w-5 h-5" />
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Stats Row */}
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-4">
                    <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
                      <p className="text-xs text-gray-600 dark:text-gray-400">Events</p>
                      <p className="text-lg font-semibold text-gray-900 dark:text-white">{webhook.events.length}</p>
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
                      <p className="text-xs text-gray-600 dark:text-gray-400">Total</p>
                      <p className="text-lg font-semibold text-gray-900 dark:text-white">{webhook.total_deliveries}</p>
                    </div>
                    <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                      <p className="text-xs text-green-600 dark:text-green-400">Success</p>
                      <p className="text-lg font-semibold text-green-900 dark:text-green-200">{webhook.successful_deliveries}</p>
                    </div>
                    <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                      <p className="text-xs text-red-600 dark:text-red-400">Failed</p>
                      <p className="text-lg font-semibold text-red-900 dark:text-red-200">{webhook.failed_deliveries}</p>
                    </div>
                    <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3">
                      <p className="text-xs text-purple-600 dark:text-purple-400">Success Rate</p>
                      <p className="text-lg font-semibold text-purple-900 dark:text-purple-200">
                        {webhook.total_deliveries > 0
                          ? ((webhook.successful_deliveries / webhook.total_deliveries) * 100).toFixed(0)
                          : 0}%
                      </p>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center space-x-3 mt-4">
                    <button
                      onClick={() => handleViewDeliveries(webhook.id)}
                      className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                      data-testid={`view-deliveries-button-${webhook.id}`}
                    >
                      <Clock className="w-4 h-4" />
                      <span>View Deliveries</span>
                    </button>
                    <button
                      onClick={() => handleViewStats(webhook.id)}
                      className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm"
                      data-testid={`view-stats-button-${webhook.id}`}
                    >
                      <Activity className="w-4 h-4" />
                      <span>Statistics</span>
                    </button>
                  </div>
                </div>

                {/* Expanded Details */}
                {expandedWebhook === webhook.id && (
                  <div className="border-t border-gray-200 dark:border-gray-700 p-6 bg-gray-50 dark:bg-gray-700/50">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Subscribed Events</h4>
                        <div className="flex flex-wrap gap-2">
                          {webhook.events.map((event) => (
                            <span
                              key={event}
                              className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200"
                            >
                              {event}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Configuration</h4>
                        <div className="space-y-1 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Max Retries:</span>
                            <span className="text-gray-900 dark:text-white">{webhook.max_retries}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Retry Backoff:</span>
                            <span className="text-gray-900 dark:text-white">{webhook.retry_backoff_seconds}s</span>
                          </div>
                          {webhook.last_triggered_at && (
                            <div className="flex justify-between">
                              <span className="text-gray-600 dark:text-gray-400">Last Triggered:</span>
                              <span className="text-gray-900 dark:text-white">
                                {new Date(webhook.last_triggered_at).toLocaleString()}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Create Webhook Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto" data-testid="create-webhook-modal">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Create Webhook</h2>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Configure a webhook to receive event notifications
                </p>
              </div>
              
              <div className="p-6 space-y-6">
                {/* Basic Info */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Name *
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="Production Webhook"
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                      data-testid="webhook-name-input"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Webhook URL *
                    </label>
                    <input
                      type="url"
                      value={formData.url}
                      onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                      placeholder="https://api.example.com/webhooks"
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                      data-testid="webhook-url-input"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Description (Optional)
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Describe the purpose of this webhook..."
                    rows={2}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                    data-testid="webhook-description-input"
                  />
                </div>

                {/* Secret */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Secret (Optional)
                  </label>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={formData.secret}
                      onChange={(e) => setFormData({ ...formData, secret: e.target.value })}
                      placeholder="Leave empty to auto-generate"
                      className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
                      data-testid="webhook-secret-input"
                    />
                    <button
                      onClick={generateSecret}
                      className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                      data-testid="generate-secret-button"
                    >
                      <RefreshCw className="w-4 h-4" />
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Used for HMAC-SHA256 signature verification
                  </p>
                </div>

                {/* Events */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Events * ({formData.events.length} selected)
                  </label>
                  <div className="space-y-3" data-testid="events-selector">
                    {Object.entries(eventsByCategory).map(([category, categoryEvents]) => {
                      const allSelected = categoryEvents.every(e => formData.events.includes(e.event));
                      return (
                        <div key={category} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-semibold text-gray-900 dark:text-white">{category}</h4>
                            <button
                              onClick={() => selectAllEventsInCategory(category)}
                              className="text-xs text-purple-600 hover:text-purple-700 font-medium"
                            >
                              {allSelected ? 'Deselect All' : 'Select All'}
                            </button>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            {categoryEvents.map((event) => (
                              <label key={event.event} className="flex items-start space-x-2 cursor-pointer">
                                <input
                                  type="checkbox"
                                  checked={formData.events.includes(event.event)}
                                  onChange={() => toggleEvent(event.event)}
                                  className="mt-1 rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                                />
                                <div>
                                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                                    {event.event}
                                  </div>
                                  <div className="text-xs text-gray-500 dark:text-gray-400">
                                    {event.description}
                                  </div>
                                </div>
                              </label>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Retry Configuration */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Max Retries
                    </label>
                    <input
                      type="number"
                      value={formData.max_retries}
                      onChange={(e) => setFormData({ ...formData, max_retries: parseInt(e.target.value) })}
                      min="0"
                      max="10"
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                      data-testid="webhook-max-retries-input"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Retry Backoff (seconds)
                    </label>
                    <input
                      type="number"
                      value={formData.retry_backoff_seconds}
                      onChange={(e) => setFormData({ ...formData, retry_backoff_seconds: parseInt(e.target.value) })}
                      min="1"
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                      data-testid="webhook-retry-backoff-input"
                    />
                  </div>
                </div>
              </div>

              <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    resetForm();
                  }}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  data-testid="cancel-create-button"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateWebhook}
                  disabled={!formData.name || !formData.url || formData.events.length === 0}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  data-testid="submit-create-button"
                >
                  Create Webhook
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Deliveries Modal */}
        {showDeliveriesModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-5xl w-full max-h-[90vh] overflow-y-auto" data-testid="deliveries-modal">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Delivery Logs</h2>
              </div>
              
              <div className="p-6">
                {deliveries.length === 0 ? (
                  <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                    <Clock className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No deliveries yet</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Event</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Status</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Response</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Time</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Attempts</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Date</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                        {deliveries.map((delivery) => (
                          <tr key={delivery.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                            <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">{delivery.event_type}</td>
                            <td className="px-4 py-3">
                              {delivery.status === 'delivered' ? (
                                <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs rounded-full flex items-center space-x-1 w-fit">
                                  <CheckCircle className="w-3 h-3" />
                                  <span>Success</span>
                                </span>
                              ) : delivery.status === 'failed' ? (
                                <span className="px-2 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 text-xs rounded-full flex items-center space-x-1 w-fit">
                                  <XCircle className="w-3 h-3" />
                                  <span>Failed</span>
                                </span>
                              ) : (
                                <span className="px-2 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 text-xs rounded-full flex items-center space-x-1 w-fit">
                                  <Clock className="w-3 h-3" />
                                  <span>Pending</span>
                                </span>
                              )}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                              {delivery.response_status_code || '-'}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                              {delivery.response_time_ms ? `${delivery.response_time_ms}ms` : '-'}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                              {delivery.attempt_count}/{delivery.max_attempts}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                              {new Date(delivery.created_at).toLocaleString()}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end">
                <button
                  onClick={() => {
                    setShowDeliveriesModal(false);
                    setDeliveries([]);
                    setSelectedWebhookId(null);
                  }}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                  data-testid="close-deliveries-modal-button"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Stats Modal */}
        {showStatsModal && stats && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto" data-testid="stats-modal">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Statistics</h2>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{stats.webhook_name}</p>
              </div>
              
              <div className="p-6 space-y-6">
                {/* Overview Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                    <p className="text-sm text-blue-600 dark:text-blue-400">Total Deliveries</p>
                    <p className="text-2xl font-bold text-blue-900 dark:text-blue-200">
                      {stats.total_deliveries.toLocaleString()}
                    </p>
                  </div>
                  <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                    <p className="text-sm text-green-600 dark:text-green-400">Successful</p>
                    <p className="text-2xl font-bold text-green-900 dark:text-green-200">
                      {stats.successful_deliveries.toLocaleString()}
                    </p>
                  </div>
                  <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                    <p className="text-sm text-red-600 dark:text-red-400">Failed</p>
                    <p className="text-2xl font-bold text-red-900 dark:text-red-200">
                      {stats.failed_deliveries.toLocaleString()}
                    </p>
                  </div>
                  <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                    <p className="text-sm text-purple-600 dark:text-purple-400">Success Rate</p>
                    <p className="text-2xl font-bold text-purple-900 dark:text-purple-200">
                      {(stats.success_rate * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>

                {/* Time Period Stats */}
                <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Delivery History</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Last 24 hours</span>
                      <span className="font-semibold text-gray-900 dark:text-white">{stats.deliveries_last_24h.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Last 7 days</span>
                      <span className="font-semibold text-gray-900 dark:text-white">{stats.deliveries_last_7d.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Last 30 days</span>
                      <span className="font-semibold text-gray-900 dark:text-white">{stats.deliveries_last_30d.toLocaleString()}</span>
                    </div>
                    {stats.avg_response_time_ms !== undefined && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600 dark:text-gray-400">Avg Response Time</span>
                        <span className="font-semibold text-gray-900 dark:text-white">{stats.avg_response_time_ms.toFixed(0)}ms</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Recent Deliveries */}
                {stats.recent_deliveries.length > 0 && (
                  <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Recent Deliveries</h3>
                    <div className="space-y-2">
                      {stats.recent_deliveries.slice(0, 5).map((delivery) => (
                        <div key={delivery.id} className="flex items-center justify-between text-sm">
                          <div className="flex items-center space-x-2">
                            {delivery.status === 'delivered' ? (
                              <CheckCircle className="w-4 h-4 text-green-600" />
                            ) : (
                              <XCircle className="w-4 h-4 text-red-600" />
                            )}
                            <span className="text-gray-900 dark:text-white">{delivery.event_type}</span>
                          </div>
                          <span className="text-gray-600 dark:text-gray-400">
                            {new Date(delivery.created_at).toLocaleString()}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end">
                <button
                  onClick={() => {
                    setShowStatsModal(false);
                    setStats(null);
                    setSelectedWebhookId(null);
                  }}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                  data-testid="close-stats-modal-button"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WebhooksPage;
