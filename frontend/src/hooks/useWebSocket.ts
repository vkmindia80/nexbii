import { useEffect, useState, useCallback } from 'react';
import { websocketService } from '../services/websocketService';

export interface OnlineUser {
  user_id: string;
  name: string;
  last_seen: string;
  status: string;
}

export const useWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState<OnlineUser[]>([]);

  useEffect(() => {
    // Get user from localStorage
    const userStr = localStorage.getItem('user');
    if (!userStr) return;

    const user = JSON.parse(userStr);
    
    // Connect to WebSocket
    websocketService
      .connect(user.id, user.full_name || user.email)
      .then(() => {
        setIsConnected(true);
      })
      .catch((err) => {
        console.error('Failed to connect WebSocket:', err);
      });

    // Listen for online users updates
    websocketService.on('user_online', (data) => {
      console.log('User came online:', data);
      setOnlineUsers((prev) => {
        const exists = prev.find((u) => u.user_id === data.user_id);
        if (exists) return prev;
        return [...prev, { ...data, status: 'online', last_seen: new Date().toISOString() }];
      });
    });

    websocketService.on('user_offline', (data) => {
      console.log('User went offline:', data);
      setOnlineUsers((prev) => prev.filter((u) => u.user_id !== data.user_id));
    });

    return () => {
      websocketService.disconnect();
      setIsConnected(false);
    };
  }, []);

  return {
    isConnected,
    onlineUsers,
    websocketService,
  };
};

export const useDashboardCollaboration = (dashboardId: string | undefined) => {
  const [viewers, setViewers] = useState<string[]>([]);
  const [updates, setUpdates] = useState<any[]>([]);

  useEffect(() => {
    if (!dashboardId || !websocketService.isConnected()) return;

    // Join dashboard
    websocketService.joinDashboard(dashboardId).then((response) => {
      if (response?.viewers) {
        setViewers(response.viewers);
      }
    });

    // Listen for viewers joining/leaving
    const handleUserJoined = (data: any) => {
      if (data.dashboard_id === dashboardId) {
        setViewers((prev) => [...new Set([...prev, data.user_id])]);
      }
    };

    const handleUserLeft = (data: any) => {
      if (data.dashboard_id === dashboardId) {
        setViewers((prev) => prev.filter((id) => id !== data.user_id));
      }
    };

    const handleDashboardUpdate = (data: any) => {
      if (data.dashboard_id === dashboardId) {
        setUpdates((prev) => [...prev, data]);
      }
    };

    websocketService.on('user_joined_dashboard', handleUserJoined);
    websocketService.on('user_left_dashboard', handleUserLeft);
    websocketService.on('dashboard_update', handleDashboardUpdate);

    return () => {
      websocketService.leaveDashboard(dashboardId);
      websocketService.off('user_joined_dashboard', handleUserJoined);
      websocketService.off('user_left_dashboard', handleUserLeft);
      websocketService.off('dashboard_update', handleDashboardUpdate);
    };
  }, [dashboardId]);

  const notifyUpdate = useCallback(
    (updateType: string = 'update') => {
      if (dashboardId) {
        websocketService.notifyDashboardUpdate(dashboardId, updateType);
      }
    },
    [dashboardId]
  );

  return {
    viewers,
    updates,
    notifyUpdate,
  };
};

export const useQueryCollaboration = (queryId: string | undefined) => {
  const [editors, setEditors] = useState<string[]>([]);
  const [cursors, setCursors] = useState<Map<string, any>>(new Map());

  useEffect(() => {
    if (!queryId || !websocketService.isConnected()) return;

    // Join query editor
    websocketService.joinQueryEditor(queryId).then((response) => {
      if (response?.editors) {
        setEditors(response.editors);
      }
    });

    // Listen for editors joining/leaving
    const handleUserJoined = (data: any) => {
      if (data.query_id === queryId) {
        setEditors((prev) => [...new Set([...prev, data.user_id])]);
      }
    };

    const handleUserLeft = (data: any) => {
      if (data.query_id === queryId) {
        setEditors((prev) => prev.filter((id) => id !== data.user_id));
        setCursors((prev) => {
          const newCursors = new Map(prev);
          newCursors.delete(data.user_id);
          return newCursors;
        });
      }
    };

    const handleCursorUpdate = (data: any) => {
      if (data.query_id === queryId) {
        setCursors((prev) => {
          const newCursors = new Map(prev);
          newCursors.set(data.user_id, {
            user_name: data.user_name,
            position: data.position,
            selection: data.selection,
          });
          return newCursors;
        });
      }
    };

    websocketService.on('user_joined_query', handleUserJoined);
    websocketService.on('user_left_query', handleUserLeft);
    websocketService.on('cursor_update', handleCursorUpdate);

    return () => {
      websocketService.leaveQueryEditor(queryId);
      websocketService.off('user_joined_query', handleUserJoined);
      websocketService.off('user_left_query', handleUserLeft);
      websocketService.off('cursor_update', handleCursorUpdate);
    };
  }, [queryId]);

  const updateCursor = useCallback(
    (position: any, selection: any) => {
      if (queryId) {
        websocketService.updateCursorPosition(queryId, position, selection);
      }
    },
    [queryId]
  );

  return {
    editors,
    cursors,
    updateCursor,
  };
};
