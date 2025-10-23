import React from 'react';
import ReactECharts from 'echarts-for-react';

interface RadarChartProps {
  data: {
    indicators: Array<{ name: string; max: number }>;
    series: Array<{
      name: string;
      value: number[];
      color?: string;
    }>;
  };
  title?: string;
  height?: string;
}

const RadarChart: React.FC<RadarChartProps> = ({ data, title, height = '400px' }) => {
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
    },
    legend: {
      top: 30,
      left: 'center',
      data: data.series.map(s => s.name),
    },
    radar: {
      center: ['50%', '55%'],
      radius: '60%',
      indicator: data.indicators,
      splitArea: {
        areaStyle: {
          color: ['rgba(114, 172, 209, 0.2)', 'rgba(114, 172, 209, 0.4)'],
          shadowColor: 'rgba(0, 0, 0, 0.2)',
          shadowBlur: 10,
        },
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(211, 253, 250, 0.8)',
        },
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(211, 253, 250, 0.8)',
        },
      },
    },
    series: [
      {
        type: 'radar',
        data: data.series.map(s => ({
          value: s.value,
          name: s.name,
          itemStyle: {
            color: s.color || undefined,
          },
          areaStyle: {
            opacity: 0.3,
          },
        })),
        emphasis: {
          lineStyle: {
            width: 4,
          },
        },
      },
    ],
  };

  return <ReactECharts option={option} style={{ height }} />;
};

export default RadarChart;