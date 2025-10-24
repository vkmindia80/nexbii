import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface Props {
  dataSources: Array<{ id: string; name: string; type: string }>;
}

const AnomalyDetection: React.FC<Props> = ({ dataSources }) => {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <AlertTriangle className="w-6 h-6 text-blue-600" />
          Anomaly Detection
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Identify outliers using Isolation Forest, Local Outlier Factor, or One-Class SVM
        </p>
      </div>
      <div className="bg-orange-50 border border-orange-200 rounded-lg p-8 text-center">
        <p className="text-orange-800">Anomaly detection interface - Coming soon!</p>
        <p className="text-sm text-orange-600 mt-2">API endpoints ready. Use /api/analytics/anomaly-detection</p>
      </div>
    </div>
  );
};

export default AnomalyDetection;