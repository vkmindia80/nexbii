import React from 'react';
import ReactECharts from 'echarts-for-react';

interface BoxPlotChartProps {
  data: {
    categories: string[];
    values: Array<[number, number, number, number, number]>; // [min, Q1, median, Q3, max]
  };
  title?: string;
  height?: string;
}

const BoxPlotChart: React.FC<BoxPlotChartProps> = ({ data, title, height = '400px' }) => {
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
        const [min, q1, median, q3, max] = params.value;
        return `${params.name}<br/>
          Max: ${max}<br/>
          Q3: ${q3}<br/>
          Median: ${median}<br/>
          Q1: ${q1}<br/>
          Min: ${min}`;
      },
    },
    grid: {
      left: '10%',
      right: '4%',
      bottom: '3%',
      top: 60,
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: data.categories,
      boundaryGap: true,
      splitArea: {
        show: false,
      },
      splitLine: {
        show: false,
      },
    },
    yAxis: {
      type: 'value',
      splitArea: {
        show: true,
      },
    },
    series: [
      {
        name: 'Box Plot',
        type: 'boxplot',
        data: data.values,
        itemStyle: {
          color: '#3b82f6',
          borderColor: '#1e40af',
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  };

  return <ReactECharts option={option} style={{ height }} />;
};

export default BoxPlotChart;