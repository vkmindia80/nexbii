import React from 'react';
import { Brain } from 'lucide-react';

interface Props {
  dataSources: Array<{ id: string; name: string; type: string }>;
}

const PredictiveModels: React.FC<Props> = ({ dataSources }) => {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Brain className="w-6 h-6 text-blue-600" />
          Predictive Models
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Train ML models for predictions: Linear/Logistic Regression, Random Forest, Decision Trees
        </p>
      </div>
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-8 text-center">
        <p className="text-purple-800">ML model training interface - Coming soon!</p>
        <p className="text-sm text-purple-600 mt-2">API endpoints ready. Use /api/analytics/predictive-model</p>
      </div>
    </div>
  );
};

export default PredictiveModels;