import React, { useState, useEffect } from 'react';
import { Database, Download, Upload, Trash2, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import adminService, { BackupJob, BackupJobCreate } from '../services/adminService';

const BackupManagementPage: React.FC = () => {
  const [backups, setBackups] = useState<BackupJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showRestoreModal, setShowRestoreModal] = useState(false);
  const [selectedBackup, setSelectedBackup] = useState<BackupJob | null>(null);
  const [createForm, setCreateForm] = useState<BackupJobCreate>({
    backup_type: 'full',
    include_data: true,
    include_files: true,
    compression: true
  });

  useEffect(() => {
    fetchBackups();
  }, []);

  const fetchBackups = async () => {
    try {
      setLoading(true);
      const data = await adminService.listBackups(undefined, 50);
      setBackups(data);
    } catch (error) {
      console.error('Failed to fetch backups:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBackup = async () => {
    try {
      await adminService.createBackup(createForm);
      alert('Backup job created successfully');
      setShowCreateModal(false);
      fetchBackups();
    } catch (error) {
      console.error('Failed to create backup:', error);
      alert('Failed to create backup');
    }
  };

  const handleRestoreBackup = async () => {
    if (!selectedBackup) return;

    const confirmed = window.confirm(
      'WARNING: Restoring from backup will overwrite existing data. Are you sure you want to continue?'
    );
    if (!confirmed) return;

    try {
      await adminService.restoreBackup(selectedBackup.id, {
        backup_id: selectedBackup.id,
        restore_data: true,
        restore_files: true,
        overwrite_existing: true
      });
      alert('Restore completed successfully');
      setShowRestoreModal(false);
      setSelectedBackup(null);
    } catch (error) {
      console.error('Failed to restore backup:', error);
      alert('Failed to restore backup');
    }
  };

  const handleCleanupOldBackups = async () => {
    const days = prompt('Enter retention period in days (backups older than this will be deleted):');
    if (!days) return;

    try {
      const result = await adminService.cleanupOldBackups(parseInt(days));
      alert(`Cleaned up ${result.deleted_count} old backups`);
      fetchBackups();
    } catch (error) {
      console.error('Failed to cleanup backups:', error);
      alert('Failed to cleanup backups');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed':
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'running':
      case 'in_progress':
        return <Clock className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'failed':
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed':
      case 'success':
        return 'bg-green-100 text-green-800';
      case 'running':
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getBackupTypeColor = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'full':
        return 'bg-purple-100 text-purple-800';
      case 'incremental':
        return 'bg-blue-100 text-blue-800';
      case 'tenant_only':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
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
            <Database className="w-8 h-8 mr-3 text-primary-600" />
            Backup Management
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Create, manage, and restore system backups
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleCleanupOldBackups}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 flex items-center"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Cleanup Old
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            Create Backup
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <p className="text-sm text-gray-500">Total Backups</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{backups.length}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <p className="text-sm text-gray-500">Completed</p>
          <p className="text-2xl font-bold text-green-600 mt-1">
            {backups.filter(b => b.status === 'completed').length}
          </p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <p className="text-sm text-gray-500">In Progress</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">
            {backups.filter(b => b.status === 'running' || b.status === 'in_progress').length}
          </p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <p className="text-sm text-gray-500">Total Size</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            {backups.reduce((sum, b) => sum + (b.file_size_mb || 0), 0).toFixed(2)} MB
          </p>
        </div>
      </div>

      {/* Backups Table */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4">Available Backups</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Size
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Completed
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {backups.map((backup) => (
                <tr key={backup.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getBackupTypeColor(backup.backup_type)}`}>
                      {backup.backup_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getStatusIcon(backup.status)}
                      <span className={`ml-2 px-2 py-1 text-xs font-medium rounded ${getStatusColor(backup.status)}`}>
                        {backup.status}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {backup.file_size_mb?.toFixed(2) || 0} MB
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(backup.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {backup.completed_at ? new Date(backup.completed_at).toLocaleString() : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                    {backup.status === 'completed' && (
                      <button
                        onClick={() => {
                          setSelectedBackup(backup);
                          setShowRestoreModal(true);
                        }}
                        className="text-blue-600 hover:text-blue-800 flex items-center"
                        title="Restore"
                      >
                        <Upload className="w-4 h-4 mr-1" />
                        Restore
                      </button>
                    )}
                    {backup.error_message && (
                      <span className="text-red-600 text-xs" title={backup.error_message}>
                        Error
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Backup Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">Create New Backup</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Backup Type
                </label>
                <select
                  value={createForm.backup_type}
                  onChange={(e) => setCreateForm({ ...createForm, backup_type: e.target.value as any })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value="full">Full Backup</option>
                  <option value="incremental">Incremental Backup</option>
                  <option value="tenant_only">Tenant Only</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={createForm.include_data}
                    onChange={(e) => setCreateForm({ ...createForm, include_data: e.target.checked })}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Include Data</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={createForm.include_files}
                    onChange={(e) => setCreateForm({ ...createForm, include_files: e.target.checked })}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Include Files</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={createForm.compression}
                    onChange={(e) => setCreateForm({ ...createForm, compression: e.target.checked })}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Enable Compression</span>
                </label>
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={handleCreateBackup}
                className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                Create Backup
              </button>
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Restore Modal */}
      {showRestoreModal && selectedBackup && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4 text-red-600">Restore Backup - Warning</h3>
            <div className="space-y-4">
              <p className="text-sm text-gray-700">
                You are about to restore from backup:
              </p>
              <div className="bg-gray-50 rounded p-3 text-sm">
                <p><strong>Type:</strong> {selectedBackup.backup_type}</p>
                <p><strong>Created:</strong> {new Date(selectedBackup.created_at).toLocaleString()}</p>
                <p><strong>Size:</strong> {selectedBackup.file_size_mb?.toFixed(2)} MB</p>
              </div>
              <div className="bg-red-50 border border-red-200 rounded p-3">
                <p className="text-sm text-red-800">
                  <strong>WARNING:</strong> This will overwrite existing data. This action cannot be undone.
                </p>
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={handleRestoreBackup}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Restore Now
              </button>
              <button
                onClick={() => {
                  setShowRestoreModal(false);
                  setSelectedBackup(null);
                }}
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

export default BackupManagementPage;