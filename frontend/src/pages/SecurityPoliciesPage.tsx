import React, { useState, useEffect } from 'react';
import { Shield, Plus, Edit2, Trash2, Eye, EyeOff } from 'lucide-react';
import api from '../services/api';

interface SecurityPolicy {
  id: string;
  name: string;
  description: string;
  policy_type: 'row_level' | 'column_level';
  is_active: boolean;
  priority: number;
  created_at: string;
}

const SecurityPoliciesPage: React.FC = () => {
  const [policies, setPolicies] = useState<SecurityPolicy[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedPolicy, setSelectedPolicy] = useState<SecurityPolicy | null>(null);
  const [filterType, setFilterType] = useState<string>('all');

  useEffect(() => {
    fetchPolicies();
  }, []);

  const fetchPolicies = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/security/policies');
      setPolicies(response.data);
    } catch (error) {
      console.error('Failed to fetch policies:', error);
    } finally {
      setLoading(false);
    }
  };

  const deletePolicy = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this policy?')) return;
    
    try {
      await api.delete(`/api/security/policies/${id}`);
      fetchPolicies();
    } catch (error) {
      console.error('Failed to delete policy:', error);
    }
  };

  const togglePolicy = async (policy: SecurityPolicy) => {
    try {
      await api.put(`/api/security/policies/${policy.id}`, {
        is_active: !policy.is_active
      });
      fetchPolicies();
    } catch (error) {
      console.error('Failed to toggle policy:', error);
    }
  };

  const filteredPolicies = filterType === 'all' 
    ? policies 
    : policies.filter(p => p.policy_type === filterType);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Shield className="w-8 h-8 text-blue-600" />
              Security Policies
            </h1>
            <p className="text-gray-600 mt-2">
              Manage Row-Level and Column-Level Security policies
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            data-testid="create-policy-button"
          >
            <Plus className="w-5 h-5" />
            Create Policy
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="flex gap-4">
            <button
              onClick={() => setFilterType('all')}
              className={`px-4 py-2 rounded-lg ${
                filterType === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              All Policies
            </button>
            <button
              onClick={() => setFilterType('row_level')}
              className={`px-4 py-2 rounded-lg ${
                filterType === 'row_level'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Row-Level Security
            </button>
            <button
              onClick={() => setFilterType('column_level')}
              className={`px-4 py-2 rounded-lg ${
                filterType === 'column_level'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Column-Level Security
            </button>
          </div>
        </div>

        {/* Policies List */}
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : filteredPolicies.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <Shield className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No security policies yet
            </h3>
            <p className="text-gray-600 mb-6">
              Create your first security policy to protect your data
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Create Policy
            </button>
          </div>
        ) : (
          <div className="grid gap-4">
            {filteredPolicies.map((policy) => (
              <div
                key={policy.id}
                className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow"
                data-testid={`policy-${policy.id}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-semibold text-gray-900">
                        {policy.name}
                      </h3>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${
                          policy.policy_type === 'row_level'
                            ? 'bg-purple-100 text-purple-700'
                            : 'bg-green-100 text-green-700'
                        }`}
                      >
                        {policy.policy_type === 'row_level' ? 'RLS' : 'CLS'}
                      </span>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${
                          policy.is_active
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {policy.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    <p className="text-gray-600 mb-2">{policy.description}</p>
                    <div className="text-sm text-gray-500">
                      Priority: {policy.priority} | Created:{' '}
                      {new Date(policy.created_at).toLocaleDateString()}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => togglePolicy(policy)}
                      className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                      title={policy.is_active ? 'Disable' : 'Enable'}
                    >
                      {policy.is_active ? (
                        <Eye className="w-5 h-5" />
                      ) : (
                        <EyeOff className="w-5 h-5" />
                      )}
                    </button>
                    <button
                      onClick={() => setSelectedPolicy(policy)}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                    >
                      <Edit2 className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => deletePolicy(policy.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SecurityPoliciesPage;
