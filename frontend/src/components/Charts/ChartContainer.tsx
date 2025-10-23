import React from 'react';
import LineChart from './LineChart';
import BarChart from './BarChart';
import ColumnChart from './ColumnChart';
import AreaChart from './AreaChart';
import PieChart from './PieChart';
import DonutChart from './DonutChart';
import ScatterChart from './ScatterChart';
import GaugeChart from './GaugeChart';
import MetricCard from './MetricCard';
import DataTable from './DataTable';
import BubbleChart from './BubbleChart';
import HeatmapChart from './HeatmapChart';
import BoxPlotChart from './BoxPlotChart';
import TreemapChart from './TreemapChart';
import SunburstChart from './SunburstChart';
import WaterfallChart from './WaterfallChart';
import FunnelChart from './FunnelChart';
import RadarChart from './RadarChart';
import CandlestickChart from './CandlestickChart';
import SankeyChart from './SankeyChart';

export type ChartType = 'line' | 'bar' | 'column' | 'area' | 'pie' | 'donut' | 'scatter' | 'gauge' | 'metric' | 'table' | 
  'bubble' | 'heatmap' | 'boxplot' | 'treemap' | 'sunburst' | 'waterfall' | 'funnel' | 'radar' | 'candlestick' | 'sankey';

interface ChartContainerProps {
  type: ChartType;
  data: any;
  config?: any;
  title?: string;
  height?: string;
}

const ChartContainer: React.FC<ChartContainerProps> = ({ type, data, config = {}, title, height }) => {
  const renderChart = () => {
    switch (type) {
      case 'line':
        return <LineChart data={data} title={title} height={height} />;
      
      case 'bar':
        return <BarChart data={data} title={title} height={height} />;
      
      case 'column':
        return <ColumnChart data={data} title={title} height={height} />;
      
      case 'area':
        return <AreaChart data={data} title={title} height={height} stacked={config.stacked} />;
      
      case 'pie':
        return <PieChart data={data} title={title} height={height} />;
      
      case 'donut':
        return <DonutChart data={data} title={title} height={height} />;
      
      case 'scatter':
        return (
          <ScatterChart 
            data={data} 
            title={title} 
            height={height}
            xAxisLabel={config.xAxisLabel}
            yAxisLabel={config.yAxisLabel}
          />
        );
      
      case 'gauge':
        return (
          <GaugeChart 
            value={data.value} 
            min={config.min}
            max={config.max}
            title={title} 
            height={height}
            unit={config.unit}
          />
        );
      
      case 'metric':
        return (
          <MetricCard 
            title={title || 'Metric'}
            value={data.value}
            prefix={config.prefix}
            suffix={config.suffix}
            change={data.change}
            changeLabel={config.changeLabel}
            format={config.format}
            height={height}
          />
        );
      
      case 'table':
        return (
          <DataTable 
            columns={data.columns} 
            data={data.rows}
            title={title}
            height={height}
            pageSize={config.pageSize}
          />
        );
      
      case 'bubble':
        return (
          <BubbleChart 
            data={data} 
            title={title} 
            height={height}
            xAxisLabel={config.xAxisLabel}
            yAxisLabel={config.yAxisLabel}
          />
        );
      
      case 'heatmap':
        return (
          <HeatmapChart 
            data={data} 
            title={title} 
            height={height}
            colorRange={config.colorRange}
          />
        );
      
      case 'boxplot':
        return <BoxPlotChart data={data} title={title} height={height} />;
      
      case 'treemap':
        return <TreemapChart data={data} title={title} height={height} />;
      
      case 'sunburst':
        return <SunburstChart data={data} title={title} height={height} />;
      
      case 'waterfall':
        return <WaterfallChart data={data} title={title} height={height} />;
      
      case 'funnel':
        return <FunnelChart data={data} title={title} height={height} />;
      
      case 'radar':
        return <RadarChart data={data} title={title} height={height} />;
      
      case 'candlestick':
        return <CandlestickChart data={data} title={title} height={height} />;
      
      case 'sankey':
        return <SankeyChart data={data} title={title} height={height} />;
      
      default:
        return (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 flex items-center justify-center" style={{ height: height || '400px' }}>
            <p className="text-gray-500">Unsupported chart type: {type}</p>
          </div>
        );
    }
  };

  return (
    <div className="chart-container" data-testid={`chart-${type}`}>
      {renderChart()}
    </div>
  );
};

export default ChartContainer;
