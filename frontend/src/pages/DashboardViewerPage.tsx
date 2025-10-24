import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Edit, Share2, RefreshCw, Download, FileText, Image, Mail, MessageCircle } from 'lucide-react';
import { dashboardService } from '../services/dashboardService';
import { queryService } from '../services/queryService';
import { Dashboard } from '../types';
import { ChartContainer } from '../components/Charts';
import ShareModal from '../components/ShareModal';
import SubscriptionModal from '../components/SubscriptionModal';
import CommentsSection from '../components/CommentsSection';
import PresenceIndicator from '../components/PresenceIndicator';
import { useDashboardCollaboration } from '../hooks/useWebSocket';
import exportService from '../services/exportService';

const DashboardViewerPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [widgetData, setWidgetData] = useState<Record<string, any>>({});
  const [refreshing, setRefreshing] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);
  const [showComments, setShowComments] = useState(false);
  
  // WebSocket collaboration
  const { viewers, updates, notifyUpdate } = useDashboardCollaboration(id);

  useEffect(() => {
    if (id) {
      loadDashboard();
    }
  }, [id]);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const data = await dashboardService.get(id!);
      setDashboard(data);
      
      // Load data for each widget
      if (data.widgets && data.widgets.length > 0) {
        await loadWidgetData(data.widgets);
      }
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadWidgetData = async (widgets: any[]) => {
    console.log('Loading widget data for', widgets.length, 'widgets');
    const dataPromises = widgets.map(async (widget) => {
      console.log('Processing widget:', widget.id, 'with query_id:', widget.query_id);
      if (widget.query_id) {
        try {
          // Execute the query to get data
          console.log('Executing query for widget', widget.id);
          const result = await queryService.execute({
            query_id: widget.query_id,
            limit: 1000
          });
          console.log('Query result for widget', widget.id, ':', result);
          
          // Transform data based on chart type
          const transformedData = transformDataForChart(result, widget);
          console.log('Transformed data for widget', widget.id, ':', transformedData);
          return { [widget.id]: transformedData };
        } catch (error: any) {
          console.error(`Failed to load data for widget ${widget.id}:`, error);
          console.error('Error details:', error.response?.data || error.message);
          return { [widget.id]: { error: error.message } };
        }
      }
      console.log('Widget', widget.id, 'has no query_id');
      return { [widget.id]: null };
    });

    const results = await Promise.all(dataPromises);
    console.log('All widget data loaded:', results);
    const dataMap = results.reduce((acc, curr) => ({ ...acc, ...curr }), {});
    setWidgetData(dataMap);
  };

  const transformDataForChart = (queryResult: any, widget: any) => {
    const { columns, rows } = queryResult;
    const chartType = widget.chart_type || widget.type;
    const config = widget.config || {};

    switch (chartType) {
      case 'line':
      case 'area':
      case 'column':
        // For line/area/column charts, need xAxis and series
        const xAxisCol = config.x_axis || columns[0];
        const yAxisCol = config.y_axis || columns[1];
        
        const xAxisIndex = columns.indexOf(xAxisCol);
        const yAxisIndex = columns.indexOf(yAxisCol);
        
        return {
          xAxis: rows.map((row: any) => String(row[xAxisIndex])),
          series: [{
            name: yAxisCol,
            data: rows.map((row: any) => Number(row[yAxisIndex]) || 0),
            color: config.color
          }]
        };

      case 'bar':
        // For bar charts, need yAxis (categories) and series
        const barYAxisCol = config.x_axis || columns[0];
        const barValueCol = config.y_axis || columns[1];
        
        const barYAxisIndex = columns.indexOf(barYAxisCol);
        const barValueIndex = columns.indexOf(barValueCol);
        
        return {
          yAxis: rows.map((row: any) => String(row[barYAxisIndex])),
          series: [{
            name: barValueCol,
            data: rows.map((row: any) => Number(row[barValueIndex]) || 0),
            color: config.color
          }]
        };

      case 'pie':
      case 'donut':
        // For pie/donut charts, need array of {name, value}
        const labelCol = config.label || columns[0];
        const valueCol = config.value || columns[1];
        
        const labelIndex = columns.indexOf(labelCol);
        const valueIndex = columns.indexOf(valueCol);
        
        return rows.map((row: any) => ({
          name: String(row[labelIndex]),
          value: Number(row[valueIndex]) || 0
        }));

      case 'metric':
        // For metric cards, extract single value
        const metricField = config.field || columns[0];
        const metricIndex = columns.indexOf(metricField);
        
        let value = 0;
        if (config.aggregation === 'sum') {
          value = rows.reduce((sum: number, row: any) => sum + (Number(row[metricIndex]) || 0), 0);
        } else if (config.aggregation === 'avg') {
          const sum = rows.reduce((sum: number, row: any) => sum + (Number(row[metricIndex]) || 0), 0);
          value = rows.length > 0 ? sum / rows.length : 0;
        } else if (config.aggregation === 'count') {
          value = rows.length;
        } else {
          value = rows.length > 0 ? Number(rows[0][metricIndex]) || 0 : 0;
        }
        
        return { value };

      case 'table':
        // For tables, return columns and rows as-is
        return {
          columns,
          rows
        };

      case 'gauge':
        // For gauge, extract single value
        const gaugeField = config.field || columns[0];
        const gaugeIndex = columns.indexOf(gaugeField);
        const gaugeValue = rows.length > 0 ? Number(rows[0][gaugeIndex]) || 0 : 0;
        
        return { value: gaugeValue };

      default:
        return { columns, rows };
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDashboard();
    setRefreshing(false);
  };

  const handleExportPDF = async () => {
    try {
      await exportService.exportDashboardToPDF(id!);
      setShowExportMenu(false);
    } catch (error) {
      console.error('Failed to export PDF:', error);
      alert('Failed to export dashboard as PDF');
    }
  };

  const handleExportPNG = async () => {
    try {
      await exportService.exportDashboardToPNG(
        'dashboard-content',
        `dashboard_${dashboard?.name || id}.png`
      );
      setShowExportMenu(false);
    } catch (error) {
      console.error('Failed to export PNG:', error);
      alert('Failed to export dashboard as PNG');
    }
  };

  const handleExportJSON = async () => {
    try {
      await exportService.exportDashboardToJSON(id!);
      setShowExportMenu(false);
    } catch (error) {
      console.error('Failed to export JSON:', error);
      alert('Failed to export dashboard configuration');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Dashboard not found</h3>
        <button
          onClick={() => navigate('/dashboards')}
          className="text-primary-600 hover:text-primary-700"
        >
          Back to Dashboards
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/dashboards')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{dashboard.name}</h1>
              {dashboard.description && (
                <p className="text-gray-600 mt-1">{dashboard.description}</p>
              )}
            </div>
            {/* Presence Indicator */}
            <PresenceIndicator viewers={viewers} />
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
              data-testid="refresh-button"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
            
            {/* Export Dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowExportMenu(!showExportMenu)}
                className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                data-testid="export-button"
              >
                <Download className="w-4 h-4" />
                <span>Export</span>
              </button>
              
              {showExportMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
                  <button
                    onClick={handleExportPDF}
                    className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center space-x-2"
                    data-testid="export-pdf-button"
                  >
                    <FileText className="w-4 h-4" />
                    <span>Export as PDF</span>
                  </button>
                  <button
                    onClick={handleExportPNG}
                    className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center space-x-2"
                    data-testid="export-png-button"
                  >
                    <Image className="w-4 h-4" />
                    <span>Export as PNG</span>
                  </button>
                  <button
                    onClick={handleExportJSON}
                    className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center space-x-2 border-t"
                    data-testid="export-json-button"
                  >
                    <FileText className="w-4 h-4" />
                    <span>Export Config (JSON)</span>
                  </button>
                </div>
              )}
            </div>
            
            <button
              onClick={() => setShowSubscriptionModal(true)}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              data-testid="subscribe-button"
            >
              <Mail className="w-4 h-4" />
              <span>Subscribe</span>
            </button>
            
            <button
              onClick={() => setShowShareModal(true)}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              data-testid="share-button"
            >
              <Share2 className="w-4 h-4" />
              <span>Share</span>
            </button>
            
            <button
              onClick={() => setShowComments(!showComments)}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              data-testid="comments-button"
            >
              <MessageCircle className="w-4 h-4" />
              <span>Comments</span>
            </button>
            
            <button
              onClick={() => navigate(`/dashboards/${id}/edit`)}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              data-testid="edit-button"
            >
              <Edit className="w-4 h-4" />
              <span>Edit</span>
            </button>
          </div>
        </div>
      </div>

      {/* Widgets */}
      <div id="dashboard-content">
        {dashboard.widgets && dashboard.widgets.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {dashboard.widgets.map((widget) => {
              const data = widgetData[widget.id];
              const chartType = widget.chart_type || widget.type;

              return (
                <div 
                  key={widget.id} 
                  className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
                  style={{ 
                    gridColumn: widget.w ? `span ${widget.w}` : 'span 1',
                    gridRow: widget.h ? `span ${widget.h}` : 'span 1'
                  }}
                >
                  {data ? (
                    data.error ? (
                      <div className="flex flex-col items-center justify-center h-64 text-center">
                        <p className="text-red-600 mb-2">Failed to load data</p>
                        <p className="text-sm text-gray-500">{data.error}</p>
                      </div>
                    ) : (
                      <ChartContainer
                        type={chartType}
                        data={data}
                        config={widget.config || {}}
                        title={widget.title}
                        height="300px"
                      />
                    )
                  ) : (
                    <div className="flex items-center justify-center h-64">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
            <h3 className="text-lg font-medium text-gray-900 mb-2">No widgets yet</h3>
            <p className="text-gray-600 mb-4">Add widgets to visualize your data</p>
            <button
              onClick={() => navigate(`/dashboards/${id}/edit`)}
              className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
            >
              Add Widgets
            </button>
          </div>
        )}
      </div>
      
      {/* Comments Section */}
      {showComments && dashboard && (
        <div className="mt-6">
          <CommentsSection dashboardId={dashboard.id} />
        </div>
      )}
      
      {/* Share Modal */}
      {showShareModal && dashboard && (
        <ShareModal
          dashboardId={dashboard.id}
          dashboardName={dashboard.name}
          onClose={() => setShowShareModal(false)}
        />
      )}
      
      {/* Subscription Modal */}
      {showSubscriptionModal && dashboard && (
        <SubscriptionModal
          dashboardId={dashboard.id}
          dashboardName={dashboard.name}
          onClose={() => setShowSubscriptionModal(false)}
        />
      )}
    </div>
  );
};

export default DashboardViewerPage;
