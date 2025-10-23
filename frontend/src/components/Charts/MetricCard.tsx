import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: number | string;
  prefix?: string;
  suffix?: string;
  change?: number;
  changeLabel?: string;
  format?: 'number' | 'currency' | 'percentage';
  height?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ 
  title, 
  value, 
  prefix = '',
  suffix = '',
  change,
  changeLabel = 'vs last period',
  format = 'number',
  height = '200px'
}) => {
  const formatValue = (val: number | string): string => {
    if (typeof val === 'string') return val;
    
    switch (format) {
      case 'currency':
        return `$${val.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`;
      case 'percentage':
        return `${val.toFixed(1)}%`;
      default:
        return val.toLocaleString('en-US');
    }
  };

  const displayValue = prefix + formatValue(value) + suffix;
  const hasChange = change !== undefined;
  const isPositive = hasChange && change > 0;
  const isNegative = hasChange && change < 0;

  return (
    <div 
      className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 flex flex-col justify-center"
      style={{ height }}
      data-testid="metric-card"
    >
      <div className="text-sm font-medium text-gray-600 mb-2">{title}</div>
      <div className="text-4xl font-bold text-gray-900 mb-2">{displayValue}</div>
      {hasChange && (
        <div className="flex items-center space-x-2">
          {isPositive && (
            <>
              <TrendingUp className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium text-green-600">+{change.toFixed(1)}%</span>
            </>
          )}
          {isNegative && (
            <>
              <TrendingDown className="w-4 h-4 text-red-600" />
              <span className="text-sm font-medium text-red-600">{change.toFixed(1)}%</span>
            </>
          )}
          <span className="text-sm text-gray-500">{changeLabel}</span>
        </div>
      )}
    </div>
  );
};

export default MetricCard;
