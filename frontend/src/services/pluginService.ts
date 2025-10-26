import api from './api';

export interface PluginType {
  type: string;
  description: string;
  example_use_cases: string[];
}

export interface Plugin {
  id: string;
  name: string;
  display_name: string;
  description?: string;
  version: string;
  author?: string;
  plugin_type: string;
  is_enabled: boolean;
  is_verified: boolean;
  usage_count: number;
  last_used_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface PluginDetail extends Plugin {
  entry_point: string;
  dependencies: string[];
  required_scopes: string[];
  config_schema?: any;
  default_config?: any;
  installed_by: string;
  tenant_id?: string;
}

export interface PluginManifest {
  name: string;
  display_name: string;
  description: string;
  version: string;
  author?: string;
  plugin_type: string;
  entry_point: string;
  dependencies?: string[];
  required_scopes?: string[];
  config_schema?: any;
  default_config?: any;
}

export interface PluginCreate {
  manifest: PluginManifest;
  files: { [filename: string]: string };
}

export interface PluginUpdate {
  display_name?: string;
  description?: string;
  is_enabled?: boolean;
  config_schema?: any;
  default_config?: any;
}

export interface PluginInstance {
  id: string;
  plugin_id: string;
  name: string;
  config: any;
  is_enabled: boolean;
  execution_count: number;
  last_executed_at?: string;
  error_count: number;
  last_error?: string;
  last_error_at?: string;
  created_at: string;
}

export interface PluginInstanceCreate {
  plugin_id: string;
  name: string;
  config?: any;
}

export interface PluginInstanceUpdate {
  name?: string;
  config?: any;
  is_enabled?: boolean;
}

export interface PluginExecutionResult {
  success: boolean;
  output?: any;
  error?: string;
  execution_time_ms: number;
}

export interface PluginStats {
  plugin_id: string;
  plugin_name: string;
  total_instances: number;
  total_executions: number;
  total_errors: number;
  avg_execution_time_ms?: number;
  success_rate: number;
  last_30d_executions: number;
}

class PluginService {
  async getPluginTypes(): Promise<PluginType[]> {
    const response = await api.get('/api/plugins/types');
    return response.data.types;
  }

  async installPlugin(data: PluginCreate): Promise<PluginDetail> {
    const response = await api.post('/api/plugins/', data);
    return response.data;
  }

  async listPlugins(
    pluginType?: string,
    enabledOnly: boolean = false
  ): Promise<Plugin[]> {
    const response = await api.get('/api/plugins/', {
      params: { plugin_type: pluginType, enabled_only: enabledOnly }
    });
    return response.data;
  }

  async getPlugin(pluginId: string): Promise<PluginDetail> {
    const response = await api.get(`/api/plugins/${pluginId}`);
    return response.data;
  }

  async updatePlugin(pluginId: string, data: PluginUpdate): Promise<Plugin> {
    const response = await api.put(`/api/plugins/${pluginId}`, data);
    return response.data;
  }

  async uninstallPlugin(pluginId: string): Promise<void> {
    await api.delete(`/api/plugins/${pluginId}`);
  }

  async getPluginStats(pluginId: string): Promise<PluginStats> {
    const response = await api.get(`/api/plugins/${pluginId}/stats`);
    return response.data;
  }

  // Plugin Instances
  async createInstance(data: PluginInstanceCreate): Promise<PluginInstance> {
    const response = await api.post('/api/plugins/instances', data);
    return response.data;
  }

  async listInstances(pluginId?: string): Promise<PluginInstance[]> {
    const response = await api.get('/api/plugins/instances', {
      params: { plugin_id: pluginId }
    });
    return response.data;
  }

  async getInstance(instanceId: string): Promise<PluginInstance> {
    const response = await api.get(`/api/plugins/instances/${instanceId}`);
    return response.data;
  }

  async updateInstance(
    instanceId: string,
    data: PluginInstanceUpdate
  ): Promise<PluginInstance> {
    const response = await api.put(`/api/plugins/instances/${instanceId}`, data);
    return response.data;
  }

  async deleteInstance(instanceId: string): Promise<void> {
    await api.delete(`/api/plugins/instances/${instanceId}`);
  }

  async executePlugin(
    instanceId: string,
    inputData?: any,
    params?: any
  ): Promise<PluginExecutionResult> {
    const response = await api.post('/api/plugins/execute', {
      instance_id: instanceId,
      input_data: inputData || {},
      params: params || {}
    });
    return response.data;
  }
}

export default new PluginService();
