/**
 * Plugins Management Page
 * Comprehensive plugin management with installation, instances, and execution
 */

import React, { useState, useEffect } from 'react';
import {
  Puzzle, Plus, Trash2, Play, Power, Settings, Download, Upload,
  AlertCircle, Check, Grid, List, Search, Filter, Code, Box,
  BarChart3, Activity, Clock, RefreshCw, Eye, Edit, Copy, Terminal
} from 'lucide-react';
import pluginService, {
  Plugin,
  PluginDetail,
  PluginType,
  PluginInstance,
  PluginCreate,
  PluginInstanceCreate,
  PluginExecutionResult,
  PluginStats
} from '../services/pluginService';

type ViewMode = 'grid' | 'list';

const PluginsPage: React.FC = () => {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [pluginTypes, setPluginTypes] = useState<PluginType[]>([]);
  const [instances, setInstances] = useState<PluginInstance[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [showInstallModal, setShowInstallModal] = useState(false);
  const [showInstanceModal, setShowInstanceModal] = useState(false);
  const [showExecuteModal, setShowExecuteModal] = useState(false);
  const [showStatsModal, setShowStatsModal] = useState(false);
  const [selectedPlugin, setSelectedPlugin] = useState<PluginDetail | null>(null);
  const [selectedInstance, setSelectedInstance] = useState<PluginInstance | null>(null);
  const [stats, setStats] = useState<PluginStats | null>(null);
  const [executionResult, setExecutionResult] = useState<PluginExecutionResult | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('');

  // Form states
  const [installFormData, setInstallFormData] = useState<{
    manifest: string;
    files: string;
  }>({
    manifest: '',
    files: ''
  });

  const [instanceFormData, setInstanceFormData] = useState<PluginInstanceCreate>({
    plugin_id: '',
    name: '',
    config: {}
  });

  const [executeFormData, setExecuteFormData] = useState<{
    instance_id: string;
    input_data: string;
    params: string;
  }>({
    instance_id: '',
    input_data: '{}',
    params: '{}'
  });

  useEffect(() => {
    loadData();
  }, [typeFilter]);

  const loadData = async () => {
    try {
      const [pluginsData, typesData, instancesData] = await Promise.all([
        pluginService.listPlugins(typeFilter || undefined),
        pluginService.getPluginTypes(),
        pluginService.listInstances()
      ]);
      setPlugins(pluginsData);
      setPluginTypes(typesData);
      setInstances(instancesData);
    } catch (error) {
      showMessage('error', 'Failed to load plugins');
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const handleInstallPlugin = async () => {
    try {
      const manifest = JSON.parse(installFormData.manifest);
      const files = JSON.parse(installFormData.files);
      
      const pluginData: PluginCreate = {
        manifest,
        files
      };

      await pluginService.installPlugin(pluginData);
      setShowInstallModal(false);
      await loadData();
      resetInstallForm();
      showMessage('success', 'Plugin installed successfully!');
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to install plugin. Check JSON format.');
    }
  };

  const handleTogglePlugin = async (plugin: Plugin) => {
    try {
      await pluginService.updatePlugin(plugin.id, { is_enabled: !plugin.is_enabled });
      await loadData();
      showMessage('success', `Plugin ${plugin.is_enabled ? 'disabled' : 'enabled'} successfully!`);
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to update plugin');
    }
  };

  const handleUninstallPlugin = async (pluginId: string) => {
    if (!confirm('Are you sure you want to uninstall this plugin? All instances will be deleted.')) {
      return;
    }
    try {
      await pluginService.uninstallPlugin(pluginId);
      await loadData();
      showMessage('success', 'Plugin uninstalled successfully!');
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to uninstall plugin');
    }
  };

  const handleViewPluginDetails = async (pluginId: string) => {
    try {
      const details = await pluginService.getPlugin(pluginId);
      setSelectedPlugin(details);
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to load plugin details');
    }
  };

  const handleCreateInstance = async () => {
    try {
      const config = instanceFormData.config && typeof instanceFormData.config === 'string'
        ? JSON.parse(instanceFormData.config as string)
        : instanceFormData.config;

      await pluginService.createInstance({
        ...instanceFormData,
        config
      });
      setShowInstanceModal(false);
      await loadData();
      resetInstanceForm();
      showMessage('success', 'Plugin instance created successfully!');
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to create instance');
    }
  };

  const handleDeleteInstance = async (instanceId: string) => {
    if (!confirm('Are you sure you want to delete this instance?')) {
      return;
    }
    try {
      await pluginService.deleteInstance(instanceId);
      await loadData();
      showMessage('success', 'Instance deleted successfully!');
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to delete instance');
    }
  };

  const handleToggleInstance = async (instance: PluginInstance) => {
    try {
      await pluginService.updateInstance(instance.id, { is_enabled: !instance.is_enabled });
      await loadData();
      showMessage('success', `Instance ${instance.is_enabled ? 'disabled' : 'enabled'} successfully!`);
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to update instance');
    }
  };

  const handleExecutePlugin = async () => {
    try {
      const inputData = JSON.parse(executeFormData.input_data);
      const params = JSON.parse(executeFormData.params);

      const result = await pluginService.executePlugin(
        executeFormData.instance_id,
        inputData,
        params
      );
      setExecutionResult(result);
      await loadData();
      showMessage(result.success ? 'success' : 'error', 
        result.success ? 'Plugin executed successfully!' : `Execution failed: ${result.error}`
      );
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to execute plugin');
    }
  };

  const handleViewStats = async (pluginId: string) => {
    try {
      const statsData = await pluginService.getPluginStats(pluginId);
      setStats(statsData);
      setShowStatsModal(true);
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to load statistics');
    }
  };

  const resetInstallForm = () => {
    setInstallFormData({
      manifest: '',
      files: ''
    });
  };

  const resetInstanceForm = () => {
    setInstanceFormData({
      plugin_id: '',
      name: '',
      config: {}
    });
  };

  const filteredPlugins = plugins.filter(plugin =>
    plugin.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    plugin.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    plugin.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getPluginTypeIcon = (type: string) => {
    switch (type) {
      case 'visualization': return <BarChart3 className="w-5 h-5" />;
      case 'datasource': return <Box className="w-5 h-5" />;
      case 'transformation': return <Code className="w-5 h-5" />;
      case 'export': return <Download className="w-5 h-5" />;
      default: return <Puzzle className="w-5 h-5" />;
    }
  };

  const getPluginTypeBadgeColor = (type: string) => {
    switch (type) {
      case 'visualization': return 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200';
      case 'datasource': return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200';
      case 'transformation': return 'bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200';
      case 'export': return 'bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200';
      default: return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200';
    }
  };

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
            Plugins Management
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Install and manage plugins to extend your analytics platform
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
          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-3 md:space-y-0">
            <div className="flex items-center space-x-3">
              <div className="relative flex-1 md:w-64">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search plugins..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                  data-testid="search-input"
                />
              </div>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                data-testid="type-filter"
              >
                <option value="">All Types</option>
                {pluginTypes.map((type) => (
                  <option key={type.type} value={type.type}>
                    {type.type}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded ${
                    viewMode === 'grid'
                      ? 'bg-white dark:bg-gray-600 text-purple-600 dark:text-purple-400'
                      : 'text-gray-600 dark:text-gray-400'
                  }`}
                  data-testid="grid-view-button"
                >
                  <Grid className="w-5 h-5" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded ${
                    viewMode === 'list'
                      ? 'bg-white dark:bg-gray-600 text-purple-600 dark:text-purple-400'
                      : 'text-gray-600 dark:text-gray-400'
                  }`}
                  data-testid="list-view-button"
                >
                  <List className="w-5 h-5" />
                </button>
              </div>
              <button
                onClick={() => setShowInstallModal(true)}
                className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                data-testid="install-plugin-button"
              >
                <Plus className="w-5 h-5" />
                <span>Install Plugin</span>
              </button>
            </div>
          </div>
        </div>

        {/* Plugins Display */}
        {filteredPlugins.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 text-center py-12">
            <Puzzle className="w-12 h-12 mx-auto mb-3 opacity-50 text-gray-400" />
            <p className="text-gray-500 dark:text-gray-400">No plugins found</p>
            <button
              onClick={() => setShowInstallModal(true)}
              className="mt-4 text-purple-600 hover:text-purple-700 font-medium"
            >
              Install your first plugin
            </button>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPlugins.map((plugin) => {
              const pluginInstances = instances.filter(i => i.plugin_id === plugin.id);
              return (
                <div
                  key={plugin.id}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow"
                  data-testid={`plugin-card-${plugin.id}`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${getPluginTypeBadgeColor(plugin.plugin_type)}`}>
                        {getPluginTypeIcon(plugin.plugin_type)}
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white">{plugin.display_name}</h3>
                        <p className="text-xs text-gray-500 dark:text-gray-400">v{plugin.version}</p>
                      </div>
                    </div>
                    {plugin.is_verified && (
                      <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded-full">
                        Verified
                      </span>
                    )}
                  </div>

                  {plugin.description && (
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
                      {plugin.description}
                    </p>
                  )}

                  <div className="flex items-center justify-between mb-4 text-sm">
                    <div className="flex items-center space-x-4">
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Instances:</span>
                        <span className="ml-1 font-semibold text-gray-900 dark:text-white">{pluginInstances.length}</span>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Usage:</span>
                        <span className="ml-1 font-semibold text-gray-900 dark:text-white">{plugin.usage_count}</span>
                      </div>
                    </div>
                    <button
                      onClick={() => handleTogglePlugin(plugin)}
                      className={`p-1 rounded ${
                        plugin.is_enabled
                          ? 'text-green-600 hover:text-green-700'
                          : 'text-gray-400 hover:text-gray-600'
                      }`}
                      data-testid={`toggle-plugin-button-${plugin.id}`}
                    >
                      <Power className="w-5 h-5" />
                    </button>
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleViewPluginDetails(plugin.id)}
                      className="flex-1 px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-sm"
                      data-testid={`view-details-button-${plugin.id}`}
                    >
                      <Eye className="w-4 h-4 inline mr-1" />
                      Details
                    </button>
                    <button
                      onClick={() => {
                        setInstanceFormData({ ...instanceFormData, plugin_id: plugin.id });
                        setShowInstanceModal(true);
                      }}
                      className="flex-1 px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm"
                      data-testid={`create-instance-button-${plugin.id}`}
                    >
                      <Plus className="w-4 h-4 inline mr-1" />
                      Instance
                    </button>
                    <button
                      onClick={() => handleViewStats(plugin.id)}
                      className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                      data-testid={`view-stats-button-${plugin.id}`}
                    >
                      <BarChart3 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleUninstallPlugin(plugin.id)}
                      className="px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
                      data-testid={`uninstall-button-${plugin.id}`}
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Plugin</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Version</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Instances</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Usage</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {filteredPlugins.map((plugin) => {
                    const pluginInstances = instances.filter(i => i.plugin_id === plugin.id);
                    return (
                      <tr key={plugin.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                        <td className="px-6 py-4">
                          <div className="font-medium text-gray-900 dark:text-white">{plugin.display_name}</div>
                          {plugin.description && (
                            <div className="text-sm text-gray-500 dark:text-gray-400 line-clamp-1">{plugin.description}</div>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getPluginTypeBadgeColor(plugin.plugin_type)}`}>
                            {plugin.plugin_type}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{plugin.version}</td>
                        <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{pluginInstances.length}</td>
                        <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{plugin.usage_count}</td>
                        <td className="px-6 py-4">
                          {plugin.is_enabled ? (
                            <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs rounded-full">
                              Enabled
                            </span>
                          ) : (
                            <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-xs rounded-full">
                              Disabled
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => handleTogglePlugin(plugin)}
                              className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200"
                              title="Toggle status"
                            >
                              <Power className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleUninstallPlugin(plugin.id)}
                              className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                              title="Uninstall"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Plugin Instances Section */}
        {instances.length > 0 && (
          <div className="mt-8">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Plugin Instances</h2>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Instance Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Plugin</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Executions</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Errors</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                    {instances.map((instance) => {
                      const plugin = plugins.find(p => p.id === instance.plugin_id);
                      return (
                        <tr key={instance.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50" data-testid={`instance-row-${instance.id}`}>
                          <td className="px-6 py-4">
                            <div className="font-medium text-gray-900 dark:text-white">{instance.name}</div>
                            {instance.last_executed_at && (
                              <div className="text-xs text-gray-500 dark:text-gray-400 flex items-center mt-1">
                                <Clock className="w-3 h-3 mr-1" />
                                Last run {new Date(instance.last_executed_at).toLocaleString()}
                              </div>
                            )}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">
                            {plugin?.display_name || 'Unknown'}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{instance.execution_count}</td>
                          <td className="px-6 py-4">
                            {instance.error_count > 0 ? (
                              <span className="text-sm text-red-600 dark:text-red-400">{instance.error_count}</span>
                            ) : (
                              <span className="text-sm text-gray-600 dark:text-gray-300">0</span>
                            )}
                          </td>
                          <td className="px-6 py-4">
                            <button
                              onClick={() => handleToggleInstance(instance)}
                              className="relative inline-flex items-center"
                              data-testid={`toggle-instance-button-${instance.id}`}
                            >
                              {instance.is_enabled ? (
                                <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs rounded-full">
                                  Enabled
                                </span>
                              ) : (
                                <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-xs rounded-full">
                                  Disabled
                                </span>
                              )}
                            </button>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={() => {
                                  setExecuteFormData({ ...executeFormData, instance_id: instance.id });
                                  setShowExecuteModal(true);
                                }}
                                className="text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300"
                                title="Execute"
                                data-testid={`execute-instance-button-${instance.id}`}
                              >
                                <Play className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => handleDeleteInstance(instance.id)}
                                className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                                title="Delete"
                                data-testid={`delete-instance-button-${instance.id}`}
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Install Plugin Modal */}
        {showInstallModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto" data-testid="install-plugin-modal">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Install Plugin</h2>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Provide the plugin manifest and files in JSON format
                </p>
              </div>
              
              <div className="p-6 space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Plugin Manifest (JSON) *
                  </label>
                  <textarea
                    value={installFormData.manifest}
                    onChange={(e) => setInstallFormData({ ...installFormData, manifest: e.target.value })}
                    placeholder={`{\n  "name": "my-plugin",\n  "display_name": "My Plugin",\n  "version": "1.0.0",\n  "plugin_type": "visualization",\n  "entry_point": "main.py",\n  "description": "Custom visualization plugin"\n}`}
                    rows={10}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
                    data-testid="plugin-manifest-input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Plugin Files (JSON object with filename as key, content as value) *
                  </label>
                  <textarea
                    value={installFormData.files}
                    onChange={(e) => setInstallFormData({ ...installFormData, files: e.target.value })}
                    placeholder={`{\n  "main.py": "def execute(data, params):\\n    return data"\n}`}
                    rows={8}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
                    data-testid="plugin-files-input"
                  />
                </div>

                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-blue-700 dark:text-blue-300">
                      <p className="font-semibold mb-1">Plugin Security Notice</p>
                      <p>Only install plugins from trusted sources. Plugins run in a sandboxed environment with limited permissions.</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowInstallModal(false);
                    resetInstallForm();
                  }}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  data-testid="cancel-install-button"
                >
                  Cancel
                </button>
                <button
                  onClick={handleInstallPlugin}
                  disabled={!installFormData.manifest || !installFormData.files}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  data-testid="submit-install-button"
                >
                  Install Plugin
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Create Instance Modal */}
        {showInstanceModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto" data-testid="create-instance-modal">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Create Plugin Instance</h2>
              </div>
              
              <div className="p-6 space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Plugin *
                  </label>
                  <select
                    value={instanceFormData.plugin_id}
                    onChange={(e) => setInstanceFormData({ ...instanceFormData, plugin_id: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                    data-testid="instance-plugin-select"
                  >
                    <option value="">-- Select a plugin --</option>
                    {plugins.map((plugin) => (
                      <option key={plugin.id} value={plugin.id}>
                        {plugin.display_name} (v{plugin.version})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Instance Name *
                  </label>
                  <input
                    type="text"
                    value={instanceFormData.name}
                    onChange={(e) => setInstanceFormData({ ...instanceFormData, name: e.target.value })}
                    placeholder="My Plugin Instance"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                    data-testid="instance-name-input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Configuration (JSON)
                  </label>
                  <textarea
                    value={typeof instanceFormData.config === 'string' ? instanceFormData.config : JSON.stringify(instanceFormData.config, null, 2)}
                    onChange={(e) => setInstanceFormData({ ...instanceFormData, config: e.target.value })}
                    placeholder={`{\n  "param1": "value1",\n  "param2": "value2"\n}`}
                    rows={8}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
                    data-testid="instance-config-input"
                  />
                </div>
              </div>

              <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowInstanceModal(false);
                    resetInstanceForm();
                  }}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  data-testid="cancel-instance-button"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateInstance}
                  disabled={!instanceFormData.plugin_id || !instanceFormData.name}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  data-testid="submit-instance-button"
                >
                  Create Instance
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Execute Plugin Modal */}
        {showExecuteModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto" data-testid="execute-plugin-modal">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Execute Plugin</h2>
              </div>
              
              <div className="p-6 space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Plugin Instance *
                  </label>
                  <select
                    value={executeFormData.instance_id}
                    onChange={(e) => setExecuteFormData({ ...executeFormData, instance_id: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                    data-testid="execute-instance-select"
                  >
                    <option value="">-- Select an instance --</option>
                    {instances.map((instance) => (
                      <option key={instance.id} value={instance.id}>
                        {instance.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Input Data (JSON)
                  </label>
                  <textarea
                    value={executeFormData.input_data}
                    onChange={(e) => setExecuteFormData({ ...executeFormData, input_data: e.target.value })}
                    placeholder={`{\n  "data": [1, 2, 3, 4, 5]\n}`}
                    rows={6}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
                    data-testid="execute-input-data"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Parameters (JSON)
                  </label>
                  <textarea
                    value={executeFormData.params}
                    onChange={(e) => setExecuteFormData({ ...executeFormData, params: e.target.value })}
                    placeholder={`{\n  "option1": true\n}`}
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
                    data-testid="execute-params"
                  />
                </div>

                {executionResult && (
                  <div className={`border rounded-lg p-4 ${
                    executionResult.success
                      ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                      : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
                  }`}>
                    <h4 className={`font-semibold mb-2 ${
                      executionResult.success
                        ? 'text-green-800 dark:text-green-200'
                        : 'text-red-800 dark:text-red-200'
                    }`}>
                      {executionResult.success ? '✓ Success' : '✗ Error'}
                    </h4>
                    <pre className="text-sm overflow-x-auto">
                      {executionResult.success
                        ? JSON.stringify(executionResult.output, null, 2)
                        : executionResult.error}
                    </pre>
                    <p className="text-xs mt-2 text-gray-600 dark:text-gray-400">
                      Execution time: {executionResult.execution_time_ms}ms
                    </p>
                  </div>
                )}
              </div>

              <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowExecuteModal(false);
                    setExecutionResult(null);
                  }}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  data-testid="cancel-execute-button"
                >
                  Close
                </button>
                <button
                  onClick={handleExecutePlugin}
                  disabled={!executeFormData.instance_id}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  data-testid="submit-execute-button"
                >
                  <Play className="w-4 h-4 inline mr-2" />
                  Execute
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Stats Modal */}
        {showStatsModal && stats && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto" data-testid="stats-modal">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Plugin Statistics</h2>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{stats.plugin_name}</p>
              </div>
              
              <div className="p-6 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                    <p className="text-sm text-blue-600 dark:text-blue-400">Total Instances</p>
                    <p className="text-2xl font-bold text-blue-900 dark:text-blue-200">{stats.total_instances}</p>
                  </div>
                  <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                    <p className="text-sm text-purple-600 dark:text-purple-400">Total Executions</p>
                    <p className="text-2xl font-bold text-purple-900 dark:text-purple-200">{stats.total_executions.toLocaleString()}</p>
                  </div>
                  <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                    <p className="text-sm text-red-600 dark:text-red-400">Total Errors</p>
                    <p className="text-2xl font-bold text-red-900 dark:text-red-200">{stats.total_errors}</p>
                  </div>
                  <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                    <p className="text-sm text-green-600 dark:text-green-400">Success Rate</p>
                    <p className="text-2xl font-bold text-green-900 dark:text-green-200">{(stats.success_rate * 100).toFixed(1)}%</p>
                  </div>
                  <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
                    <p className="text-sm text-orange-600 dark:text-orange-400">Avg Exec Time</p>
                    <p className="text-2xl font-bold text-orange-900 dark:text-orange-200">
                      {stats.avg_execution_time_ms?.toFixed(0) || 0}ms
                    </p>
                  </div>
                  <div className="bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800 rounded-lg p-4">
                    <p className="text-sm text-indigo-600 dark:text-indigo-400">Last 30 Days</p>
                    <p className="text-2xl font-bold text-indigo-900 dark:text-indigo-200">{stats.last_30d_executions.toLocaleString()}</p>
                  </div>
                </div>
              </div>

              <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end">
                <button
                  onClick={() => {
                    setShowStatsModal(false);
                    setStats(null);
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

        {/* Plugin Details Sidebar */}
        {selectedPlugin && (
          <div className="fixed inset-y-0 right-0 w-96 bg-white dark:bg-gray-800 shadow-xl border-l border-gray-200 dark:border-gray-700 overflow-y-auto z-50">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">Plugin Details</h3>
                <button
                  onClick={() => setSelectedPlugin(null)}
                  className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-gray-900 dark:text-white text-lg">{selectedPlugin.display_name}</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{selectedPlugin.description}</p>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Version:</span>
                    <p className="font-semibold text-gray-900 dark:text-white">{selectedPlugin.version}</p>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Author:</span>
                    <p className="font-semibold text-gray-900 dark:text-white">{selectedPlugin.author || 'Unknown'}</p>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Type:</span>
                    <p className="font-semibold text-gray-900 dark:text-white">{selectedPlugin.plugin_type}</p>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Entry Point:</span>
                    <p className="font-mono text-xs text-gray-900 dark:text-white">{selectedPlugin.entry_point}</p>
                  </div>
                </div>

                {selectedPlugin.dependencies && selectedPlugin.dependencies.length > 0 && (
                  <div>
                    <h5 className="font-semibold text-gray-900 dark:text-white mb-2">Dependencies</h5>
                    <div className="flex flex-wrap gap-2">
                      {selectedPlugin.dependencies.map((dep, index) => (
                        <span key={index} className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded text-xs">
                          {dep}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {selectedPlugin.required_scopes && selectedPlugin.required_scopes.length > 0 && (
                  <div>
                    <h5 className="font-semibold text-gray-900 dark:text-white mb-2">Required Scopes</h5>
                    <div className="flex flex-wrap gap-2">
                      {selectedPlugin.required_scopes.map((scope, index) => (
                        <span key={index} className="px-2 py-1 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded text-xs">
                          {scope}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {selectedPlugin.config_schema && (
                  <div>
                    <h5 className="font-semibold text-gray-900 dark:text-white mb-2">Config Schema</h5>
                    <pre className="text-xs bg-gray-100 dark:bg-gray-700 p-3 rounded overflow-x-auto">
                      {JSON.stringify(selectedPlugin.config_schema, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PluginsPage;
