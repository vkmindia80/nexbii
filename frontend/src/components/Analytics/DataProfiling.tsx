import React, { useState } from 'react';
import { Play, Database, AlertCircle, CheckCircle } from 'lucide-react';
import analyticsService, { DataProfilingRequest } from '../../services/analyticsService';

interface Props {
  dataSources: Array<{ id: string; name: string; type: string }>;
}

const DataProfiling: React.FC<Props> = ({ dataSources }) => {
  const [formData, setFormData] = useState<Partial<DataProfilingRequest>>({
    datasource_id: '',
    table_name: '',
    sample_size: 10000
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
      const data = await analyticsService.profileData(formData as DataProfilingRequest);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to profile data');
    } finally {
      setLoading(false);
    }
  };

  const getQualityColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Database className="w-6 h-6 text-blue-600" />
          Data Profiling
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Comprehensive data quality assessment, missing values, outliers, and distributions
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
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
            placeholder="e.g., customers"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Sample Size</label>
          <input
            type="number"
            value={formData.sample_size}
            onChange={(e) => setFormData({ ...formData, sample_size: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
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
        {loading ? 'Profiling...' : 'Profile Data'}
      </button>

      {result && (
        <div className="mt-8 space-y-6">
          {/* Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-sm text-blue-600 font-medium">Total Rows</div>
              <div className="text-2xl font-bold text-blue-900">{result.row_count.toLocaleString()}</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-sm text-green-600 font-medium">Total Columns</div>
              <div className="text-2xl font-bold text-green-900">{result.column_count}</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-sm text-purple-600 font-medium">Data Quality Score</div>
              <div className={`text-2xl font-bold ${getQualityColor(result.data_quality_score)}`}>
                {result.data_quality_score.toFixed(1)}%
              </div>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-sm text-orange-600 font-medium">Issues Found</div>
              <div className="text-2xl font-bold text-orange-900">{result.issues.length}</div>
            </div>
          </div>

          {/* Issues */}
          {result.issues.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h3 className="font-semibold text-yellow-900 mb-2 flex items-center gap-2">
                <AlertCircle className="w-5 h-5" />
                Data Quality Issues
              </h3>
              <ul className="space-y-1">
                {result.issues.map((issue: string, idx: number) => (
                  <li key={idx} className="text-sm text-yellow-800">• {issue}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Column Profiles */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Column Profiles</h3>
            <div className="space-y-4">
              {result.columns.map((col: any, idx: number) => (
                <div key={idx} className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="font-semibold text-gray-900">{col.column_name}</h4>
                      <p className="text-sm text-gray-600">{col.data_type}</p>
                    </div>
                    {col.missing_percentage === 0 && (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    )}
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Missing:</span>
                      <span className={`ml-2 font-semibold ${col.missing_percentage > 10 ? 'text-red-600' : 'text-green-600'}`}>
                        {col.missing_percentage.toFixed(1)}%
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">Unique:</span>
                      <span className="ml-2 font-semibold text-gray-900">
                        {col.unique_count} ({col.unique_percentage.toFixed(1)}%)
                      </span>
                    </div>
                    {col.mean !== null && (
                      <>
                        <div>
                          <span className="text-gray-600">Mean:</span>
                          <span className="ml-2 font-semibold text-gray-900">{col.mean.toFixed(2)}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Std:</span>
                          <span className="ml-2 font-semibold text-gray-900">{col.std?.toFixed(2)}</span>
                        </div>
                      </>
                    )}
                    {col.outliers_count !== null && col.outliers_count > 0 && (
                      <div>
                        <span className="text-gray-600">Outliers:</span>
                        <span className="ml-2 font-semibold text-orange-600">{col.outliers_count}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataProfiling;