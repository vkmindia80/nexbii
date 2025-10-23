import React from 'react';
import ReactECharts from 'echarts-for-react';

interface AreaChartProps {
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
  stacked?: boolean;
}

const AreaChart: React.FC<AreaChartProps> = ({ data, title, height = '400px', stacked = false }) => {
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
      stack: stacked ? 'Total' : undefined,
      areaStyle: {
        opacity: 0.6,
      },
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

export default AreaChart;
