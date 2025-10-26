import React, { useState, useEffect } from 'react';
import { Key, Plus, Edit2, Trash2, Settings, CheckCircle, XCircle, Github, Mail, Globe, Server, AlertCircle, Copy, Eye, EyeOff } from 'lucide-react';
import ssoService, { OAuthProvider, SAMLConfig, LDAPConfig, CreateOAuthProviderRequest, CreateSAMLConfigRequest, CreateLDAPConfigRequest } from '../services/ssoService';

const SSOConfigPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'oauth' | 'saml' | 'ldap'>('oauth');
  const [providers, setProviders] = useState<OAuthProvider[]>([]);
  const [samlConfig, setSamlConfig] = useState<SAMLConfig | null>(null);
  const [ldapConfig, setLDAPConfig] = useState<LDAPConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCreateOAuthModal, setShowCreateOAuthModal] = useState(false);
  const [showEditOAuthModal, setShowEditOAuthModal] = useState(false);
  const [showSAMLModal, setShowSAMLModal] = useState(false);
  const [showLDAPModal, setShowLDAPModal] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<OAuthProvider | null>(null);
  const [testResult, setTestResult] = useState<any>(null);
  const [showSecret, setShowSecret] = useState(false);

  // Form states
  const [oauthForm, setOauthForm] = useState<CreateOAuthProviderRequest>({
    provider_name: 'google',
    display_name: '',
    client_id: '',
    client_secret: '',
    scopes: ['openid', 'email', 'profile']
  });

  const [samlForm, setSamlForm] = useState<CreateSAMLConfigRequest>({
    idp_entity_id: '',
    sso_url: '',
    x509_cert: '',
    name_id_format: 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress'
  });

  const [ldapForm, setLdapForm] = useState<CreateLDAPConfigRequest>({
    server_url: '',
    bind_dn: '',
    bind_password: '',
    search_base: '',
    user_filter: '(uid={username})'
  });

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    try {
      setLoading(true);
      if (activeTab === 'oauth') {
        const data = await ssoService.getProviders();
        setProviders(data);
      } else if (activeTab === 'saml') {
        try {
          const data = await ssoService.getSAMLConfig();
          setSamlConfig(data);
        } catch (error) {
          setSamlConfig(null);
        }
      } else if (activeTab === 'ldap') {
        try {
          const data = await ssoService.getLDAPConfig();
          setLDAPConfig(data);
        } catch (error) {
          setLDAPConfig(null);
        }
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOAuthProvider = async () => {
    try {
      await ssoService.createProvider(oauthForm);
      setShowCreateOAuthModal(false);
      resetOAuthForm();
      fetchData();
    } catch (error) {
      console.error('Failed to create provider:', error);
      alert('Failed to create OAuth provider');
    }
  };

  const handleUpdateProvider = async () => {
    if (!selectedProvider) return;
    try {
      await ssoService.updateProvider(selectedProvider.id, {
        display_name: oauthForm.display_name,
        client_id: oauthForm.client_id,
        scopes: oauthForm.scopes
      });
      setShowEditOAuthModal(false);
      setSelectedProvider(null);
      resetOAuthForm();
      fetchData();
    } catch (error) {
      console.error('Failed to update provider:', error);
      alert('Failed to update provider');
    }
  };

  const handleDeleteProvider = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this OAuth provider?')) return;
    try {
      await ssoService.deleteProvider(id);
      fetchData();
    } catch (error) {
      console.error('Failed to delete provider:', error);
      alert('Failed to delete provider');
    }
  };

  const handleToggleProvider = async (provider: OAuthProvider) => {
    try {
      await ssoService.updateProvider(provider.id, {
        is_enabled: !provider.is_enabled
      });
      fetchData();
    } catch (error) {
      console.error('Failed to toggle provider:', error);
    }
  };

  const handleCreateSAML = async () => {
    try {
      await ssoService.createSAMLConfig(samlForm);
      setShowSAMLModal(false);
      fetchData();
    } catch (error) {
      console.error('Failed to create SAML config:', error);
      alert('Failed to create SAML configuration');
    }
  };

  const handleCreateLDAP = async () => {
    try {
      await ssoService.createLDAPConfig(ldapForm);
      setShowLDAPModal(false);
      fetchData();
    } catch (error) {
      console.error('Failed to create LDAP config:', error);
      alert('Failed to create LDAP configuration');
    }
  };

  const handleTestLDAP = async () => {
    try {
      const result = await ssoService.testLDAPConnection();
      setTestResult(result);
    } catch (error) {
      console.error('Failed to test LDAP:', error);
      setTestResult({ success: false, message: 'Connection test failed' });
    }
  };

  const handleSyncLDAP = async () => {
    try {
      const result = await ssoService.syncLDAPUsers();
      alert(`Successfully synced ${result.synced_count} users`);
    } catch (error) {
      console.error('Failed to sync users:', error);
      alert('Failed to sync LDAP users');
    }
  };

  const resetOAuthForm = () => {
    setOauthForm({
      provider_name: 'google',
      display_name: '',
      client_id: '',
      client_secret: '',
      scopes: ['openid', 'email', 'profile']
    });
  };

  const getProviderIcon = (name: string) => {
    switch (name.toLowerCase()) {
      case 'google':
        return <Mail className="w-6 h-6 text-red-500" />;
      case 'github':
        return <Github className="w-6 h-6 text-gray-800" />;
      case 'microsoft':
        return <Globe className="w-6 h-6 text-blue-500" />;
      default:
        return <Key className="w-6 h-6 text-gray-500" />;
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3" data-testid="page-title">
            <Key className="w-8 h-8 text-blue-600" />
            Single Sign-On (SSO)
          </h1>
          <p className="text-gray-600 mt-2">
            Configure OAuth 2.0, SAML 2.0, and LDAP/Active Directory authentication
          </p>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('oauth')}
              className={`px-6 py-4 font-medium transition-colors ${
                activeTab === 'oauth'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
              data-testid="oauth-tab"
            >
              OAuth 2.0
            </button>
            <button
              onClick={() => setActiveTab('saml')}
              className={`px-6 py-4 font-medium transition-colors ${
                activeTab === 'saml'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
              data-testid="saml-tab"
            >
              SAML 2.0
            </button>
            <button
              onClick={() => setActiveTab('ldap')}
              className={`px-6 py-4 font-medium transition-colors ${
                activeTab === 'ldap'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
              data-testid="ldap-tab"
            >
              LDAP / Active Directory
            </button>
          </div>
        </div>

        {/* OAuth Tab */}
        {activeTab === 'oauth' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">OAuth 2.0 Providers</h2>
              <button
                onClick={() => setShowCreateOAuthModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                data-testid="add-oauth-provider"
              >
                <Plus className="w-5 h-5" />
                Add OAuth Provider
              </button>
            </div>

            {loading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : providers.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm p-12 text-center">
                <Key className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  No OAuth providers configured
                </h3>
                <p className="text-gray-600 mb-6">
                  Add OAuth providers like Google, Microsoft, or GitHub for single sign-on
                </p>
                <button
                  onClick={() => setShowCreateOAuthModal(true)}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Add Provider
                </button>
              </div>
            ) : (
              <div className="grid gap-4">
                {providers.map((provider) => (
                  <div
                    key={provider.id}
                    className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow"
                    data-testid={`provider-${provider.provider_name}`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 flex-1">
                        {getProviderIcon(provider.provider_name)}
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-1">
                            <h3 className="text-lg font-semibold text-gray-900">
                              {provider.display_name}
                            </h3>
                            <span
                              className={`px-3 py-1 rounded-full text-xs font-medium ${
                                provider.is_enabled
                                  ? 'bg-green-100 text-green-700'
                                  : 'bg-gray-100 text-gray-700'
                              }`}
                            >
                              {provider.is_enabled ? 'Enabled' : 'Disabled'}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mb-2">
                            Provider: {provider.provider_name}
                          </p>
                          <div className="flex items-center gap-4 text-xs text-gray-500">
                            <span>Client ID: {provider.client_id.substring(0, 20)}...</span>
                            <span>Scopes: {provider.scopes.join(', ')}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleToggleProvider(provider)}
                          className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                          title={provider.is_enabled ? 'Disable' : 'Enable'}
                          data-testid={`toggle-${provider.id}`}
                        >
                          {provider.is_enabled ? <Eye className="w-5 h-5" /> : <EyeOff className="w-5 h-5" />}
                        </button>
                        <button
                          onClick={() => {
                            setSelectedProvider(provider);
                            setOauthForm({
                              provider_name: provider.provider_name,
                              display_name: provider.display_name,
                              client_id: provider.client_id,
                              client_secret: '',
                              scopes: provider.scopes
                            });
                            setShowEditOAuthModal(true);
                          }}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          data-testid={`edit-${provider.id}`}
                        >
                          <Edit2 className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => handleDeleteProvider(provider.id)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          data-testid={`delete-${provider.id}`}
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
        )}

        {/* SAML Tab */}
        {activeTab === 'saml' && (
          <div className="bg-white rounded-lg shadow-sm p-8">
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : samlConfig ? (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">SAML 2.0 Configuration</h2>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      samlConfig.is_enabled
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {samlConfig.is_enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>

                <div className="space-y-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <label className="block text-sm font-medium text-gray-700 mb-1">IdP Entity ID</label>
                    <p className="text-gray-900">{samlConfig.idp_entity_id}</p>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-lg">
                    <label className="block text-sm font-medium text-gray-700 mb-1">SSO URL</label>
                    <p className="text-gray-900">{samlConfig.sso_url}</p>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-lg">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Name ID Format</label>
                    <p className="text-gray-900">{samlConfig.name_id_format}</p>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-lg">
                    <label className="block text-sm font-medium text-gray-700 mb-1">X.509 Certificate</label>
                    <pre className="text-xs text-gray-900 bg-white p-2 rounded border overflow-x-auto">
                      {samlConfig.x509_cert}
                    </pre>
                  </div>

                  <button
                    onClick={() => setShowSAMLModal(true)}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Update Configuration
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <Server className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  SAML 2.0 Not Configured
                </h3>
                <p className="text-gray-600 mb-6">
                  Configure SAML 2.0 for enterprise identity providers like Okta, Azure AD, or OneLogin
                </p>
                <button
                  onClick={() => setShowSAMLModal(true)}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  data-testid="configure-saml-button"
                >
                  Configure SAML 2.0
                </button>
              </div>
            )}
          </div>
        )}

        {/* LDAP Tab */}
        {activeTab === 'ldap' && (
          <div className="bg-white rounded-lg shadow-sm p-8">
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : ldapConfig ? (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">LDAP / Active Directory Configuration</h2>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      ldapConfig.is_enabled
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {ldapConfig.is_enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>

                <div className="space-y-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Server URL</label>
                    <p className="text-gray-900">{ldapConfig.server_url}</p>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-lg">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Bind DN</label>
                    <p className="text-gray-900">{ldapConfig.bind_dn}</p>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-lg">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Search Base</label>
                    <p className="text-gray-900">{ldapConfig.search_base}</p>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-lg">
                    <label className="block text-sm font-medium text-gray-700 mb-1">User Filter</label>
                    <p className="text-gray-900 font-mono text-sm">{ldapConfig.user_filter}</p>
                  </div>

                  <div className="flex gap-3">
                    <button
                      onClick={handleTestLDAP}
                      className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
                      data-testid="test-ldap-button"
                    >
                      <CheckCircle className="w-5 h-5" />
                      Test Connection
                    </button>
                    <button
                      onClick={handleSyncLDAP}
                      className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                      data-testid="sync-ldap-button"
                    >
                      Sync Users
                    </button>
                    <button
                      onClick={() => setShowLDAPModal(true)}
                      className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      Update Configuration
                    </button>
                  </div>

                  {testResult && (
                    <div
                      className={`p-4 rounded-lg ${
                        testResult.success
                          ? 'bg-green-50 border border-green-200'
                          : 'bg-red-50 border border-red-200'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        {testResult.success ? (
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        ) : (
                          <XCircle className="w-5 h-5 text-red-600" />
                        )}
                        <span
                          className={`font-medium ${
                            testResult.success ? 'text-green-900' : 'text-red-900'
                          }`}
                        >
                          {testResult.message}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <Server className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  LDAP / Active Directory Not Configured
                </h3>
                <p className="text-gray-600 mb-6">
                  Configure LDAP or Active Directory for user authentication and synchronization
                </p>
                <button
                  onClick={() => setShowLDAPModal(true)}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  data-testid="configure-ldap-button"
                >
                  Configure LDAP / AD
                </button>
              </div>
            )}
          </div>
        )}

        {/* Create OAuth Provider Modal */}
        {showCreateOAuthModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" data-testid="create-oauth-modal">
            <div className="bg-white rounded-lg p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Add OAuth 2.0 Provider</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Provider *</label>
                  <select
                    value={oauthForm.provider_name}
                    onChange={(e) => setOauthForm({ ...oauthForm, provider_name: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    data-testid="provider-select"
                  >
                    <option value="google">Google</option>
                    <option value="github">GitHub</option>
                    <option value="microsoft">Microsoft</option>
                    <option value="okta">Okta</option>
                    <option value="custom">Custom OAuth Provider</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Display Name *</label>
                  <input
                    type="text"
                    value={oauthForm.display_name}
                    onChange={(e) => setOauthForm({ ...oauthForm, display_name: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Google Workspace"
                    data-testid="display-name-input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Client ID *</label>
                  <input
                    type="text"
                    value={oauthForm.client_id}
                    onChange={(e) => setOauthForm({ ...oauthForm, client_id: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Client ID from OAuth provider"
                    data-testid="client-id-input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Client Secret *</label>
                  <div className="relative">
                    <input
                      type={showSecret ? 'text' : 'password'}
                      value={oauthForm.client_secret}
                      onChange={(e) => setOauthForm({ ...oauthForm, client_secret: e.target.value })}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="Client Secret from OAuth provider"
                      data-testid="client-secret-input"
                    />
                    <button
                      type="button"
                      onClick={() => setShowSecret(!showSecret)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                    >
                      {showSecret ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Scopes</label>
                  <input
                    type="text"
                    value={oauthForm.scopes?.join(', ')}
                    onChange={(e) =>
                      setOauthForm({
                        ...oauthForm,
                        scopes: e.target.value.split(',').map((s) => s.trim())
                      })
                    }
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="openid, email, profile"
                  />
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-blue-900">
                      <p className="font-medium mb-1">Callback URL</p>
                      <p className="mb-2">Configure this URL in your OAuth provider:</p>
                      <div className="flex items-center gap-2 bg-white p-2 rounded border border-blue-200">
                        <code className="text-xs flex-1">https://yourdomain.com/api/sso/oauth/callback</code>
                        <button
                          onClick={() => copyToClipboard('https://yourdomain.com/api/sso/oauth/callback')}
                          className="p-1 hover:bg-blue-50 rounded"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleCreateOAuthProvider}
                  className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  data-testid="save-oauth-button"
                >
                  Add Provider
                </button>
                <button
                  onClick={() => {
                    setShowCreateOAuthModal(false);
                    resetOAuthForm();
                  }}
                  className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* SAML Configuration Modal */}
        {showSAMLModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" data-testid="saml-modal">
            <div className="bg-white rounded-lg p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Configure SAML 2.0</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">IdP Entity ID *</label>
                  <input
                    type="text"
                    value={samlForm.idp_entity_id}
                    onChange={(e) => setSamlForm({ ...samlForm, idp_entity_id: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="https://idp.example.com/entity-id"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">SSO URL *</label>
                  <input
                    type="text"
                    value={samlForm.sso_url}
                    onChange={(e) => setSamlForm({ ...samlForm, sso_url: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="https://idp.example.com/sso"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">X.509 Certificate *</label>
                  <textarea
                    value={samlForm.x509_cert}
                    onChange={(e) => setSamlForm({ ...samlForm, x509_cert: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                    rows={6}
                    placeholder="-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Name ID Format</label>
                  <select
                    value={samlForm.name_id_format}
                    onChange={(e) => setSamlForm({ ...samlForm, name_id_format: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress">Email Address</option>
                    <option value="urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified">Unspecified</option>
                    <option value="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent">Persistent</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleCreateSAML}
                  className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Save Configuration
                </button>
                <button
                  onClick={() => setShowSAMLModal(false)}
                  className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* LDAP Configuration Modal */}
        {showLDAPModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" data-testid="ldap-modal">
            <div className="bg-white rounded-lg p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Configure LDAP / Active Directory</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Server URL *</label>
                  <input
                    type="text"
                    value={ldapForm.server_url}
                    onChange={(e) => setLdapForm({ ...ldapForm, server_url: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="ldap://ldap.example.com:389 or ldaps://ldap.example.com:636"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Bind DN *</label>
                  <input
                    type="text"
                    value={ldapForm.bind_dn}
                    onChange={(e) => setLdapForm({ ...ldapForm, bind_dn: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="CN=admin,DC=example,DC=com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Bind Password *</label>
                  <input
                    type="password"
                    value={ldapForm.bind_password}
                    onChange={(e) => setLdapForm({ ...ldapForm, bind_password: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="••••••••"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Search Base *</label>
                  <input
                    type="text"
                    value={ldapForm.search_base}
                    onChange={(e) => setLdapForm({ ...ldapForm, search_base: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="OU=Users,DC=example,DC=com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">User Filter</label>
                  <input
                    type="text"
                    value={ldapForm.user_filter}
                    onChange={(e) => setLdapForm({ ...ldapForm, user_filter: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                    placeholder="(uid={username})"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleCreateLDAP}
                  className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Save Configuration
                </button>
                <button
                  onClick={() => setShowLDAPModal(false)}
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

export default SSOConfigPage;
