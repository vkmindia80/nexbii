import React, { useState, useEffect } from 'react';
import { Smartphone, Key, Download, RefreshCw, Shield, QrCode, Copy, AlertCircle, CheckCircle, X, Save } from 'lucide-react';
import mfaService, { MFAStatus, MFAEnrollmentData } from '../services/mfaService';

const MFAManagementPage: React.FC = () => {
  const [mfaStatus, setMfaStatus] = useState<MFAStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [enrollmentData, setEnrollmentData] = useState<MFAEnrollmentData | null>(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [showBackupCodes, setShowBackupCodes] = useState(false);
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [showEnforcementModal, setShowEnforcementModal] = useState(false);
  const [enforceMFA, setEnforceMFA] = useState(false);

  useEffect(() => {
    fetchMFAStatus();
  }, []);

  const fetchMFAStatus = async () => {
    try {
      setLoading(true);
      const response = await mfaService.getStatus();
      setMfaStatus(response);
    } catch (error) {
      console.error('Failed to fetch MFA status:', error);
    } finally {
      setLoading(false);
    }
  };

  const startEnrollment = async () => {
    try {
      const response = await mfaService.startEnrollment();
      setEnrollmentData(response);
    } catch (error) {
      console.error('Failed to start enrollment:', error);
      alert('Failed to start MFA enrollment');
    }
  };

  const verifyEnrollment = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      alert('Please enter a valid 6-digit code');
      return;
    }

    try {
      await mfaService.verifyEnrollment(verificationCode);
      setEnrollmentData(null);
      setVerificationCode('');
      fetchMFAStatus();
      alert('MFA enrollment completed successfully!');
    } catch (error) {
      console.error('Failed to verify enrollment:', error);
      alert('Invalid verification code. Please try again.');
    }
  };

  const disableMFA = async () => {
    if (!window.confirm('Are you sure you want to disable MFA? This will reduce your account security.')) return;

    const password = prompt('Enter your password to confirm:');
    if (!password) return;

    try {
      await mfaService.disable(password);
      fetchMFAStatus();
      alert('MFA disabled successfully');
    } catch (error) {
      console.error('Failed to disable MFA:', error);
      alert('Failed to disable MFA. Check your password.');
    }
  };

  const viewBackupCodes = async () => {
    try {
      const codes = await mfaService.getBackupCodes();
      setBackupCodes(codes);
      setShowBackupCodes(true);
    } catch (error) {
      console.error('Failed to fetch backup codes:', error);
      alert('Failed to fetch backup codes');
    }
  };

  const regenerateBackupCodes = async () => {
    if (!window.confirm('This will invalidate your existing backup codes. Continue?')) return;

    try {
      const codes = await mfaService.regenerateBackupCodes();
      setBackupCodes(codes);
      alert('Backup codes regenerated successfully! Please save them securely.');
      setShowBackupCodes(true);
    } catch (error) {
      console.error('Failed to regenerate backup codes:', error);
      alert('Failed to regenerate backup codes');
    }
  };

  const handleSetEnforcement = async () => {
    try {
      await mfaService.setEnforcement(enforceMFA);
      setShowEnforcementModal(false);
      alert(`MFA enforcement ${enforceMFA ? 'enabled' : 'disabled'} for all users`);
    } catch (error) {
      console.error('Failed to set enforcement:', error);
      alert('Failed to update MFA enforcement policy');
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  const downloadBackupCodes = () => {
    const content = backupCodes.join('\n');
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `mfa-backup-codes-${new Date().toISOString()}.txt`;
    a.click();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3" data-testid="page-title">
            <Smartphone className="w-8 h-8 text-purple-600" />
            Multi-Factor Authentication (MFA)
          </h1>
          <p className="text-gray-600 mt-2">
            Add an extra layer of security to your account with Time-based One-Time Passwords (TOTP)
          </p>
        </div>

        {/* MFA Not Enabled */}
        {mfaStatus && !mfaStatus.is_enabled && !enrollmentData && (
          <div className="bg-white rounded-lg shadow-sm p-8 mb-6">
            <div className="flex items-start gap-6">
              <div className="p-4 bg-purple-100 rounded-lg">
                <Shield className="w-12 h-12 text-purple-600" />
              </div>
              <div className="flex-1">
                <h2 className="text-2xl font-semibold text-gray-900 mb-3">
                  Secure Your Account with MFA
                </h2>
                <p className="text-gray-600 mb-6">
                  Multi-factor authentication adds an additional security layer by requiring a verification code from your mobile device in addition to your password.
                </p>
                <div className="space-y-3 mb-6">
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <p className="text-gray-700">Works with Google Authenticator, Authy, and other TOTP apps</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <p className="text-gray-700">Backup codes provided for account recovery</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <p className="text-gray-700">Protects against unauthorized access</p>
                  </div>
                </div>
                <button
                  onClick={startEnrollment}
                  className="px-8 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium transition-colors"
                  data-testid="enable-mfa-button"
                >
                  Enable MFA
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Enrollment Flow */}
        {enrollmentData && (
          <div className="bg-white rounded-lg shadow-sm p-8 mb-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">
              Set Up Multi-Factor Authentication
            </h2>

            <div className="space-y-8">
              {/* Step 1: QR Code */}
              <div className="border-b pb-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold">
                    1
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">Scan QR Code</h3>
                </div>
                <p className="text-gray-600 mb-4 ml-11">
                  Open your authenticator app (Google Authenticator, Authy, 1Password, etc.) and scan this QR code:
                </p>
                <div className="ml-11 bg-white p-6 rounded-lg inline-block border-2 border-gray-200">
                  <img
                    src={enrollmentData.qr_code_url}
                    alt="MFA QR Code"
                    className="w-64 h-64"
                    data-testid="qr-code"
                  />
                </div>
                <div className="ml-11 mt-4 p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-700 mb-2">
                    <strong>Can't scan?</strong> Enter this key manually:
                  </p>
                  <div className="flex items-center gap-2">
                    <code className="bg-white px-4 py-2 rounded border flex-1 font-mono text-sm">
                      {enrollmentData.secret_key}
                    </code>
                    <button
                      onClick={() => copyToClipboard(enrollmentData.secret_key)}
                      className="p-2 hover:bg-gray-200 rounded transition-colors"
                      title="Copy to clipboard"
                    >
                      <Copy className="w-5 h-5 text-gray-600" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Step 2: Verify */}
              <div className="border-b pb-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold">
                    2
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">Verify Code</h3>
                </div>
                <p className="text-gray-600 mb-4 ml-11">
                  Enter the 6-digit code from your authenticator app to verify the setup:
                </p>
                <div className="flex gap-3 ml-11 max-w-md">
                  <input
                    type="text"
                    value={verificationCode}
                    onChange={(e) => {
                      const value = e.target.value.replace(/\D/g, '').slice(0, 6);
                      setVerificationCode(value);
                    }}
                    className="flex-1 px-6 py-3 border-2 rounded-lg focus:ring-2 focus:ring-purple-500 text-center text-2xl font-mono tracking-widest"
                    placeholder="000000"
                    maxLength={6}
                    data-testid="mfa-verification-input"
                  />
                  <button
                    onClick={verifyEnrollment}
                    disabled={verificationCode.length !== 6}
                    className="px-8 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    data-testid="verify-mfa-button"
                  >
                    Verify & Enable
                  </button>
                </div>
              </div>

              {/* Step 3: Backup Codes */}
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold">
                    3
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">Save Backup Codes</h3>
                </div>
                <div className="ml-11 bg-yellow-50 border-2 border-yellow-200 rounded-lg p-6">
                  <div className="flex items-start gap-3 mb-4">
                    <AlertCircle className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-yellow-900 mb-2">
                        Important: Save These Backup Codes
                      </p>
                      <p className="text-sm text-yellow-800">
                        Store these codes in a secure place. You can use them to access your account if you lose your device. Each code can only be used once.
                      </p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3 mb-4">
                    {enrollmentData.backup_codes.map((code, index) => (
                      <div
                        key={index}
                        className="bg-white px-4 py-3 rounded border border-yellow-300 font-mono text-sm text-center"
                      >
                        {code}
                      </div>
                    ))}
                  </div>
                  <button
                    onClick={() => {
                      const content = enrollmentData.backup_codes.join('\n');
                      const blob = new Blob([content], { type: 'text/plain' });
                      const url = window.URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `mfa-backup-codes-${new Date().toISOString()}.txt`;
                      a.click();
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
                  >
                    <Download className="w-5 h-5" />
                    Download Backup Codes
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* MFA Enabled */}
        {mfaStatus && mfaStatus.is_enabled && !enrollmentData && (
          <>
            <div className="bg-white rounded-lg shadow-sm p-8 mb-6">
              <div className="flex items-start gap-6">
                <div className="p-4 bg-green-100 rounded-lg">
                  <Shield className="w-12 h-12 text-green-600" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h2 className="text-2xl font-semibold text-gray-900">
                      MFA is Active
                    </h2>
                    <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                      Protected
                    </span>
                  </div>
                  <p className="text-gray-600 mb-4">
                    Your account is protected with two-factor authentication using TOTP.
                  </p>
                  <div className="flex items-center gap-6 text-sm text-gray-600">
                    {mfaStatus.enrolled_at && (
                      <div>
                        <span className="font-medium text-gray-700">Enrolled:</span>{' '}
                        {new Date(mfaStatus.enrolled_at).toLocaleDateString()}
                      </div>
                    )}
                    {mfaStatus.last_used_at && (
                      <div>
                        <span className="font-medium text-gray-700">Last Used:</span>{' '}
                        {new Date(mfaStatus.last_used_at).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Management Options */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Backup Codes Card */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Key className="w-6 h-6 text-purple-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Backup Codes</h3>
                </div>
                <p className="text-gray-600 mb-6 text-sm">
                  View or regenerate your backup codes for account recovery.
                </p>
                <div className="flex gap-3">
                  <button
                    onClick={viewBackupCodes}
                    className="flex-1 px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 font-medium transition-colors"
                  >
                    View Codes
                  </button>
                  <button
                    onClick={regenerateBackupCodes}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                    title="Regenerate"
                  >
                    <RefreshCw className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Enforcement Policy Card */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Shield className="w-6 h-6 text-blue-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Enforcement Policy</h3>
                </div>
                <p className="text-gray-600 mb-6 text-sm">
                  Require MFA for all users in your organization (Admin only).
                </p>
                <button
                  onClick={() => setShowEnforcementModal(true)}
                  className="w-full px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 font-medium transition-colors"
                >
                  Configure Policy
                </button>
              </div>

              {/* Disable MFA Card */}
              <div className="bg-white rounded-lg shadow-sm p-6 border-2 border-red-200">
                <div className="flex items-center gap-3 mb-4">
                  <AlertCircle className="w-6 h-6 text-red-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Disable MFA</h3>
                </div>
                <p className="text-gray-600 mb-6 text-sm">
                  Remove two-factor authentication from your account. This will reduce your security.
                </p>
                <button
                  onClick={disableMFA}
                  className="w-full px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 font-medium transition-colors"
                  data-testid="disable-mfa-button"
                >
                  Disable MFA
                </button>
              </div>
            </div>
          </>
        )}

        {/* Backup Codes Modal */}
        {showBackupCodes && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" data-testid="backup-codes-modal">
            <div className="bg-white rounded-lg p-8 max-w-2xl w-full">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Backup Codes</h2>
                <button
                  onClick={() => setShowBackupCodes(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                <div className="flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-yellow-900">
                    Each code can only be used once. Store them securely and keep them private.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 mb-6">
                {backupCodes.map((code, index) => (
                  <div
                    key={index}
                    className="bg-gray-50 px-4 py-3 rounded-lg border font-mono text-sm text-center"
                  >
                    {code}
                  </div>
                ))}
              </div>

              <div className="flex gap-3">
                <button
                  onClick={downloadBackupCodes}
                  className="flex-1 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium flex items-center justify-center gap-2"
                >
                  <Download className="w-5 h-5" />
                  Download Codes
                </button>
                <button
                  onClick={() => setShowBackupCodes(false)}
                  className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Enforcement Policy Modal */}
        {showEnforcementModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" data-testid="enforcement-modal">
            <div className="bg-white rounded-lg p-8 max-w-md w-full">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">MFA Enforcement Policy</h2>

              <div className="mb-6">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={enforceMFA}
                    onChange={(e) => setEnforceMFA(e.target.checked)}
                    className="w-5 h-5 text-purple-600 rounded focus:ring-purple-500"
                  />
                  <div>
                    <div className="font-medium text-gray-900">Require MFA for All Users</div>
                    <div className="text-sm text-gray-600">
                      All users will be required to enable MFA on their next login
                    </div>
                  </div>
                </label>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <p className="text-sm text-blue-900">
                  <strong>Note:</strong> Users without MFA will be prompted to set it up before they can access their account.
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleSetEnforcement}
                  className="flex-1 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium"
                >
                  Save Policy
                </button>
                <button
                  onClick={() => setShowEnforcementModal(false)}
                  className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium"
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

export default MFAManagementPage;
