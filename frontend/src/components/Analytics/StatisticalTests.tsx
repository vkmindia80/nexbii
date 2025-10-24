import React from 'react';
import { BarChart3 } from 'lucide-react';

interface Props {
  dataSources: Array<{ id: string; name: string; type: string }>;
}

const StatisticalTests: React.FC<Props> = ({ dataSources }) => {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-blue-600" />
          Statistical Tests
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Perform hypothesis testing: t-tests, chi-square, ANOVA, correlation, normality tests
        </p>
      </div>
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
        <p className="text-blue-800">Statistical testing interface - Coming soon!</p>
        <p className="text-sm text-blue-600 mt-2">API endpoints ready. Use /api/analytics/statistical-test</p>
      </div>
    </div>
  );
};

export default StatisticalTests;