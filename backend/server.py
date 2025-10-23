from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.api.v1 import auth, datasources, queries, dashboards, demo
from app.models.user import User, UserRole
from app.core.security import get_password_hash
import uvicorn
import uuid

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize demo user if it doesn't exist
def init_demo_user():
    db = SessionLocal()
    try:
        demo_user = db.query(User).filter(User.email == 'admin@nexbii.demo').first()
        if not demo_user:
            demo_user = User(
                id=str(uuid.uuid4()),
                email='admin@nexbii.demo',
                hashed_password=get_password_hash('demo123'),
                full_name='Demo Admin',
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(demo_user)
            db.commit()
            print('✅ Demo user created: admin@nexbii.demo / demo123')
    except Exception as e:
        print(f'⚠️  Error creating demo user: {e}')
        db.rollback()
    finally:
        db.close()

init_demo_user()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Advanced Business Intelligence & Analytics Platform"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(datasources.router, prefix="/api/datasources", tags=["Data Sources"])
app.include_router(queries.router, prefix="/api/queries", tags=["Queries"])
app.include_router(dashboards.router, prefix="/api/dashboards", tags=["Dashboards"])
app.include_router(demo.router, prefix="/api/demo", tags=["Demo Data"])

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

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)