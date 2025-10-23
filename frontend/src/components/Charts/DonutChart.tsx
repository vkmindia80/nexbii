import React from 'react';
import ReactECharts from 'echarts-for-react';

interface DonutChartProps {
  data: Array<{
    name: string;
    value: number;
  }>;
  title?: string;
  height?: string;
}

const DonutChart: React.FC<DonutChartProps> = ({ data, title, height = '400px' }) => {
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
      formatter: '{a} <br/>{b}: {c} ({d}%)',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle',
    },
    series: [
      {
        name: title || 'Data',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['60%', '50%'],
        avoidLabelOverlap: false,
        data: data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
        label: {
          formatter: '{b}: {d}%',
        },
      },
    ],
  };

  return <ReactECharts option={option} style={{ height }} />;
};

export default DonutChart;
