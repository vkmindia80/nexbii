"""
WebSocket Service for Real-time Collaboration
Handles user presence, live updates, and real-time notifications
"""
import socketio
from typing import Dict, Set, List
from datetime import datetime
import json

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=False
)

# Track connected users and their presence
connected_users: Dict[str, Set[str]] = {}  # {user_id: {sid1, sid2, ...}}
user_presence: Dict[str, dict] = {}  # {user_id: {name, last_seen, status}}
dashboard_viewers: Dict[str, Set[str]] = {}  # {dashboard_id: {user_id1, user_id2, ...}}
query_editors: Dict[str, Set[str]] = {}  # {query_id: {user_id1, user_id2, ...}}


class WebSocketService:
    """Manages WebSocket connections and real-time events"""
    
    @staticmethod
    async def broadcast_to_dashboard(dashboard_id: str, event: str, data: dict):
        """Broadcast event to all users viewing a dashboard"""
        if dashboard_id in dashboard_viewers:
            for user_id in dashboard_viewers[dashboard_id]:
                if user_id in connected_users:
                    for sid in connected_users[user_id]:
                        await sio.emit(event, data, room=sid)
    
    @staticmethod
    async def broadcast_to_query_editor(query_id: str, event: str, data: dict):
        """Broadcast event to all users editing a query"""
        if query_id in query_editors:
            for user_id in query_editors[query_id]:
                if user_id in connected_users:
                    for sid in connected_users[user_id]:
                        await sio.emit(event, data, room=sid)
    
    @staticmethod
    async def send_to_user(user_id: str, event: str, data: dict):
        """Send event to specific user (all their connections)"""
        if user_id in connected_users:
            for sid in connected_users[user_id]:
                await sio.emit(event, data, room=sid)
    
    @staticmethod
    def get_online_users() -> List[dict]:
        """Get list of all online users"""
        return [
            {"user_id": user_id, **presence}
            for user_id, presence in user_presence.items()
        ]
    
    @staticmethod
    def get_dashboard_viewers(dashboard_id: str) -> List[str]:
        """Get list of users viewing a dashboard"""
        return list(dashboard_viewers.get(dashboard_id, set()))
    
    @staticmethod
    def get_query_editors(query_id: str) -> List[str]:
        """Get list of users editing a query"""
        return list(query_editors.get(query_id, set()))


# Socket.IO Event Handlers

@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    print(f"Client connected: {sid}")
    return True

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    print(f"Client disconnected: {sid}")
    
    # Remove user from tracking
    user_id_to_remove = None
    for user_id, sids in connected_users.items():
        if sid in sids:
            sids.remove(sid)
            if not sids:  # No more connections for this user
                user_id_to_remove = user_id
            break
    
    if user_id_to_remove:
        del connected_users[user_id_to_remove]
        if user_id_to_remove in user_presence:
            del user_presence[user_id_to_remove]
        
        # Remove from dashboard viewers
        for dashboard_id in list(dashboard_viewers.keys()):
            if user_id_to_remove in dashboard_viewers[dashboard_id]:
                dashboard_viewers[dashboard_id].remove(user_id_to_remove)
                # Notify others in dashboard
                await sio.emit('user_left_dashboard', {
                    'user_id': user_id_to_remove,
                    'dashboard_id': dashboard_id
                }, skip_sid=sid)
        
        # Remove from query editors
        for query_id in list(query_editors.keys()):
            if user_id_to_remove in query_editors[query_id]:
                query_editors[query_id].remove(user_id_to_remove)
                # Notify others in query
                await sio.emit('user_left_query', {
                    'user_id': user_id_to_remove,
                    'query_id': query_id
                }, skip_sid=sid)

@sio.event
async def authenticate(sid, data):
    """Authenticate user and track presence"""
    user_id = data.get('user_id')
    user_name = data.get('user_name', 'Anonymous')
    
    if not user_id:
        return {'success': False, 'error': 'user_id required'}
    
    # Add to connected users
    if user_id not in connected_users:
        connected_users[user_id] = set()
    connected_users[user_id].add(sid)
    
    # Update presence
    user_presence[user_id] = {
        'name': user_name,
        'last_seen': datetime.utcnow().isoformat(),
        'status': 'online'
    }
    
    # Broadcast user online status
    await sio.emit('user_online', {
        'user_id': user_id,
        'name': user_name
    }, skip_sid=sid)
    
    return {'success': True, 'online_users': WebSocketService.get_online_users()}

@sio.event
async def join_dashboard(sid, data):
    """User joins a dashboard for viewing"""
    user_id = data.get('user_id')
    dashboard_id = data.get('dashboard_id')
    
    if not user_id or not dashboard_id:
        return {'success': False, 'error': 'user_id and dashboard_id required'}
    
    if dashboard_id not in dashboard_viewers:
        dashboard_viewers[dashboard_id] = set()
    dashboard_viewers[dashboard_id].add(user_id)
    
    # Notify others in dashboard
    await sio.emit('user_joined_dashboard', {
        'user_id': user_id,
        'dashboard_id': dashboard_id,
        'user_name': user_presence.get(user_id, {}).get('name', 'Anonymous')
    }, skip_sid=sid)
    
    return {
        'success': True,
        'viewers': list(dashboard_viewers[dashboard_id])
    }

@sio.event
async def leave_dashboard(sid, data):
    """User leaves a dashboard"""
    user_id = data.get('user_id')
    dashboard_id = data.get('dashboard_id')
    
    if dashboard_id in dashboard_viewers and user_id in dashboard_viewers[dashboard_id]:
        dashboard_viewers[dashboard_id].remove(user_id)
        
        # Notify others
        await sio.emit('user_left_dashboard', {
            'user_id': user_id,
            'dashboard_id': dashboard_id
        }, skip_sid=sid)
    
    return {'success': True}

@sio.event
async def dashboard_updated(sid, data):
    """Dashboard was updated, notify all viewers"""
    dashboard_id = data.get('dashboard_id')
    update_type = data.get('type', 'update')
    updated_by = data.get('user_id')
    
    if dashboard_id:
        await WebSocketService.broadcast_to_dashboard(
            dashboard_id,
            'dashboard_update',
            {
                'dashboard_id': dashboard_id,
                'type': update_type,
                'updated_by': updated_by,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    return {'success': True}

@sio.event
async def join_query_editor(sid, data):
    """User joins a query editor"""
    user_id = data.get('user_id')
    query_id = data.get('query_id')
    
    if not user_id or not query_id:
        return {'success': False, 'error': 'user_id and query_id required'}
    
    if query_id not in query_editors:
        query_editors[query_id] = set()
    query_editors[query_id].add(user_id)
    
    # Notify others
    await sio.emit('user_joined_query', {
        'user_id': user_id,
        'query_id': query_id,
        'user_name': user_presence.get(user_id, {}).get('name', 'Anonymous')
    }, skip_sid=sid)
    
    return {
        'success': True,
        'editors': list(query_editors[query_id])
    }

@sio.event
async def leave_query_editor(sid, data):
    """User leaves a query editor"""
    user_id = data.get('user_id')
    query_id = data.get('query_id')
    
    if query_id in query_editors and user_id in query_editors[query_id]:
        query_editors[query_id].remove(user_id)
        
        # Notify others
        await sio.emit('user_left_query', {
            'user_id': user_id,
            'query_id': query_id
        }, skip_sid=sid)
    
    return {'success': True}

@sio.event
async def cursor_position(sid, data):
    """Update cursor position in query editor"""
    user_id = data.get('user_id')
    query_id = data.get('query_id')
    position = data.get('position')
    selection = data.get('selection')
    
    if query_id in query_editors:
        # Broadcast to other editors (not sender)
        for editor_user_id in query_editors[query_id]:
            if editor_user_id != user_id and editor_user_id in connected_users:
                for editor_sid in connected_users[editor_user_id]:
                    await sio.emit('cursor_update', {
                        'user_id': user_id,
                        'user_name': user_presence.get(user_id, {}).get('name', 'Anonymous'),
                        'query_id': query_id,
                        'position': position,
                        'selection': selection
                    }, room=editor_sid)
    
    return {'success': True}

@sio.event
async def new_comment(sid, data):
    """New comment was added"""
    entity_type = data.get('entity_type')
    entity_id = data.get('entity_id')
    comment = data.get('comment')
    
    # Broadcast to relevant viewers
    if entity_type == 'dashboard':
        await WebSocketService.broadcast_to_dashboard(
            entity_id,
            'comment_added',
            {
                'entity_type': entity_type,
                'entity_id': entity_id,
                'comment': comment,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    elif entity_type == 'query':
        await WebSocketService.broadcast_to_query_editor(
            entity_id,
            'comment_added',
            {
                'entity_type': entity_type,
                'entity_id': entity_id,
                'comment': comment,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    return {'success': True}

@sio.event
async def send_notification(sid, data):
    """Send notification to specific user"""
    target_user_id = data.get('user_id')
    notification = data.get('notification')
    
    if target_user_id:
        await WebSocketService.send_to_user(
            target_user_id,
            'notification',
            notification
        )
    
    return {'success': True}


# Export service and socket instance
websocket_service = WebSocketService()
socket_app = socketio.ASGIApp(sio)
