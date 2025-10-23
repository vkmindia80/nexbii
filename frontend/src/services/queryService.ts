import api from './api';
import { Query, QueryResult } from '../types';

export const queryService = {
  async create(data: Partial<Query>): Promise<Query> {
    const response = await api.post('/api/queries/', data);
    return response.data;
  },

  async list(): Promise<Query[]> {
    const response = await api.get('/api/queries/');
    return response.data;
  },

  async get(id: string): Promise<Query> {
    const response = await api.get(`/api/queries/${id}`);
    return response.data;
  },

  async execute(params: { 
    query_id?: string; 
    datasource_id?: string; 
    sql_query?: string; 
    limit?: number 
  }): Promise<QueryResult> {
    const response = await api.post('/api/queries/execute', params);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/api/queries/${id}`);
  }
};