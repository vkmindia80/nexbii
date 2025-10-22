import api from './api';
import { Dashboard } from '../types';

export const dashboardService = {
  async create(data: Partial<Dashboard>): Promise<Dashboard> {
    const response = await api.post('/api/dashboards/', data);
    return response.data;
  },

  async list(): Promise<Dashboard[]> {
    const response = await api.get('/api/dashboards/');
    return response.data;
  },

  async get(id: string): Promise<Dashboard> {
    const response = await api.get(`/api/dashboards/${id}`);
    return response.data;
  },

  async update(id: string, data: Partial<Dashboard>): Promise<Dashboard> {
    const response = await api.put(`/api/dashboards/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/api/dashboards/${id}`);
  }
}