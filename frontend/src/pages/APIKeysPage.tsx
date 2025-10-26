/**
 * API Keys Management Page
 * Comprehensive CRUD interface for API key management
 */

import React, { useState, useEffect } from 'react';
import {
  Key, Plus, Copy, RotateCw, Trash2, Edit, Eye, EyeOff, Clock,
  Activity, TrendingUp, AlertCircle, Check, X, Settings, Search,
  Calendar, Shield, BarChart3, RefreshCw
} from 'lucide-react';
import apiKeyService, {
  APIKey,
  APIKeyCreate,
  APIKeyCreated,
  APIScope,
  APIKeyUsageStats
} from '../services/apiKeyService';

const APIKeysPage: React.FC = () => {
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [scopes, setScopes] = useState<APIScope[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showUsageModal, setShowUsageModal] = useState(false);
  const [selectedKeyId, setSelectedKeyId] = useState<string | null>(null);
  const [usageStats, setUsageStats] = useState<APIKeyUsageStats | null>(null);
  const [createdKey, setCreatedKey] = useState<APIKeyCreated | null>(null);
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [includeInactive, setIncludeInactive] = useState(false);

  // Form state
  const [formData, setFormData] = useState<APIKeyCreate>({
    name: '',
    description: '',
    scopes: [],
    rate_limit_per_minute: 60,
    rate_limit_per_hour: 1000,
    rate_limit_per_day: 10000,
    expires_at: ''
  });

  useEffect(() => {
    loadData();
  }, [includeInactive]);

  const loadData = async () => {
    try {
      const [keysData, scopesData] = await Promise.all([
        apiKeyService.listAPIKeys(includeInactive),
        apiKeyService.getAvailableScopes()
      ]);
      setApiKeys(keysData);
      setScopes(scopesData);
    } catch (error) {
      showMessage('error', 'Failed to load API keys');
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const handleCreateKey = async () => {
    try {
      const created = await apiKeyService.createAPIKey(formData);
      setCreatedKey(created);
      setShowCreateModal(false);
      setShowKeyModal(true);
      await loadData();
      resetForm();
      showMessage('success', 'API key created successfully!');
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to create API key');
    }
  };

  const handleRotateKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to rotate this API key? The old key will be invalidated immediately.')) {
      return;
    }
    try {
      const rotated = await apiKeyService.rotateAPIKey(keyId);
      setCreatedKey({ ...apiKeys.find(k => k.id === keyId)!, api_key: rotated.api_key });
      setShowKeyModal(true);
      await loadData();
      showMessage('success', 'API key rotated successfully!');
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to rotate API key');
    }
  };

  const handleDeleteKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      return;
    }
    try {
      await apiKeyService.deleteAPIKey(keyId);
      await loadData();
      showMessage('success', 'API key deleted successfully!');
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to delete API key');
    }
  };

  const handleToggleActive = async (key: APIKey) => {
    try {
      await apiKeyService.updateAPIKey(key.id, { is_active: !key.is_active });
      await loadData();
      showMessage('success', `API key ${key.is_active ? 'deactivated' : 'activated'} successfully!`);
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to update API key');
    }
  };

  const handleViewUsage = async (keyId: string) => {
    try {
      const stats = await apiKeyService.getAPIKeyUsage(keyId);
      setUsageStats(stats);
      setSelectedKeyId(keyId);
      setShowUsageModal(true);
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to load usage statistics');
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    showMessage('success', 'Copied to clipboard!');
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      scopes: [],
      rate_limit_per_minute: 60,
      rate_limit_per_hour: 1000,
      rate_limit_per_day: 10000,
      expires_at: ''
    });
  };

  const toggleScope = (scope: string) => {
    setFormData({
      ...formData,
      scopes: formData.scopes.includes(scope)
        ? formData.scopes.filter(s => s !== scope)
        : [...formData.scopes, scope]
    });
  };

  const selectAllScopesInCategory = (category: string) => {
    const categoryScopes = scopes.filter(s => s.category === category).map(s => s.scope);
    const allSelected = categoryScopes.every(s => formData.scopes.includes(s));
    
    if (allSelected) {
      setFormData({
        ...formData,
        scopes: formData.scopes.filter(s => !categoryScopes.includes(s))
      });
    } else {
      setFormData({
        ...formData,
        scopes: [...new Set([...formData.scopes, ...categoryScopes])]
      });
    }
  };

  const filteredKeys = apiKeys.filter(key =>
    key.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    key.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const scopesByCategory = scopes.reduce((acc, scope) => {
    if (!acc[scope.category]) acc[scope.category] = [];
    acc[scope.category].push(scope);
    return acc;
  }, {} as Record<string, APIScope[]>);

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
            API Keys Management
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Create and manage API keys for programmatic access to your analytics platform
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
                  placeholder="Search API keys..."
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
                data-testid="create-api-key-button"
              >
                <Plus className="w-5 h-5" />
                <span>Create API Key</span>
              </button>
            </div>
          </div>
        </div>

        {/* API Keys Table */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          {filteredKeys.length === 0 ? (
            <div className="text-center py-12 text-gray-500 dark:text-gray-400">
              <Key className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No API keys found</p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="mt-4 text-purple-600 hover:text-purple-700 font-medium"
              >
                Create your first API key
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Key Prefix
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Scopes
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Rate Limits
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Requests
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {filteredKeys.map((key) => (
                    <tr key={key.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50" data-testid={`api-key-row-${key.id}`}>
                      <td className="px-6 py-4">
                        <div>
                          <div className="font-medium text-gray-900 dark:text-white">{key.name}</div>
                          {key.description && (
                            <div className="text-sm text-gray-500 dark:text-gray-400">{key.description}</div>
                          )}
                          {key.last_used_at && (
                            <div className="text-xs text-gray-400 dark:text-gray-500 flex items-center mt-1">
                              <Clock className="w-3 h-3 mr-1" />
                              Last used {new Date(key.last_used_at).toLocaleString()}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <code className="text-sm bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                          {key.key_prefix}***
                        </code>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1">
                          {key.scopes.slice(0, 3).map((scope) => (
                            <span
                              key={scope}
                              className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200"
                            >
                              {scope}
                            </span>
                          ))}
                          {key.scopes.length > 3 && (
                            <span className="text-xs text-gray-500 dark:text-gray-400">+{key.scopes.length - 3} more</span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">
                        <div>{key.rate_limit_per_minute}/min</div>
                        <div className="text-xs text-gray-400">{key.rate_limit_per_hour}/hr</div>
                      </td>
                      <td className="px-6 py-4">
                        <button
                          onClick={() => handleViewUsage(key.id)}
                          className="text-purple-600 hover:text-purple-700 font-medium text-sm flex items-center space-x-1"
                          data-testid={`view-usage-button-${key.id}`}
                        >
                          <Activity className="w-4 h-4" />
                          <span>{key.request_count}</span>
                        </button>
                      </td>
                      <td className="px-6 py-4">
                        <button
                          onClick={() => handleToggleActive(key)}
                          className="relative inline-flex items-center"
                          data-testid={`toggle-status-button-${key.id}`}
                        >
                          {key.is_active ? (
                            <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs rounded-full flex items-center space-x-1">
                              <Check className="w-3 h-3" />
                              <span>Active</span>
                            </span>
                          ) : (
                            <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-xs rounded-full flex items-center space-x-1">
                              <X className="w-3 h-3" />
                              <span>Inactive</span>
                            </span>
                          )}
                        </button>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleRotateKey(key.id)}
                            className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200"
                            title="Rotate key"
                            data-testid={`rotate-key-button-${key.id}`}
                          >
                            <RotateCw className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteKey(key.id)}
                            className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                            title="Delete key"
                            data-testid={`delete-key-button-${key.id}`}
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Create API Key Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto" data-testid="create-api-key-modal">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Create API Key</h2>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Configure your new API key with scopes and rate limits
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
                      placeholder="Production API Key"
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                      data-testid="api-key-name-input"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Expires At (Optional)
                    </label>
                    <input
                      type="datetime-local"
                      value={formData.expires_at}
                      onChange={(e) => setFormData({ ...formData, expires_at: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                      data-testid="api-key-expires-input"
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
                    placeholder="Describe the purpose of this API key..."
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                    data-testid="api-key-description-input"
                  />
                </div>

                {/* Scopes */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Scopes * ({formData.scopes.length} selected)
                  </label>
                  <div className="space-y-3" data-testid="scopes-selector">
                    {Object.entries(scopesByCategory).map(([category, categoryScopes]) => {
                      const allSelected = categoryScopes.every(s => formData.scopes.includes(s.scope));
                      return (
                        <div key={category} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-semibold text-gray-900 dark:text-white">{category}</h4>
                            <button
                              onClick={() => selectAllScopesInCategory(category)}
                              className="text-xs text-purple-600 hover:text-purple-700 font-medium"
                            >
                              {allSelected ? 'Deselect All' : 'Select All'}
                            </button>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            {categoryScopes.map((scope) => (
                              <label key={scope.scope} className="flex items-start space-x-2 cursor-pointer">
                                <input
                                  type="checkbox"
                                  checked={formData.scopes.includes(scope.scope)}
                                  onChange={() => toggleScope(scope.scope)}
                                  className="mt-1 rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                                />
                                <div>
                                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                                    {scope.scope}
                                  </div>
                                  <div className="text-xs text-gray-500 dark:text-gray-400">
                                    {scope.description}
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

                {/* Rate Limits */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Rate Limits
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Per Minute</label>
                      <input
                        type="number"
                        value={formData.rate_limit_per_minute}
                        onChange={(e) => setFormData({ ...formData, rate_limit_per_minute: parseInt(e.target.value) })}
                        min="1"
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                        data-testid="rate-limit-minute-input"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Per Hour</label>
                      <input
                        type="number"
                        value={formData.rate_limit_per_hour}
                        onChange={(e) => setFormData({ ...formData, rate_limit_per_hour: parseInt(e.target.value) })}
                        min="1"
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                        data-testid="rate-limit-hour-input"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Per Day</label>
                      <input
                        type="number"
                        value={formData.rate_limit_per_day}
                        onChange={(e) => setFormData({ ...formData, rate_limit_per_day: parseInt(e.target.value) })}
                        min="1"
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                        data-testid="rate-limit-day-input"
                      />
                    </div>
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
                  onClick={handleCreateKey}
                  disabled={!formData.name || formData.scopes.length === 0}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  data-testid="submit-create-button"
                >
                  Create API Key
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Show Key Modal */}
        {showKeyModal && createdKey && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full" data-testid="show-key-modal">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">API Key Created!</h2>
              </div>
              
              <div className="p-6 space-y-4">
                <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-semibold text-yellow-800 dark:text-yellow-200 mb-1">
                        Save this key now!
                      </h4>
                      <p className="text-sm text-yellow-700 dark:text-yellow-300">
                        This is the only time you'll see the full API key. Store it securely.
                      </p>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Your API Key
                  </label>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={createdKey.api_key}
                      readOnly
                      className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 dark:text-white font-mono text-sm"
                      data-testid="created-api-key-value"
                    />
                    <button
                      onClick={() => copyToClipboard(createdKey.api_key)}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2"
                      data-testid="copy-api-key-button"
                    >
                      <Copy className="w-4 h-4" />
                      <span>Copy</span>
                    </button>
                  </div>
                </div>
              </div>

              <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end">
                <button
                  onClick={() => {
                    setShowKeyModal(false);
                    setCreatedKey(null);
                  }}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  data-testid="close-key-modal-button"
                >
                  I've saved my key
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Usage Stats Modal */}
        {showUsageModal && usageStats && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto" data-testid="usage-stats-modal">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Usage Statistics</h2>
              </div>
              
              <div className="p-6 space-y-6">
                {/* Overview Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-blue-600 dark:text-blue-400">Total Requests</p>
                        <p className="text-2xl font-bold text-blue-900 dark:text-blue-200">
                          {usageStats.total_requests.toLocaleString()}
                        </p>
                      </div>
                      <BarChart3 className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                    </div>
                  </div>
                  <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-green-600 dark:text-green-400">Last 24 Hours</p>
                        <p className="text-2xl font-bold text-green-900 dark:text-green-200">
                          {usageStats.requests_last_24h.toLocaleString()}
                        </p>
                      </div>
                      <TrendingUp className="w-8 h-8 text-green-600 dark:text-green-400" />
                    </div>
                  </div>
                  <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-purple-600 dark:text-purple-400">Avg Response Time</p>
                        <p className="text-2xl font-bold text-purple-900 dark:text-purple-200">
                          {usageStats.avg_response_time_ms?.toFixed(0) || 0}ms
                        </p>
                      </div>
                      <Activity className="w-8 h-8 text-purple-600 dark:text-purple-400" />
                    </div>
                  </div>
                </div>

                {/* Time Period Stats */}
                <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Request History</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Last 7 days</span>
                      <span className="font-semibold text-gray-900 dark:text-white">{usageStats.requests_last_7d.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Last 30 days</span>
                      <span className="font-semibold text-gray-900 dark:text-white">{usageStats.requests_last_30d.toLocaleString()}</span>
                    </div>
                    {usageStats.error_rate !== undefined && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600 dark:text-gray-400">Error Rate</span>
                        <span className="font-semibold text-red-600 dark:text-red-400">{(usageStats.error_rate * 100).toFixed(2)}%</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Most Used Endpoints */}
                {usageStats.most_used_endpoints.length > 0 && (
                  <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Most Used Endpoints</h3>
                    <div className="space-y-2">
                      {usageStats.most_used_endpoints.map((endpoint, index) => (
                        <div key={index} className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <span className="text-xs font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                              {endpoint.method}
                            </span>
                            <span className="text-sm text-gray-900 dark:text-white">{endpoint.endpoint}</span>
                          </div>
                          <span className="text-sm font-semibold text-gray-600 dark:text-gray-400">
                            {endpoint.count.toLocaleString()}
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
                    setShowUsageModal(false);
                    setUsageStats(null);
                    setSelectedKeyId(null);
                  }}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                  data-testid="close-usage-modal-button"
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

export default APIKeysPage;
