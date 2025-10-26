import React, { useState, useEffect } from 'react';
import {
  GitBranch, Database, FileText, BarChart3, AlertTriangle, Search,
  ArrowRight, Info, TrendingUp, Users, Activity
} from 'lucide-react';
import governanceService from '../services/governanceService';

interface LineageNode {
  id: string;
  type: string;
  resource_id: string;
  table?: string;
  column?: string;
}

interface LineageEdge {
  source: string;
  target: string;
  transformation?: string;
  confidence: number;
}

interface LineageGraph {
  nodes: LineageNode[];
  edges: LineageEdge[];
}

interface ImpactAnalysis {
  id: string;
  change_type: string;
  affected_resource_type: string;
  affected_resource_id: string;
  affected_resource_name?: string;
  impact_level: string;
  impact_summary: string;
  affected_queries: string[];
  affected_dashboards: string[];
  affected_users: string[];
  recommendations: string[];
  mitigation_steps: string[];
  analysis_date: string;
}

const DataLineagePage: React.FC = () => {
  const [resourceType, setResourceType] = useState('datasource');
  const [resourceId, setResourceId] = useState('');
  const [lineageGraph, setLineageGraph] = useState<LineageGraph | null>(null);
  const [loading, setLoading] = useState(false);
  const [showImpactAnalysis, setShowImpactAnalysis] = useState(false);
  const [impactAnalysis, setImpactAnalysis] = useState<ImpactAnalysis | null>(null);
  const [impactLoading, setImpactLoading] = useState(false);

  const loadLineage = async () => {
    if (!resourceId) {
      alert('Please enter a resource ID');
      return;
    }

    try {
      setLoading(true);
      const data = await governanceService.getLineageGraph(resourceType, resourceId);
      setLineageGraph(data);
    } catch (error) {
      console.error('Failed to load lineage:', error);
      alert('Failed to load lineage data');
    } finally {
      setLoading(false);
    }
  };

  const runImpactAnalysis = async () => {
    if (!resourceId) {
      alert('Please enter a resource ID');
      return;
    }

    try {
      setImpactLoading(true);
      const result = await governanceService.analyzeImpact({
        change_type: 'schema_change',
        affected_resource_type: resourceType,
        affected_resource_id: resourceId,
      });
      setImpactAnalysis(result);
      setShowImpactAnalysis(true);
    } catch (error) {
      console.error('Failed to run impact analysis:', error);
      alert('Failed to run impact analysis');
    } finally {
      setImpactLoading(false);
    }
  };

  const getImpactLevelColor = (level: string) => {
    const colors: Record<string, string> = {
      low: 'bg-green-100 text-green-800 border-green-200',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      high: 'bg-orange-100 text-orange-800 border-orange-200',
      critical: 'bg-red-100 text-red-800 border-red-200',
    };
    return colors[level] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'datasource':
        return <Database className="w-5 h-5" />;
      case 'query':
        return <FileText className="w-5 h-5" />;
      case 'dashboard':
        return <BarChart3 className="w-5 h-5" />;
      default:
        return <Activity className="w-5 h-5" />;
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto" data-testid="data-lineage-page">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <GitBranch className="w-8 h-8 text-primary-600" />
          Data Lineage
        </h1>
        <p className="text-gray-600 mt-2">
          Track data flow, transformations, and analyze downstream impact of changes
        </p>
      </div>

      {/* Search Section */}
      <div className="bg-white rounded-lg shadow p-6 border border-gray-200 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Explore Lineage</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Resource Type
            </label>
            <select
              value={resourceType}
              onChange={(e) => setResourceType(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="datasource">Data Source</option>
              <option value="query">Query</option>
              <option value="dashboard">Dashboard</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Resource ID
            </label>
            <input
              type="text"
              value={resourceId}
              onChange={(e) => setResourceId(e.target.value)}
              placeholder="Enter resource ID..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div className="flex items-end gap-2">
            <button
              onClick={loadLineage}
              disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Loading...
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  View Lineage
                </>
              )}
            </button>
            <button
              onClick={runImpactAnalysis}
              disabled={impactLoading}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50"
            >
              {impactLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  <TrendingUp className="w-5 h-5" />
                  Impact Analysis
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Lineage Graph Visualization */}
      {lineageGraph && (
        <div className="bg-white rounded-lg shadow p-6 border border-gray-200 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Lineage Graph</h2>

          {lineageGraph.nodes.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <GitBranch className="w-12 h-12 mx-auto mb-3 text-gray-400" />
              <p>No lineage data found for this resource</p>
              <p className="text-sm mt-1">This resource has no tracked dependencies</p>
            </div>
          ) : (
            <>
              {/* Statistics */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                  <p className="text-sm text-blue-600 font-medium">Total Nodes</p>
                  <p className="text-2xl font-bold text-blue-900 mt-1">{lineageGraph.nodes.length}</p>
                </div>
                <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                  <p className="text-sm text-green-600 font-medium">Connections</p>
                  <p className="text-2xl font-bold text-green-900 mt-1">{lineageGraph.edges.length}</p>
                </div>
                <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                  <p className="text-sm text-purple-600 font-medium">Resource Types</p>
                  <p className="text-2xl font-bold text-purple-900 mt-1">
                    {new Set(lineageGraph.nodes.map(n => n.type)).size}
                  </p>
                </div>
              </div>

              {/* Simple List View (instead of complex graph visualization) */}
              <div className="space-y-4">
                <h3 className="text-sm font-semibold text-gray-700">Connected Resources</h3>
                
                {lineageGraph.edges.map((edge, index) => {
                  const sourceNode = lineageGraph.nodes.find(n => n.id === edge.source);
                  const targetNode = lineageGraph.nodes.find(n => n.id === edge.target);
                  
                  if (!sourceNode || !targetNode) return null;

                  return (
                    <div key={index} className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                      {/* Source */}
                      <div className="flex items-center gap-2 flex-1">
                        <div className="p-2 bg-white rounded-lg border border-gray-300">
                          {getTypeIcon(sourceNode.type)}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">{sourceNode.type}</p>
                          <p className="text-xs text-gray-600">
                            {sourceNode.table && `${sourceNode.table}`}
                            {sourceNode.column && `.${sourceNode.column}`}
                          </p>
                        </div>
                      </div>

                      {/* Arrow with transformation */}
                      <div className="flex items-center gap-2">
                        <ArrowRight className="w-5 h-5 text-gray-400" />
                        {edge.transformation && (
                          <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
                            {edge.transformation}
                          </span>
                        )}
                        <span className="text-xs text-gray-500">{edge.confidence}%</span>
                      </div>

                      {/* Target */}
                      <div className="flex items-center gap-2 flex-1">
                        <div className="p-2 bg-white rounded-lg border border-gray-300">
                          {getTypeIcon(targetNode.type)}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">{targetNode.type}</p>
                          <p className="text-xs text-gray-600">
                            {targetNode.table && `${targetNode.table}`}
                            {targetNode.column && `.${targetNode.column}`}
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>
      )}

      {/* Impact Analysis Results */}
      {showImpactAnalysis && impactAnalysis && (
        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Impact Analysis Results</h2>
            <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getImpactLevelColor(impactAnalysis.impact_level)}`}>
              {impactAnalysis.impact_level.toUpperCase()} Impact
            </span>
          </div>

          {/* Summary */}
          <div className="bg-blue-50 rounded-lg p-4 mb-6 border border-blue-200">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-blue-900">Impact Summary</p>
                <p className="text-sm text-blue-800 mt-1">{impactAnalysis.impact_summary}</p>
              </div>
            </div>
          </div>

          {/* Affected Resources */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <div className="flex items-center gap-2 mb-2">
                <FileText className="w-5 h-5 text-gray-600" />
                <p className="text-sm font-medium text-gray-700">Affected Queries</p>
              </div>
              <p className="text-2xl font-bold text-gray-900">{impactAnalysis.affected_queries.length}</p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="w-5 h-5 text-gray-600" />
                <p className="text-sm font-medium text-gray-700">Affected Dashboards</p>
              </div>
              <p className="text-2xl font-bold text-gray-900">{impactAnalysis.affected_dashboards.length}</p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <div className="flex items-center gap-2 mb-2">
                <Users className="w-5 h-5 text-gray-600" />
                <p className="text-sm font-medium text-gray-700">Affected Users</p>
              </div>
              <p className="text-2xl font-bold text-gray-900">{impactAnalysis.affected_users.length}</p>
            </div>
          </div>

          {/* Recommendations */}
          {impactAnalysis.recommendations.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Recommendations</h3>
              <ul className="space-y-2">
                {impactAnalysis.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                    <AlertTriangle className="w-4 h-4 text-orange-600 mt-0.5 flex-shrink-0" />
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Mitigation Steps */}
          {impactAnalysis.mitigation_steps.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Mitigation Steps</h3>
              <ol className="space-y-2">
                {impactAnalysis.mitigation_steps.map((step, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                    <span className="flex-shrink-0 w-5 h-5 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-xs font-medium">
                      {index + 1}
                    </span>
                    {step}
                  </li>
                ))}
              </ol>
            </div>
          )}
        </div>
      )}

      {/* Info Box */}
      {!lineageGraph && !showImpactAnalysis && (
        <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
          <div className="flex items-start gap-3">
            <Info className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-semibold text-blue-900 mb-2">How Data Lineage Works</h3>
              <ul className="text-sm text-blue-800 space-y-2">
                <li>• <strong>View Lineage:</strong> See how data flows from sources through queries to dashboards</li>
                <li>• <strong>Impact Analysis:</strong> Understand what will be affected if you change a resource</li>
                <li>• <strong>Resource Types:</strong> Track lineage for data sources, queries, and dashboards</li>
                <li>• <strong>Confidence Scores:</strong> Each connection has a confidence level (0-100%)</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataLineagePage;
