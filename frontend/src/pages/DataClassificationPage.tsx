import React, { useState, useEffect } from 'react';
import {
  Shield, Plus, Edit2, Trash2, Search, Play, AlertCircle,
  CheckCircle, Database, Table, Eye, EyeOff, Lock
} from 'lucide-react';
import governanceService from '../services/governanceService';

interface ClassificationRule {
  id: string;
  name: string;
  description?: string;
  pii_type: string;
  pattern?: string;
  column_name_pattern?: string;
  classification_level: string;
  is_enabled: boolean;
  priority: number;
  created_at: string;
}

interface ScanResult {
  datasource_id: string;
  table_name: string;
  column_name: string;
  pii_type: string;
  matches_found: number;
  confidence_score: number;
  sample_values: string[];
}

const DataClassificationPage: React.FC = () => {
  const [rules, setRules] = useState<ClassificationRule[]>([]);
  const [scanResults, setScanResults] = useState<ScanResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [datasourceId, setDatasourceId] = useState('');

  useEffect(() => {
    loadRules();
  }, []);

  const loadRules = async () => {
    try {
      setLoading(true);
      const data = await governanceService.getClassificationRules();
      setRules(data);
    } catch (error) {
      console.error('Failed to load classification rules:', error);
    } finally {
      setLoading(false);
    }
  };

  const runScan = async () => {
    if (!datasourceId) {
      alert('Please enter a datasource ID');
      return;
    }

    try {
      setScanning(true);
      const results = await governanceService.scanForPII(datasourceId);
      setScanResults(results);
    } catch (error) {
      console.error('Failed to scan for PII:', error);
      alert('Failed to scan for PII');
    } finally {
      setScanning(false);
    }
  };

  const getPIITypeColor = (type: string) => {
    const colors: Record<string, string> = {
      ssn: 'bg-red-100 text-red-800',
      email: 'bg-blue-100 text-blue-800',
      phone: 'bg-green-100 text-green-800',
      credit_card: 'bg-purple-100 text-purple-800',
      passport: 'bg-yellow-100 text-yellow-800',
      driver_license: 'bg-orange-100 text-orange-800',
      address: 'bg-pink-100 text-pink-800',
      date_of_birth: 'bg-indigo-100 text-indigo-800',
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto" data-testid="data-classification-page">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Shield className="w-8 h-8 text-primary-600" />
          Data Classification
        </h1>
        <p className="text-gray-600 mt-2">
          Define rules to automatically detect and classify sensitive data (PII)
        </p>
      </div>

      {/* PII Scanner */}
      <div className="bg-white rounded-lg shadow p-6 border border-gray-200 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Search className="w-5 h-5" />
          PII Scanner
        </h2>
        
        <div className="flex gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Data Source ID
            </label>
            <input
              type="text"
              value={datasourceId}
              onChange={(e) => setDatasourceId(e.target.value)}
              placeholder="Enter datasource ID to scan..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={runScan}
              disabled={scanning}
              className="flex items-center gap-2 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
            >
              {scanning ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Scanning...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Scan for PII
                </>
              )}
            </button>
          </div>
        </div>

        {/* Scan Results */}
        {scanResults.length > 0 && (
          <div className="mt-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">
              Scan Results ({scanResults.length} findings)
            </h3>
            <div className="space-y-2">
              {scanResults.map((result, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <div className="flex items-center gap-4 flex-1">
                    <AlertCircle className="w-5 h-5 text-orange-600" />
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-gray-900">
                          {result.table_name}.{result.column_name}
                        </p>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getPIITypeColor(result.pii_type)}`}>
                          {result.pii_type.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {result.matches_found} matches found • {result.confidence_score}% confidence
                      </p>
                    </div>
                  </div>
                  <button
                    className="px-4 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                  >
                    Tag as PII
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Classification Rules */}
      <div className="bg-white rounded-lg shadow border border-gray-200">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Classification Rules</h2>
            <p className="text-sm text-gray-600 mt-1">
              {rules.length} rules configured • {rules.filter(r => r.is_enabled).length} active
            </p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            <Plus className="w-5 h-5" />
            Add Rule
          </button>
        </div>

        <div className="divide-y divide-gray-200">
          {rules.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <Shield className="w-12 h-12 mx-auto mb-3 text-gray-400" />
              <p>No classification rules defined</p>
              <p className="text-sm mt-1">Create your first rule to start auto-classifying data</p>
            </div>
          ) : (
            rules.map((rule) => (
              <div key={rule.id} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 flex-1">
                    <div className={`p-2 rounded-lg ${rule.is_enabled ? 'bg-green-100' : 'bg-gray-100'}`}>
                      {rule.is_enabled ? (
                        <Eye className="w-5 h-5 text-green-600" />
                      ) : (
                        <EyeOff className="w-5 h-5 text-gray-600" />
                      )}
                    </div>

                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-gray-900">{rule.name}</h3>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getPIITypeColor(rule.pii_type)}`}>
                          {rule.pii_type.replace('_', ' ').toUpperCase()}
                        </span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getClassificationColor(rule.classification_level)}`}>
                          {rule.classification_level}
                        </span>
                        <span className="text-xs text-gray-500">Priority: {rule.priority}</span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {rule.description || 'No description'}
                      </p>
                      {rule.pattern && (
                        <p className="text-xs text-gray-500 mt-1 font-mono bg-gray-50 px-2 py-1 rounded inline-block">
                          Pattern: {rule.pattern}
                        </p>
                      )}
                      {rule.column_name_pattern && (
                        <p className="text-xs text-gray-500 mt-1">
                          Column pattern: <code className="bg-gray-50 px-1 py-0.5 rounded">{rule.column_name_pattern}</code>
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                      title="Edit"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Info Box */}
      <div className="mt-6 bg-blue-50 rounded-lg p-6 border border-blue-200">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-blue-900 mb-2">PII Types Detected</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm text-blue-800">
              <div className="flex items-center gap-2">
                <Lock className="w-4 h-4" />
                Social Security Numbers (SSN)
              </div>
              <div className="flex items-center gap-2">
                <Lock className="w-4 h-4" />
                Email Addresses
              </div>
              <div className="flex items-center gap-2">
                <Lock className="w-4 h-4" />
                Phone Numbers
              </div>
              <div className="flex items-center gap-2">
                <Lock className="w-4 h-4" />
                Credit Card Numbers
              </div>
              <div className="flex items-center gap-2">
                <Lock className="w-4 h-4" />
                Passport Numbers
              </div>
              <div className="flex items-center gap-2">
                <Lock className="w-4 h-4" />
                Driver License Numbers
              </div>
              <div className="flex items-center gap-2">
                <Lock className="w-4 h-4" />
                Physical Addresses
              </div>
              <div className="flex items-center gap-2">
                <Lock className="w-4 h-4" />
                Date of Birth
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataClassificationPage;
