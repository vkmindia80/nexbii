from typing import Dict, Any, List
import psycopg2
import mysql.connector
from pymongo import MongoClient
import sqlite3
from ..models.datasource import DataSourceType

class DataSourceService:
    async def test_connection(self, ds_type: DataSourceType, config: Dict[str, Any]) -> bool:
        """Test connection to a data source"""
        try:
            if ds_type == DataSourceType.POSTGRESQL:
                conn = psycopg2.connect(
                    host=config.get("host"),
                    port=config.get("port", 5432),
                    database=config.get("database"),
                    user=config.get("user"),
                    password=config.get("password")
                )
                conn.close()
                return True
            
            elif ds_type == DataSourceType.MYSQL:
                conn = mysql.connector.connect(
                    host=config.get("host"),
                    port=config.get("port", 3306),
                    database=config.get("database"),
                    user=config.get("user"),
                    password=config.get("password")
                )
                conn.close()
                return True
            
            elif ds_type == DataSourceType.MONGODB:
                client = MongoClient(
                    host=config.get("host"),
                    port=config.get("port", 27017),
                    username=config.get("user"),
                    password=config.get("password")
                )
                client.server_info()  # Test connection
                client.close()
                return True
            
            elif ds_type == DataSourceType.SQLITE:
                conn = sqlite3.connect(config.get("database_path"))
                conn.close()
                return True
            
            return True
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False
    
    async def get_schema(self, ds_type: DataSourceType, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get schema information from a data source"""
        tables = []
        
        try:
            if ds_type == DataSourceType.POSTGRESQL:
                conn = psycopg2.connect(
                    host=config.get("host"),
                    port=config.get("port", 5432),
                    database=config.get("database"),
                    user=config.get("user"),
                    password=config.get("password")
                )
                cursor = conn.cursor()
                
                # Get tables
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                table_names = cursor.fetchall()
                
                for (table_name,) in table_names:
                    # Get columns for each table
                    cursor.execute("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = %s
                    """, (table_name,))
                    columns = cursor.fetchall()
                    
                    tables.append({
                        "name": table_name,
                        "columns": [{"name": col[0], "type": col[1]} for col in columns]
                    })
                
                conn.close()
            
            elif ds_type == DataSourceType.MYSQL:
                conn = mysql.connector.connect(
                    host=config.get("host"),
                    port=config.get("port", 3306),
                    database=config.get("database"),
                    user=config.get("user"),
                    password=config.get("password")
                )
                cursor = conn.cursor()
                
                # Get tables
                cursor.execute("SHOW TABLES")
                table_names = cursor.fetchall()
                
                for (table_name,) in table_names:
                    # Get columns for each table
                    cursor.execute(f"DESCRIBE {table_name}")
                    columns = cursor.fetchall()
                    
                    tables.append({
                        "name": table_name,
                        "columns": [{"name": col[0], "type": col[1]} for col in columns]
                    })
                
                conn.close()
            
            elif ds_type == DataSourceType.MONGODB:
                client = MongoClient(
                    host=config.get("host"),
                    port=config.get("port", 27017),
                    username=config.get("user"),
                    password=config.get("password")
                )
                db = client[config.get("database")]
                collection_names = db.list_collection_names()
                
                for collection_name in collection_names:
                    # Sample document to infer schema
                    sample = db[collection_name].find_one()
                    columns = []
                    if sample:
                        columns = [{"name": key, "type": type(value).__name__} for key, value in sample.items()]
                    
                    tables.append({
                        "name": collection_name,
                        "columns": columns
                    })
                
                client.close()
            
            elif ds_type == DataSourceType.SQLITE:
                conn = sqlite3.connect(config.get("database_path"))
                cursor = conn.cursor()
                
                # Get tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                table_names = cursor.fetchall()
                
                for (table_name,) in table_names:
                    # Get columns for each table
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    
                    tables.append({
                        "name": table_name,
                        "columns": [{"name": col[1], "type": col[2]} for col in columns]
                    })
                
                conn.close()
        
        except Exception as e:
            print(f"Schema retrieval failed: {str(e)}")
        
        return tables