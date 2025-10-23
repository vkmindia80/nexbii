import api from './api';

export interface Comment {
  id: string;
  user_id: string;
  content: string;
  dashboard_id?: string;
  query_id?: string;
  mentions?: string[];
  parent_id?: string;
  created_at: string;
  updated_at?: string;
}

export interface CreateCommentRequest {
  content: string;
  dashboard_id?: string;
  query_id?: string;
  mentions?: string[];
  parent_id?: string;
}

class CommentService {
  async createComment(data: CreateCommentRequest): Promise<Comment> {
    const response = await api.post('/api/comments/', data);
    return response.data;
  }

  async getComments(
    dashboardId?: string,
    queryId?: string,
    parentId?: string
  ): Promise<Comment[]> {
    const params: any = {};
    if (dashboardId) params.dashboard_id = dashboardId;
    if (queryId) params.query_id = queryId;
    if (parentId !== undefined) params.parent_id = parentId;
    
    const response = await api.get('/api/comments/', { params });
    return response.data;
  }

  async updateComment(commentId: string, content: string): Promise<Comment> {
    const response = await api.put(`/api/comments/${commentId}`, { content });
    return response.data;
  }

  async deleteComment(commentId: string): Promise<void> {
    await api.delete(`/api/comments/${commentId}`);
  }
}

export default new CommentService();