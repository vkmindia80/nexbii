import React, { useState } from 'react';
import { Layers, Play, AlertCircle, Info } from 'lucide-react';
import analyticsService, { ClusteringRequest } from '../../services/analyticsService';
import ReactECharts from 'echarts-for-react';

interface Props {
  dataSources: Array<{ id: string; name: string; type: string }>;
}

interface ClusterResult {
  clusters: number[];
  cluster_centers?: number[][];
  n_clusters: number;
  silhouette_score?: number;
  cluster_sizes: { [key: number]: number };
  data_with_clusters: any[];
}

const Clustering: React.FC<Props> = ({ dataSources }) => {
  const [selectedDatasource, setSelectedDatasource] = useState('');
  const [query, setQuery] = useState('');
  const [featureColumns, setFeatureColumns] = useState<string[]>(['', '']);
  const [method, setMethod] = useState<'kmeans' | 'hierarchical' | 'dbscan'>('kmeans');
  const [nClusters, setNClusters] = useState(3);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ClusterResult | null>(null);
  const [error, setError] = useState('');

  const methodDescriptions = {
    kmeans: 'Fast and efficient for large datasets, requires specifying number of clusters',
    hierarchical: 'Creates a tree of clusters, good for discovering hierarchy in data',
    dbscan: 'Density-based, automatically finds clusters without specifying count'
  };

  const handleAddFeature = () => setFeatureColumns([...featureColumns, '']);
  const handleRemoveFeature = (index: number) => {
    if (featureColumns.length > 2) setFeatureColumns(featureColumns.filter((_, i) => i !== index));
  };
  const handleFeatureChange = (index: number, value: string) => {
    const newFeatures = [...featureColumns];
    newFeatures[index] = value;
    setFeatureColumns(newFeatures);
  };

  const handlePerformClustering = async () => {
    if (!selectedDatasource || !query) {
      setError('Please select data source and enter query');
      return;
    }

    const validFeatures = featureColumns.filter(f => f.trim() !== '');
    if (validFeatures.length < 2) {
      setError('Please specify at least 2 feature columns');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const request: ClusteringRequest = {
        datasource_id: selectedDatasource,
        query: query,
        feature_columns: validFeatures,
        n_clusters: method !== 'dbscan' ? nClusters : undefined,
        method: method
      };

      const data = await analyticsService.performClustering(request);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to perform clustering');
    } finally {
      setLoading(false);
    }
  };

  const loadSampleQuery = () => {
    setQuery('SELECT age, annual_income, spending_score FROM customers');
    setFeatureColumns(['age', 'annual_income']);
    setMethod('kmeans');
    setNClusters(3);
  };

  const getChartOption = () => {
    if (!result || !result.data_with_clusters || result.data_with_clusters.length === 0) return {};

    const features = featureColumns.filter(f => f.trim() !== '');
    const xFeature = features[0];
    const yFeature = features[1];

    const clusterColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];
    
    const series = Object.keys(result.cluster_sizes).map(clusterId => {
      const clusterData = result.data_with_clusters
        .filter(item => item.cluster === parseInt(clusterId))
        .map(item => [item[xFeature], item[yFeature]]);

      return {
        name: `Cluster ${clusterId}`,
        type: 'scatter',
        data: clusterData,
        symbolSize: 8,
        itemStyle: {
          color: clusterColors[parseInt(clusterId) % clusterColors.length]
        }
      };
    });

    return {
      title: {
        text: 'Cluster Visualization',
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          return `${params.seriesName}<br/>${xFeature}: ${params.value[0]}<br/>${yFeature}: ${params.value[1]}`;
        }
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        data: Object.keys(result.cluster_sizes).map(c => `Cluster ${c}`)
      },
      xAxis: {
        name: xFeature,
        nameLocation: 'middle',
        nameGap: 30,
        type: 'value'
      },
      yAxis: {
        name: yFeature,
        nameLocation: 'middle',
        nameGap: 40,
        type: 'value'
      },
      series: series
    };
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Layers className="w-6 h-6 text-indigo-600" />
          Clustering Analysis
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Customer segmentation using K-Means, Hierarchical, or DBSCAN clustering
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configuration Panel */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Clustering Configuration</h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Data Source *</label>
              <select
                value={selectedDatasource}
                onChange={(e) => setSelectedDatasource(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                data-testid="datasource-select"
              >
                <option value="">Select a data source...</option>
                {dataSources.map((ds) => (
                  <option key={ds.id} value={ds.id}>{ds.name} ({ds.type})</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Clustering Method *</label>
              <select
                value={method}
                onChange={(e) => setMethod(e.target.value as any)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                data-testid="method-select"
              >
                <option value="kmeans">K-Means</option>
                <option value="hierarchical">Hierarchical</option>
                <option value="dbscan">DBSCAN</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">{methodDescriptions[method]}</p>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-700">SQL Query *</label>
                <button onClick={loadSampleQuery} className="text-xs text-indigo-600 hover:text-indigo-700">Load Sample</button>
              </div>
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 font-mono text-sm"
                rows={4}
                placeholder="SELECT features FROM table"
                data-testid="query-input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Feature Columns * (min 2)</label>
              {featureColumns.map((feature, index) => (
                <div key={index} className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={feature}
                    onChange={(e) => handleFeatureChange(index, e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    placeholder="feature_column"
                    data-testid={`feature-input-${index}`}
                  />
                  {featureColumns.length > 2 && (
                    <button onClick={() => handleRemoveFeature(index)} className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg">Remove</button>
                  )}
                </div>
              ))}
              <button onClick={handleAddFeature} className="text-sm text-indigo-600 hover:text-indigo-700">+ Add Feature</button>
            </div>

            {method !== 'dbscan' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Number of Clusters: {nClusters}</label>
                <input
                  type="range"
                  min="2"
                  max="10"
                  value={nClusters}
                  onChange={(e) => setNClusters(parseInt(e.target.value))}
                  className="w-full"
                  data-testid="clusters-slider"
                />
              </div>
            )}

            <button
              onClick={handlePerformClustering}
              disabled={loading || !selectedDatasource || !query}
              className="w-full bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              data-testid="cluster-button"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  Clustering...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Perform Clustering
                </>
              )}
            </button>
          </div>
        </div>

        {/* Results Panel */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Clustering Results</h3>

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
              <p className="text-gray-600">Configure and run clustering to see results</p>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-indigo-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Clusters Found</p>
                  <p className="text-2xl font-bold text-indigo-600">{result.n_clusters}</p>
                </div>
                {result.silhouette_score !== undefined && (
                  <div className="bg-green-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Silhouette Score</p>
                    <p className="text-2xl font-bold text-green-600">{result.silhouette_score.toFixed(3)}</p>
                  </div>
                )}
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm font-medium text-gray-700 mb-3">Cluster Sizes</p>
                {Object.entries(result.cluster_sizes).map(([cluster, size]) => (
                  <div key={cluster} className="mb-2">
                    <div className="flex justify-between text-xs text-gray-600 mb-1">
                      <span>Cluster {cluster}</span>
                      <span>{size} members</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-indigo-600 h-2 rounded-full"
                        style={{ width: `${(size / result.data_with_clusters.length) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>

              {result.data_with_clusters && result.data_with_clusters.length > 0 && (
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <ReactECharts option={getChartOption()} style={{ height: '400px' }} />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Clustering;