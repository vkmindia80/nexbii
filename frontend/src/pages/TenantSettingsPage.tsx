/**
 * Tenant Settings Page
 * Manage tenant branding, custom domains, and SSL certificates
 */

import React, { useState, useEffect } from 'react';
import {
  Building2, Palette, Globe, Lock, Save, Plus, Check, X, AlertCircle,
  Upload, RefreshCw, Copy, ExternalLink, Shield
} from 'lucide-react';
import tenantService, { Tenant, TenantBranding, TenantDomain } from '../services/tenantService';
import BrandingPreview from '../components/BrandingPreview';

const TenantSettingsPage: React.FC = () => {
  const [tenant, setTenant] = useState<Tenant | null>(null);
  const [branding, setBranding] = useState<TenantBranding>({});
  const [domains, setDomains] = useState<TenantDomain[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'branding' | 'domains' | 'ssl'>('branding');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // New domain form
  const [newDomain, setNewDomain] = useState('');
  const [addingDomain, setAddingDomain] = useState(false);

  // SSL upload form
  const [selectedDomainId, setSelectedDomainId] = useState<string | null>(null);
  const [sslMethod, setSSLMethod] = useState<'upload' | 'letsencrypt'>('upload');
  const [certificatePem, setCertificatePem] = useState('');
  const [privateKeyPem, setPrivateKeyPem] = useState('');
  const [chainPem, setChainPem] = useState('');
  const [letsEncryptEmail, setLetsEncryptEmail] = useState('');

  useEffect(() => {
    loadTenantData();
  }, []);

  const loadTenantData = async () => {
    try {
      const currentTenant = await tenantService.getCurrentTenant();
      console.log('Loaded tenant:', currentTenant);
      setTenant(currentTenant);
      
      // Initialize branding with default values if empty
      const initialBranding = currentTenant.branding && Object.keys(currentTenant.branding).length > 0
        ? currentTenant.branding
        : {
            primary_color: '#667eea',
            secondary_color: '#764ba2',
            accent_color: '#3b82f6',
            font_family: 'Inter, sans-serif'
          };
      setBranding(initialBranding);
      
      const tenantDomains = await tenantService.listCustomDomains(currentTenant.id);
      console.log('Loaded domains:', tenantDomains);
      setDomains(tenantDomains);
    } catch (error) {
      console.error('Failed to load tenant data:', error);
      showMessage('error', `Failed to load tenant settings: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const handleSaveBranding = async () => {
    if (!tenant) return;

    setSaving(true);
    try {
      const updated = await tenantService.updateBranding(tenant.id, branding);
      setTenant(updated);
      tenantService.applyTenantBranding(branding);
      tenantService.saveTenantBrandingToStorage(branding);
      showMessage('success', 'Branding updated successfully!');
    } catch (error) {
      showMessage('error', 'Failed to update branding');
    } finally {
      setSaving(false);
    }
  };

  const handleAddDomain = async () => {
    if (!tenant || !newDomain.trim()) return;

    setAddingDomain(true);
    try {
      const domain = await tenantService.addCustomDomain(tenant.id, newDomain.trim());
      setDomains([...domains, domain]);
      setNewDomain('');
      showMessage('success', `Domain ${domain.domain} added! Please verify ownership.`);
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to add domain');
    } finally {
      setAddingDomain(false);
    }
  };

  const handleVerifyDomain = async (domainId: string) => {
    if (!tenant) return;

    try {
      const result = await tenantService.verifyDomain(tenant.id, domainId);
      if (result.success) {
        // Reload domains
        const updated = await tenantService.listCustomDomains(tenant.id);
        setDomains(updated);
        showMessage('success', result.message);
      } else {
        showMessage('error', result.message || 'Verification failed');
      }
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Verification failed');
    }
  };

  const handleUploadSSL = async () => {
    if (!tenant || !selectedDomainId) return;

    setSaving(true);
    try {
      const result = await tenantService.uploadSSLCertificate(
        tenant.id,
        selectedDomainId,
        certificatePem,
        privateKeyPem,
        chainPem || undefined
      );
      
      if (result.success) {
        showMessage('success', 'SSL certificate uploaded successfully!');
        // Reload domains
        const updated = await tenantService.listCustomDomains(tenant.id);
        setDomains(updated);
        // Clear form
        setCertificatePem('');
        setPrivateKeyPem('');
        setChainPem('');
      } else {
        showMessage('error', result.message || 'SSL upload failed');
      }
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'SSL upload failed');
    } finally {
      setSaving(false);
    }
  };

  const handleRequestLetsEncrypt = async () => {
    if (!tenant || !selectedDomainId || !letsEncryptEmail) return;

    setSaving(true);
    try {
      const result = await tenantService.requestLetsEncrypt(
        tenant.id,
        selectedDomainId,
        letsEncryptEmail,
        false
      );
      
      if (result.success) {
        showMessage('success', 'Let\'s Encrypt certificate obtained successfully!');
        // Reload domains
        const updated = await tenantService.listCustomDomains(tenant.id);
        setDomains(updated);
      } else {
        showMessage('error', result.message || 'Certificate request failed');
      }
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Certificate request failed');
    } finally {
      setSaving(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    showMessage('success', 'Copied to clipboard!');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (!tenant) {
    return (
      <div className="flex flex-col items-center justify-center h-screen space-y-4">
        <Building2 className="w-16 h-16 text-gray-400" />
        <div className="text-center">
          <p className="text-xl font-semibold text-gray-700 dark:text-gray-300">No Tenant Found</p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
            Please log in to access tenant settings
          </p>
        </div>
      </div>
    );
  }

  const hasWhitelabeling = tenant.features?.white_labeling || false;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Tenant Settings
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Manage your organization's branding, custom domains, and SSL certificates
          </p>
        </div>

        {/* Message */}
        {message && (
          <div
            className={`mb-6 p-4 rounded-lg flex items-start space-x-3 ${
              message.type === 'success'
                ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200'
                : 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200'
            }`}
          >
            {message.type === 'success' ? (
              <Check className="w-5 h-5 flex-shrink-0 mt-0.5" />
            ) : (
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            )}
            <p>{message.text}</p>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="flex space-x-8 px-6" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('branding')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'branding'
                    ? 'border-purple-500 text-purple-600 dark:text-purple-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                <Palette className="w-5 h-5 inline mr-2" />
                Branding
              </button>
              <button
                onClick={() => setActiveTab('domains')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'domains'
                    ? 'border-purple-500 text-purple-600 dark:text-purple-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                <Globe className="w-5 h-5 inline mr-2" />
                Custom Domains
              </button>
              <button
                onClick={() => setActiveTab('ssl')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'ssl'
                    ? 'border-purple-500 text-purple-600 dark:text-purple-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                <Lock className="w-5 h-5 inline mr-2" />
                SSL Certificates
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {/* Branding Tab */}
            {activeTab === 'branding' && (
              <div className="space-y-6">
                {!hasWhitelabeling && (
                  <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 mb-4">
                    <div className="flex items-start space-x-3">
                      <Shield className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
                      <div>
                        <h4 className="font-semibold text-yellow-800 dark:text-yellow-200 mb-1">
                          Enterprise Feature
                        </h4>
                        <p className="text-sm text-yellow-700 dark:text-yellow-300">
                          White-labeling features are only available on the Enterprise plan. 
                          Upgrade to customize your branding.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {hasWhitelabeling && Object.keys(tenant.branding || {}).length === 0 && (
                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-4">
                    <div className="flex items-start space-x-3">
                      <Palette className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                      <div>
                        <h4 className="font-semibold text-blue-800 dark:text-blue-200 mb-1">
                          Customize Your Brand
                        </h4>
                        <p className="text-sm text-blue-700 dark:text-blue-300">
                          Get started by adding your company logo, colors, and custom styling below. 
                          Your branding will be applied across the entire platform.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Logo URL (Light Mode)
                    </label>
                    <input
                      type="url"
                      value={branding.logo_url || ''}
                      onChange={(e) => setBranding({ ...branding, logo_url: e.target.value })}
                      placeholder="https://example.com/logo.png"
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                      disabled={!hasWhitelabeling}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Logo URL (Dark Mode)
                    </label>
                    <input
                      type="url"
                      value={branding.logo_dark_url || ''}
                      onChange={(e) => setBranding({ ...branding, logo_dark_url: e.target.value })}
                      placeholder="https://example.com/logo-dark.png"
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                      disabled={!hasWhitelabeling}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Primary Color
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type="color"
                        value={branding.primary_color || '#667eea'}
                        onChange={(e) => setBranding({ ...branding, primary_color: e.target.value })}
                        className="h-10 w-16 rounded border border-gray-300 dark:border-gray-600"
                        disabled={!hasWhitelabeling}
                      />
                      <input
                        type="text"
                        value={branding.primary_color || '#667eea'}
                        onChange={(e) => setBranding({ ...branding, primary_color: e.target.value })}
                        placeholder="#667eea"
                        className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                        disabled={!hasWhitelabeling}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Secondary Color
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type="color"
                        value={branding.secondary_color || '#764ba2'}
                        onChange={(e) => setBranding({ ...branding, secondary_color: e.target.value })}
                        className="h-10 w-16 rounded border border-gray-300 dark:border-gray-600"
                        disabled={!hasWhitelabeling}
                      />
                      <input
                        type="text"
                        value={branding.secondary_color || '#764ba2'}
                        onChange={(e) => setBranding({ ...branding, secondary_color: e.target.value })}
                        placeholder="#764ba2"
                        className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                        disabled={!hasWhitelabeling}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Accent Color
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type="color"
                        value={branding.accent_color || '#3b82f6'}
                        onChange={(e) => setBranding({ ...branding, accent_color: e.target.value })}
                        className="h-10 w-16 rounded border border-gray-300 dark:border-gray-600"
                        disabled={!hasWhitelabeling}
                      />
                      <input
                        type="text"
                        value={branding.accent_color || '#3b82f6'}
                        onChange={(e) => setBranding({ ...branding, accent_color: e.target.value })}
                        placeholder="#3b82f6"
                        className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                        disabled={!hasWhitelabeling}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Font Family
                    </label>
                    <input
                      type="text"
                      value={branding.font_family || ''}
                      onChange={(e) => setBranding({ ...branding, font_family: e.target.value })}
                      placeholder="Arial, sans-serif"
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                      disabled={!hasWhitelabeling}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Favicon URL
                    </label>
                    <input
                      type="url"
                      value={branding.favicon_url || ''}
                      onChange={(e) => setBranding({ ...branding, favicon_url: e.target.value })}
                      placeholder="https://example.com/favicon.ico"
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                      disabled={!hasWhitelabeling}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Custom CSS
                  </label>
                  <textarea
                    value={branding.custom_css || ''}
                    onChange={(e) => setBranding({ ...branding, custom_css: e.target.value })}
                    placeholder="/* Add custom CSS here */"
                    rows={6}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
                    disabled={!hasWhitelabeling}
                  />
                </div>

                <div className="flex justify-end">
                  <button
                    onClick={handleSaveBranding}
                    disabled={saving || !hasWhitelabeling}
                    className="flex items-center space-x-2 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    data-testid="save-branding-button"
                  >
                    {saving ? (
                      <RefreshCw className="w-5 h-5 animate-spin" />
                    ) : (
                      <Save className="w-5 h-5" />
                    )}
                    <span>{saving ? 'Saving...' : 'Save Branding'}</span>
                  </button>
                </div>
              </div>
            )}

            {/* Custom Domains Tab */}
            {activeTab === 'domains' && (
              <div className="space-y-6">
                {!hasWhitelabeling && (
                  <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 mb-4">
                    <div className="flex items-start space-x-3">
                      <Shield className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
                      <div>
                        <h4 className="font-semibold text-yellow-800 dark:text-yellow-200 mb-1">
                          Enterprise Feature
                        </h4>
                        <p className="text-sm text-yellow-700 dark:text-yellow-300">
                          Custom domains are only available on the Enterprise plan.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Add Domain Form */}
                <div className="flex space-x-3">
                  <input
                    type="text"
                    value={newDomain}
                    onChange={(e) => setNewDomain(e.target.value)}
                    placeholder="analytics.yourcompany.com"
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                    disabled={!hasWhitelabeling}
                  />
                  <button
                    onClick={handleAddDomain}
                    disabled={addingDomain || !newDomain.trim() || !hasWhitelabeling}
                    className="flex items-center space-x-2 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <Plus className="w-5 h-5" />
                    <span>{addingDomain ? 'Adding...' : 'Add Domain'}</span>
                  </button>
                </div>

                {/* Domains List */}
                {domains.length === 0 ? (
                  <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                    <Globe className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No custom domains added yet</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {domains.map((domain) => (
                      <div
                        key={domain.id}
                        className="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3">
                              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                                {domain.domain}
                              </h3>
                              {domain.is_verified ? (
                                <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs rounded-full flex items-center space-x-1">
                                  <Check className="w-3 h-3" />
                                  <span>Verified</span>
                                </span>
                              ) : (
                                <span className="px-2 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 text-xs rounded-full">
                                  Pending Verification
                                </span>
                              )}
                              {domain.ssl_enabled && (
                                <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded-full flex items-center space-x-1">
                                  <Lock className="w-3 h-3" />
                                  <span>SSL</span>
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                              Added {new Date(domain.created_at).toLocaleDateString()}
                            </p>
                          </div>
                          {!domain.is_verified && (
                            <button
                              onClick={() => handleVerifyDomain(domain.id)}
                              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                            >
                              <Check className="w-4 h-4" />
                              <span>Verify</span>
                            </button>
                          )}
                        </div>

                        {!domain.is_verified && (
                          <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 space-y-3">
                            <h4 className="font-semibold text-gray-900 dark:text-white text-sm">
                              {domain.verification_method.toUpperCase()} Verification
                            </h4>
                            <div className="space-y-2 text-sm">
                              {domain.verification_method === 'cname' && (
                                <>
                                  <div>
                                    <span className="text-gray-600 dark:text-gray-400">Host:</span>
                                    <div className="flex items-center space-x-2 mt-1">
                                      <code className="flex-1 px-3 py-2 bg-white dark:bg-gray-800 rounded border border-gray-300 dark:border-gray-600">
                                        {domain.domain}
                                      </code>
                                      <button
                                        onClick={() => copyToClipboard(domain.domain)}
                                        className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                                      >
                                        <Copy className="w-4 h-4" />
                                      </button>
                                    </div>
                                  </div>
                                  <div>
                                    <span className="text-gray-600 dark:text-gray-400">Points to:</span>
                                    <div className="flex items-center space-x-2 mt-1">
                                      <code className="flex-1 px-3 py-2 bg-white dark:bg-gray-800 rounded border border-gray-300 dark:border-gray-600">
                                        verify-{domain.verification_token.substring(0, 12)}....nexbii.com
                                      </code>
                                      <button
                                        onClick={() => copyToClipboard(`verify-${domain.verification_token}.nexbii.com`)}
                                        className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                                      >
                                        <Copy className="w-4 h-4" />
                                      </button>
                                    </div>
                                  </div>
                                </>
                              )}
                              {domain.verification_method === 'txt' && (
                                <div>
                                  <span className="text-gray-600 dark:text-gray-400">TXT Record:</span>
                                  <div className="flex items-center space-x-2 mt-1">
                                    <code className="flex-1 px-3 py-2 bg-white dark:bg-gray-800 rounded border border-gray-300 dark:border-gray-600">
                                      nexbii-verification={domain.verification_token}
                                    </code>
                                    <button
                                      onClick={() => copyToClipboard(`nexbii-verification=${domain.verification_token}`)}
                                      className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                                    >
                                      <Copy className="w-4 h-4" />
                                    </button>
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* SSL Certificates Tab */}
            {activeTab === 'ssl' && (
              <div className="space-y-6">
                {!hasWhitelabeling && (
                  <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 mb-4">
                    <div className="flex items-start space-x-3">
                      <Shield className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
                      <div>
                        <h4 className="font-semibold text-yellow-800 dark:text-yellow-200 mb-1">
                          Enterprise Feature
                        </h4>
                        <p className="text-sm text-yellow-700 dark:text-yellow-300">
                          SSL certificate management is only available on the Enterprise plan.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {domains.filter(d => d.is_verified).length === 0 ? (
                  <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                    <Lock className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No verified domains available for SSL configuration</p>
                    <p className="text-sm mt-2">Please add and verify a custom domain first</p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Select Domain
                      </label>
                      <select
                        value={selectedDomainId || ''}
                        onChange={(e) => setSelectedDomainId(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                        disabled={!hasWhitelabeling}
                      >
                        <option value="">-- Select a domain --</option>
                        {domains.filter(d => d.is_verified).map((domain) => (
                          <option key={domain.id} value={domain.id}>
                            {domain.domain} {domain.ssl_enabled && '(SSL Enabled)'}
                          </option>
                        ))}
                      </select>
                    </div>

                    {selectedDomainId && (
                      <>
                        <div className="flex space-x-4 border-b border-gray-200 dark:border-gray-700">
                          <button
                            onClick={() => setSSLMethod('upload')}
                            className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
                              sslMethod === 'upload'
                                ? 'border-purple-500 text-purple-600 dark:text-purple-400'
                                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
                            }`}
                          >
                            <Upload className="w-4 h-4 inline mr-2" />
                            Manual Upload
                          </button>
                          <button
                            onClick={() => setSSLMethod('letsencrypt')}
                            className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
                              sslMethod === 'letsencrypt'
                                ? 'border-purple-500 text-purple-600 dark:text-purple-400'
                                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
                            }`}
                          >
                            <Shield className="w-4 h-4 inline mr-2" />
                            Let's Encrypt
                          </button>
                        </div>

                        {sslMethod === 'upload' ? (
                          <div className="space-y-4">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                SSL Certificate (PEM Format)
                              </label>
                              <textarea
                                value={certificatePem}
                                onChange={(e) => setCertificatePem(e.target.value)}
                                placeholder="-----BEGIN CERTIFICATE-----&#10;...&#10;-----END CERTIFICATE-----"
                                rows={8}
                                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
                                disabled={!hasWhitelabeling}
                              />
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Private Key (PEM Format)
                              </label>
                              <textarea
                                value={privateKeyPem}
                                onChange={(e) => setPrivateKeyPem(e.target.value)}
                                placeholder="-----BEGIN PRIVATE KEY-----&#10;...&#10;-----END PRIVATE KEY-----"
                                rows={8}
                                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
                                disabled={!hasWhitelabeling}
                              />
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Certificate Chain (Optional)
                              </label>
                              <textarea
                                value={chainPem}
                                onChange={(e) => setChainPem(e.target.value)}
                                placeholder="-----BEGIN CERTIFICATE-----&#10;...&#10;-----END CERTIFICATE-----"
                                rows={6}
                                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
                                disabled={!hasWhitelabeling}
                              />
                            </div>

                            <div className="flex justify-end">
                              <button
                                onClick={handleUploadSSL}
                                disabled={saving || !certificatePem || !privateKeyPem || !hasWhitelabeling}
                                className="flex items-center space-x-2 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                              >
                                {saving ? (
                                  <RefreshCw className="w-5 h-5 animate-spin" />
                                ) : (
                                  <Upload className="w-5 h-5" />
                                )}
                                <span>{saving ? 'Uploading...' : 'Upload Certificate'}</span>
                              </button>
                            </div>
                          </div>
                        ) : (
                          <div className="space-y-4">
                            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                              <div className="flex items-start space-x-3">
                                <Shield className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                                <div>
                                  <h4 className="font-semibold text-blue-800 dark:text-blue-200 mb-1">
                                    Automatic SSL with Let's Encrypt
                                  </h4>
                                  <p className="text-sm text-blue-700 dark:text-blue-300">
                                    Free SSL certificates with automatic renewal. 
                                    Your domain must point to this server and port 80 must be accessible.
                                  </p>
                                </div>
                              </div>
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Contact Email
                              </label>
                              <input
                                type="email"
                                value={letsEncryptEmail}
                                onChange={(e) => setLetsEncryptEmail(e.target.value)}
                                placeholder="admin@example.com"
                                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                                disabled={!hasWhitelabeling}
                              />
                              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                Let's Encrypt will send renewal reminders to this email
                              </p>
                            </div>

                            <div className="flex justify-end">
                              <button
                                onClick={handleRequestLetsEncrypt}
                                disabled={saving || !letsEncryptEmail || !hasWhitelabeling}
                                className="flex items-center space-x-2 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                              >
                                {saving ? (
                                  <RefreshCw className="w-5 h-5 animate-spin" />
                                ) : (
                                  <Shield className="w-5 h-5" />
                                )}
                                <span>{saving ? 'Requesting...' : 'Request Certificate'}</span>
                              </button>
                            </div>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TenantSettingsPage;
