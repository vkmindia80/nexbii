import React from 'react';
import ReactECharts from 'echarts-for-react';

interface LineChartProps {
  data: {
    xAxis: string[];
    series: Array<{
      name: string;
      data: number[];
      color?: string;
    }>;
  };
  title?: string;
  height?: string;
}

const LineChart: React.FC<LineChartProps> = ({ data, title, height = '400px' }) => {
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
        type: 'cross',
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
      type: 'category',
      data: data.xAxis,
      boundaryGap: false,
    },
    yAxis: {
      type: 'value',
    },
    series: data.series.map((s) => ({
      name: s.name,
      type: 'line',
      data: s.data,
      smooth: true,
      itemStyle: {
        color: s.color || undefined,
      },
      lineStyle: {
        width: 2,
      },
      emphasis: {
        focus: 'series',
      },
    })),
  };

  return <ReactECharts option={option} style={{ height }} />;
};

export default LineChart;
