import api from './api';

export interface NaturalQueryRequest {
  natural_query: string;
  datasource_id: string;
}

export interface ValidateQueryRequest {
  sql_query: string;
  datasource_id: string;
}

export interface OptimizeQueryRequest {
  sql_query: string;
  datasource_id: string;
  execution_time?: number;
}

export interface RecommendChartRequest {
  query_result: any;
  sql_query: string;
}

export interface GenerateInsightsRequest {
  query_result: any;
  sql_query: string;
}

export const aiService = {
  // Convert natural language to SQL
  naturalLanguageToSQL: async (request: NaturalQueryRequest) => {
    const response = await api.post('/api/ai/natural-query', request);
    return response.data;
  },

  // Validate SQL query
  validateQuery: async (request: ValidateQueryRequest) => {
    const response = await api.post('/api/ai/validate-query', request);
    return response.data;
  },

  // Optimize SQL query
  optimizeQuery: async (request: OptimizeQueryRequest) => {
    const response = await api.post('/api/ai/optimize-query', request);
    return response.data;
  },

  // Recommend chart type
  recommendChart: async (request: RecommendChartRequest) => {
    const response = await api.post('/api/ai/recommend-chart', request);
    return response.data;
  },

  // Generate insights
  generateInsights: async (request: GenerateInsightsRequest) => {
    const response = await api.post('/api/ai/generate-insights', request);
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/api/ai/health');
    return response.data;
  },
};
