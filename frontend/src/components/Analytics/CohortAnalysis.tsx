import React, { useState } from 'react';
import { Play, Download, Users } from 'lucide-react';
import analyticsService, { CohortAnalysisRequest } from '../../services/analyticsService';
import ReactECharts from 'echarts-for-react';

interface Props {
  dataSources: Array<{ id: string; name: string; type: string }>;
}

const CohortAnalysis: React.FC<Props> = ({ dataSources }) => {
  const [formData, setFormData] = useState<Partial<CohortAnalysisRequest>>({
    datasource_id: '',
    table_name: '',
    user_id_column: 'user_id',
    event_date_column: 'event_date',
    cohort_date_column: 'created_at',
    period_type: 'monthly'
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>('');

  const handleAnalyze = async () => {
    if (!formData.datasource_id || !formData.table_name) {
      setError('Please select data source and enter table name');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const data = await analyticsService.cohortAnalysis(formData as CohortAnalysisRequest);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to perform cohort analysis');
    } finally {
      setLoading(false);
    }
  };

  const getHeatmapOption = () => {
    if (!result) return {};

    return {
      title: { text: 'Cohort Retention Heatmap', left: 'center' },
      tooltip: {
        position: 'top',
        formatter: (params: any) => {
          const cohort = result.cohort_labels[params.data[1]];
          const period = result.period_labels[params.data[0]];
          return `${cohort}<br/>${period}: ${params.data[2].toFixed(1)}%`;
        }
      },
      grid: { top: '80px', bottom: '60px', left: '150px', right: '80px' },
      xAxis: {
        type: 'category',
        data: result.period_labels,
        axisLabel: { rotate: 45 }
      },
      yAxis: {
        type: 'category',
        data: result.cohort_labels
      },
      visualMap: {
        min: 0,
        max: 100,
        calculable: true,
        orient: 'vertical',
        right: '10',
        top: 'center',
        text: ['100%', '0%'],
        inRange: { color: ['#e3f2fd', '#2196f3', '#0d47a1'] }
      },
      series: [{
        type: 'heatmap',
        data: result.retention_matrix.flatMap((row: number[], y: number) =>
          row.map((value: number, x: number) => [x, y, value])
        ),
        label: { show: true, formatter: (params: any) => `${params.data[2].toFixed(0)}%` },
        emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
      }]
    };
  };

  return (
    <div className="p-6" data-testid="cohort-analysis">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Users className="w-6 h-6 text-blue-600" />
          Cohort Analysis
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Track user retention over time by grouping users into cohorts
        </p>
      </div>

      {/* Configuration Form */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Data Source *
          </label>
          <select
            value={formData.datasource_id}
            onChange={(e) => setFormData({ ...formData, datasource_id: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select data source</option>
            {dataSources.map(ds => (
              <option key={ds.id} value={ds.id}>{ds.name} ({ds.type})</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Table Name *
          </label>
          <input
            type="text"
            value={formData.table_name}
            onChange={(e) => setFormData({ ...formData, table_name: e.target.value })}
            placeholder="e.g., user_events"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            User ID Column
          </label>
          <input
            type="text"
            value={formData.user_id_column}
            onChange={(e) => setFormData({ ...formData, user_id_column: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Event Date Column
          </label>
          <input
            type="text"
            value={formData.event_date_column}
            onChange={(e) => setFormData({ ...formData, event_date_column: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Cohort Date Column
          </label>
          <input
            type="text"
            value={formData.cohort_date_column}
            onChange={(e) => setFormData({ ...formData, cohort_date_column: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Period Type
          </label>
          <select
            value={formData.period_type}
            onChange={(e) => setFormData({ ...formData, period_type: e.target.value as any })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <button
        onClick={handleAnalyze}
        disabled={loading}
        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition flex items-center gap-2"
        data-testid="run-cohort-analysis"
      >
        <Play className="w-4 h-4" />
        {loading ? 'Analyzing...' : 'Run Cohort Analysis'}
      </button>

      {/* Results */}
      {result && (
        <div className="mt-8 space-y-6">
          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-sm text-blue-600 font-medium">Total Cohorts</div>
              <div className="text-2xl font-bold text-blue-900">
                {result.summary.total_cohorts}
              </div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-sm text-green-600 font-medium">Best Cohort</div>
              <div className="text-lg font-bold text-green-900">
                {result.summary.best_cohort || 'N/A'}
              </div>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-sm text-orange-600 font-medium">Worst Cohort</div>
              <div className="text-lg font-bold text-orange-900">
                {result.summary.worst_cohort || 'N/A'}
              </div>
            </div>
          </div>

          {/* Heatmap */}
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <ReactECharts option={getHeatmapOption()} style={{ height: '500px' }} />
          </div>
        </div>
      )}
    </div>
  );
};

export default CohortAnalysis;