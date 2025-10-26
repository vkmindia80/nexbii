import React, { useState, useEffect } from 'react';
import { TrendingUp, Clock, AlertTriangle, Activity, BarChart3 } from 'lucide-react';
import adminService from '../services/adminService';

interface QueryPerformance {
  query_id: string;
  query_name: string;
  avg_execution_time: number;
  max_execution_time: number;
  execution_count: number;
  error_count: number;
  last_executed: string;
}

interface APIPerformance {
  endpoint: string;
  method: string;
  avg_response_time: number;
  max_response_time: number;
  request_count: number;
  error_count: number;
  error_rate: number;
}

const PerformanceAnalyticsPage: React.FC = () => {
  const [queryPerformance, setQueryPerformance] = useState<QueryPerformance[]>([]);
  const [apiPerformance, setAPIPerformance] = useState<APIPerformance[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'queries' | 'apis'>('queries');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      // Note: These are placeholder calls - actual implementation would use proper performance endpoints
      const [queries, apis] = await Promise.all([
        adminService.getQueryPerformanceStats(),
        adminService.getAPIPerformanceStats()
      ]);
      
      // Mock data for demonstration
      setQueryPerformance([
        {
          query_id: '1',
          query_name: 'Sales Dashboard Query',
          avg_execution_time: 245,
          max_execution_time: 520,
          execution_count: 1234,
          error_count: 5,
          last_executed: new Date().toISOString()
        },
        {
          query_id: '2',
          query_name: 'User Analytics',
          avg_execution_time: 180,
          max_execution_time: 350,
          execution_count: 856,
          error_count: 2,
          last_executed: new Date().toISOString()
        }
      ]);

      setAPIPerformance([
        {
          endpoint: '/api/queries/execute',
          method: 'POST',
          avg_response_time: 235,
          max_response_time: 1200,
          request_count: 5678,
          error_count: 12,
          error_rate: 0.21
        },
        {
          endpoint: '/api/dashboards',
          method: 'GET',
          avg_response_time: 85,
          max_response_time: 250,
          request_count: 8234,
          error_count: 3,
          error_rate: 0.04
        }
      ]);
    } catch (error) {
      console.error('Failed to fetch performance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPerformanceColor = (time: number) => {
    if (time < 100) return 'text-green-600';
    if (time < 500) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getErrorRateColor = (rate: number) => {
    if (rate < 1) return 'text-green-600';
    if (rate < 5) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <TrendingUp className="w-8 h-8 mr-3 text-primary-600" />
          Performance Analytics
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Query and API performance monitoring and optimization
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Avg Query Time</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">213ms</p>
            </div>
            <Clock className="w-8 h-8 text-blue-500" />
          </div>
          <p className="text-xs text-green-600 mt-2">↓ 12% from last week</p>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Slow Queries</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">8</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-yellow-500" />
          </div>
          <p className="text-xs text-gray-500 mt-2">&gt;1s execution time</p>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total API Calls</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">13.9K</p>
            </div>
            <Activity className="w-8 h-8 text-green-500" />
          </div>
          <p className="text-xs text-green-600 mt-2">↑ 24% from last week</p>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Error Rate</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">0.15%</p>
            </div>
            <BarChart3 className="w-8 h-8 text-purple-500" />
          </div>
          <p className="text-xs text-green-600 mt-2">↓ 0.05% from last week</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            <button
              onClick={() => setActiveTab('queries')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'queries'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Query Performance
            </button>
            <button
              onClick={() => setActiveTab('apis')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'apis'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              API Endpoints
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'queries' && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Top Queries by Performance</h3>
                <button className="text-sm text-primary-600 hover:text-primary-700">
                  View All Queries →
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Query Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Avg Time
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Max Time
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Executions
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Errors
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Last Executed
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {queryPerformance.map((query) => (
                      <tr key={query.query_id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {query.query_name}
                          </div>
                          <div className="text-xs text-gray-500">ID: {query.query_id}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`text-sm font-medium ${getPerformanceColor(query.avg_execution_time)}`}>
                            {query.avg_execution_time}ms
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`text-sm ${getPerformanceColor(query.max_execution_time)}`}>
                            {query.max_execution_time}ms
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {query.execution_count.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={query.error_count > 0 ? 'text-red-600' : 'text-green-600'}>
                            {query.error_count}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(query.last_executed).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'apis' && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">API Endpoint Performance</h3>
                <button className="text-sm text-primary-600 hover:text-primary-700">
                  View All Endpoints →
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Endpoint
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Method
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Avg Response
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Max Response
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Requests
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Error Rate
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {apiPerformance.map((api, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div className="text-sm font-medium text-gray-900">
                            {api.endpoint}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-medium rounded ${
                            api.method === 'GET' ? 'bg-blue-100 text-blue-800' :
                            api.method === 'POST' ? 'bg-green-100 text-green-800' :
                            api.method === 'PUT' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {api.method}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`text-sm font-medium ${getPerformanceColor(api.avg_response_time)}`}>
                            {api.avg_response_time}ms
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`text-sm ${getPerformanceColor(api.max_response_time)}`}>
                            {api.max_response_time}ms
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {api.request_count.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`text-sm font-medium ${getErrorRateColor(api.error_rate)}`}>
                            {api.error_rate.toFixed(2)}%
                          </span>
                          <div className="text-xs text-gray-500">
                            {api.error_count} errors
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Performance Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">Performance Optimization Tips</h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li>• Queries with avg execution time &gt;500ms should be optimized with indexes</li>
          <li>• API endpoints with error rate &gt;1% require investigation</li>
          <li>• Consider caching for frequently executed queries</li>
          <li>• Monitor slow queries during peak usage hours</li>
        </ul>
      </div>
    </div>
  );
};

export default PerformanceAnalyticsPage;
