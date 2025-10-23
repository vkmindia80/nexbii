import api from './api';

export interface Activity {
  id: string;
  user_id: string;
  activity_type: string;
  entity_type?: string;
  entity_id?: string;
  entity_name?: string;
  description?: string;
  activity_metadata?: any;
  created_at: string;
}

class ActivityService {
  async getMyActivities(limit: number = 50, offset: number = 0): Promise<Activity[]> {
    const response = await api.get('/api/activities/me', {
      params: { limit, offset }
    });
    return response.data;
  }

  async getAllActivities(
    limit: number = 100,
    offset: number = 0,
    days?: number
  ): Promise<Activity[]> {
    const params: any = { limit, offset };
    if (days) params.days = days;
    
    const response = await api.get('/api/activities/all', { params });
    return response.data;
  }

  async getEntityActivities(
    entityType: string,
    entityId: string,
    limit: number = 50
  ): Promise<Activity[]> {
    const response = await api.get(
      `/api/activities/entity/${entityType}/${entityId}`,
      { params: { limit } }
    );
    return response.data;
  }
}

export default new ActivityService();