import React, { useState } from 'react';
import { Wand2, Sparkles, CheckCircle, AlertCircle, TrendingUp, BarChart3, Lightbulb, Loader } from 'lucide-react';
import { aiService } from '../services/aiService';

interface AIQueryPanelProps {
  datasourceId: string;
  onSQLGenerated: (sql: string, explanation: string) => void;
  currentSQL?: string;
  queryResult?: any;
}

const AIQueryPanel: React.FC<AIQueryPanelProps> = ({
  datasourceId,
  onSQLGenerated,
  currentSQL,
  queryResult
}) => {
  const [naturalQuery, setNaturalQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'generate' | 'validate' | 'optimize' | 'insights' | 'chart'>('generate');
  const [validationResult, setValidationResult] = useState<any>(null);
  const [optimizationResult, setOptimizationResult] = useState<any>(null);
  const [insights, setInsights] = useState<any>(null);
  const [chartRecommendation, setChartRecommendation] = useState<any>(null);

  const handleNaturalQuery = async () => {
    if (!naturalQuery.trim() || !datasourceId) return;

    setLoading(true);
    setAiResponse(null);

    try {
      const response = await aiService.naturalLanguageToSQL({
        natural_query: naturalQuery,
        datasource_id: datasourceId
      });

      setAiResponse(response);

      if (response.success && response.sql_query) {
        onSQLGenerated(response.sql_query, response.explanation);
      }
    } catch (error: any) {
      setAiResponse({
        success: false,
        error: error.response?.data?.detail || 'Failed to process query'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleValidateQuery = async () => {
    if (!currentSQL || !datasourceId) return;

    setLoading(true);
    setValidationResult(null);

    try {
      const response = await aiService.validateQuery({
        sql_query: currentSQL,
        datasource_id: datasourceId
      });

      setValidationResult(response);
    } catch (error: any) {
      setValidationResult({
        success: false,
        error: error.response?.data?.detail || 'Failed to validate query'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleOptimizeQuery = async () => {
    if (!currentSQL || !datasourceId) return;

    setLoading(true);
    setOptimizationResult(null);

    try {
      const response = await aiService.optimizeQuery({
        sql_query: currentSQL,
        datasource_id: datasourceId
      });

      setOptimizationResult(response);

      if (response.success && response.optimized_query) {
        // Optionally auto-apply the optimized query
        // onSQLGenerated(response.optimized_query, response.explanation);
      }
    } catch (error: any) {
      setOptimizationResult({
        success: false,
        error: error.response?.data?.detail || 'Failed to optimize query'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateInsights = async () => {
    if (!queryResult || !currentSQL) return;

    setLoading(true);
    setInsights(null);

    try {
      const response = await aiService.generateInsights({
        query_result: queryResult,
        sql_query: currentSQL
      });

      setInsights(response);
    } catch (error: any) {
      setInsights({
        success: false,
        error: error.response?.data?.detail || 'Failed to generate insights'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRecommendChart = async () => {
    if (!queryResult || !currentSQL) return;

    setLoading(true);
    setChartRecommendation(null);

    try {
      const response = await aiService.recommendChart({
        query_result: queryResult,
        sql_query: currentSQL
      });

      setChartRecommendation(response);
    } catch (error: any) {
      setChartRecommendation({
        success: false,
        error: error.response?.data?.detail || 'Failed to recommend chart'
      });
    } finally {
      setLoading(false);
    }
  };

  const exampleQueries = [
    "Show me top 10 customers by revenue",
    "What are the monthly sales trends for the last year?",
    "List all products with low stock (below 100 units)",
    "Calculate average order value by customer segment",
    "Find employees with performance rating above 4.5"
  ];

  return (
    <div className="bg-white rounded-lg shadow-md border-2 border-purple-200">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-4 rounded-t-lg">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-6 h-6" />
          <h3 className="text-lg font-semibold">AI-Powered Query Assistant</h3>
        </div>
        <p className="text-sm text-purple-100 mt-1">
          Natural language queries, validation, optimization, and insights
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => setActiveTab('generate')}
          className={`flex-1 px-4 py-3 text-sm font-medium flex items-center justify-center space-x-2 ${
            activeTab === 'generate'
              ? 'border-b-2 border-purple-600 text-purple-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Wand2 className="w-4 h-4" />
          <span>Generate SQL</span>
        </button>
        <button
          onClick={() => setActiveTab('validate')}
          className={`flex-1 px-4 py-3 text-sm font-medium flex items-center justify-center space-x-2 ${
            activeTab === 'validate'
              ? 'border-b-2 border-purple-600 text-purple-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
          disabled={!currentSQL}
        >
          <CheckCircle className="w-4 h-4" />
          <span>Validate</span>
        </button>
        <button
          onClick={() => setActiveTab('optimize')}
          className={`flex-1 px-4 py-3 text-sm font-medium flex items-center justify-center space-x-2 ${
            activeTab === 'optimize'
              ? 'border-b-2 border-purple-600 text-purple-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
          disabled={!currentSQL}
        >
          <TrendingUp className="w-4 h-4" />
          <span>Optimize</span>
        </button>
        <button
          onClick={() => setActiveTab('insights')}
          className={`flex-1 px-4 py-3 text-sm font-medium flex items-center justify-center space-x-2 ${
            activeTab === 'insights'
              ? 'border-b-2 border-purple-600 text-purple-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
          disabled={!queryResult}
        >
          <Lightbulb className="w-4 h-4" />
          <span>Insights</span>
        </button>
        <button
          onClick={() => setActiveTab('chart')}
          className={`flex-1 px-4 py-3 text-sm font-medium flex items-center justify-center space-x-2 ${
            activeTab === 'chart'
              ? 'border-b-2 border-purple-600 text-purple-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
          disabled={!queryResult}
        >
          <BarChart3 className="w-4 h-4" />
          <span>Chart</span>
        </button>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Generate SQL Tab */}
        {activeTab === 'generate' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ask in plain English:
              </label>
              <textarea
                value={naturalQuery}
                onChange={(e) => setNaturalQuery(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                rows={3}
                placeholder="e.g., Show me top 10 customers by revenue this year..."
              />
            </div>

            <button
              onClick={handleNaturalQuery}
              disabled={loading || !naturalQuery.trim()}
              className="w-full bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  <span>Generating SQL...</span>
                </>
              ) : (
                <>
                  <Wand2 className="w-5 h-5" />
                  <span>Generate SQL Query</span>
                </>
              )}
            </button>

            {/* Example queries */}
            <div>
              <p className="text-xs text-gray-500 mb-2">Try these examples:</p>
              <div className="flex flex-wrap gap-2">
                {exampleQueries.map((example, index) => (
                  <button
                    key={index}
                    onClick={() => setNaturalQuery(example)}
                    className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded-full"
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>

            {/* AI Response */}
            {aiResponse && (
              <div className={`p-4 rounded-lg ${aiResponse.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                {aiResponse.success ? (
                  <div className="space-y-2">
                    <div className="flex items-start space-x-2">
                      <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-green-900">SQL Generated Successfully</p>
                        <p className="text-xs text-green-700 mt-1">{aiResponse.explanation}</p>
                        {aiResponse.confidence && (
                          <p className="text-xs text-green-600 mt-1">Confidence: {aiResponse.confidence}%</p>
                        )}
                        {aiResponse.tables_used && aiResponse.tables_used.length > 0 && (
                          <p className="text-xs text-green-600 mt-1">
                            Tables: {aiResponse.tables_used.join(', ')}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-start space-x-2">
                    <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-red-900">Error</p>
                      <p className="text-xs text-red-700">{aiResponse.error}</p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Validate Tab */}
        {activeTab === 'validate' && (
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Validate your SQL query for syntax errors, schema issues, and security concerns.
            </p>
            <button
              onClick={handleValidateQuery}
              disabled={loading || !currentSQL}
              className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  <span>Validating...</span>
                </>
              ) : (
                <>
                  <CheckCircle className="w-5 h-5" />
                  <span>Validate Query</span>
                </>
              )}
            </button>

            {validationResult && (
              <div className={`p-4 rounded-lg ${validationResult.is_valid ? 'bg-green-50 border border-green-200' : 'bg-yellow-50 border border-yellow-200'}`}>
                <div className="space-y-3">
                  <div className="flex items-center space-x-2">
                    {validationResult.is_valid ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-yellow-600" />
                    )}
                    <span className={`font-medium ${validationResult.is_valid ? 'text-green-900' : 'text-yellow-900'}`}>
                      {validationResult.is_valid ? 'Query is valid' : 'Issues found'}
                    </span>
                  </div>

                  {validationResult.suggestions && validationResult.suggestions.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-gray-900 mb-1">Suggestions:</p>
                      <ul className="list-disc list-inside space-y-1">
                        {validationResult.suggestions.map((suggestion: string, index: number) => (
                          <li key={index} className="text-xs text-gray-700">{suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {validationResult.performance_issues && validationResult.performance_issues.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-orange-900 mb-1">Performance Issues:</p>
                      <ul className="list-disc list-inside space-y-1">
                        {validationResult.performance_issues.map((issue: string, index: number) => (
                          <li key={index} className="text-xs text-orange-700">{issue}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Optimize Tab */}
        {activeTab === 'optimize' && (
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Get AI-powered suggestions to improve query performance.
            </p>
            <button
              onClick={handleOptimizeQuery}
              disabled={loading || !currentSQL}
              className="w-full bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  <span>Optimizing...</span>
                </>
              ) : (
                <>
                  <TrendingUp className="w-5 h-5" />
                  <span>Optimize Query</span>
                </>
              )}
            </button>

            {optimizationResult && optimizationResult.success && (
              <div className="p-4 rounded-lg bg-blue-50 border border-blue-200 space-y-3">
                {optimizationResult.optimizations_applied && optimizationResult.optimizations_applied.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-blue-900 mb-2">Optimizations Applied:</p>
                    <ul className="list-disc list-inside space-y-1">
                      {optimizationResult.optimizations_applied.map((opt: string, index: number) => (
                        <li key={index} className="text-xs text-blue-700">{opt}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {optimizationResult.estimated_improvement > 0 && (
                  <div className="flex items-center space-x-2 text-sm text-blue-900">
                    <TrendingUp className="w-4 h-4" />
                    <span>Estimated improvement: {optimizationResult.estimated_improvement}%</span>
                  </div>
                )}

                {optimizationResult.recommended_indexes && optimizationResult.recommended_indexes.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-blue-900 mb-1">Recommended Indexes:</p>
                    <ul className="list-disc list-inside space-y-1">
                      {optimizationResult.recommended_indexes.map((idx: string, index: number) => (
                        <li key={index} className="text-xs text-blue-700">{idx}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {optimizationResult.optimized_query && optimizationResult.optimized_query !== currentSQL && (
                  <div>
                    <p className="text-sm font-medium text-blue-900 mb-2">Optimized Query:</p>
                    <pre className="bg-white p-3 rounded border border-blue-200 text-xs overflow-x-auto">
                      {optimizationResult.optimized_query}
                    </pre>
                    <button
                      onClick={() => onSQLGenerated(optimizationResult.optimized_query, optimizationResult.explanation)}
                      className="mt-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
                    >
                      Apply Optimized Query
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Insights Tab */}
        {activeTab === 'insights' && (
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Get AI-generated insights and recommendations from your query results.
            </p>
            <button
              onClick={handleGenerateInsights}
              disabled={loading || !queryResult}
              className="w-full bg-amber-600 text-white px-6 py-3 rounded-lg hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  <span>Generating insights...</span>
                </>
              ) : (
                <>
                  <Lightbulb className="w-5 h-5" />
                  <span>Generate Insights</span>
                </>
              )}
            </button>

            {insights && insights.success && (
              <div className="space-y-4">
                {insights.key_insights && insights.key_insights.length > 0 && (
                  <div className="p-4 rounded-lg bg-amber-50 border border-amber-200">
                    <p className="text-sm font-semibold text-amber-900 mb-3">Key Insights:</p>
                    <div className="space-y-2">
                      {insights.key_insights.map((insight: any, index: number) => (
                        <div key={index} className="bg-white p-3 rounded border border-amber-100">
                          <p className="text-sm font-medium text-gray-900">{insight.title}</p>
                          <p className="text-xs text-gray-600 mt-1">{insight.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {insights.recommendations && insights.recommendations.length > 0 && (
                  <div className="p-4 rounded-lg bg-green-50 border border-green-200">
                    <p className="text-sm font-semibold text-green-900 mb-2">Recommendations:</p>
                    <ul className="list-disc list-inside space-y-1">
                      {insights.recommendations.map((rec: string, index: number) => (
                        <li key={index} className="text-xs text-green-700">{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Chart Tab */}
        {activeTab === 'chart' && (
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Get AI recommendations for the best chart type to visualize your data.
            </p>
            <button
              onClick={handleRecommendChart}
              disabled={loading || !queryResult}
              className="w-full bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  <span>Analyzing data...</span>
                </>
              ) : (
                <>
                  <BarChart3 className="w-5 h-5" />
                  <span>Recommend Chart Type</span>
                </>
              )}
            </button>

            {chartRecommendation && chartRecommendation.success && (
              <div className="p-4 rounded-lg bg-purple-50 border border-purple-200 space-y-3">
                <div>
                  <p className="text-sm font-semibold text-purple-900 mb-2">
                    Recommended: {chartRecommendation.primary_recommendation}
                  </p>
                  <p className="text-xs text-purple-700">{chartRecommendation.reasoning}</p>
                </div>

                {chartRecommendation.alternative_charts && chartRecommendation.alternative_charts.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-purple-900 mb-2">Alternative Charts:</p>
                    <div className="space-y-2">
                      {chartRecommendation.alternative_charts.map((alt: any, index: number) => (
                        <div key={index} className="bg-white p-2 rounded border border-purple-100">
                          <p className="text-xs font-medium text-gray-900">{alt.chart_type}</p>
                          <p className="text-xs text-gray-600">{alt.reasoning}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AIQueryPanel;
