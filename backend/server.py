from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.api.v1 import auth, datasources, queries, dashboards, demo, cache, exports, sharing, subscriptions, comments, activities, alerts, integrations, ai, analytics, tenants, api_keys
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.services.websocket_service import socket_app, sio
from app.core.tenant_context import TenantContextMiddleware
import uvicorn
import uuid

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize demo tenant and user if they don't exist
def init_demo_data():
    from app.models.tenant import Tenant
    from datetime import datetime, timedelta
    
    db = SessionLocal()
    try:
        # Check if demo tenant exists
        demo_tenant = db.query(Tenant).filter(Tenant.slug == 'demo').first()
        if not demo_tenant:
            demo_tenant = Tenant(
                id=str(uuid.uuid4()),
                name='Demo Organization',
                slug='demo',
                contact_email='admin@nexbii.demo',
                contact_name='Demo Admin',
                plan='enterprise',  # Give full features for demo
                is_active=True,
                features={
                    "ai_enabled": True,
                    "advanced_analytics": True,
                    "white_labeling": True,
                    "api_access": True
                },
                trial_ends_at=datetime.utcnow() + timedelta(days=365)  # 1 year trial
            )
            db.add(demo_tenant)
            db.flush()
            print('✅ Demo tenant created: demo')
        
        # Check if demo user exists
        demo_user = db.query(User).filter(User.email == 'admin@nexbii.demo').first()
        if not demo_user:
            demo_user = User(
                id=str(uuid.uuid4()),
                email='admin@nexbii.demo',
                hashed_password=get_password_hash('demo123'),
                full_name='Demo Admin',
                role=UserRole.ADMIN,
                is_active=True,
                tenant_id=demo_tenant.id
            )
            db.add(demo_user)
            db.commit()
            print('✅ Demo user created: admin@nexbii.demo / demo123')
        elif not demo_user.tenant_id:
            # Update existing demo user to have tenant_id
            demo_user.tenant_id = demo_tenant.id
            db.commit()
            print('✅ Demo user updated with tenant association')
    except Exception as e:
        print(f'⚠️  Error creating demo data: {e}')
        db.rollback()
    finally:
        db.close()

init_demo_data()

# Start background monitoring for alerts and subscriptions
from app.services.background_monitor import background_monitor

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Advanced Business Intelligence & Analytics Platform"
)

@app.on_event("startup")
async def startup_event():
    """Start background services on startup"""
    background_monitor.start()
    print("✅ Background monitor started for alerts and subscriptions")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background services on shutdown"""
    background_monitor.stop()
    print("🛑 Background monitor stopped")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add tenant context middleware
app.add_middleware(TenantContextMiddleware)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tenants.router, prefix="/api/tenants", tags=["Multi-Tenancy"])
app.include_router(datasources.router, prefix="/api/datasources", tags=["Data Sources"])
app.include_router(queries.router, prefix="/api/queries", tags=["Queries"])
app.include_router(dashboards.router, prefix="/api/dashboards", tags=["Dashboards"])
app.include_router(demo.router, prefix="/api/demo", tags=["Demo Data"])
app.include_router(cache.router, prefix="/api/cache", tags=["Cache Management"])
app.include_router(exports.router, prefix="/api/exports", tags=["Exports"])
app.include_router(sharing.router, prefix="/api/sharing", tags=["Sharing"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["Subscriptions"])
app.include_router(comments.router, prefix="/api/comments", tags=["Comments"])
app.include_router(activities.router, prefix="/api/activities", tags=["Activities"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI Features"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/api")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

# Mount Socket.IO app for WebSocket support
app.mount("/socket.io", socket_app)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)