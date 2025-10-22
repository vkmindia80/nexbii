export interface User {
  id: string;
  email: string;
  full_name?: string;
  role: 'admin' | 'editor' | 'viewer';
  is_active: boolean;
  created_at: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  user: User;
}

export interface DataSource {
  id: string;
  name: string;
  type: 'postgresql' | 'mysql' | 'mongodb' | 'sqlite' | 'csv' | 'excel' | 'json';
  connection_config: any;
  created_by: string;
  is_active: boolean;
  created_at: string;
}

export interface Query {
  id: string;
  name: string;
  description?: string;
  datasource_id: string;
  query_type: 'visual' | 'sql';
  query_config?: any;
  sql_query?: string;
  created_by: string;
  created_at: string;
}

export interface QueryResult {
  columns: string[];
  rows: any[][];
  total_rows: number;
  execution_time: number;
}

export interface Dashboard {
  id: string;
  name: string;
  description?: string;
  layout?: any;
  widgets?: any[];
  filters?: any;
  is_public: boolean;
  created_by: string;
  created_at: string;
  updated_at?: string;
}

export interface ChartConfig {
  type: 'line' | 'bar' | 'column' | 'area' | 'pie' | 'donut' | 'scatter' | 'table' | 'metric' | 'gauge';
  title?: string;
  data: any;
  options?: any;
}