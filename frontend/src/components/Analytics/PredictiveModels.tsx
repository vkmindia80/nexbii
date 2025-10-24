import React, { useState } from 'react';
import { Brain, Play, AlertCircle, Info, TrendingUp, CheckCircle } from 'lucide-react';
import analyticsService, { PredictiveModelRequest } from '../../services/analyticsService';

interface Props {
  dataSources: Array<{ id: string; name: string; type: string }>;
}

interface ModelResult {
  model_id: string;
  model_type: string;
  target_column: string;
  feature_columns: string[];
  metrics: {
    accuracy?: number;
    precision?: number;
    recall?: number;
    f1_score?: number;
    r2_score?: number;
    mse?: number;
    rmse?: number;
    mae?: number;
  };
  feature_importance?: { [key: string]: number };
  predictions_sample: any[];
  training_info: {
    train_samples: number;
    test_samples: number;
    training_time: number;
  };
}

const PredictiveModels: React.FC<Props> = ({ dataSources }) => {
  const [selectedDatasource, setSelectedDatasource] = useState('');
  const [query, setQuery] = useState('');
  const [modelType, setModelType] = useState<'linear_regression' | 'logistic_regression' | 'random_forest' | 'decision_tree'>('random_forest');
  const [targetColumn, setTargetColumn] = useState('');
  const [featureColumns, setFeatureColumns] = useState<string[]>(['']);
  const [testSize, setTestSize] = useState(0.2);
  const [crossValidation, setCrossValidation] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ModelResult | null>(null);
  const [error, setError] = useState('');

  const modelDescriptions = {
    linear_regression: 'Predict continuous numeric values (e.g., sales, price, revenue)',
    logistic_regression: 'Binary classification (yes/no, true/false outcomes)',
    random_forest: 'Versatile model for both regression and classification with high accuracy',
    decision_tree: 'Interpretable model that creates decision rules'
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

  const handleTrainModel = async () => {
    if (!selectedDatasource || !query || !targetColumn) {
      setError('Please select data source, enter query, and specify target column');
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
      const request: PredictiveModelRequest = {
        datasource_id: selectedDatasource,
        query: query,
        target_column: targetColumn,
        feature_columns: validFeatures,
        model_type: modelType,
        test_size: testSize,
        cross_validation: crossValidation
      };

      const data = await analyticsService.trainPredictiveModel(request);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to train model');
    } finally {
      setLoading(false);
    }
  };

  const loadSampleQuery = () => {
    setQuery('SELECT age, income, years_customer, purchase_frequency, churn FROM customers');
    setTargetColumn('churn');
    setFeatureColumns(['age', 'income', 'years_customer', 'purchase_frequency']);
    setModelType('random_forest');
  };

  const isClassification = modelType === 'logistic_regression' || modelType === 'random_forest' || modelType === 'decision_tree';

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Brain className="w-6 h-6 text-purple-600" />
          Predictive Models
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Train ML models for predictions: Regression, Classification, Random Forest, Decision Trees
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configuration Panel */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Configuration</h3>

          <div className="space-y-4">
            {/* Data Source */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Data Source *
              </label>
              <select
                value={selectedDatasource}
                onChange={(e) => setSelectedDatasource(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
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

            {/* Model Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Model Type *
              </label>
              <select
                value={modelType}
                onChange={(e) => setModelType(e.target.value as any)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                data-testid="model-type-select"
              >
                <option value="linear_regression">Linear Regression</option>
                <option value="logistic_regression">Logistic Regression</option>
                <option value="random_forest">Random Forest</option>
                <option value="decision_tree">Decision Tree</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">{modelDescriptions[modelType]}</p>
            </div>

            {/* Query */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-700">
                  SQL Query *
                </label>
                <button
                  onClick={loadSampleQuery}
                  className="text-xs text-purple-600 hover:text-purple-700"
                >
                  Load Sample
                </button>
              </div>
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 font-mono text-sm"
                rows={4}
                placeholder="SELECT features, target FROM table"
                data-testid="query-input"
              />
            </div>

            {/* Target Column */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target Column * (what to predict)
              </label>
              <input
                type="text"
                value={targetColumn}
                onChange={(e) => setTargetColumn(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                placeholder="target_column"
                data-testid="target-input"
              />
            </div>

            {/* Feature Columns */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Feature Columns * (predictors)
              </label>
              {featureColumns.map((feature, index) => (
                <div key={index} className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={feature}
                    onChange={(e) => handleFeatureChange(index, e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
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
                className="text-sm text-purple-600 hover:text-purple-700"
              >
                + Add Feature
              </button>
            </div>

            {/* Test Size */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Test Size: {(testSize * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0.1"
                max="0.4"
                step="0.05"
                value={testSize}
                onChange={(e) => setTestSize(parseFloat(e.target.value))}
                className="w-full"
                data-testid="test-size-slider"
              />
              <p className="text-xs text-gray-500 mt-1">
                {((1 - testSize) * 100).toFixed(0)}% training, {(testSize * 100).toFixed(0)}% testing
              </p>
            </div>

            {/* Cross Validation */}
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={crossValidation}
                onChange={(e) => setCrossValidation(e.target.checked)}
                className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                data-testid="cv-checkbox"
              />
              <label className="ml-2 text-sm text-gray-700">
                Use Cross-Validation (5-fold)
              </label>
            </div>

            {/* Train Button */}
            <button
              onClick={handleTrainModel}
              disabled={loading || !selectedDatasource || !query}
              className="w-full bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              data-testid="train-button"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  Training Model...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Train Model
                </>
              )}
            </button>
          </div>
        </div>

        {/* Results Panel */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Results</h3>

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
              <p className="text-gray-600">Configure and train a model to see results</p>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              {/* Model Info */}
              <div className="flex items-center justify-between pb-4 border-b border-gray-200">
                <div>
                  <h4 className="font-medium text-gray-900">{result.model_type.replace('_', ' ').toUpperCase()}</h4>
                  <p className="text-sm text-gray-500">Model ID: {result.model_id}</p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-500" />
              </div>

              {/* Performance Metrics */}
              <div>
                <p className="text-sm font-medium text-gray-700 mb-3">Performance Metrics</p>
                <div className="grid grid-cols-2 gap-3">
                  {result.metrics.accuracy !== undefined && (
                    <div className="bg-green-50 p-3 rounded-lg">
                      <p className="text-xs text-gray-600">Accuracy</p>
                      <p className="text-xl font-bold text-gray-900">{(result.metrics.accuracy * 100).toFixed(2)}%</p>
                    </div>
                  )}
                  {result.metrics.precision !== undefined && (
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <p className="text-xs text-gray-600">Precision</p>
                      <p className="text-xl font-bold text-gray-900">{(result.metrics.precision * 100).toFixed(2)}%</p>
                    </div>
                  )}
                  {result.metrics.recall !== undefined && (
                    <div className="bg-purple-50 p-3 rounded-lg">
                      <p className="text-xs text-gray-600">Recall</p>
                      <p className="text-xl font-bold text-gray-900">{(result.metrics.recall * 100).toFixed(2)}%</p>
                    </div>
                  )}
                  {result.metrics.f1_score !== undefined && (
                    <div className="bg-yellow-50 p-3 rounded-lg">
                      <p className="text-xs text-gray-600">F1 Score</p>
                      <p className="text-xl font-bold text-gray-900">{(result.metrics.f1_score * 100).toFixed(2)}%</p>
                    </div>
                  )}
                  {result.metrics.r2_score !== undefined && (
                    <div className="bg-indigo-50 p-3 rounded-lg">
                      <p className="text-xs text-gray-600">R² Score</p>
                      <p className="text-xl font-bold text-gray-900">{result.metrics.r2_score.toFixed(4)}</p>
                    </div>
                  )}
                  {result.metrics.rmse !== undefined && (
                    <div className="bg-red-50 p-3 rounded-lg">
                      <p className="text-xs text-gray-600">RMSE</p>
                      <p className="text-xl font-bold text-gray-900">{result.metrics.rmse.toFixed(2)}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Feature Importance */}
              {result.feature_importance && Object.keys(result.feature_importance).length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-3">Feature Importance</p>
                  <div className="space-y-2">
                    {Object.entries(result.feature_importance)
                      .sort(([, a], [, b]) => b - a)
                      .map(([feature, importance]) => (
                        <div key={feature}>
                          <div className="flex justify-between text-xs text-gray-600 mb-1">
                            <span>{feature}</span>
                            <span>{(importance * 100).toFixed(1)}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-purple-600 h-2 rounded-full"
                              style={{ width: `${importance * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {/* Training Info */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm font-medium text-gray-700 mb-2">Training Information</p>
                <div className="grid grid-cols-3 gap-2 text-xs text-gray-600">
                  <div>
                    <p className="text-gray-500">Train Samples</p>
                    <p className="font-medium text-gray-900">{result.training_info.train_samples}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Test Samples</p>
                    <p className="font-medium text-gray-900">{result.training_info.test_samples}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Training Time</p>
                    <p className="font-medium text-gray-900">{result.training_info.training_time.toFixed(2)}s</p>
                  </div>
                </div>
              </div>

              {/* Predictions Sample */}
              {result.predictions_sample && result.predictions_sample.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Sample Predictions</p>
                  <div className="bg-gray-50 p-3 rounded-lg text-xs font-mono overflow-x-auto">
                    <pre>{JSON.stringify(result.predictions_sample.slice(0, 5), null, 2)}</pre>
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

export default PredictiveModels;