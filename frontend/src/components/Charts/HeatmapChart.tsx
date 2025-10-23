import React from 'react';
import ReactECharts from 'echarts-for-react';

interface HeatmapChartProps {
  data: {
    xAxis: string[];
    yAxis: string[];
    values: number[][]; // 2D array of values
  };
  title?: string;
  height?: string;
  colorRange?: [string, string];
}

const HeatmapChart: React.FC<HeatmapChartProps> = ({ 
  data, 
  title, 
  height = '400px',
  colorRange = ['#ffffff', '#3b82f6']
}) => {
  // Transform data to ECharts format: [x_index, y_index, value]
  const seriesData = [];
  for (let i = 0; i < data.yAxis.length; i++) {
    for (let j = 0; j < data.xAxis.length; j++) {
      seriesData.push([j, i, data.values[i][j] || 0]);
    }
  }

  const option = {
    title: {
      text: title,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold',
      },
    },
    tooltip: {
      position: 'top',
      formatter: (params: any) => {
        return `${data.yAxis[params.value[1]]} - ${data.xAxis[params.value[0]]}<br/>Value: ${params.value[2]}`;
      },
    },
    grid: {
      left: '10%',
      right: '4%',
      bottom: '3%',
      top: 80,
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: data.xAxis,
      splitArea: {
        show: true,
      },
    },
    yAxis: {
      type: 'category',
      data: data.yAxis,
      splitArea: {
        show: true,
      },
    },
    visualMap: {
      min: Math.min(...seriesData.map(d => d[2])),
      max: Math.max(...seriesData.map(d => d[2])),
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      top: 30,
      inRange: {
        color: colorRange,
      },
    },
    series: [
      {
        name: 'Heatmap',
        type: 'heatmap',
        data: seriesData,
        label: {
          show: true,
          formatter: (params: any) => params.value[2],
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  };

  return <ReactECharts option={option} style={{ height }} />;
};

export default HeatmapChart;