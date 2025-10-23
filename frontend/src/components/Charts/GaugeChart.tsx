import React from 'react';
import ReactECharts from 'echarts-for-react';

interface GaugeChartProps {
  value: number;
  min?: number;
  max?: number;
  title?: string;
  height?: string;
  unit?: string;
}

const GaugeChart: React.FC<GaugeChartProps> = ({ 
  value, 
  min = 0, 
  max = 100, 
  title, 
  height = '400px',
  unit = '%'
}) => {
  const option = {
    title: {
      text: title,
      left: 'center',
      top: 10,
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold',
      },
    },
    series: [
      {
        type: 'gauge',
        min: min,
        max: max,
        startAngle: 200,
        endAngle: -20,
        center: ['50%', '60%'],
        radius: '80%',
        progress: {
          show: true,
          width: 18,
        },
        pointer: {
          show: true,
          length: '60%',
          width: 8,
        },
        axisLine: {
          lineStyle: {
            width: 18,
          },
        },
        axisTick: {
          show: true,
          distance: -18,
          length: 5,
        },
        splitLine: {
          distance: -20,
          length: 14,
        },
        axisLabel: {
          distance: -35,
          fontSize: 12,
        },
        detail: {
          valueAnimation: true,
          formatter: `{value}${unit}`,
          fontSize: 24,
          offsetCenter: [0, '80%'],
        },
        data: [
          {
            value: value,
          },
        ],
      },
    ],
  };

  return <ReactECharts option={option} style={{ height }} />;
};

export default GaugeChart;
