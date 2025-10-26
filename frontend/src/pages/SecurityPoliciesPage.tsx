import React, { useState, useEffect } from 'react';
import { Shield, Plus, Edit2, Trash2, Eye, EyeOff, PlayCircle, Save, X, AlertCircle, CheckCircle } from 'lucide-react';
import securityService, { SecurityPolicy, DataMaskingRule, CreatePolicyRequest, CreateMaskingRuleRequest } from '../services/securityService';

const SecurityPoliciesPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'policies' | 'masking'>('policies');
  const [policies, setPolicies] = useState<SecurityPolicy[]>([]);
  const [maskingRules, setMaskingRules] = useState<DataMaskingRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreatePolicyModal, setShowCreatePolicyModal] = useState(false);
  const [showCreateMaskingModal, setShowCreateMaskingModal] = useState(false);
  const [showEditPolicyModal, setShowEditPolicyModal] = useState(false);
  const [showTestPolicyModal, setShowTestPolicyModal] = useState(false);
  const [selectedPolicy, setSelectedPolicy] = useState<SecurityPolicy | null>(null);
  const [filterType, setFilterType] = useState<string>('all');
  const [testResult, setTestResult] = useState<any>(null);

  // Form states
  const [policyForm, setPolicyForm] = useState<CreatePolicyRequest>({
    name: '',
    description: '',
    policy_type: 'row_level',
    rules: {},
    priority: 1,
    applies_to: []
  });

  const [maskingForm, setMaskingForm] = useState<CreateMaskingRuleRequest>({
    name: '',
    description: '',
    data_type: 'email',
    masking_pattern: '***'
  });

  const [ruleBuilder, setRuleBuilder] = useState({
    conditions: [{ field: '', operator: '=', value: '' }],
    columns: [] as string[],
    maskingType: 'hide'
  });

  const [testData, setTestData] = useState({
    user_role: 'viewer',
    user_id: '',
    sample_data: ''
  });

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    try {
      setLoading(true);
      if (activeTab === 'policies') {
        const data = await securityService.getPolicies();
        setPolicies(data);
      } else {
        const data = await securityService.getMaskingRules();
        setMaskingRules(data);
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePolicy = async () => {
    try {
      const rulesData = policyForm.policy_type === 'row_level'
        ? { conditions: ruleBuilder.conditions }
        : { columns: ruleBuilder.columns, masking_type: ruleBuilder.maskingType };

      await securityService.createPolicy({
        ...policyForm,
        rules: rulesData
      });
      setShowCreatePolicyModal(false);
      resetPolicyForm();
      fetchData();
    } catch (error) {
      console.error('Failed to create policy:', error);
      alert('Failed to create policy');
    }
  };

  const handleUpdatePolicy = async () => {
    if (!selectedPolicy) return;
    try {
      await securityService.updatePolicy(selectedPolicy.id, policyForm);
      setShowEditPolicyModal(false);
      setSelectedPolicy(null);
      resetPolicyForm();
      fetchData();
    } catch (error) {
      console.error('Failed to update policy:', error);
      alert('Failed to update policy');
    }
  };

  const handleDeletePolicy = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this policy?')) return;
    try {
      await securityService.deletePolicy(id);
      fetchData();
    } catch (error) {
      console.error('Failed to delete policy:', error);
      alert('Failed to delete policy');
    }
  };

  const handleTogglePolicy = async (policy: SecurityPolicy) => {
    try {
      await securityService.updatePolicy(policy.id, {
        is_active: !policy.is_active
      });
      fetchData();
    } catch (error) {
      console.error('Failed to toggle policy:', error);
    }
  };

  const handleTestPolicy = async () => {
    if (!selectedPolicy) return;
    try {
      const result = await securityService.testPolicy(selectedPolicy.id, testData);
      setTestResult(result);
    } catch (error) {
      console.error('Failed to test policy:', error);
      setTestResult({ success: false, message: 'Test failed' });
    }
  };

  const handleCreateMaskingRule = async () => {
    try {
      await securityService.createMaskingRule(maskingForm);
      setShowCreateMaskingModal(false);
      resetMaskingForm();
      fetchData();
    } catch (error) {
      console.error('Failed to create masking rule:', error);
      alert('Failed to create masking rule');
    }
  };

  const handleDeleteMaskingRule = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this rule?')) return;
    try {
      await securityService.deleteMaskingRule(id);
      fetchData();
    } catch (error) {
      console.error('Failed to delete rule:', error);
    }
  };

  const resetPolicyForm = () => {
    setPolicyForm({
      name: '',
      description: '',
      policy_type: 'row_level',
      rules: {},
      priority: 1,
      applies_to: []
    });
    setRuleBuilder({
      conditions: [{ field: '', operator: '=', value: '' }],
      columns: [],
      maskingType: 'hide'
    });
  };

  const resetMaskingForm = () => {
    setMaskingForm({
      name: '',
      description: '',
      data_type: 'email',
      masking_pattern: '***'
    });
  };

  const addCondition = () => {
    setRuleBuilder({
      ...ruleBuilder,
      conditions: [...ruleBuilder.conditions, { field: '', operator: '=', value: '' }]
    });
  };

  const removeCondition = (index: number) => {
    setRuleBuilder({
      ...ruleBuilder,
      conditions: ruleBuilder.conditions.filter((_, i) => i !== index)
    });
  };

  const updateCondition = (index: number, key: string, value: string) => {
    const newConditions = [...ruleBuilder.conditions];
    newConditions[index] = { ...newConditions[index], [key]: value };
    setRuleBuilder({ ...ruleBuilder, conditions: newConditions });
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
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3" data-testid="page-title">
              <Shield className="w-8 h-8 text-purple-600" />
              Security Policies
            </h1>
            <p className="text-gray-600 mt-2">
              Manage Row-Level Security (RLS), Column-Level Security (CLS), and Data Masking
            </p>
          </div>
          <button
            onClick={() => activeTab === 'policies' ? setShowCreatePolicyModal(true) : setShowCreateMaskingModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            data-testid="create-button"
          >
            <Plus className="w-5 h-5" />
            {activeTab === 'policies' ? 'Create Policy' : 'Create Masking Rule'}
          </button>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('policies')}
              className={`px-6 py-4 font-medium transition-colors ${
                activeTab === 'policies'
                  ? 'text-purple-600 border-b-2 border-purple-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
              data-testid="policies-tab"
            >
              Security Policies
            </button>
            <button
              onClick={() => setActiveTab('masking')}
              className={`px-6 py-4 font-medium transition-colors ${
                activeTab === 'masking'
                  ? 'text-purple-600 border-b-2 border-purple-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
              data-testid="masking-tab"
            >
              Data Masking Rules
            </button>
          </div>
        </div>

        {/* Policies Tab */}
        {activeTab === 'policies' && (
          <>
            {/* Filters */}
            <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
              <div className="flex gap-4">
                <button
                  onClick={() => setFilterType('all')}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    filterType === 'all'
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  All Policies ({policies.length})
                </button>
                <button
                  onClick={() => setFilterType('row_level')}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    filterType === 'row_level'
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Row-Level Security ({policies.filter(p => p.policy_type === 'row_level').length})
                </button>
                <button
                  onClick={() => setFilterType('column_level')}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    filterType === 'column_level'
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Column-Level Security ({policies.filter(p => p.policy_type === 'column_level').length})
                </button>
              </div>
            </div>

            {/* Policies List */}
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
              </div>
            ) : filteredPolicies.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm p-12 text-center">
                <Shield className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  No security policies yet
                </h3>
                <p className="text-gray-600 mb-6">
                  Create your first security policy to protect sensitive data
                </p>
                <button
                  onClick={() => setShowCreatePolicyModal(true)}
                  className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
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
                          <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                            Priority: {policy.priority}
                          </span>
                        </div>
                        <p className="text-gray-600 mb-3">{policy.description}</p>
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          <span>Created: {new Date(policy.created_at).toLocaleDateString()}</span>
                          {policy.applies_to && policy.applies_to.length > 0 && (
                            <span>Applies to: {policy.applies_to.join(', ')}</span>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => {
                            setSelectedPolicy(policy);
                            setShowTestPolicyModal(true);
                          }}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          title="Test Policy"
                          data-testid={`test-policy-${policy.id}`}
                        >
                          <PlayCircle className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => handleTogglePolicy(policy)}
                          className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                          title={policy.is_active ? 'Disable' : 'Enable'}
                          data-testid={`toggle-policy-${policy.id}`}
                        >
                          {policy.is_active ? (
                            <Eye className="w-5 h-5" />
                          ) : (
                            <EyeOff className="w-5 h-5" />
                          )}
                        </button>
                        <button
                          onClick={() => {
                            setSelectedPolicy(policy);
                            setPolicyForm({
                              name: policy.name,
                              description: policy.description,
                              policy_type: policy.policy_type,
                              rules: policy.rules,
                              priority: policy.priority,
                              applies_to: policy.applies_to
                            });
                            setShowEditPolicyModal(true);
                          }}
                          className="p-2 text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                          title="Edit"
                          data-testid={`edit-policy-${policy.id}`}
                        >
                          <Edit2 className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => handleDeletePolicy(policy.id)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Delete"
                          data-testid={`delete-policy-${policy.id}`}
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {/* Masking Rules Tab */}
        {activeTab === 'masking' && (
          <>
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
              </div>
            ) : maskingRules.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm p-12 text-center">
                <Shield className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  No masking rules yet
                </h3>
                <p className="text-gray-600 mb-6">
                  Create masking rules to protect PII data
                </p>
                <button
                  onClick={() => setShowCreateMaskingModal(true)}
                  className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                >
                  Create Masking Rule
                </button>
              </div>
            ) : (
              <div className="grid gap-4">
                {maskingRules.map((rule) => (
                  <div
                    key={rule.id}
                    className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow"
                    data-testid={`masking-rule-${rule.id}`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-xl font-semibold text-gray-900">
                            {rule.name}
                          </h3>
                          <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                            {rule.data_type}
                          </span>
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-medium ${
                              rule.is_active
                                ? 'bg-green-100 text-green-700'
                                : 'bg-gray-100 text-gray-700'
                            }`}
                          >
                            {rule.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </div>
                        <p className="text-gray-600 mb-2">{rule.description}</p>
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          <span>Pattern: <code className="bg-gray-100 px-2 py-1 rounded">{rule.masking_pattern}</code></span>
                          <span>Created: {new Date(rule.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleDeleteMaskingRule(rule.id)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Delete"
                          data-testid={`delete-masking-${rule.id}`}
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {/* Create Policy Modal */}
        {showCreatePolicyModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" data-testid="create-policy-modal">
            <div className="bg-white rounded-lg p-8 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Create Security Policy</h2>
                <button onClick={() => { setShowCreatePolicyModal(false); resetPolicyForm(); }} className="p-2 hover:bg-gray-100 rounded-lg">
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-6">
                {/* Basic Info */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Policy Name *</label>
                  <input
                    type="text"
                    value={policyForm.name}
                    onChange={(e) => setPolicyForm({ ...policyForm, name: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                    placeholder="e.g., Customer Data Access Policy"
                    data-testid="policy-name-input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <textarea
                    value={policyForm.description}
                    onChange={(e) => setPolicyForm({ ...policyForm, description: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                    rows={3}
                    placeholder="Describe what this policy does"
                    data-testid="policy-description-input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Policy Type *</label>
                  <select
                    value={policyForm.policy_type}
                    onChange={(e) => setPolicyForm({ ...policyForm, policy_type: e.target.value as 'row_level' | 'column_level' })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                    data-testid="policy-type-select"
                  >
                    <option value="row_level">Row-Level Security (RLS)</option>
                    <option value="column_level">Column-Level Security (CLS)</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Priority</label>
                    <input
                      type="number"
                      value={policyForm.priority}
                      onChange={(e) => setPolicyForm({ ...policyForm, priority: parseInt(e.target.value) })}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                      min="1"
                      data-testid="policy-priority-input"
                    />
                  </div>
                </div>

                {/* Rule Builder */}
                {policyForm.policy_type === 'row_level' ? (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">Row Filtering Conditions</label>
                    {ruleBuilder.conditions.map((condition, index) => (
                      <div key={index} className="flex gap-2 mb-2">
                        <input
                          type="text"
                          value={condition.field}
                          onChange={(e) => updateCondition(index, 'field', e.target.value)}
                          className="flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                          placeholder="Field name"
                        />
                        <select
                          value={condition.operator}
                          onChange={(e) => updateCondition(index, 'operator', e.target.value)}
                          className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                        >
                          <option value="=">=</option>
                          <option value="!=">!=</option>
                          <option value=">">{'>'}</option>
                          <option value="<">{'<'}</option>
                          <option value="IN">IN</option>
                        </select>
                        <input
                          type="text"
                          value={condition.value}
                          onChange={(e) => updateCondition(index, 'value', e.target.value)}
                          className="flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                          placeholder="Value"
                        />
                        <button
                          onClick={() => removeCondition(index)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                          disabled={ruleBuilder.conditions.length === 1}
                        >
                          <X className="w-5 h-5" />
                        </button>
                      </div>
                    ))}
                    <button
                      onClick={addCondition}
                      className="mt-2 px-4 py-2 text-purple-600 hover:bg-purple-50 rounded-lg"
                    >
                      + Add Condition
                    </button>
                  </div>
                ) : (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Columns to Mask/Hide</label>
                    <input
                      type="text"
                      value={ruleBuilder.columns.join(', ')}
                      onChange={(e) => setRuleBuilder({ ...ruleBuilder, columns: e.target.value.split(',').map(c => c.trim()) })}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                      placeholder="email, ssn, credit_card (comma separated)"
                    />
                    <label className="block text-sm font-medium text-gray-700 mt-4 mb-2">Masking Type</label>
                    <select
                      value={ruleBuilder.maskingType}
                      onChange={(e) => setRuleBuilder({ ...ruleBuilder, maskingType: e.target.value })}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="hide">Hide Column</option>
                      <option value="mask">Mask Data</option>
                      <option value="redact">Redact</option>
                    </select>
                  </div>
                )}
              </div>

              <div className="flex gap-3 mt-8">
                <button
                  onClick={handleCreatePolicy}
                  className="flex-1 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center justify-center gap-2"
                  data-testid="save-policy-button"
                >
                  <Save className="w-5 h-5" />
                  Create Policy
                </button>
                <button
                  onClick={() => { setShowCreatePolicyModal(false); resetPolicyForm(); }}
                  className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Test Policy Modal */}
        {showTestPolicyModal && selectedPolicy && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" data-testid="test-policy-modal">
            <div className="bg-white rounded-lg p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Test Policy: {selectedPolicy.name}</h2>
                <button onClick={() => { setShowTestPolicyModal(false); setTestResult(null); }} className="p-2 hover:bg-gray-100 rounded-lg">
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">User Role</label>
                  <select
                    value={testData.user_role}
                    onChange={(e) => setTestData({ ...testData, user_role: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="admin">Admin</option>
                    <option value="editor">Editor</option>
                    <option value="viewer">Viewer</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">User ID (optional)</label>
                  <input
                    type="text"
                    value={testData.user_id}
                    onChange={(e) => setTestData({ ...testData, user_id: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                    placeholder="test-user-123"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Sample Data (JSON)</label>
                  <textarea
                    value={testData.sample_data}
                    onChange={(e) => setTestData({ ...testData, sample_data: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 font-mono text-sm"
                    rows={6}
                    placeholder='{"id": 1, "email": "user@example.com"}'
                  />
                </div>

                <button
                  onClick={handleTestPolicy}
                  className="w-full px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center justify-center gap-2"
                >
                  <PlayCircle className="w-5 h-5" />
                  Run Test
                </button>

                {testResult && (
                  <div className={`p-4 rounded-lg ${
                    testResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                  }`}>
                    <div className="flex items-center gap-2 mb-2">
                      {testResult.success ? (
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      ) : (
                        <AlertCircle className="w-5 h-5 text-red-600" />
                      )}
                      <span className={`font-medium ${
                        testResult.success ? 'text-green-900' : 'text-red-900'
                      }`}>
                        {testResult.success ? 'Policy Test Passed' : 'Policy Test Failed'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700">{testResult.message}</p>
                    {testResult.filtered_data && (
                      <pre className="mt-3 p-3 bg-white rounded text-xs overflow-x-auto">
                        {JSON.stringify(testResult.filtered_data, null, 2)}
                      </pre>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Create Masking Rule Modal */}
        {showCreateMaskingModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" data-testid="create-masking-modal">
            <div className="bg-white rounded-lg p-8 max-w-2xl w-full">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Create Data Masking Rule</h2>
                <button onClick={() => { setShowCreateMaskingModal(false); resetMaskingForm(); }} className="p-2 hover:bg-gray-100 rounded-lg">
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Rule Name *</label>
                  <input
                    type="text"
                    value={maskingForm.name}
                    onChange={(e) => setMaskingForm({ ...maskingForm, name: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                    placeholder="e.g., Email Masking"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <textarea
                    value={maskingForm.description}
                    onChange={(e) => setMaskingForm({ ...maskingForm, description: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                    rows={3}
                    placeholder="Describe the masking rule"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Data Type *</label>
                  <select
                    value={maskingForm.data_type}
                    onChange={(e) => setMaskingForm({ ...maskingForm, data_type: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="email">Email</option>
                    <option value="phone">Phone Number</option>
                    <option value="ssn">Social Security Number</option>
                    <option value="credit_card">Credit Card</option>
                    <option value="custom">Custom</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Masking Pattern *</label>
                  <input
                    type="text"
                    value={maskingForm.masking_pattern}
                    onChange={(e) => setMaskingForm({ ...maskingForm, masking_pattern: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                    placeholder="*** or XXXXX"
                  />
                  <p className="text-xs text-gray-500 mt-1">Pattern to replace sensitive data</p>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleCreateMaskingRule}
                  className="flex-1 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                >
                  Create Rule
                </button>
                <button
                  onClick={() => { setShowCreateMaskingModal(false); resetMaskingForm(); }}
                  className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SecurityPoliciesPage;
