import React from 'react';
import { Layers } from 'lucide-react';

interface Props {
  dataSources: Array<{ id: string; name: string; type: string }>;
}

const Clustering: React.FC<Props> = ({ dataSources }) => {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Layers className="w-6 h-6 text-blue-600" />
          Clustering Analysis
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Customer segmentation using K-Means, Hierarchical, or DBSCAN clustering
        </p>
      </div>
      <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-8 text-center">
        <p className="text-indigo-800">Clustering interface - Coming soon!</p>
        <p className="text-sm text-indigo-600 mt-2">API endpoints ready. Use /api/analytics/clustering</p>
      </div>
    </div>
  );
};

export default Clustering;