import React, { useState, useEffect } from 'react';
import { Activity as ActivityIcon, Clock, User, Database, FileText, BarChart3 } from 'lucide-react';
import activityService, { Activity } from '../services/activityService';

const ActivityFeedPage: React.FC = () => {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'me'>('me');

  useEffect(() => {
    fetchActivities();
  }, [filter]);

  const fetchActivities = async () => {
    try {
      setLoading(true);
      const data = filter === 'me' 
        ? await activityService.getMyActivities(100)
        : await activityService.getAllActivities(100);
      setActivities(data);
    } catch (error) {
      console.error('Failed to fetch activities:', error);
    } finally {
      setLoading(false);
    }
  };

  const getActivityIcon = (type: string) => {
    if (type.includes('dashboard')) return <BarChart3 className="h-5 w-5" />;
    if (type.includes('query')) return <FileText className="h-5 w-5" />;
    if (type.includes('datasource')) return <Database className="h-5 w-5" />;
    if (type.includes('comment')) return <ActivityIcon className="h-5 w-5" />;
    return <ActivityIcon className="h-5 w-5" />;
  };

  const getActivityColor = (type: string) => {
    if (type.includes('created')) return 'text-green-600 bg-green-100';
    if (type.includes('updated')) return 'text-blue-600 bg-blue-100';
    if (type.includes('deleted')) return 'text-red-600 bg-red-100';
    if (type.includes('triggered')) return 'text-orange-600 bg-orange-100';
    return 'text-gray-600 bg-gray-100';
  };

  const formatRelativeTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div data-testid="activity-feed-page">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Activity Feed</h1>
        <p className="mt-1 text-sm text-gray-600">
          Track all activities and changes across your workspace
        </p>
      </div>

      <div className="mb-6 flex gap-2">
        <button
          onClick={() => setFilter('me')}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            filter === 'me'
              ? 'bg-indigo-600 text-white'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
          data-testid="filter-my-activities"
        >
          My Activities
        </button>
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            filter === 'all'
              ? 'bg-indigo-600 text-white'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
          data-testid="filter-all-activities"
        >
          All Activities
        </button>
      </div>

      {activities.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border-2 border-dashed border-gray-300">
          <ActivityIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No activities</h3>
          <p className="mt-1 text-sm text-gray-500">
            Activities will appear here as you work.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <ul className="divide-y divide-gray-200">
            {activities.map((activity) => (
              <li
                key={activity.id}
                className="p-4 hover:bg-gray-50 transition-colors"
                data-testid={`activity-${activity.id}`}
              >
                <div className="flex items-start">
                  <div className={`p-2 rounded-full ${getActivityColor(activity.activity_type)} mr-4`}>
                    {getActivityIcon(activity.activity_type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {activity.entity_name || activity.entity_type}
                      </p>
                      <p className="text-xs text-gray-500 ml-2 whitespace-nowrap flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {formatRelativeTime(activity.created_at)}
                      </p>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {activity.description || activity.activity_type.replace(/_/g, ' ')}
                    </p>
                    <div className="mt-1 flex items-center text-xs text-gray-500">
                      <span className="inline-flex items-center px-2 py-0.5 rounded bg-gray-100 text-gray-800">
                        {activity.activity_type.replace(/_/g, ' ')}
                      </span>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ActivityFeedPage;
