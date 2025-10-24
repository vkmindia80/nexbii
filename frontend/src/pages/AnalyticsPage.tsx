import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, Users, Target, BarChart3, Table, Database, 
  Brain, AlertTriangle, Layers, UserX, Activity
} from 'lucide-react';
import datasourceService from '../services/datasourceService';

// Import analytics components (we'll create these next)
import CohortAnalysis from '../components/Analytics/CohortAnalysis';
import FunnelAnalysis from '../components/Analytics/FunnelAnalysis';
import TimeSeriesForecasting from '../components/Analytics/TimeSeriesForecasting';
import StatisticalTests from '../components/Analytics/StatisticalTests';
import PivotTable from '../components/Analytics/PivotTable';
import DataProfiling from '../components/Analytics/DataProfiling';
import PredictiveModels from '../components/Analytics/PredictiveModels';
import AnomalyDetection from '../components/Analytics/AnomalyDetection';
import Clustering from '../components/Analytics/Clustering';
import ChurnPrediction from '../components/Analytics/ChurnPrediction';

type AnalyticsTab = 
  | 'cohort'
  | 'funnel'
  | 'forecast'
  | 'statistical'
  | 'pivot'
  | 'profiling'
  | 'predictive'
  | 'anomaly'
  | 'clustering'
  | 'churn';

interface DataSource {
  id: string;
  name: string;
  type: string;
}

const AnalyticsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<AnalyticsTab>('cohort');
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDataSources();
  }, []);

  const loadDataSources = async () => {
    try {
      const sources = await datasourceService.getDataSources();
      setDataSources(sources);
    } catch (error) {
      console.error('Failed to load data sources:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'cohort' as AnalyticsTab, name: 'Cohort Analysis', icon: Users, description: 'User retention tracking' },
    { id: 'funnel' as AnalyticsTab, name: 'Funnel Analysis', icon: Target, description: 'Conversion optimization' },
    { id: 'forecast' as AnalyticsTab, name: 'Forecasting', icon: TrendingUp, description: 'Time series prediction' },
    { id: 'statistical' as AnalyticsTab, name: 'Statistical Tests', icon: BarChart3, description: 'Hypothesis testing' },
    { id: 'pivot' as AnalyticsTab, name: 'Pivot Tables', icon: Table, description: 'Interactive data slicing' },
    { id: 'profiling' as AnalyticsTab, name: 'Data Profiling', icon: Database, description: 'Quality assessment' },
    { id: 'predictive' as AnalyticsTab, name: 'Predictive Models', icon: Brain, description: 'ML predictions' },
    { id: 'anomaly' as AnalyticsTab, name: 'Anomaly Detection', icon: AlertTriangle, description: 'Outlier identification' },
    { id: 'clustering' as AnalyticsTab, name: 'Clustering', icon: Layers, description: 'Segmentation analysis' },
    { id: 'churn' as AnalyticsTab, name: 'Churn Prediction', icon: UserX, description: 'Customer retention' },
  ];

  const renderTabContent = () => {
    const props = { dataSources };

    switch (activeTab) {
      case 'cohort':
        return <CohortAnalysis {...props} />;
      case 'funnel':
        return <FunnelAnalysis {...props} />;
      case 'forecast':
        return <TimeSeriesForecasting {...props} />;
      case 'statistical':
        return <StatisticalTests {...props} />;
      case 'pivot':
        return <PivotTable {...props} />;
      case 'profiling':
        return <DataProfiling {...props} />;
      case 'predictive':
        return <PredictiveModels {...props} />;
      case 'anomaly':
        return <AnomalyDetection {...props} />;
      case 'clustering':
        return <Clustering {...props} />;
      case 'churn':
        return <ChurnPrediction {...props} />;
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <Activity className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <Brain className="w-8 h-8 text-blue-600" />
                Advanced Analytics
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                Powerful analytics, data profiling, and machine learning tools
              </p>
            </div>
            {dataSources.length === 0 && (
              <div className="text-sm text-orange-600 bg-orange-50 px-4 py-2 rounded-lg">
                ⚠️ No data sources connected. Add one to get started.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-1 overflow-x-auto py-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center gap-2 px-4 py-3 rounded-lg transition-all whitespace-nowrap
                    ${isActive
                      ? 'bg-blue-50 text-blue-700 border-2 border-blue-200 font-semibold'
                      : 'bg-white text-gray-700 hover:bg-gray-50 border-2 border-transparent'
                    }
                  `}
                  data-testid={`analytics-tab-${tab.id}`}
                >
                  <Icon className="w-4 h-4" />
                  <div className="text-left">
                    <div className="text-sm font-medium">{tab.name}</div>
                    {isActive && (
                      <div className="text-xs text-gray-500">{tab.description}</div>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {dataSources.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <Database className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No Data Sources Available
            </h3>
            <p className="text-gray-600 mb-6">
              Connect a data source to start using advanced analytics features
            </p>
            <button
              onClick={() => window.location.href = '/datasources'}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Connect Data Source
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm">
            {renderTabContent()}
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalyticsPage;
