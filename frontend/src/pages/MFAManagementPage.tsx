import React, { useState, useEffect } from 'react';
import { Smartphone, Key, Download, RefreshCw, Shield } from 'lucide-react';
import api from '../services/api';

interface MFAStatus {
  is_enabled: boolean;
  enrollment_completed: boolean;
  enrolled_at: string | null;
  last_used_at: string | null;
}

const MFAManagementPage: React.FC = () => {
  const [mfaStatus, setMfaStatus] = useState<MFAStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [enrollmentData, setEnrollmentData] = useState<any>(null);
  const [verificationCode, setVerificationCode] = useState('');

  useEffect(() => {
    fetchMFAStatus();
  }, []);

  const fetchMFAStatus = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/mfa/status');
      setMfaStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch MFA status:', error);
    } finally {
      setLoading(false);
    }
  };

  const startEnrollment = async () => {
    try {
      const response = await api.post('/api/mfa/enroll');
      setEnrollmentData(response.data);
    } catch (error) {
      console.error('Failed to start enrollment:', error);
    }
  };

  const verifyEnrollment = async () => {
    try {
      await api.post('/api/mfa/verify-enrollment', {
        code: verificationCode
      });
      setEnrollmentData(null);
      setVerificationCode('');
      fetchMFAStatus();
      alert('MFA enrollment completed successfully!');
    } catch (error) {
      console.error('Failed to verify enrollment:', error);
      alert('Invalid verification code');
    }
  };

  const disableMFA = async () => {
    if (!window.confirm('Are you sure you want to disable MFA?')) return;
    
    const password = prompt('Enter your password to confirm:');
    if (!password) return;

    try {
      await api.post('/api/mfa/disable', { password });
      fetchMFAStatus();
      alert('MFA disabled successfully');
    } catch (error) {
      console.error('Failed to disable MFA:', error);
      alert('Failed to disable MFA. Check your password.');
    }
  };

  const regenerateBackupCodes = async () => {
    try {
      const response = await api.post('/api/mfa/backup-codes/regenerate');
      alert('Backup codes regenerated. Save them securely!');
      console.log('New backup codes:', response.data.backup_codes);
    } catch (error) {
      console.error('Failed to regenerate backup codes:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Smartphone className="w-8 h-8 text-blue-600" />
            Multi-Factor Authentication
          </h1>
          <p className="text-gray-600 mt-2">
            Add an extra layer of security to your account
          </p>
        </div>

        {/* MFA Status */}
        {mfaStatus && !mfaStatus.is_enabled && !enrollmentData && (
          <div className="bg-white rounded-lg shadow-sm p-8 mb-6">
            <div className="flex items-start gap-4 mb-6">
              <Shield className="w-12 h-12 text-gray-400" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  MFA is not enabled
                </h2>
                <p className="text-gray-600 mb-4">
                  Protect your account with Time-based One-Time Passwords (TOTP)
                </p>
                <button
                  onClick={startEnrollment}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
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
            <h2 className="text-xl font-semibold text-gray-900 mb-6">
              Set Up MFA
            </h2>
            
            <div className="space-y-6">
              {/* Step 1: QR Code */}
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Step 1: Scan QR Code</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Use an authenticator app (Google Authenticator, Authy, etc.) to scan this QR code
                </p>
                <div className="bg-gray-50 p-4 rounded-lg inline-block">
                  <img src={enrollmentData.qr_code_url} alt="MFA QR Code" className="w-64 h-64" />
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Or enter this key manually: <code className="bg-gray-100 px-2 py-1 rounded">{enrollmentData.secret_key}</code>
                </p>
              </div>

              {/* Step 2: Verify */}
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Step 2: Verify Code</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Enter the 6-digit code from your authenticator app
                </p>
                <div className="flex gap-4">
                  <input
                    type="text"
                    value={verificationCode}
                    onChange={(e) => setVerificationCode(e.target.value)}
                    className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="000000"
                    maxLength={6}
                    data-testid="mfa-verification-input"
                  />
                  <button
                    onClick={verifyEnrollment}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    data-testid="verify-mfa-button"
                  >
                    Verify
                  </button>
                </div>
              </div>

              {/* Backup Codes */}
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                  <Key className="w-5 h-5 text-yellow-600" />
                  Backup Codes
                </h3>
                <p className="text-sm text-gray-700 mb-4">
                  Save these backup codes in a secure place. You can use them to access your account if you lose your device.
                </p>
                <div className="grid grid-cols-2 gap-2 font-mono text-sm">
                  {enrollmentData.backup_codes.map((code: string, index: number) => (
                    <div key={index} className="bg-white px-3 py-2 rounded border">
                      {code}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* MFA Enabled */}
        {mfaStatus && mfaStatus.is_enabled && (
          <div className="bg-white rounded-lg shadow-sm p-8">
            <div className="flex items-start gap-4 mb-6">
              <div className="p-3 bg-green-100 rounded-lg">
                <Shield className="w-8 h-8 text-green-600" />
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  MFA is enabled
                </h2>
                <p className="text-gray-600">
                  Your account is protected with two-factor authentication
                </p>
                {mfaStatus.enrolled_at && (
                  <p className="text-sm text-gray-500 mt-2">
                    Enrolled: {new Date(mfaStatus.enrolled_at).toLocaleDateString()}
                  </p>
                )}
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={regenerateBackupCodes}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                <RefreshCw className="w-5 h-5" />
                Regenerate Backup Codes
              </button>
              <button
                onClick={disableMFA}
                className="flex items-center gap-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
                data-testid="disable-mfa-button"
              >
                Disable MFA
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MFAManagementPage;