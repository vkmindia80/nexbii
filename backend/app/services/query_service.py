from typing import Dict, Any
import psycopg2
import mysql.connector
from pymongo import MongoClient
import sqlite3
from ..models.datasource import DataSourceType

class QueryService:
    async def execute_query(
        self,
        ds_type: DataSourceType,
        config: Dict[str, Any],
        query: str,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """Execute a query against a data source"""
        
        if ds_type == DataSourceType.POSTGRESQL:
            return await self._execute_postgresql(config, query, limit)
        elif ds_type == DataSourceType.MYSQL:
            return await self._execute_mysql(config, query, limit)
        elif ds_type == DataSourceType.MONGODB:
            # MongoDB queries are handled differently
            return await self._execute_mongodb(config, query, limit)
        elif ds_type == DataSourceType.SQLITE:
            return await self._execute_sqlite(config, query, limit)
        else:
            raise ValueError(f"Unsupported data source type: {ds_type}")
    
    async def _execute_postgresql(self, config: Dict[str, Any], query: str, limit: int) -> Dict[str, Any]:
        conn = psycopg2.connect(
            host=config.get("host"),
            port=config.get("port", 5432),
            database=config.get("database"),
            user=config.get("user"),
            password=config.get("password")
        )
        cursor = conn.cursor()
        
        # Add limit if not present
        if "LIMIT" not in query.upper():
            query = f"{query} LIMIT {limit}"
        
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        conn.close()
        
        return {
            "columns": columns,
            "rows": [list(row) for row in rows]
        }
    
    async def _execute_mysql(self, config: Dict[str, Any], query: str, limit: int) -> Dict[str, Any]:
        conn = mysql.connector.connect(
            host=config.get("host"),
            port=config.get("port", 3306),
            database=config.get("database"),
            user=config.get("user"),
            password=config.get("password")
        )
        cursor = conn.cursor()
        
        # Add limit if not present
        if "LIMIT" not in query.upper():
            query = f"{query} LIMIT {limit}"
        
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        conn.close()
        
        return {
            "columns": columns,
            "rows": [list(row) for row in rows]
        }
    
    async def _execute_sqlite(self, config: Dict[str, Any], query: str, limit: int) -> Dict[str, Any]:
        # Support both 'database_path' and 'database' field names
        db_path = config.get("database_path") or config.get("database")
        if not db_path:
            raise ValueError("SQLite database path not specified in configuration")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Strip trailing semicolons and whitespace to avoid SQLite errors
        query = query.strip().rstrip(';').strip()
        
        # Add limit if not present
        if "LIMIT" not in query.upper():
            query = f"{query} LIMIT {limit}"
        
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        conn.close()
        
        return {
            "columns": columns,
            "rows": [list(row) for row in rows]
        }
    
    async def _execute_mongodb(self, config: Dict[str, Any], query: str, limit: int) -> Dict[str, Any]:
        # For MongoDB, query should be a JSON string representing the find query
        import json
        
        client = MongoClient(
            host=config.get("host"),
            port=config.get("port", 27017),
            username=config.get("user"),
            password=config.get("password")
        )
        db = client[config.get("database")]
        
        # Parse query (expecting format: {"collection": "name", "query": {}})
        query_obj = json.loads(query)
        collection_name = query_obj.get("collection")
        find_query = query_obj.get("query", {})
        
        collection = db[collection_name]
        results = list(collection.find(find_query).limit(limit))
        
        # Convert ObjectId to string
        for doc in results:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
        
        # Extract columns from first document
        columns = list(results[0].keys()) if results else []
        rows = [[doc.get(col) for col in columns] for doc in results]
        
        client.close()
        
        return {
            "columns": columns,
            "rows": rows
        }