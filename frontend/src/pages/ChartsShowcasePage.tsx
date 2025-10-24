import React from 'react';
import { 
  LineChart, 
  BarChart, 
  ColumnChart, 
  AreaChart, 
  PieChart, 
  DonutChart,
  ScatterChart,
  GaugeChart,
  MetricCard,
  DataTable 
} from '../components/Charts';

const ChartsShowcasePage: React.FC = () => {
  // Sample data for charts
  const lineData = {
    xAxis: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    series: [
      { name: 'Revenue', data: [45000, 52000, 48000, 62000, 58000, 70000], color: '#3b82f6' },
      { name: 'Profit', data: [12000, 15000, 14000, 19000, 17000, 22000], color: '#10b981' }
    ]
  };

  const barData = {
    yAxis: ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
    series: [
      { name: 'Sales', data: [320, 402, 301, 434, 290], color: '#8b5cf6' }
    ]
  };

  const columnData = {
    xAxis: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    series: [
      { name: 'Orders', data: [120, 132, 101, 134, 90, 230, 210], color: '#f59e0b' }
    ]
  };

  const areaData = {
    xAxis: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    series: [
      { name: 'Traffic', data: [8500, 9200, 8800, 10500], color: '#06b6d4' }
    ]
  };

  const pieData = [
    { name: 'Enterprise', value: 335 },
    { name: 'SMB', value: 234 },
    { name: 'Startup', value: 156 },
    { name: 'Individual', value: 178 }
  ];

  const scatterData: Array<{
    name: string;
    data: Array<[number, number]>;
    color: string;
  }> = [
    {
      name: 'Dataset 1',
      data: [[10, 20], [15, 30], [20, 25], [25, 40], [30, 35]],
      color: '#ef4444'
    }
  ];

  const tableData = {
    columns: ['Product', 'Category', 'Price', 'Stock'],
    rows: [
      ['Laptop Pro 15', 'Electronics', '$1,299.99', '45'],
      ['Wireless Mouse', 'Electronics', '$29.99', '120'],
      ['Desk Chair', 'Furniture', '$299.99', '30'],
      ['Monitor 27"', 'Electronics', '$349.99', '67'],
      ['Standing Desk', 'Furniture', '$599.99', '15']
    ]
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Charts Showcase</h1>
        <p className="text-gray-600 mt-2">Explore all 10 chart types available in the visualization engine</p>
      </div>

      <div className="space-y-8">
        {/* Line Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold mb-4">Line Chart</h2>
          <LineChart data={lineData} title="Revenue & Profit Trend" />
        </div>

        {/* Bar Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold mb-4">Bar Chart</h2>
          <BarChart data={barData} title="Product Sales Comparison" />
        </div>

        {/* Column Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold mb-4">Column Chart</h2>
          <ColumnChart data={columnData} title="Daily Orders" />
        </div>

        {/* Area Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold mb-4">Area Chart</h2>
          <AreaChart data={areaData} title="Website Traffic" />
        </div>

        {/* Pie and Donut Charts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold mb-4">Pie Chart</h2>
            <PieChart data={pieData} title="Customer Segments" />
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold mb-4">Donut Chart</h2>
            <DonutChart data={pieData} title="Customer Segments" />
          </div>
        </div>

        {/* Scatter Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold mb-4">Scatter Chart</h2>
          <ScatterChart data={scatterData} title="Correlation Analysis" xAxisLabel="X Value" yAxisLabel="Y Value" />
        </div>

        {/* Gauge Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold mb-4">Gauge Chart</h2>
          <GaugeChart value={78.5} title="Performance Score" />
        </div>

        {/* Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <MetricCard 
            title="Total Revenue"
            value={284500}
            format="currency"
            change={12.5}
            changeLabel="vs last month"
          />
          <MetricCard 
            title="Active Users"
            value={1245}
            format="number"
            change={-3.2}
            changeLabel="vs last week"
          />
          <MetricCard 
            title="Conversion Rate"
            value={4.8}
            format="percentage"
            change={0.5}
            changeLabel="vs last quarter"
          />
        </div>

        {/* Data Table */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Data Table</h2>
          <DataTable 
            columns={tableData.columns}
            data={tableData.rows}
            title="Product Inventory"
          />
        </div>
      </div>
    </div>
  );
};

export default ChartsShowcasePage;
