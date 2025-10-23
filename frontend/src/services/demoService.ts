import api from './api';

export const demoService = {
  generateDemoData: async () => {
    const response = await api.post('/api/demo/generate');
    return response.data;
  },
};
