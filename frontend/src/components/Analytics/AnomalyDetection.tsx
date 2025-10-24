import React, { useState } from 'react';
import { AlertTriangle, Play, AlertCircle, Info } from 'lucide-react';
import analyticsService, { AnomalyDetectionRequest } from '../../services/analyticsService';

interface Props {
  dataSources: Array<{ id: string; name: string; type: string }>;
}

interface AnomalyResult {
  anomalies: any[];
  anomaly_indices: number[];
  total_records: number;
  anomaly_count: number;
  anomaly_percentage: number;
  method: string;
  contamination: number;
}

const AnomalyDetection: React.FC<Props> = ({ dataSources }) => {
  const [selectedDatasource, setSelectedDatasource] = useState('');
  const [query, setQuery] = useState('');
  const [featureColumns, setFeatureColumns] = useState<string[]>(['']);
  const [method, setMethod] = useState<'isolation_forest' | 'local_outlier_factor' | 'one_class_svm'>('isolation_forest');
  const [contamination, setContamination] = useState(0.1);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnomalyResult | null>(null);
  const [error, setError] = useState('');

  const methodDescriptions = {
    isolation_forest: 'Effective for high-dimensional datasets, isolates anomalies using random forests',
    local_outlier_factor: 'Identifies local outliers based on density of neighbors',
    one_class_svm: 'Learns the boundary of normal data, effective for complex patterns'
  };

  const handleAddFeature = () => setFeatureColumns([...featureColumns, '']);

  const handleRemoveFeature = (index: number) => {
    if (featureColumns.length > 1) {
      setFeatureColumns(featureColumns.filter((_, i) => i !== index));
    }
  };

  const handleFeatureChange = (index: number, value: string) => {
    const newFeatures = [...featureColumns];
    newFeatures[index] = value;
    setFeatureColumns(newFeatures);
  };

  const handleDetectAnomalies = async () => {
    if (!selectedDatasource || !query) {
      setError('Please select data source and enter query');
      return;
    }

    const validFeatures = featureColumns.filter(f => f.trim() !== '');
    if (validFeatures.length === 0) {
      setError('Please specify at least one feature column');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const request: AnomalyDetectionRequest = {
        datasource_id: selectedDatasource,
        query: query,
        feature_columns: validFeatures,
        method: method,
        contamination: contamination
      };

      const data = await analyticsService.detectAnomalies(request);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to detect anomalies');
    } finally {
      setLoading(false);
    }
  };

  const loadSampleQuery = () => {
    setQuery('SELECT transaction_amount, transaction_count, user_age, account_balance FROM transactions');
    setFeatureColumns(['transaction_amount', 'transaction_count', 'user_age', 'account_balance']);
    setMethod('isolation_forest');
    setContamination(0.1);
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <AlertTriangle className="w-6 h-6 text-orange-600" />
          Anomaly Detection
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Identify outliers using Isolation Forest, Local Outlier Factor, or One-Class SVM
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configuration Panel */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Detection Configuration</h3>

          <div className="space-y-4">
            {/* Data Source */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Data Source *
              </label>
              <select
                value={selectedDatasource}
                onChange={(e) => setSelectedDatasource(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                data-testid="datasource-select"
              >
                <option value="">Select a data source...</option>
                {dataSources.map((ds) => (
                  <option key={ds.id} value={ds.id}>
                    {ds.name} ({ds.type})
                  </option>
                ))}
              </select>
            </div>

            {/* Detection Method */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Detection Method *
              </label>
              <select
                value={method}
                onChange={(e) => setMethod(e.target.value as any)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                data-testid="method-select"
              >
                <option value="isolation_forest">Isolation Forest</option>
                <option value="local_outlier_factor">Local Outlier Factor</option>
                <option value="one_class_svm">One-Class SVM</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">{methodDescriptions[method]}</p>
            </div>

            {/* Query */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-700">
                  SQL Query *
                </label>
                <button
                  onClick={loadSampleQuery}
                  className="text-xs text-orange-600 hover:text-orange-700"
                >
                  Load Sample
                </button>
              </div>
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 font-mono text-sm"
                rows={4}
                placeholder="SELECT features FROM table"
                data-testid="query-input"
              />
            </div>

            {/* Feature Columns */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Feature Columns * (numeric)
              </label>
              {featureColumns.map((feature, index) => (
                <div key={index} className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={feature}
                    onChange={(e) => handleFeatureChange(index, e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                    placeholder="feature_column"
                    data-testid={`feature-input-${index}`}
                  />
                  {featureColumns.length > 1 && (
                    <button
                      onClick={() => handleRemoveFeature(index)}
                      className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg"
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
              <button
                onClick={handleAddFeature}
                className="text-sm text-orange-600 hover:text-orange-700"
              >
                + Add Feature
              </button>
            </div>

            {/* Contamination */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Expected Anomaly Rate: {(contamination * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0.01"
                max="0.5"
                step="0.01"
                value={contamination}
                onChange={(e) => setContamination(parseFloat(e.target.value))}
                className="w-full"
                data-testid="contamination-slider"
              />
              <p className="text-xs text-gray-500 mt-1">
                Proportion of outliers in the dataset (typically 1-10%)
              </p>
            </div>

            {/* Detect Button */}
            <button
              onClick={handleDetectAnomalies}
              disabled={loading || !selectedDatasource || !query}
              className="w-full bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              data-testid="detect-button"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  Detecting Anomalies...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Detect Anomalies
                </>
              )}
            </button>
          </div>
        </div>

        {/* Results Panel */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Detection Results</h3>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-red-800">Error</p>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          )}

          {!result && !error && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
              <Info className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600">Configure and run anomaly detection to see results</p>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              {/* Summary Stats */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Total Records</p>
                  <p className="text-2xl font-bold text-gray-900">{result.total_records.toLocaleString()}</p>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Anomalies Found</p>
                  <p className="text-2xl font-bold text-orange-600">{result.anomaly_count.toLocaleString()}</p>
                </div>
              </div>

              <div className="bg-orange-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Anomaly Rate</p>
                <p className="text-3xl font-bold text-orange-600">{result.anomaly_percentage.toFixed(2)}%</p>
                <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-orange-600 h-2 rounded-full"
                    style={{ width: `${result.anomaly_percentage}%` }}
                  ></div>
                </div>
              </div>

              {/* Method Info */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm font-medium text-gray-700 mb-2">Detection Method</p>
                <p className="text-sm text-gray-900">{result.method.replace(/_/g, ' ').toUpperCase()}</p>
                <p className="text-xs text-gray-500 mt-1">
                  Expected contamination: {(result.contamination * 100).toFixed(1)}%
                </p>
              </div>

              {/* Anomalous Records */}
              {result.anomalies && result.anomalies.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    Sample Anomalies (showing first 10)
                  </p>
                  <div className="bg-orange-50 border border-orange-200 rounded-lg overflow-hidden">
                    <div className="max-h-96 overflow-y-auto">
                      <table className="min-w-full divide-y divide-orange-200">
                        <thead className="bg-orange-100 sticky top-0">
                          <tr>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-700">Index</th>
                            {Object.keys(result.anomalies[0] || {}).map((key) => (
                              <th key={key} className="px-3 py-2 text-left text-xs font-medium text-gray-700">
                                {key}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-orange-100">
                          {result.anomalies.slice(0, 10).map((anomaly, idx) => (
                            <tr key={idx} className="hover:bg-orange-50">
                              <td className="px-3 py-2 text-sm text-gray-900 font-medium">
                                {result.anomaly_indices[idx]}
                              </td>
                              {Object.values(anomaly).map((value: any, i) => (
                                <td key={i} className="px-3 py-2 text-sm text-gray-700">
                                  {typeof value === 'number' ? value.toLocaleString() : String(value)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {/* Recommendations */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm font-medium text-blue-900 mb-2">💡 Next Steps</p>
                <ul className="text-xs text-blue-800 space-y-1">
                  <li>• Investigate flagged anomalies for potential fraud or errors</li>
                  <li>• Consider domain expertise to validate findings</li>
                  <li>• Adjust contamination parameter if results seem off</li>
                  <li>• Try different detection methods for comparison</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnomalyDetection;