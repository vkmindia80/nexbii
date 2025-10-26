import React, { useState } from 'react';
import { Shield, Download, Trash2, CheckCircle } from 'lucide-react';
import api from '../services/api';

const CompliancePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'gdpr' | 'hipaa' | 'reports'>('gdpr');
  const [loading, setLoading] = useState(false);

  const exportUserData = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/compliance/gdpr/export');
      alert('Data export initiated. You will receive a download link via email.');
      console.log('Export response:', response.data);
    } catch (error) {
      console.error('Failed to export data:', error);
      alert('Failed to export data');
    } finally {
      setLoading(false);
    }
  };

  const deleteUserData = async () => {
    const confirmation = prompt('Type "DELETE MY DATA" to confirm deletion:');
    if (confirmation !== 'DELETE MY DATA') {
      alert('Deletion cancelled');
      return;
    }

    setLoading(true);
    try {
      await api.post('/api/compliance/gdpr/delete', {
        confirmation: 'DELETE MY DATA'
      });
      alert('Your data has been deleted. You will be logged out.');
      // Logout user
      localStorage.removeItem('token');
      window.location.href = '/login';
    } catch (error) {
      console.error('Failed to delete data:', error);
      alert('Failed to delete data');
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async (reportType: string) => {
    setLoading(true);
    try {
      const response = await api.get(`/api/compliance/reports/${reportType}`);
      // Create download
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${reportType}-compliance-report-${new Date().toISOString()}.json`;
      a.click();
    } catch (error) {
      console.error('Failed to generate report:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Shield className="w-8 h-8 text-blue-600" />
            Compliance Center
          </h1>
          <p className="text-gray-600 mt-2">
            GDPR, HIPAA, and SOC 2 compliance tools
          </p>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('gdpr')}
              className={`px-6 py-4 font-medium ${
                activeTab === 'gdpr'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              GDPR
            </button>
            <button
              onClick={() => setActiveTab('hipaa')}
              className={`px-6 py-4 font-medium ${
                activeTab === 'hipaa'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              HIPAA
            </button>
            <button
              onClick={() => setActiveTab('reports')}
              className={`px-6 py-4 font-medium ${
                activeTab === 'reports'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Compliance Reports
            </button>
          </div>
        </div>

        {/* GDPR Tab */}
        {activeTab === 'gdpr' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm p-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">GDPR Tools</h2>
              <p className="text-gray-600 mb-6">
                General Data Protection Regulation compliance features
              </p>

              <div className="space-y-4">
                {/* Data Export */}
                <div className="border rounded-lg p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        Export Your Data
                      </h3>
                      <p className="text-gray-600 mb-4">
                        Download a copy of all your data in JSON format
                      </p>
                    </div>
                    <button
                      onClick={exportUserData}
                      disabled={loading}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                      data-testid="export-data-button"
                    >
                      <Download className="w-5 h-5" />
                      Export Data
                    </button>
                  </div>
                </div>

                {/* Right to be Forgotten */}
                <div className="border border-red-200 rounded-lg p-6 bg-red-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        Delete Your Data
                      </h3>
                      <p className="text-gray-600 mb-4">
                        Permanently delete all your data from our systems (irreversible)
                      </p>
                    </div>
                    <button
                      onClick={deleteUserData}
                      disabled={loading}
                      className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                      data-testid="delete-data-button"
                    >
                      <Trash2 className="w-5 h-5" />
                      Delete Data
                    </button>
                  </div>
                </div>

                {/* Consent Management */}
                <div className="border rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Consent Management
                  </h3>
                  <div className="space-y-3">
                    <label className="flex items-center gap-3">
                      <input type="checkbox" checked disabled className="w-5 h-5" />
                      <span className="text-gray-700">Terms of Service (Required)</span>
                    </label>
                    <label className="flex items-center gap-3">
                      <input type="checkbox" defaultChecked className="w-5 h-5" />
                      <span className="text-gray-700">Analytics & Performance</span>
                    </label>
                    <label className="flex items-center gap-3">
                      <input type="checkbox" className="w-5 h-5" />
                      <span className="text-gray-700">Marketing Communications</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* HIPAA Tab */}
        {activeTab === 'hipaa' && (
          <div className="bg-white rounded-lg shadow-sm p-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">HIPAA Compliance</h2>
            <p className="text-gray-600 mb-6">
              Health Insurance Portability and Accountability Act features
            </p>

            <div className="space-y-6">
              <div className="flex items-start gap-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    PHI Data Classification
                  </h3>
                  <p className="text-gray-600 text-sm">
                    Protected Health Information is automatically classified and masked
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Audit Logging
                  </h3>
                  <p className="text-gray-600 text-sm">
                    All access to PHI data is logged and tracked
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Encryption
                  </h3>
                  <p className="text-gray-600 text-sm">
                    Data is encrypted at rest and in transit
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Reports Tab */}
        {activeTab === 'reports' && (
          <div className="space-y-4">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                SOC 2 Compliance Report
              </h3>
              <p className="text-gray-600 mb-4">
                Service Organization Control 2 compliance status
              </p>
              <button
                onClick={() => generateReport('soc2')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Generate Report
              </button>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                GDPR Compliance Report
              </h3>
              <p className="text-gray-600 mb-4">
                Data protection and privacy compliance status
              </p>
              <button
                onClick={() => generateReport('gdpr')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Generate Report
              </button>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                HIPAA Compliance Report
              </h3>
              <p className="text-gray-600 mb-4">
                Healthcare data protection compliance status
              </p>
              <button
                onClick={() => generateReport('hipaa')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Generate Report
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CompliancePage;