import { io, Socket } from 'socket.io-client';

class WebSocketService {
  private socket: Socket | null = null;
  private userId: string | null = null;
  private userName: string | null = null;
  private backendUrl: string;

  constructor() {
    this.backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
  }

  connect(userId: string, userName: string): Promise<boolean> {
    return new Promise((resolve, reject) => {
      if (this.socket?.connected) {
        resolve(true);
        return;
      }

      this.userId = userId;
      this.userName = userName;

      // Connect to WebSocket
      this.socket = io(this.backendUrl, {
        path: '/socket.io',
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000,
      });

      this.socket.on('connect', async () => {
        console.log('✅ WebSocket connected');
        
        // Authenticate after connection
        try {
          const response = await this.emit('authenticate', {
            user_id: userId,
            user_name: userName,
          });
          
          if (response.success) {
            console.log('✅ WebSocket authenticated', response);
            resolve(true);
          } else {
            console.error('❌ WebSocket authentication failed', response);
            reject(new Error('Authentication failed'));
          }
        } catch (err) {
          console.error('❌ WebSocket authentication error', err);
          reject(err);
        }
      });

      this.socket.on('connect_error', (error) => {
        console.error('❌ WebSocket connection error:', error);
        reject(error);
      });

      this.socket.on('disconnect', (reason) => {
        console.log('🔌 WebSocket disconnected:', reason);
      });
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  emit(event: string, data: any): Promise<any> {
    return new Promise((resolve, reject) => {
      if (!this.socket?.connected) {
        reject(new Error('Socket not connected'));
        return;
      }

      this.socket.emit(event, data, (response: any) => {
        resolve(response);
      });
    });
  }

  on(event: string, callback: (data: any) => void) {
    if (this.socket) {
      this.socket.on(event, callback);
    }
  }

  off(event: string, callback?: (data: any) => void) {
    if (this.socket) {
      this.socket.off(event, callback);
    }
  }

  // Dashboard Methods
  async joinDashboard(dashboardId: string) {
    if (!this.userId) return;
    
    return this.emit('join_dashboard', {
      user_id: this.userId,
      dashboard_id: dashboardId,
    });
  }

  async leaveDashboard(dashboardId: string) {
    if (!this.userId) return;
    
    return this.emit('leave_dashboard', {
      user_id: this.userId,
      dashboard_id: dashboardId,
    });
  }

  async notifyDashboardUpdate(dashboardId: string, updateType: string = 'update') {
    if (!this.userId) return;
    
    return this.emit('dashboard_updated', {
      dashboard_id: dashboardId,
      type: updateType,
      user_id: this.userId,
    });
  }

  // Query Editor Methods
  async joinQueryEditor(queryId: string) {
    if (!this.userId) return;
    
    return this.emit('join_query_editor', {
      user_id: this.userId,
      query_id: queryId,
    });
  }

  async leaveQueryEditor(queryId: string) {
    if (!this.userId) return;
    
    return this.emit('leave_query_editor', {
      user_id: this.userId,
      query_id: queryId,
    });
  }

  async updateCursorPosition(queryId: string, position: any, selection: any) {
    if (!this.userId) return;
    
    return this.emit('cursor_position', {
      user_id: this.userId,
      query_id: queryId,
      position,
      selection,
    });
  }

  // Comment Methods
  async notifyNewComment(entityType: string, entityId: string, comment: any) {
    return this.emit('new_comment', {
      entity_type: entityType,
      entity_id: entityId,
      comment,
    });
  }

  // Notification Methods
  async sendNotification(targetUserId: string, notification: any) {
    return this.emit('send_notification', {
      user_id: targetUserId,
      notification,
    });
  }

  isConnected(): boolean {
    return this.socket?.connected || false;
  }

  getUserId(): string | null {
    return this.userId;
  }
}

// Export singleton instance
export const websocketService = new WebSocketService();
export default websocketService;
