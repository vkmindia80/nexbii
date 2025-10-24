import React from 'react';
import { Table } from 'lucide-react';

interface Props {
  dataSources: Array<{ id: string; name: string; type: string }>;
}

const PivotTable: React.FC<Props> = ({ dataSources }) => {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Table className="w-6 h-6 text-blue-600" />
          Pivot Tables
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Interactive pivot tables for dynamic data aggregation and slicing
        </p>
      </div>
      <div className="bg-green-50 border border-green-200 rounded-lg p-8 text-center">
        <p className="text-green-800">Pivot table builder - Coming soon!</p>
        <p className="text-sm text-green-600 mt-2">API endpoints ready. Use /api/analytics/pivot-table</p>
      </div>
    </div>
  );
};

export default PivotTable;