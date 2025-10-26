import React, { useState, useEffect } from 'react';
import { Settings, Upload, Download, History, RotateCcw, FileJson } from 'lucide-react';
import adminService, { ConfigurationVersion } from '../services/adminService';

const ConfigurationManagementPage: React.FC = () => {
  const [versions, setVersions] = useState<ConfigurationVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [showExportModal, setShowExportModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [selectedTenant, setSelectedTenant] = useState<string>('demo');
  const [exportConfig, setExportConfig] = useState({
    include_secrets: false,
    sections: ['general', 'integrations', 'security', 'branding']
  });
  const [importConfig, setImportConfig] = useState({
    merge_strategy: 'merge' as 'replace' | 'merge' | 'skip_existing',
    validate_only: false,
    config_data: '{}'
  });

  useEffect(() => {
    fetchVersions();
  }, [selectedTenant]);

  const fetchVersions = async () => {
    try {
      setLoading(true);
      const data = await adminService.getConfigurationVersions(selectedTenant, 20);
      setVersions(data);
    } catch (error) {
      console.error('Failed to fetch configuration versions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const config = await adminService.exportConfiguration({
        tenant_id: selectedTenant,
        include_secrets: exportConfig.include_secrets,
        sections: exportConfig.sections
      });

      const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `config-${selectedTenant}-${new Date().toISOString()}.json`;
      a.click();

      setShowExportModal(false);
      alert('Configuration exported successfully');
    } catch (error) {
      console.error('Failed to export configuration:', error);
      alert('Failed to export configuration');
    }
  };

  const handleImport = async () => {
    try {
      const parsedConfig = JSON.parse(importConfig.config_data);
      
      await adminService.importConfiguration({
        tenant_id: selectedTenant,
        config_data: parsedConfig,
        merge_strategy: importConfig.merge_strategy,
        validate_only: importConfig.validate_only
      });

      if (importConfig.validate_only) {
        alert('Configuration validation successful');
      } else {
        alert('Configuration imported successfully');
        fetchVersions();
      }

      setShowImportModal(false);
    } catch (error) {
      console.error('Failed to import configuration:', error);
      alert('Failed to import configuration. Check JSON format.');
    }
  };

  const handleRollback = async (versionId: string) => {
    const confirmed = window.confirm(
      'Are you sure you want to rollback to this configuration version?'
    );
    if (!confirmed) return;

    try {
      await adminService.rollbackConfiguration(selectedTenant, versionId);
      alert('Configuration rolled back successfully');
      fetchVersions();
    } catch (error) {
      console.error('Failed to rollback configuration:', error);
      alert('Failed to rollback configuration');
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      setImportConfig({ ...importConfig, config_data: content });
    };
    reader.readAsText(file);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <Settings className="w-8 h-8 mr-3 text-primary-600" />
            Configuration Management
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage system configuration, versioning, and rollbacks
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowImportModal(true)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center"
          >
            <Upload className="w-4 h-4 mr-2" />
            Import Config
          </button>
          <button
            onClick={() => setShowExportModal(true)}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            Export Config
          </button>
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Versions</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{versions.length}</p>
            </div>
            <History className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Current Version</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {versions[0]?.version || 0}
              </p>
            </div>
            <Settings className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Last Modified</p>
              <p className="text-sm text-gray-900 mt-1">
                {versions[0]?.created_at ? new Date(versions[0].created_at).toLocaleDateString() : '-'}
              </p>
            </div>
            <FileJson className="w-8 h-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Configuration Sections */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4">Configuration Sections</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">General Settings</h4>
            <p className="text-sm text-gray-500">Application name, timezone, language preferences</p>
          </div>
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Integrations</h4>
            <p className="text-sm text-gray-500">Email, Slack, webhook configurations</p>
          </div>
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Security</h4>
            <p className="text-sm text-gray-500">Authentication, SSO, MFA settings</p>
          </div>
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">White-Labeling</h4>
            <p className="text-sm text-gray-500">Branding, logos, colors, custom domains</p>
          </div>
        </div>
      </div>

      {/* Version History */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4">Version History</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Version
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created By
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created At
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {versions.map((version, index) => (
                <tr key={version.id} className={index === 0 ? 'bg-green-50' : ''}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-sm font-medium text-gray-900">
                        v{version.version}
                      </span>
                      {index === 0 && (
                        <span className="ml-2 px-2 py-1 text-xs font-medium rounded bg-green-100 text-green-800">
                          Current
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {version.description || 'No description'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {version.created_by}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(version.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {index !== 0 && (
                      <button
                        onClick={() => handleRollback(version.id)}
                        className="text-blue-600 hover:text-blue-800 flex items-center"
                        title="Rollback to this version"
                      >
                        <RotateCcw className="w-4 h-4 mr-1" />
                        Rollback
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Export Modal */}
      {showExportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">Export Configuration</h3>
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={exportConfig.include_secrets}
                    onChange={(e) => setExportConfig({ ...exportConfig, include_secrets: e.target.checked })}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Include Secrets (API keys, passwords)</span>
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Sections to Export
                </label>
                <div className="space-y-2">
                  {['general', 'integrations', 'security', 'branding'].map((section) => (
                    <label key={section} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={exportConfig.sections.includes(section)}
                        onChange={(e) => {
                          const newSections = e.target.checked
                            ? [...exportConfig.sections, section]
                            : exportConfig.sections.filter(s => s !== section);
                          setExportConfig({ ...exportConfig, sections: newSections });
                        }}
                        className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      />
                      <span className="ml-2 text-sm text-gray-700 capitalize">{section}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={handleExport}
                className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                Export
              </button>
              <button
                onClick={() => setShowExportModal(false)}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Import Modal */}
      {showImportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">Import Configuration</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Upload Configuration File
                </label>
                <input
                  type="file"
                  accept=".json"
                  onChange={handleFileUpload}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Or Paste JSON Configuration
                </label>
                <textarea
                  value={importConfig.config_data}
                  onChange={(e) => setImportConfig({ ...importConfig, config_data: e.target.value })}
                  rows={10}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 font-mono text-xs"
                  placeholder='{"setting": "value"}'
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Merge Strategy
                </label>
                <select
                  value={importConfig.merge_strategy}
                  onChange={(e) => setImportConfig({ ...importConfig, merge_strategy: e.target.value as any })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value="merge">Merge with Existing</option>
                  <option value="replace">Replace All</option>
                  <option value="skip_existing">Skip Existing</option>
                </select>
              </div>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={importConfig.validate_only}
                  onChange={(e) => setImportConfig({ ...importConfig, validate_only: e.target.checked })}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-gray-700">Validate Only (Don't Import)</span>
              </label>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={handleImport}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                {importConfig.validate_only ? 'Validate' : 'Import'}
              </button>
              <button
                onClick={() => setShowImportModal(false)}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConfigurationManagementPage;