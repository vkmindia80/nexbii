#!/bin/bash

echo "🚀 Starting NexBII Services..."
echo ""

# Start Redis
echo "1. Starting Redis..."
redis-server --daemonize yes --bind 127.0.0.1 --port 6379
sleep 2
if redis-cli ping > /dev/null 2>&1; then
    echo "   ✅ Redis started successfully"
else
    echo "   ❌ Redis failed to start"
fi

# Start Backend
echo ""
echo "2. Starting Backend (FastAPI)..."
cd /app/backend
/root/.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --workers 1 --reload > /var/log/supervisor/backend.out.log 2> /var/log/supervisor/backend.err.log &
BACKEND_PID=$!
echo "   Backend started with PID: $BACKEND_PID"
sleep 5

if curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
    echo "   ✅ Backend started successfully"
else
    echo "   ⚠️  Backend is starting... (may take a few more seconds)"
fi

# Start Frontend
echo ""
echo "3. Starting Frontend (React)..."
cd /app/frontend
yarn start > /var/log/supervisor/frontend.out.log 2> /var/log/supervisor/frontend.err.log &
FRONTEND_PID=$!
echo "   Frontend started with PID: $FRONTEND_PID"
echo "   ⏳ Frontend is starting... (this may take 20-30 seconds)"

echo ""
echo "📊 Service Status:"
echo "   - Backend:  http://localhost:8001 (PID: $BACKEND_PID)"
echo "   - Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
echo "   - Redis:    localhost:6379"
echo ""
echo "✅ All services have been started!"
echo ""
echo "📝 To check logs:"
echo "   Backend:  tail -f /var/log/supervisor/backend.out.log"
echo "   Frontend: tail -f /var/log/supervisor/frontend.out.log"
