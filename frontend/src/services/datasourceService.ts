import api from './api';
import { DataSource } from '../types';

export const datasourceService = {
  async create(data: Partial<DataSource>): Promise<DataSource> {
    const response = await api.post('/api/datasources/', data);
    return response.data;
  },

  async list(): Promise<DataSource[]> {
    const response = await api.get('/api/datasources/');
    return response.data;
  },

  async get(id: string): Promise<DataSource> {
    const response = await api.get(`/api/datasources/${id}`);
    return response.data;
  },

  async testConnection(type: string, config: any): Promise<boolean> {
    const response = await api.post('/api/datasources/test', {
      type,
      connection_config: config
    });
    return response.data.valid;
  },

  async getSchema(id: string): Promise<any> {
    const response = await api.get(`/api/datasources/${id}/schema`);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/api/datasources/${id}`);
  },

  // Alias for backward compatibility
  async getDataSources(): Promise<DataSource[]> {
    return this.list();
  }
};