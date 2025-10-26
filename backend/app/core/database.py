from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from .config import settings
import os

# SQLite for metadata (fallback if PostgreSQL not available)
# Use SQLite database file in /app/backend directory
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "nexbii.db")
SQLITE_URL = f"sqlite:///{db_path}"

# Try to use PostgreSQL, fallback to SQLite
try:
    engine = create_engine(settings.POSTGRES_URL, pool_pre_ping=True)
    engine.connect()
except Exception:
    # Fallback to SQLite
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MongoDB for document storage (optional)
mongo_client = MongoClient(settings.MONGO_URL)
mongo_db = mongo_client.get_default_database()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_url():
    """Get the database URL being used"""
    try:
        return settings.POSTGRES_URL
    except:
        return SQLITE_URL

def get_mongo_db():
    return mongo_db