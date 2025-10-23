import React from 'react';
import ReactECharts from 'echarts-for-react';

interface ScatterChartProps {
  data: Array<{
    name: string;
    data: Array<[number, number]>;
    color?: string;
  }>;
  title?: string;
  height?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
}

const ScatterChart: React.FC<ScatterChartProps> = ({ 
  data, 
  title, 
  height = '400px',
  xAxisLabel = 'X Axis',
  yAxisLabel = 'Y Axis'
}) => {
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
      trigger: 'item',
      formatter: (params: any) => {
        return `${params.seriesName}<br/>${xAxisLabel}: ${params.value[0]}<br/>${yAxisLabel}: ${params.value[1]}`;
      },
    },
    legend: {
      top: 30,
      left: 'center',
    },
    grid: {
      left: '3%',
      right: '7%',
      bottom: '7%',
      containLabel: true,
    },
    xAxis: {
      type: 'value',
      name: xAxisLabel,
      nameLocation: 'middle',
      nameGap: 30,
    },
    yAxis: {
      type: 'value',
      name: yAxisLabel,
      nameLocation: 'middle',
      nameGap: 40,
    },
    series: data.map((s) => ({
      name: s.name,
      type: 'scatter',
      data: s.data,
      symbolSize: 8,
      itemStyle: {
        color: s.color || undefined,
      },
      emphasis: {
        focus: 'series',
      },
    })),
  };

  return <ReactECharts option={option} style={{ height }} />;
};

export default ScatterChart;
