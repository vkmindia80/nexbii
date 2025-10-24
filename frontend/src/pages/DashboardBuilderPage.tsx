import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, Save, Eye, Trash2, Settings, RefreshCw } from 'lucide-react';
import { Responsive, WidthProvider, Layout } from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import { dashboardService } from '../services/dashboardService';
import { queryService } from '../services/queryService';
import { Dashboard, Query } from '../types';
import { ChartContainer } from '../components/Charts';

const ResponsiveGridLayout = WidthProvider(Responsive);

interface Widget {
  id: string;
  title: string;
  type: string;
  chart_type?: string;
  query_id?: string;
  config?: any;
  x?: number;
  y?: number;
  w?: number;
  h?: number;
}

const DashboardBuilderPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [widgets, setWidgets] = useState<Widget[]>([]);
  const [layout, setLayout] = useState<Layout[]>([]);
  const [queries, setQueries] = useState<Query[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showAddWidget, setShowAddWidget] = useState(false);
  const [editingWidget, setEditingWidget] = useState<Widget | null>(null);
  const [widgetData, setWidgetData] = useState<Record<string, any>>({});

  // New widget form state
  const [newWidget, setNewWidget] = useState({
    title: '',
    type: 'chart',
    chart_type: 'line',
    query_id: '',
    config: {}
  });

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load queries first
      const queriesData = await queryService.list();
      setQueries(queriesData);

      if (id) {
        // Load existing dashboard
        const data = await dashboardService.get(id);
        setDashboard(data);
        
        if (data.widgets && data.widgets.length > 0) {
          setWidgets(data.widgets);
          
          // Convert widgets to layout format
          const layoutData = data.widgets.map((widget: Widget, index: number) => ({
            i: widget.id,
            x: widget.x ?? (index % 3) * 4,
            y: widget.y ?? Math.floor(index / 3) * 2,
            w: widget.w ?? 4,
            h: widget.h ?? 2,
            minW: 2,
            minH: 2
          }));
          setLayout(layoutData);

          // Load data for widgets
          await loadWidgetData(data.widgets);
        }
      }
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadWidgetData = async (widgetList: Widget[]) => {
    const dataPromises = widgetList.map(async (widget) => {
      if (widget.query_id) {
        try {
          const result = await queryService.execute({
            query_id: widget.query_id,
            limit: 1000
          });
          
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

  const transformDataForChart = (queryResult: any, widget: Widget) => {
    const { columns, rows } = queryResult;
    const chartType = widget.chart_type || widget.type;
    const config = widget.config || {};

    switch (chartType) {
      case 'line':
      case 'area':
      case 'column':
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
        const labelCol = config.label || columns[0];
        const valueCol = config.value || columns[1];
        
        const labelIndex = columns.indexOf(labelCol);
        const valueIndex = columns.indexOf(valueCol);
        
        return rows.map((row: any) => ({
          name: String(row[labelIndex]),
          value: Number(row[valueIndex]) || 0
        }));

      case 'metric':
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
        return { columns, rows };

      case 'gauge':
        const gaugeField = config.field || columns[0];
        const gaugeIndex = columns.indexOf(gaugeField);
        const gaugeValue = rows.length > 0 ? Number(rows[0][gaugeIndex]) || 0 : 0;
        
        return { value: gaugeValue };

      default:
        return { columns, rows };
    }
  };

  const handleLayoutChange = (newLayout: Layout[]) => {
    setLayout(newLayout);
  };

  const handleAddWidget = () => {
    if (!newWidget.title || !newWidget.query_id) {
      alert('Please fill in all required fields');
      return;
    }

    const widgetId = `widget-${Date.now()}`;
    const widget: Widget = {
      id: widgetId,
      title: newWidget.title,
      type: newWidget.type,
      chart_type: newWidget.chart_type,
      query_id: newWidget.query_id,
      config: newWidget.config,
      x: 0,
      y: Infinity, // Places at the bottom
      w: 4,
      h: 2
    };

    setWidgets([...widgets, widget]);
    
    // Add to layout
    const newLayoutItem = {
      i: widgetId,
      x: 0,
      y: Infinity,
      w: 4,
      h: 2,
      minW: 2,
      minH: 2
    };
    setLayout([...layout, newLayoutItem]);

    // Load data for new widget
    loadWidgetData([widget]);

    // Reset form
    setNewWidget({
      title: '',
      type: 'chart',
      chart_type: 'line',
      query_id: '',
      config: {}
    });
    setShowAddWidget(false);
  };

  const handleRemoveWidget = (widgetId: string) => {
    if (window.confirm('Are you sure you want to remove this widget?')) {
      setWidgets(widgets.filter(w => w.id !== widgetId));
      setLayout(layout.filter(l => l.i !== widgetId));
      const newWidgetData = { ...widgetData };
      delete newWidgetData[widgetId];
      setWidgetData(newWidgetData);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);

      // Update widgets with layout positions
      const updatedWidgets = widgets.map(widget => {
        const layoutItem = layout.find(l => l.i === widget.id);
        return {
          ...widget,
          x: layoutItem?.x,
          y: layoutItem?.y,
          w: layoutItem?.w,
          h: layoutItem?.h
        };
      });

      if (id) {
        // Update existing dashboard
        await dashboardService.update(id, {
          widgets: updatedWidgets,
          layout: { layouts: layout }
        });
      } else {
        // This shouldn't happen as we're editing an existing dashboard
        alert('Dashboard ID not found');
        return;
      }

      alert('Dashboard saved successfully!');
    } catch (error) {
      console.error('Failed to save dashboard:', error);
      alert('Failed to save dashboard');
    } finally {
      setSaving(false);
    }
  };

  const handleRefresh = async () => {
    await loadWidgetData(widgets);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="pb-8">
      {/* Header */}
      <div className="mb-6 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/dashboards')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              data-testid="back-to-dashboards-button"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {dashboard?.name || 'Dashboard Builder'}
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Drag and resize widgets to customize your dashboard
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={handleRefresh}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              data-testid="refresh-dashboard-button"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
            <button
              onClick={() => navigate(`/dashboards/${id}`)}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              data-testid="view-dashboard-button"
            >
              <Eye className="w-4 h-4" />
              <span>View</span>
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
              data-testid="save-dashboard-button"
            >
              <Save className="w-4 h-4" />
              <span>{saving ? 'Saving...' : 'Save'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Add Widget Button */}
      <div className="mb-4">
        <button
          onClick={() => setShowAddWidget(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          data-testid="add-widget-button"
        >
          <Plus className="w-4 h-4" />
          <span>Add Widget</span>
        </button>
      </div>

      {/* Dashboard Grid */}
      {widgets.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-2">No widgets yet</h3>
          <p className="text-gray-600 mb-4">Start building your dashboard by adding widgets</p>
          <button
            onClick={() => setShowAddWidget(true)}
            className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
          >
            Add Your First Widget
          </button>
        </div>
      ) : (
        <ResponsiveGridLayout
          className="layout"
          layouts={{ lg: layout }}
          breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
          cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
          rowHeight={150}
          onLayoutChange={handleLayoutChange}
          draggableHandle=".drag-handle"
        >
          {widgets.map((widget) => {
            const data = widgetData[widget.id];
            const chartType = widget.chart_type || widget.type;

            return (
              <div key={widget.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                {/* Widget Header */}
                <div className="drag-handle bg-gray-50 border-b border-gray-200 px-4 py-2 flex items-center justify-between cursor-move">
                  <h3 className="font-semibold text-gray-900 text-sm">{widget.title}</h3>
                  <button
                    onClick={() => handleRemoveWidget(widget.id)}
                    className="text-red-600 hover:text-red-700 p-1"
                    data-testid={`remove-widget-${widget.id}`}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                
                {/* Widget Content */}
                <div className="p-4 h-[calc(100%-44px)] overflow-auto">
                  {data ? (
                    <ChartContainer
                      type={chartType as any}
                      data={data}
                      config={widget.config || {}}
                      title=""
                      height="100%"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </ResponsiveGridLayout>
      )}

      {/* Add Widget Modal */}
      {showAddWidget && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Add Widget</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Widget Title *
                  </label>
                  <input
                    type="text"
                    value={newWidget.title}
                    onChange={(e) => setNewWidget({ ...newWidget, title: e.target.value })}
                    className="input"
                    placeholder="e.g., Sales Overview"
                    data-testid="widget-title-input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Query *
                  </label>
                  <select
                    value={newWidget.query_id}
                    onChange={(e) => setNewWidget({ ...newWidget, query_id: e.target.value })}
                    className="input"
                    data-testid="widget-query-select"
                  >
                    <option value="">Select a query</option>
                    {queries.map((query) => (
                      <option key={query.id} value={query.id}>
                        {query.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Chart Type *
                  </label>
                  <select
                    value={newWidget.chart_type}
                    onChange={(e) => setNewWidget({ ...newWidget, chart_type: e.target.value })}
                    className="input"
                    data-testid="widget-chart-type-select"
                  >
                    <option value="line">Line Chart</option>
                    <option value="bar">Bar Chart</option>
                    <option value="column">Column Chart</option>
                    <option value="area">Area Chart</option>
                    <option value="pie">Pie Chart</option>
                    <option value="donut">Donut Chart</option>
                    <option value="scatter">Scatter Plot</option>
                    <option value="gauge">Gauge</option>
                    <option value="metric">Metric Card</option>
                    <option value="table">Data Table</option>
                  </select>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-800">
                    <strong>Tip:</strong> After adding the widget, you can drag and resize it on the dashboard grid.
                  </p>
                </div>
              </div>

              <div className="flex space-x-3 pt-6">
                <button
                  onClick={handleAddWidget}
                  className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
                  data-testid="confirm-add-widget-button"
                >
                  Add Widget
                </button>
                <button
                  onClick={() => {
                    setShowAddWidget(false);
                    setNewWidget({
                      title: '',
                      type: 'chart',
                      chart_type: 'line',
                      query_id: '',
                      config: {}
                    });
                  }}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  data-testid="cancel-add-widget-button"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardBuilderPage;
