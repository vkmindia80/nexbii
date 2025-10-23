import React, { useEffect, useState } from 'react';
import { Plus, FileText, Play, Trash2 } from 'lucide-react';
import { queryService } from '../services/queryService';
import { datasourceService } from '../services/datasourceService';
import { Query, QueryResult, DataSource } from '../types';

const QueriesPage: React.FC = () => {
  const [queries, setQueries] = useState<Query[]>([]);
  const [datasources, setDatasources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [result, setResult] = useState<QueryResult | null>(null);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    datasource_id: '',
    sql_query: 'SELECT * FROM table_name LIMIT 10;'
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [queriesData, datasourcesData] = await Promise.all([
        queryService.list(),
        datasourceService.list()
      ]);
      setQueries(queriesData);
      setDatasources(datasourcesData);
      if (datasourcesData.length > 0) {
        setFormData(prev => ({ ...prev, datasource_id: datasourcesData[0].id }));
      }
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async () => {
    setExecuting(true);
    setResult(null);
    try {
      const queryResult = await queryService.execute({
        datasource_id: formData.datasource_id,
        sql_query: formData.sql_query,
        limit: 100
      });
      setResult(queryResult);
    } catch (error: any) {
      alert(`Query execution failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setExecuting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await queryService.create({
        name: formData.name,
        description: formData.description,
        datasource_id: formData.datasource_id,
        query_type: 'sql',
        sql_query: formData.sql_query
      });
      setShowModal(false);
      loadData();
      setFormData({
        name: '',
        description: '',
        datasource_id: datasources[0]?.id || '',
        sql_query: 'SELECT * FROM table_name LIMIT 10;'
      });
      setResult(null);
    } catch (error) {
      console.error('Failed to create query:', error);
      alert('Failed to create query');
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this query?')) {
      try {
        await queryService.delete(id);
        loadData();
      } catch (error) {
        console.error('Failed to delete query:', error);
      }
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Queries</h1>
          <p className="text-gray-600 mt-2">Create and manage SQL queries</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          disabled={datasources.length === 0}
          className="flex items-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          data-testid="create-query-button"
        >
          <Plus className="w-5 h-5" />
          <span>Create Query</span>
        </button>
      </div>

      {datasources.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg mb-6">
          Please add a data source first before creating queries.
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : queries.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No queries yet</h3>
          <p className="text-gray-600 mb-4">Start by creating your first query</p>
          {datasources.length > 0 && (
            <button
              onClick={() => setShowModal(true)}
              className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
            >
              Create Query
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {queries.map((query) => (
            <div key={query.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <FileText className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{query.name}</h3>
                    <p className="text-sm text-gray-500">{query.query_type}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(query.id)}
                  className="text-red-600 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
              {query.description && (
                <p className="text-sm text-gray-600 mb-3">{query.description}</p>
              )}
              <div className="text-sm text-gray-500">
                <p>Created: {new Date(query.created_at).toLocaleDateString()}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Create Query</h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Query Name</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="input"
                      placeholder="My Query"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Data Source</label>
                    <select
                      value={formData.datasource_id}
                      onChange={(e) => setFormData({ ...formData, datasource_id: e.target.value })}
                      className="input"
                      required
                    >
                      {datasources.map((ds) => (
                        <option key={ds.id} value={ds.id}>
                          {ds.name} ({ds.type})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <input
                    type="text"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="input"
                    placeholder="Query description"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">SQL Query</label>
                  <textarea
                    value={formData.sql_query}
                    onChange={(e) => setFormData({ ...formData, sql_query: e.target.value })}
                    className="input font-mono text-sm"
                    rows={10}
                    placeholder="SELECT * FROM table_name LIMIT 10;"
                    required
                  />
                </div>

                <button
                  type="button"
                  onClick={handleExecute}
                  disabled={executing || !formData.datasource_id}
                  className="w-full flex items-center justify-center space-x-2 border border-primary-600 text-primary-600 px-4 py-2 rounded-lg hover:bg-primary-50 transition-colors disabled:opacity-50"
                >
                  <Play className="w-4 h-4" />
                  <span>{executing ? 'Executing...' : 'Execute Query'}</span>
                </button>

                {result && (
                  <div className="border border-gray-200 rounded-lg p-4 max-h-96 overflow-auto">
                    <div className="mb-2 flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700">
                        Results: {result.total_rows} rows ({result.execution_time.toFixed(3)}s)
                      </span>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="table text-xs">
                        <thead>
                          <tr>
                            {result.columns.map((col, idx) => (
                              <th key={idx}>{col}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {result.rows.slice(0, 20).map((row, rowIdx) => (
                            <tr key={rowIdx}>
                              {row.map((cell, cellIdx) => (
                                <td key={cellIdx}>{cell !== null ? String(cell) : 'null'}</td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                <div className="flex space-x-3 pt-4">
                  <button
                    type="submit"
                    className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
                  >
                    Save Query
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowModal(false);
                      setResult(null);
                    }}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QueriesPage;