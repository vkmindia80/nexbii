import React from 'react';
import ReactECharts from 'echarts-for-react';

interface TreemapNode {
  name: string;
  value: number;
  children?: TreemapNode[];
}

interface TreemapChartProps {
  data: TreemapNode[];
  title?: string;
  height?: string;
}

const TreemapChart: React.FC<TreemapChartProps> = ({ data, title, height = '400px' }) => {
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
        return `${params.name}<br/>Value: ${params.value}`;
      },
    },
    series: [
      {
        type: 'treemap',
        top: 50,
        width: '95%',
        height: '85%',
        roam: false,
        nodeClick: 'zoomToNode',
        data: data,
        breadcrumb: {
          show: true,
          top: 30,
        },
        label: {
          show: true,
          formatter: '{b}',
        },
        upperLabel: {
          show: true,
          height: 30,
        },
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 2,
          gapWidth: 2,
        },
        levels: [
          {
            itemStyle: {
              borderColor: '#777',
              borderWidth: 0,
              gapWidth: 1,
            },
            upperLabel: {
              show: false,
            },
          },
          {
            itemStyle: {
              borderColor: '#555',
              borderWidth: 5,
              gapWidth: 1,
            },
            emphasis: {
              itemStyle: {
                borderColor: '#ddd',
              },
            },
          },
          {
            colorSaturation: [0.35, 0.5],
            itemStyle: {
              borderWidth: 5,
              gapWidth: 1,
              borderColorSaturation: 0.6,
            },
          },
        ],
      },
    ],
  };

  return <ReactECharts option={option} style={{ height }} />;
};

export default TreemapChart;