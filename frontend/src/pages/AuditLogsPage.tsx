import React, { useState, useEffect } from 'react';
import { FileText, Filter, Download, Search } from 'lucide-react';
import api from '../services/api';

interface AuditLog {
  id: string;
  event_type: string;
  event_category: string;
  username: string;
  action: string;
  status: string;
  resource_type: string;
  resource_name: string;
  ip_address: string;
  created_at: string;
}

const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    event_category: '',
    status: '',
    search: ''
  });
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetchLogs();
    fetchStats();
  }, []);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filters.event_category) params.append('event_category', filters.event_category);
      if (filters.status) params.append('status', filters.status);
      
      const response = await api.get(`/api/audit/logs?${params.toString()}`);
      setLogs(response.data);
    } catch (error) {
      console.error('Failed to fetch audit logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/audit/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const exportLogs = async () => {
    try {
      const response = await api.post('/api/audit/logs/export');
      // Create download link
      const blob = new Blob([JSON.stringify(response.data.data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit-logs-${new Date().toISOString()}.json`;
      a.click();
    } catch (error) {
      console.error('Failed to export logs:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'bg-green-100 text-green-700';
      case 'failure':
        return 'bg-red-100 text-red-700';
      case 'denied':
        return 'bg-orange-100 text-orange-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'authentication':
        return 'bg-blue-100 text-blue-700';
      case 'authorization':
        return 'bg-purple-100 text-purple-700';
      case 'data_access':
        return 'bg-green-100 text-green-700';
      case 'security_change':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <FileText className="w-8 h-8 text-blue-600" />
              Audit Logs
            </h1>
            <p className="text-gray-600 mt-2">
              Comprehensive activity logging for security and compliance
            </p>
          </div>
          <button
            onClick={exportLogs}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            data-testid="export-logs-button"
          >
            <Download className="w-5 h-5" />
            Export Logs
          </button>
        </div>

        {/* Statistics */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="text-sm text-gray-600 mb-1">Total Events</div>
              <div className="text-3xl font-bold text-gray-900">{stats.total_events}</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="text-sm text-gray-600 mb-1">Success Rate</div>
              <div className="text-3xl font-bold text-green-600">
                {stats.by_status && stats.by_status.success ? 
                  Math.round((stats.by_status.success / stats.total_events) * 100) : 0}%
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="text-sm text-gray-600 mb-1">Failed Events</div>
              <div className="text-3xl font-bold text-red-600">
                {stats.by_status && stats.by_status.failure ? stats.by_status.failure : 0}
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search logs..."
                  value={filters.search}
                  onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <select
              value={filters.event_category}
              onChange={(e) => setFilters({ ...filters, event_category: e.target.value })}
              className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              <option value="authentication">Authentication</option>
              <option value="authorization">Authorization</option>
              <option value="data_access">Data Access</option>
              <option value="security_change">Security Change</option>
              <option value="user_management">User Management</option>
            </select>
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Status</option>
              <option value="success">Success</option>
              <option value="failure">Failure</option>
              <option value="denied">Denied</option>
            </select>
            <button
              onClick={fetchLogs}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Filter className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Logs Table */}
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : logs.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No audit logs found
            </h3>
            <p className="text-gray-600">
              Audit logs will appear here as users interact with the system
            </p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Event
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    IP Address
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50" data-testid={`log-${log.id}`}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {log.username || 'System'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{log.event_type}</div>
                      <div className="text-sm text-gray-500">{log.action}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getCategoryColor(log.event_category)}`}>
                        {log.event_category}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(log.status)}`}>
                        {log.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {log.ip_address || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuditLogsPage;