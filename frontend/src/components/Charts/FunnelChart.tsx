import React from 'react';
import ReactECharts from 'echarts-for-react';

interface FunnelChartProps {
  data: Array<{
    name: string;
    value: number;
  }>;
  title?: string;
  height?: string;
}

const FunnelChart: React.FC<FunnelChartProps> = ({ data, title, height = '400px' }) => {
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
        return `${params.name}<br/>Value: ${params.value}<br/>Percentage: ${params.percent}%`;
      },
    },
    legend: {
      top: 30,
      left: 'center',
    },
    series: [
      {
        name: 'Funnel',
        type: 'funnel',
        left: '10%',
        top: 80,
        bottom: 20,
        width: '80%',
        sort: 'descending',
        gap: 2,
        label: {
          show: true,
          position: 'inside',
          formatter: '{b}: {c}',
        },
        labelLine: {
          length: 10,
          lineStyle: {
            width: 1,
            type: 'solid',
          },
        },
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 1,
        },
        emphasis: {
          label: {
            fontSize: 16,
          },
        },
        data: data,
      },
    ],
  };

  return <ReactECharts option={option} style={{ height }} />;
};

export default FunnelChart;