from typing import Dict, Any, List
import psycopg2
import mysql.connector
from pymongo import MongoClient
import sqlite3
from ..models.datasource import DataSourceType

# Optional imports for additional data sources (with fallback)
try:
    import pymssql
    MSSQL_AVAILABLE = True
except ImportError:
    MSSQL_AVAILABLE = False

try:
    import cx_Oracle
    ORACLE_AVAILABLE = True
except ImportError:
    ORACLE_AVAILABLE = False

try:
    from cassandra.cluster import Cluster
    CASSANDRA_AVAILABLE = True
except ImportError:
    CASSANDRA_AVAILABLE = False

try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

try:
    from elasticsearch import Elasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False

try:
    import clickhouse_connect
    CLICKHOUSE_AVAILABLE = True
except ImportError:
    CLICKHOUSE_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from google.cloud import bigquery
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False

try:
    from snowflake.connector import connect as snowflake_connect
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False

try:
    import couchdb
    COUCHDB_AVAILABLE = True
except ImportError:
    COUCHDB_AVAILABLE = False

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
                conn = sqlite3.connect(config.get("database_path") or config.get("database"))
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
                conn = sqlite3.connect(config.get("database_path") or config.get("database"))
                cursor = conn.cursor()
                
                # Get tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                table_names = cursor.fetchall()
                
                for (table_name,) in table_names:
                    # Get columns for each table
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]
                    
                    tables.append({
                        "name": table_name,
                        "columns": [{"name": col[1], "type": col[2]} for col in columns],
                        "row_count": row_count
                    })
                
                conn.close()
        
        except Exception as e:
            print(f"Schema retrieval failed: {str(e)}")
        
        return tables