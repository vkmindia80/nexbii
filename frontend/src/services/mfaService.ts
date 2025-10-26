import api from './api';

export interface MFAStatus {
  is_enabled: boolean;
  enrollment_completed: boolean;
  enrolled_at: string | null;
  last_used_at: string | null;
}

export interface MFAEnrollmentData {
  secret_key: string;
  qr_code_url: string;
  backup_codes: string[];
}

export interface MFAVerification {
  success: boolean;
  message: string;
}

class MFAService {
  async getStatus(): Promise<MFAStatus> {
    const response = await api.get('/api/mfa/status');
    return response.data;
  }

  async startEnrollment(): Promise<MFAEnrollmentData> {
    const response = await api.post('/api/mfa/enroll');
    return response.data;
  }

  async verifyEnrollment(code: string): Promise<MFAVerification> {
    const response = await api.post('/api/mfa/verify-enrollment', { code });
    return response.data;
  }

  async verifyCode(code: string): Promise<MFAVerification> {
    const response = await api.post('/api/mfa/verify', { code });
    return response.data;
  }

  async getBackupCodes(): Promise<string[]> {
    const response = await api.get('/api/mfa/backup-codes');
    return response.data.backup_codes;
  }

  async regenerateBackupCodes(): Promise<string[]> {
    const response = await api.post('/api/mfa/backup-codes/regenerate');
    return response.data.backup_codes;
  }

  async disable(password: string): Promise<void> {
    await api.post('/api/mfa/disable', { password });
  }

  async setEnforcement(enforce: boolean): Promise<void> {
    await api.put('/api/mfa/enforcement', { enforce });
  }
}

export default new MFAService();
