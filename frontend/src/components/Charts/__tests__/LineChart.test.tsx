/**
 * Tests for LineChart component
 */
import React from 'react';
import { render } from '@testing-library/react';
import LineChart from '../LineChart';

// Mock echarts-for-react
jest.mock('echarts-for-react', () => {
  return function MockEcharts(props: any) {
    return <div data-testid="echarts-mock">{JSON.stringify(props.option)}</div>;
  };
});

describe('LineChart Component', () => {
  const mockData = {
    columns: ['date', 'revenue'],
    rows: [
      ['2024-01-01', 1000],
      ['2024-01-02', 1200],
      ['2024-01-03', 1100]
    ]
  };

  it('should render without crashing', () => {
    const { container } = render(<LineChart data={mockData} />);
    expect(container).toBeInTheDocument();
  });

  it('should render with correct data structure', () => {
    const { getByTestId } = render(<LineChart data={mockData} />);
    
    const chartElement = getByTestId('echarts-mock');
    expect(chartElement).toBeInTheDocument();
    
    const optionText = chartElement.textContent || '';
    expect(optionText).toContain('xAxis');
    expect(optionText).toContain('yAxis');
    expect(optionText).toContain('series');
  });

  it('should handle empty data gracefully', () => {
    const emptyData = {
      columns: [],
      rows: []
    };

    const { container } = render(<LineChart data={emptyData} />);
    expect(container).toBeInTheDocument();
  });

  it('should apply custom configuration', () => {
    const config = {
      title: 'Revenue Chart',
      xAxisLabel: 'Date',
      yAxisLabel: 'Amount'
    };

    const { getByTestId } = render(
      <LineChart data={mockData} config={config} />
    );
    
    const chartElement = getByTestId('echarts-mock');
    const optionText = chartElement.textContent || '';
    expect(optionText).toContain('Revenue Chart');
  });

  it('should handle single data point', () => {
    const singlePoint = {
      columns: ['date', 'revenue'],
      rows: [['2024-01-01', 1000]]
    };

    const { container } = render(<LineChart data={singlePoint} />);
    expect(container).toBeInTheDocument();
  });

  it('should handle large datasets', () => {
    const largeData = {
      columns: ['date', 'revenue'],
      rows: Array.from({ length: 1000 }, (_, i) => [
        `2024-01-${String(i + 1).padStart(2, '0')}`,
        Math.random() * 1000
      ])
    };

    const { container } = render(<LineChart data={largeData} />);
    expect(container).toBeInTheDocument();
  });
});
