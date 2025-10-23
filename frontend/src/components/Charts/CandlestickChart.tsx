import React from 'react';
import ReactECharts from 'echarts-for-react';

interface CandlestickChartProps {
  data: {
    categories: string[]; // Dates
    values: Array<[number, number, number, number]>; // [open, close, low, high]
  };
  title?: string;
  height?: string;
}

const CandlestickChart: React.FC<CandlestickChartProps> = ({ data, title, height = '400px' }) => {
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
      formatter: (params: any) => {
        const param = params[0];
        const [open, close, low, high] = param.value;
        return `${param.name}<br/>
          Open: ${open}<br/>
          Close: ${close}<br/>
          Low: ${low}<br/>
          High: ${high}`;
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: 60,
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: data.categories,
      boundaryGap: true,
      axisLine: { onZero: false },
      splitLine: { show: false },
      min: 'dataMin',
      max: 'dataMax',
    },
    yAxis: {
      scale: true,
      splitArea: {
        show: true,
      },
    },
    dataZoom: [
      {
        type: 'inside',
        start: 50,
        end: 100,
      },
      {
        show: true,
        type: 'slider',
        top: '90%',
        start: 50,
        end: 100,
      },
    ],
    series: [
      {
        type: 'candlestick',
        data: data.values,
        itemStyle: {
          color: '#10b981',
          color0: '#ef4444',
          borderColor: '#059669',
          borderColor0: '#dc2626',
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

export default CandlestickChart;