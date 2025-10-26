import React, { useState, useEffect } from 'react';
import { Key, Github, Mail, Globe, Plus, Settings } from 'lucide-react';
import api from '../services/api';

interface OAuthProvider {
  id: string;
  provider_name: string;
  display_name: string;
  is_enabled: boolean;
  created_at: string;
}

const SSOConfigPage: React.FC = () => {
  const [providers, setProviders] = useState<OAuthProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'oauth' | 'saml' | 'ldap'>('oauth');

  useEffect(() => {
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/sso/providers');
      setProviders(response.data);
    } catch (error) {
      console.error('Failed to fetch providers:', error);
    } finally {
      setLoading(false);
    }
  };

  const getProviderIcon = (name: string) => {
    switch (name) {
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

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Key className="w-8 h-8 text-blue-600" />
            Single Sign-On (SSO)
          </h1>
          <p className="text-gray-600 mt-2">
            Configure OAuth, SAML, and LDAP authentication
          </p>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('oauth')}
              className={`px-6 py-4 font-medium ${
                activeTab === 'oauth'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              OAuth 2.0
            </button>
            <button
              onClick={() => setActiveTab('saml')}
              className={`px-6 py-4 font-medium ${
                activeTab === 'saml'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              SAML 2.0
            </button>
            <button
              onClick={() => setActiveTab('ldap')}
              className={`px-6 py-4 font-medium ${
                activeTab === 'ldap'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              LDAP / AD
            </button>
          </div>
        </div>

        {/* OAuth Tab */}
        {activeTab === 'oauth' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">OAuth Providers</h2>
              <button
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                data-testid="add-oauth-provider"
              >
                <Plus className="w-5 h-5" />
                Add Provider
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
                  Add OAuth providers like Google, Microsoft, or GitHub
                </p>
              </div>
            ) : (
              <div className="grid gap-4">
                {providers.map((provider) => (
                  <div
                    key={provider.id}
                    className="bg-white rounded-lg shadow-sm p-6 flex items-center justify-between"
                    data-testid={`provider-${provider.provider_name}`}
                  >
                    <div className="flex items-center gap-4">
                      {getProviderIcon(provider.provider_name)}
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {provider.display_name}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {provider.provider_name}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-medium ${
                          provider.is_enabled
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {provider.is_enabled ? 'Enabled' : 'Disabled'}
                      </span>
                      <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg">
                        <Settings className="w-5 h-5" />
                      </button>
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
            <h2 className="text-xl font-semibold text-gray-900 mb-4">SAML 2.0 Configuration</h2>
            <p className="text-gray-600 mb-6">
              Configure SAML 2.0 for enterprise identity providers
            </p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  IdP Entity ID
                </label>
                <input
                  type="text"
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="https://idp.example.com/entity-id"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  SSO URL
                </label>
                <input
                  type="text"
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="https://idp.example.com/sso"
                />
              </div>
              <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                Save Configuration
              </button>
            </div>
          </div>
        )}

        {/* LDAP Tab */}
        {activeTab === 'ldap' && (
          <div className="bg-white rounded-lg shadow-sm p-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">LDAP / Active Directory</h2>
            <p className="text-gray-600 mb-6">
              Configure LDAP or Active Directory authentication
            </p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Server URL
                </label>
                <input
                  type="text"
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="ldap://ldap.example.com:389"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Bind DN
                </label>
                <input
                  type="text"
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="CN=admin,DC=example,DC=com"
                />
              </div>
              <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                Test Connection
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SSOConfigPage;