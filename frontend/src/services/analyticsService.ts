import api from './api';

export interface CohortAnalysisRequest {
  datasource_id: string;
  user_id_column: string;
  event_date_column: string;
  cohort_date_column: string;
  table_name: string;
  filters?: Record<string, any>;
  period_type: 'daily' | 'weekly' | 'monthly';
}

export interface FunnelStage {
  name: string;
  condition: string;
}

export interface FunnelAnalysisRequest {
  datasource_id: string;
  table_name: string;
  user_id_column: string;
  timestamp_column: string;
  stages: FunnelStage[];
  time_window_days?: number;
}

export interface TimeSeriesForecastRequest {
  datasource_id: string;
  query: string;
  date_column: string;
  value_column: string;
  periods: number;
  frequency: 'D' | 'W' | 'M' | 'Q' | 'Y';
  model_type: 'arima' | 'prophet' | 'seasonal';
  confidence_interval: number;
}

export interface StatisticalTestRequest {
  datasource_id: string;
  test_type: 'ttest' | 'chi_square' | 'anova' | 'correlation' | 'normality';
  query: string;
  columns: string[];
  group_column?: string;
  alpha: number;
}

export interface PivotTableRequest {
  datasource_id: string;
  query: string;
  rows: string[];
  columns: string[];
  values: string;
  aggfunc: 'sum' | 'mean' | 'count' | 'min' | 'max' | 'median' | 'std';
}

export interface DataProfilingRequest {
  datasource_id: string;
  table_name?: string;
  query?: string;
  sample_size?: number;
}

export interface PredictiveModelRequest {
  datasource_id: string;
  query: string;
  target_column: string;
  feature_columns: string[];
  model_type: 'linear_regression' | 'logistic_regression' | 'random_forest' | 'decision_tree';
  test_size: number;
  cross_validation: boolean;
}

export interface AnomalyDetectionRequest {
  datasource_id: string;
  query: string;
  feature_columns: string[];
  method: 'isolation_forest' | 'local_outlier_factor' | 'one_class_svm';
  contamination: number;
}

export interface ClusteringRequest {
  datasource_id: string;
  query: string;
  feature_columns: string[];
  n_clusters?: number;
  method: 'kmeans' | 'hierarchical' | 'dbscan';
}

export interface ChurnPredictionRequest {
  datasource_id: string;
  query: string;
  customer_id_column: string;
  target_column: string;
  feature_columns: string[];
}

const analyticsService = {
  // Cohort Analysis
  cohortAnalysis: async (request: CohortAnalysisRequest) => {
    const response = await api.post('/analytics/cohort-analysis', request);
    return response.data;
  },

  // Funnel Analysis
  funnelAnalysis: async (request: FunnelAnalysisRequest) => {
    const response = await api.post('/analytics/funnel-analysis', request);
    return response.data;
  },

  // Time Series Forecasting
  timeSeriesForecast: async (request: TimeSeriesForecastRequest) => {
    const response = await api.post('/analytics/forecast', request);
    return response.data;
  },

  // Statistical Tests
  statisticalTest: async (request: StatisticalTestRequest) => {
    const response = await api.post('/analytics/statistical-test', request);
    return response.data;
  },

  // Pivot Table
  pivotTable: async (request: PivotTableRequest) => {
    const response = await api.post('/analytics/pivot-table', request);
    return response.data;
  },

  // Data Profiling
  profileData: async (request: DataProfilingRequest) => {
    const response = await api.post('/analytics/profile-data', request);
    return response.data;
  },

  getColumnDistribution: async (
    datasourceId: string,
    tableName: string,
    columnName: string,
    bins: number = 20
  ) => {
    const response = await api.get(
      `/analytics/column-distribution/${datasourceId}/${tableName}/${columnName}?bins=${bins}`
    );
    return response.data;
  },

  detectCorrelations: async (
    datasourceId: string,
    tableName: string,
    threshold: number = 0.7
  ) => {
    const response = await api.get(
      `/analytics/detect-correlations/${datasourceId}/${tableName}?threshold=${threshold}`
    );
    return response.data;
  },

  // Predictive Models
  trainPredictiveModel: async (request: PredictiveModelRequest) => {
    const response = await api.post('/analytics/predictive-model', request);
    return response.data;
  },

  // Anomaly Detection
  detectAnomalies: async (request: AnomalyDetectionRequest) => {
    const response = await api.post('/analytics/anomaly-detection', request);
    return response.data;
  },

  // Clustering
  performClustering: async (request: ClusteringRequest) => {
    const response = await api.post('/analytics/clustering', request);
    return response.data;
  },

  // Churn Prediction
  predictChurn: async (request: ChurnPredictionRequest) => {
    const response = await api.post('/analytics/churn-prediction', request);
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/analytics/health');
    return response.data;
  },
};

export default analyticsService;
