import React, { useState } from 'react';
import { Play, TrendingUp } from 'lucide-react';
import analyticsService, { TimeSeriesForecastRequest } from '../../services/analyticsService';
import ReactECharts from 'echarts-for-react';

interface Props {
  dataSources: Array<{ id: string; name: string; type: string }>;
}

const TimeSeriesForecasting: React.FC<Props> = ({ dataSources }) => {
  const [formData, setFormData] = useState<Partial<TimeSeriesForecastRequest>>({
    datasource_id: '',
    query: '',
    date_column: 'date',
    value_column: 'value',
    periods: 30,
    frequency: 'D',
    model_type: 'arima',
    confidence_interval: 0.95
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>('');

  const handleAnalyze = async () => {
    if (!formData.datasource_id || !formData.query) {
      setError('Please select data source and enter SQL query');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const data = await analyticsService.timeSeriesForecast(formData as TimeSeriesForecastRequest);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to perform forecasting');
    } finally {
      setLoading(false);
    }
  };

  const getForecastOption = () => {
    if (!result) return {};

    return {
      title: { text: 'Time Series Forecast', left: 'center' },
      tooltip: { trigger: 'axis' },
      legend: { data: ['Historical', 'Forecast', 'Confidence Interval'], bottom: 10 },
      xAxis: {
        type: 'category',
        data: [...result.historical_dates, ...result.forecast_dates],
        axisLabel: { rotate: 45 }
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: 'Historical',
          type: 'line',
          data: [...result.historical_values, ...Array(result.forecast_values.length).fill(null)],
          lineStyle: { width: 2 },
          itemStyle: { color: '#2196f3' }
        },
        {
          name: 'Forecast',
          type: 'line',
          data: [...Array(result.historical_values.length).fill(null), ...result.forecast_values],
          lineStyle: { width: 2, type: 'dashed' },
          itemStyle: { color: '#4caf50' }
        },
        {
          name: 'Confidence Interval',
          type: 'line',
          data: [...Array(result.historical_values.length).fill(null), ...result.upper_bound],
          lineStyle: { width: 0 },
          areaStyle: { color: 'rgba(76, 175, 80, 0.2)' },
          stack: 'confidence',
          symbol: 'none'
        },
        {
          name: 'Lower Bound',
          type: 'line',
          data: [...Array(result.historical_values.length).fill(null), ...result.lower_bound],
          lineStyle: { width: 0 },
          areaStyle: { color: 'rgba(76, 175, 80, 0.2)' },
          stack: 'confidence',
          symbol: 'none'
        }
      ]
    };
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-blue-600" />
          Time Series Forecasting
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Predict future trends using advanced forecasting models (ARIMA, Prophet, Seasonal)
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
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
          <label className="block text-sm font-medium text-gray-700 mb-1">Model Type</label>
          <select
            value={formData.model_type}
            onChange={(e) => setFormData({ ...formData, model_type: e.target.value as any })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="arima">ARIMA</option>
            <option value="prophet">Prophet</option>
            <option value="seasonal">Seasonal Decomposition</option>
          </select>
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">SQL Query *</label>
          <textarea
            value={formData.query}
            onChange={(e) => setFormData({ ...formData, query: e.target.value })}
            placeholder="SELECT date, revenue FROM sales ORDER BY date"
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Date Column</label>
          <input
            type="text"
            value={formData.date_column}
            onChange={(e) => setFormData({ ...formData, date_column: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Value Column</label>
          <input
            type="text"
            value={formData.value_column}
            onChange={(e) => setFormData({ ...formData, value_column: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Forecast Periods</label>
          <input
            type="number"
            value={formData.periods}
            onChange={(e) => setFormData({ ...formData, periods: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Frequency</label>
          <select
            value={formData.frequency}
            onChange={(e) => setFormData({ ...formData, frequency: e.target.value as any })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="D">Daily</option>
            <option value="W">Weekly</option>
            <option value="M">Monthly</option>
            <option value="Q">Quarterly</option>
            <option value="Y">Yearly</option>
          </select>
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
        {loading ? 'Forecasting...' : 'Generate Forecast'}
      </button>

      {result && (
        <div className="mt-8 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-sm text-blue-600 font-medium">Trend Direction</div>
              <div className="text-2xl font-bold text-blue-900 capitalize">{result.trend_direction}</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-sm text-green-600 font-medium">Model</div>
              <div className="text-lg font-bold text-green-900">{result.model_metrics.model || formData.model_type}</div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <ReactECharts option={getForecastOption()} style={{ height: '500px' }} />
          </div>
        </div>
      )}
    </div>
  );
};

export default TimeSeriesForecasting;