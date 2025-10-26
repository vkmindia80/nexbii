import React, { useState, useEffect } from 'react';
import { Users, UserX, Lock, Unlock, Download, Upload, Activity } from 'lucide-react';
import adminService, { UserManagementStats, UserSession } from '../services/adminService';
import api from '../services/api';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

const UserManagementPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [stats, setStats] = useState<UserManagementStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showSessions, setShowSessions] = useState(false);
  const [sessions, setSessions] = useState<UserSession[]>([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [usersData, statsData] = await Promise.all([
        api.get('/api/auth/users'),
        adminService.getUserStats()
      ]);
      setUsers(usersData.data);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to fetch user data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLockUser = async (userId: string) => {
    const reason = prompt('Enter reason for locking this account:');
    if (!reason) return;

    try {
      await adminService.lockUserAccount(userId, reason);
      alert('User account locked successfully');
      fetchData();
    } catch (error) {
      console.error('Failed to lock user:', error);
      alert('Failed to lock user account');
    }
  };

  const handleUnlockUser = async (userId: string) => {
    try {
      await adminService.unlockUserAccount(userId);
      alert('User account unlocked successfully');
      fetchData();
    } catch (error) {
      console.error('Failed to unlock user:', error);
      alert('Failed to unlock user account');
    }
  };

  const handleViewSessions = async (user: User) => {
    try {
      const sessionsData = await adminService.getUserSessions(user.id);
      setSelectedUser(user);
      setSessions(sessionsData);
      setShowSessions(true);
    } catch (error) {
      console.error('Failed to fetch sessions:', error);
      alert('Failed to fetch user sessions');
    }
  };

  const handleTerminateSession = async (sessionId: string) => {
    if (!selectedUser) return;
    
    try {
      await adminService.terminateUserSession(selectedUser.id, sessionId);
      alert('Session terminated successfully');
      handleViewSessions(selectedUser);
    } catch (error) {
      console.error('Failed to terminate session:', error);
      alert('Failed to terminate session');
    }
  };

  const handleCleanupSessions = async () => {
    try {
      const result = await adminService.cleanupExpiredSessions();
      alert(`Cleaned up ${result.cleaned_count} expired sessions`);
    } catch (error) {
      console.error('Failed to cleanup sessions:', error);
      alert('Failed to cleanup sessions');
    }
  };

  const getRoleColor = (role: string) => {
    switch (role.toLowerCase()) {
      case 'admin':
        return 'bg-purple-100 text-purple-800';
      case 'editor':
        return 'bg-blue-100 text-blue-800';
      case 'viewer':
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
            <Users className="w-8 h-8 mr-3 text-primary-600" />
            User Management
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage users, sessions, and access control
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleCleanupSessions}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 flex items-center"
          >
            <Activity className="w-4 h-4 mr-2" />
            Cleanup Sessions
          </button>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <p className="text-sm text-gray-500">Total Users</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total_users}</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <p className="text-sm text-gray-500">Active Users</p>
            <p className="text-2xl font-bold text-green-600 mt-1">{stats.active_users}</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <p className="text-sm text-gray-500">Inactive Users</p>
            <p className="text-2xl font-bold text-gray-600 mt-1">{stats.inactive_users}</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <p className="text-sm text-gray-500">Locked Users</p>
            <p className="text-2xl font-bold text-red-600 mt-1">{stats.locked_users}</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <p className="text-sm text-gray-500">Active Sessions</p>
            <p className="text-2xl font-bold text-blue-600 mt-1">{stats.active_sessions}</p>
          </div>
        </div>
      )}

      {/* Users Table */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4">All Users</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{user.full_name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {user.email}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getRoleColor(user.role)}`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${
                      user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                    <button
                      onClick={() => handleViewSessions(user)}
                      className="text-blue-600 hover:text-blue-800"
                      title="View Sessions"
                    >
                      <Activity className="w-4 h-4 inline" />
                    </button>
                    {user.is_active ? (
                      <button
                        onClick={() => handleLockUser(user.id)}
                        className="text-red-600 hover:text-red-800"
                        title="Lock Account"
                      >
                        <Lock className="w-4 h-4 inline" />
                      </button>
                    ) : (
                      <button
                        onClick={() => handleUnlockUser(user.id)}
                        className="text-green-600 hover:text-green-800"
                        title="Unlock Account"
                      >
                        <Unlock className="w-4 h-4 inline" />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Sessions Modal */}
      {showSessions && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">
                Active Sessions for {selectedUser.full_name}
              </h3>
              <button
                onClick={() => setShowSessions(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      IP Address
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Last Activity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {sessions.map((session) => (
                    <tr key={session.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {session.ip_address}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(session.last_activity).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button
                          onClick={() => handleTerminateSession(session.id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          Terminate
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserManagementPage;