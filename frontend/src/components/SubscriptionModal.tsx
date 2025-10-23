import React, { useState, useEffect } from 'react';
import { Mail, X, Check } from 'lucide-react';
import subscriptionService, { EmailSubscription, CreateSubscriptionRequest } from '../services/subscriptionService';

interface SubscriptionModalProps {
  dashboardId: string;
  dashboardName: string;
  onClose: () => void;
}

const SubscriptionModal: React.FC<SubscriptionModalProps> = ({ dashboardId, dashboardName, onClose }) => {
  const [frequency, setFrequency] = useState<'daily' | 'weekly' | 'monthly'>('weekly');
  const [subscription, setSubscription] = useState<EmailSubscription | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSubscription();
  }, []);

  const fetchSubscription = async () => {
    try {
      const subs = await subscriptionService.getSubscriptions(dashboardId);
      if (subs.length > 0) {
        setSubscription(subs[0]);
        setFrequency(subs[0].frequency);
      }
    } catch (error) {
      console.error('Failed to fetch subscription:', error);
    }
  };

  const handleSubscribe = async () => {
    try {
      setLoading(true);
      const request: CreateSubscriptionRequest = {
        dashboard_id: dashboardId,
        frequency
      };
      await subscriptionService.createSubscription(request);
      alert('Successfully subscribed!');
      onClose();
    } catch (error) {
      console.error('Failed to subscribe:', error);
      alert('Failed to subscribe');
    } finally {
      setLoading(false);
    }
  };

  const handleUnsubscribe = async () => {
    if (!subscription) return;
    
    try {
      setLoading(true);
      await subscriptionService.deleteSubscription(subscription.id);
      alert('Unsubscribed successfully!');
      onClose();
    } catch (error) {
      console.error('Failed to unsubscribe:', error);
      alert('Failed to unsubscribe');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" data-testid="subscription-modal">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center">
            <Mail className="h-6 w-6 text-indigo-600 mr-2" />
            <h2 className="text-xl font-bold">Email Subscription</h2>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="h-6 w-6" />
          </button>
        </div>

        <p className="text-gray-600 mb-6">
          Get {dashboardName} report delivered to your email
        </p>

        <div className="space-y-4 mb-6">
          <label className="block">
            <span className="text-sm font-medium text-gray-700 mb-2 block">Frequency</span>
            <select
              value={frequency}
              onChange={(e) => setFrequency(e.target.value as any)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              data-testid="frequency-select"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </label>

          {subscription && (
            <div className="bg-green-50 border border-green-200 rounded-md p-3">
              <div className="flex items-center text-green-800">
                <Check className="h-5 w-5 mr-2" />
                <span className="text-sm font-medium">
                  You're subscribed ({subscription.frequency})
                </span>
              </div>
            </div>
          )}
        </div>

        <div className="flex gap-3">
          {subscription ? (
            <button
              onClick={handleUnsubscribe}
              disabled={loading}
              className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
              data-testid="unsubscribe-btn"
            >
              Unsubscribe
            </button>
          ) : (
            <button
              onClick={handleSubscribe}
              disabled={loading}
              className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
              data-testid="subscribe-btn"
            >
              Subscribe
            </button>
          )}
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default SubscriptionModal;
