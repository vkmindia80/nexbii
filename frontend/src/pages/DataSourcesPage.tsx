import React, { useEffect, useState } from 'react';
import { Plus, Database, Trash2, CheckCircle, XCircle, Eye } from 'lucide-react';
import { datasourceService } from '../services/datasourceService';
import { DataSource } from '../types';
import SchemaBrowser from '../components/SchemaBrowser';

const DataSourcesPage: React.FC = () => {
  const [datasources, setDatasources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showSchemaBrowser, setShowSchemaBrowser] = useState(false);
  const [selectedDatasource, setSelectedDatasource] = useState<DataSource | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    type: 'postgresql' as any,
    host: '',
    port: '',
    database: '',
    user: '',
    password: ''
  });
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<boolean | null>(null);

  useEffect(() => {
    loadDatasources();
  }, []);

  const loadDatasources = async () => {
    try {
      const data = await datasourceService.list();
      setDatasources(data);
    } catch (error) {
      console.error('Failed to load data sources:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const config = {
        host: formData.host,
        port: parseInt(formData.port),
        database: formData.database,
        user: formData.user,
        password: formData.password
      };
      const result = await datasourceService.testConnection(formData.type, config);
      setTestResult(result);
    } catch (error) {
      setTestResult(false);
    } finally {
      setTesting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const config = {
        host: formData.host,
        port: parseInt(formData.port),
        database: formData.database,
        user: formData.user,
        password: formData.password
      };
      await datasourceService.create({
        name: formData.name,
        type: formData.type,
        connection_config: config
      });
      setShowModal(false);
      loadDatasources();
      // Reset form
      setFormData({
        name: '',
        type: 'postgresql',
        host: '',
        port: '',
        database: '',
        user: '',
        password: ''
      });
      setTestResult(null);
    } catch (error) {
      console.error('Failed to create data source:', error);
      alert('Failed to create data source');
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this data source?')) {
      try {
        await datasourceService.delete(id);
        loadDatasources();
      } catch (error) {
        console.error('Failed to delete data source:', error);
      }
    }
  };

  const handleBrowseSchema = (ds: DataSource) => {
    setSelectedDatasource(ds);
    setShowSchemaBrowser(true);
  };

  const getDefaultPort = (type: string) => {
    switch (type) {
      case 'postgresql': return '5432';
      case 'mysql': return '3306';
      case 'mongodb': return '27017';
      default: return '';
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Data Sources</h1>
          <p className="text-gray-600 mt-2">Manage your database connections</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
          data-testid="add-datasource-button"
        >
          <Plus className="w-5 h-5" />
          <span>Add Data Source</span>
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : datasources.length === 0 ? (
        <div className="text-center py-12">
          <Database className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No data sources yet</h3>
          <p className="text-gray-600 mb-4">Get started by adding your first data source</p>
          <button
            onClick={() => setShowModal(true)}
            className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
          >
            Add Data Source
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {datasources.map((ds) => (
            <div key={ds.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                    <Database className="w-5 h-5 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{ds.name}</h3>
                    <p className="text-sm text-gray-500">{ds.type}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(ds.id)}
                  className="text-red-600 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
              <div className="text-sm text-gray-600">
                <p>Created: {new Date(ds.created_at).toLocaleDateString()}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Add Data Source</h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="input"
                    placeholder="My Database"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData({ ...formData, type: e.target.value as any, port: getDefaultPort(e.target.value) })}
                    className="input"
                  >
                    <option value="postgresql">PostgreSQL</option>
                    <option value="mysql">MySQL</option>
                    <option value="mongodb">MongoDB</option>
                    <option value="sqlite">SQLite</option>
                  </select>
                </div>

                {formData.type !== 'sqlite' && (
                  <>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Host</label>
                        <input
                          type="text"
                          value={formData.host}
                          onChange={(e) => setFormData({ ...formData, host: e.target.value })}
                          className="input"
                          placeholder="localhost"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Port</label>
                        <input
                          type="text"
                          value={formData.port}
                          onChange={(e) => setFormData({ ...formData, port: e.target.value })}
                          className="input"
                          placeholder="5432"
                          required
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Database</label>
                      <input
                        type="text"
                        value={formData.database}
                        onChange={(e) => setFormData({ ...formData, database: e.target.value })}
                        className="input"
                        placeholder="mydb"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Username</label>
                      <input
                        type="text"
                        value={formData.user}
                        onChange={(e) => setFormData({ ...formData, user: e.target.value })}
                        className="input"
                        placeholder="user"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
                      <input
                        type="password"
                        value={formData.password}
                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                        className="input"
                        placeholder="••••••••"
                        required
                      />
                    </div>
                  </>
                )}

                {testResult !== null && (
                  <div className={`flex items-center space-x-2 p-3 rounded-lg ${
                    testResult ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                  }`}>
                    {testResult ? <CheckCircle className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
                    <span>{testResult ? 'Connection successful!' : 'Connection failed'}</span>
                  </div>
                )}

                <div className="flex space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={handleTestConnection}
                    disabled={testing}
                    className="flex-1 border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    {testing ? 'Testing...' : 'Test Connection'}
                  </button>
                  <button
                    type="submit"
                    disabled={testResult !== true}
                    className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Add Data Source
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowModal(false);
                      setTestResult(null);
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

export default DataSourcesPage;