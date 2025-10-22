import React, { useEffect, useState } from 'react';
import { BarChart3, Database, FileText, TrendingUp } from 'lucide-react';
import { datasourceService } from '../services/datasourceService';
import { queryService } from '../services/queryService';
import { dashboardService } from '../services/dashboardService';

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState({
    datasources: 0,
    queries: 0,
    dashboards: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [datasources, queries, dashboards] = await Promise.all([
        datasourceService.list(),
        queryService.list(),
        dashboardService.list()
      ]);
      setStats({
        datasources: datasources.length,
        queries: queries.length,
        dashboards: dashboards.length
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Data Sources',
      value: stats.datasources,
      icon: Database,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      title: 'Queries',
      value: stats.queries,
      icon: FileText,
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-50'
    },
    {
      title: 'Dashboards',
      value: stats.dashboards,
      icon: BarChart3,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50'
    }
  ];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Welcome to NexBII</h1>
        <p className="text-gray-600 mt-2">Your advanced business intelligence platform</p>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {statCards.map((card) => {
            const Icon = card.icon;
            return (
              <div key={card.title} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm font-medium">{card.title}</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">{card.value}</p>
                  </div>
                  <div className={`${card.bgColor} p-3 rounded-lg`}>
                    <Icon className="w-6 h-6 text-gray-700" />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <a
            href="/datasources"
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all"
          >
            <Database className="w-5 h-5 text-primary-600" />
            <div>
              <h3 className="font-medium text-gray-900">Connect Data Source</h3>
              <p className="text-sm text-gray-600">Add a new database or file</p>
            </div>
          </a>
          <a
            href="/queries"
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all"
          >
            <FileText className="w-5 h-5 text-primary-600" />
            <div>
              <h3 className="font-medium text-gray-900">Create Query</h3>
              <p className="text-sm text-gray-600">Build a new SQL or visual query</p>
            </div>
          </a>
          <a
            href="/dashboards"
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all"
          >
            <BarChart3 className="w-5 h-5 text-primary-600" />
            <div>
              <h3 className="font-medium text-gray-900">New Dashboard</h3>
              <p className="text-sm text-gray-600">Create a visual dashboard</p>
            </div>
          </a>
          <a
            href="/queries"
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all"
          >
            <TrendingUp className="w-5 h-5 text-primary-600" />
            <div>
              <h3 className="font-medium text-gray-900">Explore Data</h3>
              <p className="text-sm text-gray-600">Start analyzing your data</p>
            </div>
          </a>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;