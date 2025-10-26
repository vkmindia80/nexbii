import React, { useState, useEffect } from 'react';
import { Activity, Server, Database, Zap, AlertCircle, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import adminService, { SystemHealth, SystemMetrics } from '../services/adminService';

const SystemMonitoringPage: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [metrics, setMetrics] = useState<SystemMetrics[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [healthData, metricsData] = await Promise.all([
        adminService.getSystemHealth(true, true, false),
        adminService.getSystemMetrics(undefined, undefined, 'database', 20)
      ]);
      setHealth(healthData);
      setMetrics(metricsData);
    } catch (error) {
      console.error('Failed to fetch system data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  };

  const handleCollectMetrics = async () => {
    try {
      await adminService.collectMetricsNow();
      alert('Metrics collected successfully');
      fetchData();
    } catch (error) {
      console.error('Failed to collect metrics:', error);
      alert('Failed to collect metrics');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'degraded':
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'unhealthy':
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'success':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'degraded':
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'unhealthy':
      case 'error':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getLatestMetric = () => {
    return metrics.length > 0 ? metrics[0] : null;
  };

  const latestMetric = getLatestMetric();

  if (loading && !health) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <Activity className="w-8 h-8 mr-3 text-primary-600" />
            System Monitoring
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Real-time system health and performance metrics
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleCollectMetrics}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 flex items-center"
          >
            <Zap className="w-4 h-4 mr-2" />
            Collect Metrics
          </button>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 flex items-center"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Overall System Status */}
      {health && (
        <div className={`rounded-lg border-2 p-6 ${getStatusColor(health.overall_status)}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              {getStatusIcon(health.overall_status)}
              <div className="ml-3">
                <h3 className="text-lg font-semibold">System Status: {health.overall_status}</h3>
                <p className="text-sm opacity-80">
                  Last checked: {new Date(health.timestamp).toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Service Health Checks */}
      {health && health.checks && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Database Health */}
          {health.checks.database && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <Database className="w-8 h-8 text-blue-500" />
                  <h3 className="ml-3 text-lg font-semibold">Database</h3>
                </div>
                {getStatusIcon(health.checks.database.status)}
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Status:</span>
                  <span className="font-medium">{health.checks.database.status}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Response Time:</span>
                  <span className="font-medium">{health.checks.database.response_time_ms}ms</span>
                </div>
                {health.checks.database.message && (
                  <p className="text-xs text-gray-500 mt-2">{health.checks.database.message}</p>
                )}
              </div>
            </div>
          )}

          {/* Redis Health */}
          {health.checks.redis && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <Zap className="w-8 h-8 text-red-500" />
                  <h3 className="ml-3 text-lg font-semibold">Redis Cache</h3>
                </div>
                {getStatusIcon(health.checks.redis.status)}
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Status:</span>
                  <span className="font-medium">{health.checks.redis.status}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Response Time:</span>
                  <span className="font-medium">{health.checks.redis.response_time_ms}ms</span>
                </div>
                {health.checks.redis.message && (
                  <p className="text-xs text-gray-500 mt-2">{health.checks.redis.message}</p>
                )}
              </div>
            </div>
          )}

          {/* Server Health */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <Server className="w-8 h-8 text-green-500" />
                <h3 className="ml-3 text-lg font-semibold">Application</h3>
              </div>
              {getStatusIcon('healthy')}
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Status:</span>
                <span className="font-medium">Running</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Uptime:</span>
                <span className="font-medium">Active</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Real-time Metrics */}
      {latestMetric && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold mb-4">Real-time System Metrics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <p className="text-sm text-gray-500 mb-1">CPU Usage</p>
              <div className="flex items-end">
                <span className="text-3xl font-bold text-gray-900">
                  {latestMetric.cpu_percent?.toFixed(1) || 0}
                </span>
                <span className="text-lg text-gray-500 ml-1">%</span>
              </div>
              <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full"
                  style={{ width: `${Math.min(latestMetric.cpu_percent || 0, 100)}%` }}
                ></div>
              </div>
            </div>

            <div>
              <p className="text-sm text-gray-500 mb-1">Memory Usage</p>
              <div className="flex items-end">
                <span className="text-3xl font-bold text-gray-900">
                  {latestMetric.memory_percent?.toFixed(1) || 0}
                </span>
                <span className="text-lg text-gray-500 ml-1">%</span>
              </div>
              <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full"
                  style={{ width: `${Math.min(latestMetric.memory_percent || 0, 100)}%` }}
                ></div>
              </div>
            </div>

            <div>
              <p className="text-sm text-gray-500 mb-1">Active Connections</p>
              <div className="flex items-end">
                <span className="text-3xl font-bold text-gray-900">
                  {latestMetric.active_connections || 0}
                </span>
              </div>
              <p className="text-xs text-gray-400 mt-2">Database connections</p>
            </div>

            <div>
              <p className="text-sm text-gray-500 mb-1">Avg Query Time</p>
              <div className="flex items-end">
                <span className="text-3xl font-bold text-gray-900">
                  {latestMetric.avg_query_time?.toFixed(0) || 0}
                </span>
                <span className="text-lg text-gray-500 ml-1">ms</span>
              </div>
              <p className="text-xs text-gray-400 mt-2">Average execution time</p>
            </div>
          </div>
        </div>
      )}

      {/* Historical Metrics Table */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4">Recent Metrics History</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  CPU %
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Memory %
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Connections
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Queries
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Time (ms)
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {metrics.map((metric) => (
                <tr key={metric.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(metric.timestamp).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {metric.cpu_percent?.toFixed(1) || 0}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {metric.memory_percent?.toFixed(1) || 0}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {metric.active_connections || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {metric.query_count || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {metric.avg_query_time?.toFixed(0) || 0}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default SystemMonitoringPage;
