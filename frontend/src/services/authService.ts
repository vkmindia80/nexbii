import api from './api';
import { AuthToken, User } from '../types';

export const authService = {
  async register(email: string, password: string, full_name?: string): Promise<AuthToken> {
    const response = await api.post('/api/auth/register', {
      email,
      password,
      full_name,
      role: 'editor'
    });
    return response.data;
  },

  async login(email: string, password: string): Promise<AuthToken> {
    const response = await api.post('/api/auth/login', {
      email,
      password
    });
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  }
};