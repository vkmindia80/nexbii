import React from 'react';
import ReactECharts from 'echarts-for-react';

interface BubbleChartProps {
  data: {
    series: Array<{
      name: string;
      data: Array<[number, number, number]>; // [x, y, size]
      color?: string;
    }>;
  };
  title?: string;
  height?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
}

const BubbleChart: React.FC<BubbleChartProps> = ({ 
  data, 
  title, 
  height = '400px',
  xAxisLabel,
  yAxisLabel 
}) => {
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
        const [x, y, size] = params.value;
        return `${params.seriesName}<br/>X: ${x}<br/>Y: ${y}<br/>Size: ${size}`;
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
      type: 'value',
      name: xAxisLabel,
      nameLocation: 'middle',
      nameGap: 30,
      splitLine: {
        lineStyle: {
          type: 'dashed',
        },
      },
    },
    yAxis: {
      type: 'value',
      name: yAxisLabel,
      nameLocation: 'middle',
      nameGap: 40,
      splitLine: {
        lineStyle: {
          type: 'dashed',
        },
      },
    },
    series: data.series.map((s) => ({
      name: s.name,
      type: 'scatter',
      data: s.data,
      symbolSize: (data: number[]) => Math.sqrt(data[2]) * 5,
      itemStyle: {
        color: s.color || undefined,
        opacity: 0.7,
      },
      emphasis: {
        focus: 'series',
        itemStyle: {
          opacity: 1,
        },
      },
    })),
  };

  return <ReactECharts option={option} style={{ height }} />;
};

export default BubbleChart;