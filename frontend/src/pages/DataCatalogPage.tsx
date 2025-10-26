import React, { useState, useEffect } from 'react';
import {
  Database, Table, FileText, Tag, Shield, Eye, Search, Plus, Edit2, Trash2,
  Filter, ChevronDown, ChevronRight, Lock, AlertCircle, CheckCircle
} from 'lucide-react';
import governanceService from '../services/governanceService';

interface CatalogEntry {
  id: string;
  datasource_id: string;
  table_name: string;
  column_name?: string;
  display_name?: string;
  description?: string;
  business_owner?: string;
  technical_owner?: string;
  tags: string[];
  classification_level: string;
  is_pii: boolean;
  pii_types: string[];
  data_type?: string;
  is_nullable?: boolean;
  usage_notes?: string;
  created_at: string;
  updated_at: string;
}

interface Statistics {
  total_entries: number;
  total_tables: number;
  total_columns: number;
  by_classification: Record<string, number>;
  pii_count: number;
  datasources_cataloged: number;
}

const DataCatalogPage: React.FC = () => {
  const [entries, setEntries] = useState<CatalogEntry[]>([]);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterClassification, setFilterClassification] = useState('');
  const [filterPII, setFilterPII] = useState<boolean | undefined>(undefined);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState<CatalogEntry | null>(null);
  const [expandedTables, setExpandedTables] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadData();
  }, [searchQuery, filterClassification, filterPII]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [entriesData, stats] = await Promise.all([
        governanceService.getCatalogEntries({
          search: searchQuery || undefined,
          classification_level: filterClassification || undefined,
          is_pii: filterPII,
          limit: 100,
        }),
        governanceService.getCatalogStatistics(),
      ]);

      setEntries(entriesData.entries);
      setStatistics(stats);
    } catch (error) {
      console.error('Failed to load catalog data:', error);
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

  const getClassificationColor = (level: string) => {
    const colors: Record<string, string> = {
      public: 'bg-green-100 text-green-800',
      internal: 'bg-blue-100 text-blue-800',
      confidential: 'bg-yellow-100 text-yellow-800',
      restricted: 'bg-red-100 text-red-800',
    };
    return colors[level] || 'bg-gray-100 text-gray-800';
  };

  const getClassificationIcon = (level: string) => {
    if (level === 'restricted' || level === 'confidential') {
      return <Lock className="w-3 h-3" />;
    }
    return <Shield className="w-3 h-3" />;
  };

  // Group entries by table
  const groupedEntries = entries.reduce((acc, entry) => {
    if (!entry.column_name) {
      // Table-level entry
      acc[entry.table_name] = { table: entry, columns: [] };
    }
    return acc;
  }, {} as Record<string, { table: CatalogEntry; columns: CatalogEntry[] }>);

  // Add columns to their tables
  entries.forEach((entry) => {
    if (entry.column_name && groupedEntries[entry.table_name]) {
      groupedEntries[entry.table_name].columns.push(entry);
    }
  });

  const handleDelete = async (entryId: string) => {
    if (!confirm('Are you sure you want to delete this catalog entry?')) return;

    try {
      await governanceService.deleteCatalogEntry(entryId);
      loadData();
    } catch (error) {
      console.error('Failed to delete entry:', error);
      alert('Failed to delete entry');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto" data-testid="data-catalog-page">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Database className="w-8 h-8 text-primary-600" />
          Data Catalog
        </h1>
        <p className="text-gray-600 mt-2">
          Manage metadata, classification, and documentation for your data assets
        </p>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Entries</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.total_entries}</p>
              </div>
              <Database className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Tables Cataloged</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.total_tables}</p>
              </div>
              <Table className="w-8 h-8 text-green-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">PII Fields</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.pii_count}</p>
              </div>
              <AlertCircle className="w-8 h-8 text-red-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Data Sources</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.datasources_cataloged}</p>
              </div>
              <FileText className="w-8 h-8 text-purple-600" />
            </div>
          </div>
        </div>
      )}

      {/* Classification Distribution */}
      {statistics && (
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200 mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Classification Distribution</h3>
          <div className="flex gap-4">
            {Object.entries(statistics.by_classification).map(([level, count]) => (
              <div key={level} className="flex items-center gap-2">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getClassificationColor(level)}`}>
                  {level}
                </span>
                <span className="text-sm text-gray-600">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow p-4 border border-gray-200 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search tables, columns, descriptions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          {/* Classification Filter */}
          <div>
            <select
              value={filterClassification}
              onChange={(e) => setFilterClassification(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">All Classifications</option>
              <option value="public">Public</option>
              <option value="internal">Internal</option>
              <option value="confidential">Confidential</option>
              <option value="restricted">Restricted</option>
            </select>
          </div>

          {/* PII Filter */}
          <div>
            <select
              value={filterPII === undefined ? '' : filterPII.toString()}
              onChange={(e) => {
                if (e.target.value === '') {
                  setFilterPII(undefined);
                } else {
                  setFilterPII(e.target.value === 'true');
                }
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">All Data</option>
              <option value="true">PII Only</option>
              <option value="false">Non-PII Only</option>
            </select>
          </div>
        </div>

        <div className="mt-4 flex justify-between items-center">
          <button
            onClick={() => {
              setSearchQuery('');
              setFilterClassification('');
              setFilterPII(undefined);
            }}
            className="text-sm text-gray-600 hover:text-gray-900"
          >
            Clear Filters
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            <Plus className="w-5 h-5" />
            Add Entry
          </button>
        </div>
      </div>

      {/* Catalog Entries - Tree View */}
      <div className="bg-white rounded-lg shadow border border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Catalog Entries</h2>
          <p className="text-sm text-gray-600 mt-1">
            {entries.length} entries found
          </p>
        </div>

        <div className="divide-y divide-gray-200">
          {Object.entries(groupedEntries).map(([tableName, { table, columns }]) => (
            <div key={tableName} className="p-4">
              {/* Table Row */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  <button
                    onClick={() => toggleTable(tableName)}
                    className="p-1 hover:bg-gray-100 rounded"
                  >
                    {expandedTables.has(tableName) ? (
                      <ChevronDown className="w-5 h-5 text-gray-600" />
                    ) : (
                      <ChevronRight className="w-5 h-5 text-gray-600" />
                    )}
                  </button>

                  <Table className="w-5 h-5 text-blue-600" />

                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-gray-900">{table.display_name || tableName}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1 ${getClassificationColor(table.classification_level)}`}>
                        {getClassificationIcon(table.classification_level)}
                        {table.classification_level}
                      </span>
                      {table.is_pii && (
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 flex items-center gap-1">
                          <AlertCircle className="w-3 h-3" />
                          PII
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{table.description || 'No description'}</p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                      {table.business_owner && (
                        <span>Owner: {table.business_owner}</span>
                      )}
                      {columns.length > 0 && (
                        <span>{columns.length} columns</span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {
                      setSelectedEntry(table);
                      setShowEditModal(true);
                    }}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                    title="Edit"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(table.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Columns (Expanded) */}
              {expandedTables.has(tableName) && columns.length > 0 && (
                <div className="ml-12 mt-3 space-y-2">
                  {columns.map((column) => (
                    <div key={column.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
                      <div className="flex items-center gap-3 flex-1">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h4 className="font-medium text-gray-900">{column.display_name || column.column_name}</h4>
                            <span className="text-xs text-gray-500">{column.data_type}</span>
                            {column.is_pii && (
                              <span className="px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800 flex items-center gap-1">
                                <AlertCircle className="w-3 h-3" />
                                PII
                              </span>
                            )}
                          </div>
                          {column.description && (
                            <p className="text-sm text-gray-600 mt-1">{column.description}</p>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => {
                            setSelectedEntry(column);
                            setShowEditModal(true);
                          }}
                          className="p-2 text-blue-600 hover:bg-blue-100 rounded"
                          title="Edit"
                        >
                          <Edit2 className="w-3 h-3" />
                        </button>
                        <button
                          onClick={() => handleDelete(column.id)}
                          className="p-2 text-red-600 hover:bg-red-100 rounded"
                          title="Delete"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}

          {entries.length === 0 && (
            <div className="p-8 text-center text-gray-500">
              <Database className="w-12 h-12 mx-auto mb-3 text-gray-400" />
              <p>No catalog entries found</p>
              <p className="text-sm mt-1">Start by adding your first data catalog entry</p>
            </div>
          )}
        </div>
      </div>

      {/* Modals would go here - Add/Edit Entry */}
      {/* Due to length, modal components are simplified */}
    </div>
  );
};

export default DataCatalogPage;
