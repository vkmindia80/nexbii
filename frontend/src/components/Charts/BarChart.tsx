import React from 'react';
import ReactECharts from 'echarts-for-react';

interface BarChartProps {
  data: {
    yAxis: string[];
    series: Array<{
      name: string;
      data: number[];
      color?: string;
    }>;
  };
  title?: string;
  height?: string;
}

const BarChart: React.FC<BarChartProps> = ({ data, title, height = '400px' }) => {
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
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    legend: {
      top: 30,
      left: 'center',
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'value',
    },
    yAxis: {
      type: 'category',
      data: data.yAxis,
    },
    series: data.series.map((s) => ({
      name: s.name,
      type: 'bar',
      data: s.data,
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

export default BarChart;
