from pymongo import MongoClient
from .config import settings

# MongoDB for all data storage
mongo_client = MongoClient(settings.MONGO_URL)
mongo_db = mongo_client.get_database()

# Collections
users_collection = mongo_db["users"]
datasources_collection = mongo_db["datasources"]
queries_collection = mongo_db["queries"]
dashboards_collection = mongo_db["dashboards"]

def get_mongo_db():
    return mongo_db

def get_db():
    """For backward compatibility"""
    return mongo_db