import React, { useState } from 'react';
import { BarChart3, Play, AlertCircle, CheckCircle, Info } from 'lucide-react';
import analyticsService, { StatisticalTestRequest } from '../../services/analyticsService';

interface Props {
  dataSources: Array<{ id: string; name: string; type: string }>;
}

interface TestResult {
  test_type: string;
  statistic: number;
  p_value: number;
  significant: boolean;
  conclusion: string;
  details: any;
}

const StatisticalTests: React.FC<Props> = ({ dataSources }) => {
  const [selectedDatasource, setSelectedDatasource] = useState('');
  const [testType, setTestType] = useState<'ttest' | 'chi_square' | 'anova' | 'correlation' | 'normality'>('ttest');
  const [query, setQuery] = useState('');
  const [columns, setColumns] = useState<string[]>(['']);
  const [groupColumn, setGroupColumn] = useState('');
  const [alpha, setAlpha] = useState(0.05);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TestResult | null>(null);
  const [error, setError] = useState('');

  const testDescriptions = {
    ttest: 'Compare means between two groups (requires 1 numeric column and 1 group column with exactly 2 groups)',
    chi_square: 'Test independence between two categorical variables (requires 2 categorical columns)',
    anova: 'Compare means across multiple groups (requires 1 numeric column and 1 group column)',
    correlation: 'Analyze relationships between numeric variables (requires 2+ numeric columns)',
    normality: 'Test if data follows normal distribution (requires 1 numeric column)'
  };

  const handleAddColumn = () => {
    setColumns([...columns, '']);
  };

  const handleRemoveColumn = (index: number) => {
    if (columns.length > 1) {
      setColumns(columns.filter((_, i) => i !== index));
    }
  };

  const handleColumnChange = (index: number, value: string) => {
    const newColumns = [...columns];
    newColumns[index] = value;
    setColumns(newColumns);
  };

  const handleRunTest = async () => {
    if (!selectedDatasource || !query) {
      setError('Please select a data source and enter a query');
      return;
    }

    const validColumns = columns.filter(c => c.trim() !== '');
    if (validColumns.length === 0) {
      setError('Please specify at least one column');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const request: StatisticalTestRequest = {
        datasource_id: selectedDatasource,
        test_type: testType,
        query: query,
        columns: validColumns,
        group_column: groupColumn || undefined,
        alpha: alpha
      };

      const data = await analyticsService.statisticalTest(request);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to perform statistical test');
    } finally {
      setLoading(false);
    }
  };

  const loadSampleQuery = () => {
    // Load sample query based on test type
    const sampleQueries = {
      ttest: 'SELECT gender, salary FROM employees',
      chi_square: 'SELECT department, performance_rating FROM employees',
      anova: 'SELECT department, salary FROM employees',
      correlation: 'SELECT age, salary, years_experience FROM employees',
      normality: 'SELECT salary FROM employees'
    };
    setQuery(sampleQueries[testType]);
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-blue-600" />
          Statistical Tests
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Perform hypothesis testing: t-tests, chi-square, ANOVA, correlation, normality tests
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configuration Panel */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Test Configuration</h3>

          {/* Data Source */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Data Source *
            </label>
            <select
              value={selectedDatasource}
              onChange={(e) => setSelectedDatasource(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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

          {/* Test Type */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Test Type *
            </label>
            <select
              value={testType}
              onChange={(e) => setTestType(e.target.value as any)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              data-testid="test-type-select"
            >
              <option value="ttest">Independent t-test</option>
              <option value="chi_square">Chi-Square Test</option>
              <option value="anova">One-way ANOVA</option>
              <option value="correlation">Correlation Analysis</option>
              <option value="normality">Normality Test</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">{testDescriptions[testType]}</p>
          </div>

          {/* Query */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-700">
                SQL Query *
              </label>
              <button
                onClick={loadSampleQuery}
                className="text-xs text-blue-600 hover:text-blue-700"
              >
                Load Sample
              </button>
            </div>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              rows={4}
              placeholder="SELECT column1, column2 FROM table WHERE ..."
              data-testid="query-input"
            />
          </div>

          {/* Columns */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Columns to Test *
            </label>
            {columns.map((col, index) => (
              <div key={index} className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={col}
                  onChange={(e) => handleColumnChange(index, e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="column_name"
                  data-testid={`column-input-${index}`}
                />
                {columns.length > 1 && (
                  <button
                    onClick={() => handleRemoveColumn(index)}
                    className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg"
                  >
                    Remove
                  </button>
                )}
              </div>
            ))}
            <button
              onClick={handleAddColumn}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              + Add Column
            </button>
          </div>

          {/* Group Column (for t-test and ANOVA) */}
          {(testType === 'ttest' || testType === 'anova') && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Group Column *
              </label>
              <input
                type="text"
                value={groupColumn}
                onChange={(e) => setGroupColumn(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="group_column_name"
                data-testid="group-column-input"
              />
            </div>
          )}

          {/* Alpha Level */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Significance Level (alpha)
            </label>
            <select
              value={alpha}
              onChange={(e) => setAlpha(parseFloat(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              data-testid="alpha-select"
            >
              <option value="0.01">0.01 (99% confidence)</option>
              <option value="0.05">0.05 (95% confidence)</option>
              <option value="0.10">0.10 (90% confidence)</option>
            </select>
          </div>

          {/* Run Button */}
          <button
            onClick={handleRunTest}
            disabled={loading || !selectedDatasource || !query}
            className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            data-testid="run-test-button"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                Running Test...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Run Statistical Test
              </>
            )}
          </button>
        </div>

        {/* Results Panel */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Test Results</h3>

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
              <p className="text-gray-600">Configure and run a statistical test to see results</p>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              {/* Test Type & Status */}
              <div className="flex items-center justify-between pb-4 border-b border-gray-200">
                <div>
                  <h4 className="font-medium text-gray-900">{result.test_type}</h4>
                  <p className="text-sm text-gray-500">Significance level: α = {alpha}</p>
                </div>
                <div className="flex items-center gap-2">
                  {result.significant ? (
                    <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1">
                      <CheckCircle className="w-4 h-4" />
                      Significant
                    </span>
                  ) : (
                    <span className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm font-medium">
                      Not Significant
                    </span>
                  )}
                </div>
              </div>

              {/* Statistics */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Test Statistic</p>
                  <p className="text-2xl font-bold text-gray-900">{result.statistic.toFixed(4)}</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">P-Value</p>
                  <p className="text-2xl font-bold text-gray-900">{result.p_value.toFixed(6)}</p>
                </div>
              </div>

              {/* Conclusion */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm font-medium text-gray-700 mb-2">Conclusion</p>
                <p className="text-sm text-gray-900">{result.conclusion}</p>
              </div>

              {/* Details */}
              {result.details && Object.keys(result.details).length > 0 && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm font-medium text-gray-700 mb-3">Additional Details</p>
                  <div className="space-y-2">
                    {Object.entries(result.details).map(([key, value]) => (
                      <div key={key} className="flex justify-between text-sm">
                        <span className="text-gray-600">{key.replace(/_/g, ' ')}:</span>
                        <span className="font-medium text-gray-900">
                          {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Interpretation Guide */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm font-medium text-blue-900 mb-2">💡 Interpretation Guide</p>
                <ul className="text-xs text-blue-800 space-y-1">
                  <li>• p-value &lt; alpha: Reject null hypothesis (result is significant)</li>
                  <li>• p-value &gt;= alpha: Fail to reject null hypothesis (result is not significant)</li>
                  <li>• Lower p-value = stronger evidence against null hypothesis</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StatisticalTests;