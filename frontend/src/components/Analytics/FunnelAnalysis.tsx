import React, { useState } from 'react';
import { Play, Plus, Trash2, Target } from 'lucide-react';
import analyticsService, { FunnelAnalysisRequest, FunnelStage } from '../../services/analyticsService';
import ReactECharts from 'echarts-for-react';

interface Props {
  dataSources: Array<{ id: string; name: string; type: string }>;
}

const FunnelAnalysis: React.FC<Props> = ({ dataSources }) => {
  const [formData, setFormData] = useState<Partial<FunnelAnalysisRequest>>({
    datasource_id: '',
    table_name: '',
    user_id_column: 'user_id',
    timestamp_column: 'created_at',
    time_window_days: 30,
    stages: [
      { name: 'Step 1', condition: '' },
      { name: 'Step 2', condition: '' }
    ]
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>('');

  const handleAddStage = () => {
    setFormData({
      ...formData,
      stages: [...(formData.stages || []), { name: `Step ${(formData.stages?.length || 0) + 1}`, condition: '' }]
    });
  };

  const handleRemoveStage = (index: number) => {
    const stages = [...(formData.stages || [])];
    stages.splice(index, 1);
    setFormData({ ...formData, stages });
  };

  const handleStageChange = (index: number, field: keyof FunnelStage, value: string) => {
    const stages = [...(formData.stages || [])];
    stages[index] = { ...stages[index], [field]: value };
    setFormData({ ...formData, stages });
  };

  const handleAnalyze = async () => {
    if (!formData.datasource_id || !formData.table_name || !formData.stages || formData.stages.length < 2) {
      setError('Please fill all required fields and add at least 2 stages');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const data = await analyticsService.funnelAnalysis(formData as FunnelAnalysisRequest);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to perform funnel analysis');
    } finally {
      setLoading(false);
    }
  };

  const getFunnelOption = () => {
    if (!result) return {};

    return {
      title: { text: 'Conversion Funnel', left: 'center' },
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          const stage = result.stages[params.dataIndex];
          return `${stage.name}<br/>Users: ${stage.count}<br/>Conversion: ${stage.conversion_rate}%<br/>Drop-off: ${stage.drop_off_rate}%`;
        }
      },
      series: [{
        type: 'funnel',
        left: '10%',
        width: '80%',
        label: {
          formatter: (params: any) => {
            const stage = result.stages[params.dataIndex];
            return `${stage.name}\n${stage.count} users (${stage.conversion_rate}%)`;
          }
        },
        data: result.stages.map((stage: any) => ({
          value: stage.count,
          name: stage.name
        }))
      }]
    };
  };

  return (
    <div className="p-6" data-testid="funnel-analysis">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Target className="w-6 h-6 text-blue-600" />
          Funnel Analysis
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Track user conversion through multiple stages and identify drop-off points
        </p>
      </div>

      {/* Configuration Form */}
      <div className="space-y-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Data Source *</label>
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
            <label className="block text-sm font-medium text-gray-700 mb-1">Table Name *</label>
            <input
              type="text"
              value={formData.table_name}
              onChange={(e) => setFormData({ ...formData, table_name: e.target.value })}
              placeholder="e.g., user_events"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">User ID Column</label>
            <input
              type="text"
              value={formData.user_id_column}
              onChange={(e) => setFormData({ ...formData, user_id_column: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Timestamp Column</label>
            <input
              type="text"
              value={formData.timestamp_column}
              onChange={(e) => setFormData({ ...formData, timestamp_column: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Funnel Stages */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Funnel Stages</label>
          <div className="space-y-3">
            {formData.stages?.map((stage, index) => (
              <div key={index} className="flex gap-3">
                <input
                  type="text"
                  value={stage.name}
                  onChange={(e) => handleStageChange(index, 'name', e.target.value)}
                  placeholder="Stage name"
                  className="w-1/3 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="text"
                  value={stage.condition}
                  onChange={(e) => handleStageChange(index, 'condition', e.target.value)}
                  placeholder="SQL condition (e.g., event_type = 'signup')"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={() => handleRemoveStage(index)}
                  className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                  disabled={formData.stages!.length <= 2}
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            ))}
          </div>
          <button
            onClick={handleAddStage}
            className="mt-3 px-4 py-2 text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add Stage
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">{error}</div>
      )}

      <button
        onClick={handleAnalyze}
        disabled={loading}
        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition flex items-center gap-2"
      >
        <Play className="w-4 h-4" />
        {loading ? 'Analyzing...' : 'Run Funnel Analysis'}
      </button>

      {/* Results */}
      {result && (
        <div className="mt-8 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-sm text-blue-600 font-medium">Total Entered</div>
              <div className="text-2xl font-bold text-blue-900">{result.total_entered}</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-sm text-green-600 font-medium">Completed</div>
              <div className="text-2xl font-bold text-green-900">{result.total_completed}</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-sm text-purple-600 font-medium">Overall Conversion</div>
              <div className="text-2xl font-bold text-purple-900">{result.overall_conversion}%</div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <ReactECharts option={getFunnelOption()} style={{ height: '500px' }} />
          </div>
        </div>
      )}
    </div>
  );
};

export default FunnelAnalysis;