import React, { useState } from 'react';
import { UserX, Play, AlertCircle, Info, AlertTriangle, CheckCircle } from 'lucide-react';
import analyticsService, { ChurnPredictionRequest } from '../../services/analyticsService';

interface Props {
  dataSources: Array<{ id: string; name: string; type: string }>;
}

interface ChurnResult {
  model_id: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  churn_predictions: Array<{
    customer_id: string;
    churn_probability: number;
    churn_prediction: boolean;
    risk_level: 'high' | 'medium' | 'low';
  }>;
  feature_importance: { [key: string]: number };
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
}

const ChurnPrediction: React.FC<Props> = ({ dataSources }) => {
  const [selectedDatasource, setSelectedDatasource] = useState('');
  const [query, setQuery] = useState('');
  const [customerIdColumn, setCustomerIdColumn] = useState('');
  const [targetColumn, setTargetColumn] = useState('');
  const [featureColumns, setFeatureColumns] = useState<string[]>(['']);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ChurnResult | null>(null);
  const [error, setError] = useState('');

  const handleAddFeature = () => setFeatureColumns([...featureColumns, '']);
  const handleRemoveFeature = (index: number) => {
    if (featureColumns.length > 1) setFeatureColumns(featureColumns.filter((_, i) => i !== index));
  };
  const handleFeatureChange = (index: number, value: string) => {
    const newFeatures = [...featureColumns];
    newFeatures[index] = value;
    setFeatureColumns(newFeatures);
  };

  const handlePredictChurn = async () => {
    if (!selectedDatasource || !query || !customerIdColumn || !targetColumn) {
      setError('Please fill in all required fields');
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
      const request: ChurnPredictionRequest = {
        datasource_id: selectedDatasource,
        query: query,
        customer_id_column: customerIdColumn,
        target_column: targetColumn,
        feature_columns: validFeatures
      };

      const data = await analyticsService.predictChurn(request);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to predict churn');
    } finally {
      setLoading(false);
    }
  };

  const loadSampleQuery = () => {
    setQuery('SELECT customer_id, tenure_months, monthly_charges, total_charges, contract_type, payment_method, churn FROM customers');
    setCustomerIdColumn('customer_id');
    setTargetColumn('churn');
    setFeatureColumns(['tenure_months', 'monthly_charges', 'total_charges', 'contract_type', 'payment_method']);
  };

  const getRiskBadgeColor = (risk: string) => {
    switch (risk) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <UserX className="w-6 h-6 text-red-600" />
          Churn Prediction
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Predict customer churn with Random Forest models and identify high-risk customers
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configuration Panel */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Prediction Configuration</h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Data Source *</label>
              <select
                value={selectedDatasource}
                onChange={(e) => setSelectedDatasource(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                data-testid="datasource-select"
              >
                <option value="">Select a data source...</option>
                {dataSources.map((ds) => (
                  <option key={ds.id} value={ds.id}>{ds.name} ({ds.type})</option>
                ))}
              </select>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-700">SQL Query *</label>
                <button onClick={loadSampleQuery} className="text-xs text-red-600 hover:text-red-700">Load Sample</button>
              </div>
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 font-mono text-sm"
                rows={4}
                placeholder="SELECT customer_id, features, churn FROM customers"
                data-testid="query-input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Customer ID Column *</label>
              <input
                type="text"
                value={customerIdColumn}
                onChange={(e) => setCustomerIdColumn(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                placeholder="customer_id"
                data-testid="customer-id-input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Target Column * (churn indicator)</label>
              <input
                type="text"
                value={targetColumn}
                onChange={(e) => setTargetColumn(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                placeholder="churn"
                data-testid="target-input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Feature Columns *</label>
              {featureColumns.map((feature, index) => (
                <div key={index} className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={feature}
                    onChange={(e) => handleFeatureChange(index, e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                    placeholder="feature_column"
                    data-testid={`feature-input-${index}`}
                  />
                  {featureColumns.length > 1 && (
                    <button onClick={() => handleRemoveFeature(index)} className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg">Remove</button>
                  )}
                </div>
              ))}
              <button onClick={handleAddFeature} className="text-sm text-red-600 hover:text-red-700">+ Add Feature</button>
            </div>

            <button
              onClick={handlePredictChurn}
              disabled={loading || !selectedDatasource || !query}
              className="w-full bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              data-testid="predict-button"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  Predicting...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Predict Churn
                </>
              )}
            </button>
          </div>
        </div>

        {/* Results Panel */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Prediction Results</h3>

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
              <p className="text-gray-600">Configure and run churn prediction to see results</p>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              <div className="flex items-center justify-between pb-4 border-b border-gray-200">
                <div>
                  <h4 className="font-medium text-gray-900">Churn Model</h4>
                  <p className="text-sm text-gray-500">Model ID: {result.model_id}</p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-500" />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="bg-green-50 p-3 rounded-lg">
                  <p className="text-xs text-gray-600">Accuracy</p>
                  <p className="text-xl font-bold text-gray-900">{(result.accuracy * 100).toFixed(1)}%</p>
                </div>
                <div className="bg-blue-50 p-3 rounded-lg">
                  <p className="text-xs text-gray-600">Precision</p>
                  <p className="text-xl font-bold text-gray-900">{(result.precision * 100).toFixed(1)}%</p>
                </div>
                <div className="bg-purple-50 p-3 rounded-lg">
                  <p className="text-xs text-gray-600">Recall</p>
                  <p className="text-xl font-bold text-gray-900">{(result.recall * 100).toFixed(1)}%</p>
                </div>
                <div className="bg-yellow-50 p-3 rounded-lg">
                  <p className="text-xs text-gray-600">F1 Score</p>
                  <p className="text-xl font-bold text-gray-900">{(result.f1_score * 100).toFixed(1)}%</p>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm font-medium text-gray-700 mb-3">Risk Distribution</p>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-red-600" />
                      High Risk
                    </span>
                    <span className="font-bold text-red-600">{result.high_risk_count}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-yellow-600" />
                      Medium Risk
                    </span>
                    <span className="font-bold text-yellow-600">{result.medium_risk_count}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-600" />
                      Low Risk
                    </span>
                    <span className="font-bold text-green-600">{result.low_risk_count}</span>
                  </div>
                </div>
              </div>

              {result.churn_predictions && result.churn_predictions.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">High Risk Customers (Top 10)</p>
                  <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                    <div className="max-h-64 overflow-y-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50 sticky top-0">
                          <tr>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Customer</th>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Probability</th>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Risk</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {result.churn_predictions
                            .filter(p => p.churn_prediction)
                            .sort((a, b) => b.churn_probability - a.churn_probability)
                            .slice(0, 10)
                            .map((pred, idx) => (
                              <tr key={idx} className="hover:bg-gray-50">
                                <td className="px-3 py-2 text-sm text-gray-900">{pred.customer_id}</td>
                                <td className="px-3 py-2 text-sm text-gray-700">{(pred.churn_probability * 100).toFixed(1)}%</td>
                                <td className="px-3 py-2">
                                  <span className={`px-2 py-1 text-xs rounded-full border ${getRiskBadgeColor(pred.risk_level)}`}>
                                    {pred.risk_level.toUpperCase()}
                                  </span>
                                </td>
                              </tr>
                            ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {result.feature_importance && Object.keys(result.feature_importance).length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Feature Importance</p>
                  <div className="space-y-2">
                    {Object.entries(result.feature_importance)
                      .sort(([, a], [, b]) => b - a)
                      .slice(0, 5)
                      .map(([feature, importance]) => (
                        <div key={feature}>
                          <div className="flex justify-between text-xs text-gray-600 mb-1">
                            <span>{feature}</span>
                            <span>{(importance * 100).toFixed(1)}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div className="bg-red-600 h-2 rounded-full" style={{ width: `${importance * 100}%` }}></div>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChurnPrediction;