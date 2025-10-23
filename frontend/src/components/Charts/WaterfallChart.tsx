import React from 'react';
import ReactECharts from 'echarts-for-react';

interface WaterfallChartProps {
  data: {
    categories: string[];
    values: number[];
  };
  title?: string;
  height?: string;
}

const WaterfallChart: React.FC<WaterfallChartProps> = ({ data, title, height = '400px' }) => {
  // Calculate cumulative values for waterfall effect
  const cumulativeData: (number | string)[] = [];
  const positiveData: (number | string)[] = [];
  const negativeData: (number | string)[] = [];
  
  let cumulative = 0;
  data.values.forEach((value, index) => {
    if (index === 0) {
      cumulativeData.push(0);
      positiveData.push(value >= 0 ? value : 0);
      negativeData.push(value < 0 ? -value : 0);
    } else if (index === data.values.length - 1) {
      // Total bar
      cumulativeData.push(0);
      cumulative += value;
      positiveData.push(cumulative >= 0 ? cumulative : 0);
      negativeData.push(cumulative < 0 ? -cumulative : 0);
    } else {
      cumulativeData.push(cumulative);
      if (value >= 0) {
        positiveData.push(value);
        negativeData.push('-');
      } else {
        positiveData.push('-');
        negativeData.push(-value);
      }
      cumulative += value;
    }
  });

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
        type: 'shadow',
      },
      formatter: (params: any) => {
        const index = params[0].dataIndex;
        return `${data.categories[index]}<br/>Value: ${data.values[index]}`;
      },
    },
    legend: {
      show: false,
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
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        name: 'Placeholder',
        type: 'bar',
        stack: 'Total',
        itemStyle: {
          borderColor: 'transparent',
          color: 'transparent',
        },
        emphasis: {
          itemStyle: {
            borderColor: 'transparent',
            color: 'transparent',
          },
        },
        data: cumulativeData,
      },
      {
        name: 'Positive',
        type: 'bar',
        stack: 'Total',
        label: {
          show: true,
          position: 'top',
          formatter: (params: any) => {
            return data.values[params.dataIndex];
          },
        },
        itemStyle: {
          color: '#10b981',
        },
        data: positiveData,
      },
      {
        name: 'Negative',
        type: 'bar',
        stack: 'Total',
        label: {
          show: true,
          position: 'bottom',
          formatter: (params: any) => {
            return data.values[params.dataIndex];
          },
        },
        itemStyle: {
          color: '#ef4444',
        },
        data: negativeData,
      },
    ],
  };

  return <ReactECharts option={option} style={{ height }} />;
};

export default WaterfallChart;