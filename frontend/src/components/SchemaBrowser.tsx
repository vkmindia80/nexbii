import React, { useState, useEffect } from 'react';
import { X, Database, Table, Loader2, ChevronDown, ChevronRight, Search } from 'lucide-react';
import { datasourceService } from '../services/datasourceService';

interface SchemaBrowserProps {
  datasourceId: string;
  datasourceName: string;
  onClose: () => void;
}

interface TableSchema {
  name: string;
  columns: Array<{
    name: string;
    type: string;
  }>;
  row_count?: number;
}

const SchemaBrowser: React.FC<SchemaBrowserProps> = ({ datasourceId, datasourceName, onClose }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [schema, setSchema] = useState<TableSchema[]>([]);
  const [expandedTables, setExpandedTables] = useState<Set<string>>(new Set());
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadSchema();
  }, [datasourceId]);

  const loadSchema = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await datasourceService.getSchema(datasourceId);
      setSchema(result.tables || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load schema. Please ensure the data source is properly configured.');
    } finally {
      setLoading(false);
    }
  };

  const toggleTable = (tableName: string) => {
    const newExpanded = new Set(expandedTables);
    if (newExpanded.has(tableName)) {
      newExpanded.delete(tableName);
    } else {
      newExpanded.add(tableName);
    }
    setExpandedTables(newExpanded);
  };

  const filteredSchema = schema.filter(table =>
    (table.name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
    (table.columns || []).some(col => (col.name || '').toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[85vh] flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                <Database className="w-5 h-5 text-primary-600" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Schema Browser</h2>
                <p className="text-sm text-gray-600">{datasourceName}</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              data-testid="close-schema-browser"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Search Bar */}
          <div className="mt-4 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search tables and columns..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              data-testid="schema-search-input"
            />
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex flex-col items-center justify-center h-64">
              <Loader2 className="w-12 h-12 text-primary-600 animate-spin mb-4" />
              <p className="text-gray-600">Loading schema...</p>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center h-64">
              <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
                <p className="text-red-800 text-center">{error}</p>
                <button
                  onClick={loadSchema}
                  className="mt-4 w-full bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
                >
                  Retry
                </button>
              </div>
            </div>
          ) : filteredSchema.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64">
              <Database className="w-16 h-16 text-gray-400 mb-4" />
              <p className="text-gray-600">
                {searchQuery ? 'No tables or columns match your search' : 'No tables found in this data source'}
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="mb-4 text-sm text-gray-600">
                Found {filteredSchema.length} table{filteredSchema.length !== 1 ? 's' : ''}
              </div>
              {filteredSchema.map((table) => (
                <div key={table.table_name} className="border border-gray-200 rounded-lg overflow-hidden">
                  {/* Table Header */}
                  <button
                    onClick={() => toggleTable(table.table_name)}
                    className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 transition-colors text-left"
                    data-testid={`table-${table.table_name}`}
                  >
                    <div className="flex items-center space-x-3">
                      {expandedTables.has(table.table_name) ? (
                        <ChevronDown className="w-5 h-5 text-gray-600" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-gray-600" />
                      )}
                      <Table className="w-5 h-5 text-primary-600" />
                      <span className="font-semibold text-gray-900">{table.table_name}</span>
                      <span className="text-sm text-gray-500">({table.columns.length} columns)</span>
                    </div>
                  </button>

                  {/* Columns List */}
                  {expandedTables.has(table.table_name) && (
                    <div className="bg-white">
                      <table className="w-full">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Column Name
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Data Type
                            </th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {table.columns.map((column, idx) => (
                            <tr
                              key={`${table.table_name}-${column.column_name}`}
                              className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                            >
                              <td className="px-6 py-3 text-sm font-mono text-gray-900">
                                {column.column_name}
                              </td>
                              <td className="px-6 py-3 text-sm text-gray-600">
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                  {column.data_type}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-600">
              Click on a table to view its columns
            </p>
            <button
              onClick={onClose}
              className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SchemaBrowser;
