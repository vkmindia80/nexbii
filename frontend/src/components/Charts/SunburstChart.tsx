import React from 'react';
import ReactECharts from 'echarts-for-react';

interface SunburstNode {
  name: string;
  value?: number;
  children?: SunburstNode[];
}

interface SunburstChartProps {
  data: SunburstNode[];
  title?: string;
  height?: string;
}

const SunburstChart: React.FC<SunburstChartProps> = ({ data, title, height = '400px' }) => {
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
        return `${params.name}<br/>Value: ${params.value || 'N/A'}`;
      },
    },
    series: [
      {
        type: 'sunburst',
        data: data,
        radius: [0, '90%'],
        center: ['50%', '55%'],
        sort: undefined,
        emphasis: {
          focus: 'ancestor',
        },
        levels: [
          {},
          {
            r0: '15%',
            r: '35%',
            itemStyle: {
              borderWidth: 2,
            },
            label: {
              rotate: 'tangential',
            },
          },
          {
            r0: '35%',
            r: '70%',
            label: {
              align: 'right',
            },
          },
          {
            r0: '70%',
            r: '72%',
            label: {
              position: 'outside',
              padding: 3,
              silent: false,
            },
            itemStyle: {
              borderWidth: 3,
            },
          },
        ],
      },
    ],
  };

  return <ReactECharts option={option} style={{ height }} />;
};

export default SunburstChart;