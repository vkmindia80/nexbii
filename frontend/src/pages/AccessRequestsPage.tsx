import React, { useState, useEffect } from 'react';
import {
  Key, Plus, CheckCircle, XCircle, Clock, FileText, Shield,
  User, Calendar, AlertCircle, CheckSquare, MessageSquare
} from 'lucide-react';
import governanceService from '../services/governanceService';

interface AccessRequest {
  id: string;
  requester_id: string;
  requester_justification: string;
  resource_type: string;
  resource_id: string;
  resource_name?: string;
  access_level: string;
  duration_days?: number;
  status: string;
  approver_id?: string;
  approval_notes?: string;
  approved_at?: string;
  classification_level?: string;
  requires_compliance_approval: boolean;
  compliance_approver_id?: string;
  compliance_approved_at?: string;
  compliance_notes?: string;
  created_at: string;
  expires_at?: string;
}

const AccessRequestsPage: React.FC = () => {
  const [requests, setRequests] = useState<AccessRequest[]>([]);
  const [pendingRequests, setPendingRequests] = useState<AccessRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<AccessRequest | null>(null);
  const [filterStatus, setFilterStatus] = useState('');
  const [showApprovalModal, setShowApprovalModal] = useState(false);

  useEffect(() => {
    loadRequests();
  }, [filterStatus]);

  const loadRequests = async () => {
    try {
      setLoading(true);
      const [allRequests, pending] = await Promise.all([
        governanceService.getAccessRequests(filterStatus || undefined),
        governanceService.getPendingRequests().catch(() => []), // Non-admins can't access this
      ]);
      setRequests(allRequests);
      setPendingRequests(pending);
    } catch (error) {
      console.error('Failed to load access requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (requestId: string, notes?: string) => {
    try {
      await governanceService.approveAccessRequest(requestId, notes);
      loadRequests();
      setShowApprovalModal(false);
      setSelectedRequest(null);
    } catch (error) {
      console.error('Failed to approve request:', error);
      alert('Failed to approve request');
    }
  };

  const handleReject = async (requestId: string, notes: string) => {
    if (!notes) {
      alert('Rejection notes are required');
      return;
    }

    try {
      await governanceService.rejectAccessRequest(requestId, notes);
      loadRequests();
      setShowApprovalModal(false);
      setSelectedRequest(null);
    } catch (error) {
      console.error('Failed to reject request:', error);
      alert('Failed to reject request');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      approved: 'bg-green-100 text-green-800 border-green-200',
      rejected: 'bg-red-100 text-red-800 border-red-200',
      cancelled: 'bg-gray-100 text-gray-800 border-gray-200',
    };
    return colors[status] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4" />;
      case 'approved':
        return <CheckCircle className="w-4 h-4" />;
      case 'rejected':
        return <XCircle className="w-4 h-4" />;
      default:
        return <AlertCircle className="w-4 h-4" />;
    }
  };

  const getAccessLevelColor = (level: string) => {
    const colors: Record<string, string> = {
      read: 'bg-blue-100 text-blue-800',
      write: 'bg-orange-100 text-orange-800',
      admin: 'bg-red-100 text-red-800',
    };
    return colors[level] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto" data-testid="access-requests-page">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Key className="w-8 h-8 text-primary-600" />
          Access Requests
        </h1>
        <p className="text-gray-600 mt-2">
          Request and manage access to sensitive data with approval workflows
        </p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Requests</p>
              <p className="text-2xl font-bold text-gray-900">{requests.length}</p>
            </div>
            <FileText className="w-8 h-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Pending</p>
              <p className="text-2xl font-bold text-yellow-900">
                {requests.filter(r => r.status === 'pending').length}
              </p>
            </div>
            <Clock className="w-8 h-8 text-yellow-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Approved</p>
              <p className="text-2xl font-bold text-green-900">
                {requests.filter(r => r.status === 'approved').length}
              </p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Rejected</p>
              <p className="text-2xl font-bold text-red-900">
                {requests.filter(r => r.status === 'rejected').length}
              </p>
            </div>
            <XCircle className="w-8 h-8 text-red-600" />
          </div>
        </div>
      </div>

      {/* Pending Requests (Admin Only) */}
      {pendingRequests.length > 0 && (
        <div className="bg-orange-50 rounded-lg p-4 mb-6 border border-orange-200">
          <div className="flex items-center gap-2 mb-3">
            <AlertCircle className="w-5 h-5 text-orange-600" />
            <h3 className="text-sm font-semibold text-orange-900">
              {pendingRequests.length} requests awaiting your approval
            </h3>
          </div>
          <div className="space-y-2">
            {pendingRequests.slice(0, 3).map((request) => (
              <div key={request.id} className="bg-white rounded p-3 border border-orange-300">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {request.resource_type}: {request.resource_name || request.resource_id}
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      Requested {new Date(request.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      setSelectedRequest(request);
                      setShowApprovalModal(true);
                    }}
                    className="px-3 py-1 text-sm bg-orange-600 text-white rounded hover:bg-orange-700"
                  >
                    Review
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filters and Create Button */}
      <div className="bg-white rounded-lg shadow p-4 border border-gray-200 mb-6">
        <div className="flex items-center justify-between gap-4">
          <div className="flex-1">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full max-w-xs px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">All Requests</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>

          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            <Plus className="w-5 h-5" />
            Request Access
          </button>
        </div>
      </div>

      {/* Requests List */}
      <div className="bg-white rounded-lg shadow border border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Access Requests</h2>
          <p className="text-sm text-gray-600 mt-1">{requests.length} requests</p>
        </div>

        <div className="divide-y divide-gray-200">
          {requests.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <Key className="w-12 h-12 mx-auto mb-3 text-gray-400" />
              <p>No access requests found</p>
              <p className="text-sm mt-1">Create your first request to access protected resources</p>
            </div>
          ) : (
            requests.map((request) => (
              <div key={request.id} className="p-4 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium border flex items-center gap-1 ${getStatusColor(request.status)}`}>
                        {getStatusIcon(request.status)}
                        {request.status.toUpperCase()}
                      </span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getAccessLevelColor(request.access_level)}`}>
                        {request.access_level.toUpperCase()}
                      </span>
                      {request.classification_level && (
                        <span className="px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-800">
                          {request.classification_level}
                        </span>
                      )}
                      {request.requires_compliance_approval && (
                        <span className="px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-800 flex items-center gap-1">
                          <Shield className="w-3 h-3" />
                          Compliance Required
                        </span>
                      )}
                    </div>

                    <h3 className="font-semibold text-gray-900 mb-1">
                      {request.resource_type}: {request.resource_name || request.resource_id}
                    </h3>

                    <p className="text-sm text-gray-600 mb-2">{request.requester_justification}</p>

                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <User className="w-3 h-3" />
                        Request ID: {request.id.slice(0, 8)}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {new Date(request.created_at).toLocaleDateString()}
                      </span>
                      {request.duration_days && (
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {request.duration_days} days
                        </span>
                      )}
                    </div>

                    {(request.approval_notes || request.compliance_notes) && (
                      <div className="mt-2 p-2 bg-blue-50 rounded border border-blue-200">
                        <p className="text-xs text-blue-900">
                          <MessageSquare className="w-3 h-3 inline mr-1" />
                          {request.approval_notes || request.compliance_notes}
                        </p>
                      </div>
                    )}
                  </div>

                  {request.status === 'pending' && (
                    <div className="flex gap-2 ml-4">
                      <button
                        onClick={() => {
                          setSelectedRequest(request);
                          setShowApprovalModal(true);
                        }}
                        className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => {
                          setSelectedRequest(request);
                          setShowApprovalModal(true);
                        }}
                        className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                      >
                        Reject
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Info Box */}
      <div className="mt-6 bg-blue-50 rounded-lg p-6 border border-blue-200">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-blue-900 mb-2">Access Request Workflow</h3>
            <ul className="text-sm text-blue-800 space-y-2">
              <li>• <strong>Step 1:</strong> User requests access to a protected resource with justification</li>
              <li>• <strong>Step 2:</strong> Admin reviews the request and classification level</li>
              <li>• <strong>Step 3:</strong> For restricted data, compliance officer approval is also required</li>
              <li>• <strong>Step 4:</strong> Once approved, user gets time-limited or permanent access</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Simple Approval Modal */}
      {showApprovalModal && selectedRequest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Review Access Request</h3>
            
            <div className="mb-4">
              <p className="text-sm text-gray-700 mb-2">
                <strong>Resource:</strong> {selectedRequest.resource_type} - {selectedRequest.resource_name}
              </p>
              <p className="text-sm text-gray-700 mb-2">
                <strong>Justification:</strong> {selectedRequest.requester_justification}
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => handleApprove(selectedRequest.id, 'Approved by admin')}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Approve
              </button>
              <button
                onClick={() => handleReject(selectedRequest.id, 'Request rejected')}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Reject
              </button>
              <button
                onClick={() => {
                  setShowApprovalModal(false);
                  setSelectedRequest(null);
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
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

export default AccessRequestsPage;
