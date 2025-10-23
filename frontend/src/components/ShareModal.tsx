import React, { useState } from 'react';
import { X, Copy, Check, Lock, Calendar, Globe } from 'lucide-react';
import sharingService, { CreateShareRequest, ShareResponse } from '../services/sharingService';

interface ShareModalProps {
  dashboardId: string;
  dashboardName: string;
  onClose: () => void;
}

const ShareModal: React.FC<ShareModalProps> = ({ dashboardId, dashboardName, onClose }) => {
  const [shareData, setShareData] = useState<ShareResponse | null>(null);
  const [password, setPassword] = useState('');
  const [expiresInDays, setExpiresInDays] = useState<number | undefined>(undefined);
  const [allowInteractions, setAllowInteractions] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleCreateShare = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const request: CreateShareRequest = {
        dashboard_id: dashboardId,
        password: password || undefined,
        expires_in_days: expiresInDays,
        allow_interactions: allowInteractions
      };

      const response = await sharingService.createShareLink(request);
      setShareData(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create share link');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyLink = () => {
    if (shareData) {
      const fullUrl = `${window.location.origin}${shareData.share_url}`;
      navigator.clipboard.writeText(fullUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleCopyEmbed = () => {
    if (shareData) {
      const fullUrl = `${window.location.origin}${shareData.share_url}`;
      const embedCode = `<iframe src="${fullUrl}" width="100%" height="600" frameborder="0"></iframe>`;
      navigator.clipboard.writeText(embedCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" data-testid="share-modal">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Share Dashboard</h2>
            <p className="text-sm text-gray-600 mt-1">{dashboardName}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            data-testid="close-share-modal"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {!shareData ? (
            <div className="space-y-6">
              {/* Password Protection */}
              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                  <Lock size={16} />
                  Password Protection (Optional)
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter password to protect the link"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  data-testid="share-password-input"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Leave empty for public access without password
                </p>
              </div>

              {/* Expiration */}
              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                  <Calendar size={16} />
                  Expiration (Optional)
                </label>
                <select
                  value={expiresInDays || ''}
                  onChange={(e) => setExpiresInDays(e.target.value ? parseInt(e.target.value) : undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  data-testid="share-expiration-select"
                >
                  <option value="">Never expires</option>
                  <option value="1">1 day</option>
                  <option value="7">7 days</option>
                  <option value="30">30 days</option>
                  <option value="90">90 days</option>
                </select>
              </div>

              {/* Allow Interactions */}
              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                  <input
                    type="checkbox"
                    checked={allowInteractions}
                    onChange={(e) => setAllowInteractions(e.target.checked)}
                    className="rounded text-blue-600 focus:ring-2 focus:ring-blue-500"
                    data-testid="share-interactions-checkbox"
                  />
                  <Globe size={16} />
                  Allow interactions (filters, tooltips, etc.)
                </label>
                <p className="text-xs text-gray-500 mt-1 ml-6">
                  When disabled, viewers can only see static dashboard
                </p>
              </div>

              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              {/* Create Button */}
              <button
                onClick={handleCreateShare}
                disabled={isLoading}
                className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
                data-testid="create-share-button"
              >
                {isLoading ? 'Creating Share Link...' : 'Create Share Link'}
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Success Message */}
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                ✅ Share link created successfully!
              </div>

              {/* Share Details */}
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">
                    Share URL
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={`${window.location.origin}${shareData.share_url}`}
                      readOnly
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                      data-testid="share-url-input"
                    />
                    <button
                      onClick={handleCopyLink}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                      data-testid="copy-link-button"
                    >
                      {copied ? <Check size={16} /> : <Copy size={16} />}
                      {copied ? 'Copied!' : 'Copy'}
                    </button>
                  </div>
                </div>

                {/* Embed Code */}
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">
                    Embed Code
                  </label>
                  <div className="flex gap-2">
                    <textarea
                      value={`<iframe src="${window.location.origin}${shareData.share_url}" width="100%" height="600" frameborder="0"></iframe>`}
                      readOnly
                      rows={3}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 font-mono text-sm"
                      data-testid="embed-code-textarea"
                    />
                    <button
                      onClick={handleCopyEmbed}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 self-start"
                      data-testid="copy-embed-button"
                    >
                      {copied ? <Check size={16} /> : <Copy size={16} />}
                      {copied ? 'Copied!' : 'Copy'}
                    </button>
                  </div>
                </div>

                {/* Share Info */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-2">
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <Lock size={14} />
                    <span>
                      {shareData.password_protected ? 'Password protected' : 'Public access (no password)'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <Calendar size={14} />
                    <span>
                      {shareData.expires_at 
                        ? `Expires: ${new Date(shareData.expires_at).toLocaleDateString()}`
                        : 'Never expires'
                      }
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <Globe size={14} />
                    <span>
                      {shareData.allow_interactions ? 'Interactive mode' : 'View-only mode'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Close Button */}
              <button
                onClick={onClose}
                className="w-full bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 font-medium"
                data-testid="close-button"
              >
                Close
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ShareModal;