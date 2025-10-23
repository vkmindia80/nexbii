import React from 'react';
import ReactECharts from 'echarts-for-react';

interface SankeyLink {
  source: string;
  target: string;
  value: number;
}

interface SankeyNode {
  name: string;
}

interface SankeyChartProps {
  data: {
    nodes: SankeyNode[];
    links: SankeyLink[];
  };
  title?: string;
  height?: string;
}

const SankeyChart: React.FC<SankeyChartProps> = ({ data, title, height = '400px' }) => {
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
      triggerOn: 'mousemove',
      formatter: (params: any) => {
        if (params.dataType === 'edge') {
          return `${params.data.source} → ${params.data.target}<br/>Flow: ${params.value}`;
        }
        return `${params.name}<br/>Total: ${params.value}`;
      },
    },
    series: [
      {
        type: 'sankey',
        top: 60,
        bottom: 20,
        left: 50,
        right: 150,
        nodeWidth: 20,
        nodeGap: 10,
        layoutIterations: 32,
        emphasis: {
          focus: 'adjacency',
        },
        data: data.nodes,
        links: data.links,
        lineStyle: {
          color: 'gradient',
          curveness: 0.5,
        },
        label: {
          position: 'right',
          fontSize: 12,
        },
      },
    ],
  };

  return <ReactECharts option={option} style={{ height }} />;
};

export default SankeyChart;