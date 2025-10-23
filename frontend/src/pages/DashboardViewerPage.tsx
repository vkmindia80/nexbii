import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Edit, Share2, RefreshCw } from 'lucide-react';
import { dashboardService } from '../services/dashboardService';
import { queryService } from '../services/queryService';
import { Dashboard } from '../types';
import { ChartContainer } from '../components/Charts';

const DashboardViewerPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [widgetData, setWidgetData] = useState<Record<string, any>>({});
  const [refreshing, setRefreshing] = useState(false);

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
    const dataPromises = widgets.map(async (widget) => {
      if (widget.query_id) {
        try {
          // Execute the query to get data
          const result = await queryService.execute({
            query_id: widget.query_id,
            limit: 1000
          });
          
          // Transform data based on chart type
          const transformedData = transformDataForChart(result, widget);
          return { [widget.id]: transformedData };
        } catch (error) {
          console.error(`Failed to load data for widget ${widget.id}:`, error);
          return { [widget.id]: null };
        }
      }
      return { [widget.id]: null };
    });

    const results = await Promise.all(dataPromises);
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
          value = rows.reduce((sum, row) => sum + (Number(row[metricIndex]) || 0), 0);
        } else if (config.aggregation === 'avg') {
          const sum = rows.reduce((sum, row) => sum + (Number(row[metricIndex]) || 0), 0);
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
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
            <button
              onClick={() => navigate(`/dashboards/${id}/edit`)}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              <Edit className="w-4 h-4" />
              <span>Edit</span>
            </button>
          </div>
        </div>
      </div>

      {/* Widgets */}
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
                  <ChartContainer
                    type={chartType}
                    data={data}
                    config={widget.config || {}}
                    title={widget.title}
                    height="300px"
                  />
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
  );
};

export default DashboardViewerPage;
