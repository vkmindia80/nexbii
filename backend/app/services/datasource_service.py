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
            if ds_type == DataSourceType.POSTGRESQL or ds_type == DataSourceType.TIMESCALEDB:
                conn = psycopg2.connect(
                    host=config.get("host"),
                    port=config.get("port", 5432),
                    database=config.get("database"),
                    user=config.get("user"),
                    password=config.get("password")
                )
                conn.close()
                return True
            
            elif ds_type == DataSourceType.MYSQL or ds_type == DataSourceType.MARIADB:
                conn = mysql.connector.connect(
                    host=config.get("host"),
                    port=config.get("port", 3306),
                    database=config.get("database"),
                    user=config.get("user"),
                    password=config.get("password")
                )
                conn.close()
                return True
            
            elif ds_type == DataSourceType.MSSQL:
                if not MSSQL_AVAILABLE:
                    return False
                conn = pymssql.connect(
                    server=config.get("host"),
                    port=config.get("port", 1433),
                    database=config.get("database"),
                    user=config.get("user"),
                    password=config.get("password")
                )
                conn.close()
                return True
            
            elif ds_type == DataSourceType.ORACLE:
                if not ORACLE_AVAILABLE:
                    return False
                dsn = cx_Oracle.makedsn(
                    config.get("host"),
                    config.get("port", 1521),
                    service_name=config.get("service_name") or config.get("database")
                )
                conn = cx_Oracle.connect(
                    user=config.get("user"),
                    password=config.get("password"),
                    dsn=dsn
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
            
            elif ds_type == DataSourceType.CASSANDRA:
                if not CASSANDRA_AVAILABLE:
                    return False
                cluster = Cluster([config.get("host")], port=config.get("port", 9042))
                session = cluster.connect()
                cluster.shutdown()
                return True
            
            elif ds_type == DataSourceType.REDIS:
                if not REDIS_AVAILABLE:
                    return False
                r = redis.Redis(
                    host=config.get("host"),
                    port=config.get("port", 6379),
                    password=config.get("password"),
                    db=config.get("database", 0)
                )
                r.ping()
                return True
            
            elif ds_type == DataSourceType.ELASTICSEARCH:
                if not ELASTICSEARCH_AVAILABLE:
                    return False
                es = Elasticsearch(
                    [f"{config.get('host')}:{config.get('port', 9200)}"],
                    basic_auth=(config.get("user"), config.get("password")) if config.get("user") else None
                )
                es.ping()
                return True
            
            elif ds_type == DataSourceType.CLICKHOUSE:
                if not CLICKHOUSE_AVAILABLE:
                    return False
                client = clickhouse_connect.get_client(
                    host=config.get("host"),
                    port=config.get("port", 8123),
                    username=config.get("user"),
                    password=config.get("password"),
                    database=config.get("database", "default")
                )
                client.ping()
                return True
            
            elif ds_type == DataSourceType.SNOWFLAKE:
                if not SNOWFLAKE_AVAILABLE:
                    return False
                conn = snowflake_connect(
                    user=config.get("user"),
                    password=config.get("password"),
                    account=config.get("account"),
                    warehouse=config.get("warehouse"),
                    database=config.get("database"),
                    schema=config.get("schema", "PUBLIC")
                )
                conn.close()
                return True
            
            elif ds_type == DataSourceType.REDSHIFT:
                # Redshift uses PostgreSQL protocol
                conn = psycopg2.connect(
                    host=config.get("host"),
                    port=config.get("port", 5439),
                    database=config.get("database"),
                    user=config.get("user"),
                    password=config.get("password")
                )
                conn.close()
                return True
            
            elif ds_type == DataSourceType.BIGQUERY:
                if not BIGQUERY_AVAILABLE:
                    return False
                client = bigquery.Client(
                    project=config.get("project_id"),
                    credentials=config.get("credentials")  # Service account JSON
                )
                # Test query
                query = "SELECT 1"
                client.query(query).result()
                return True
            
            elif ds_type == DataSourceType.DYNAMODB:
                if not BOTO3_AVAILABLE:
                    return False
                dynamodb = boto3.resource(
                    'dynamodb',
                    region_name=config.get("region"),
                    aws_access_key_id=config.get("access_key_id"),
                    aws_secret_access_key=config.get("secret_access_key")
                )
                # List tables to test connection
                list(dynamodb.tables.all())
                return True
            
            elif ds_type == DataSourceType.COUCHDB:
                if not COUCHDB_AVAILABLE:
                    return False
                server = couchdb.Server(
                    f"http://{config.get('host')}:{config.get('port', 5984)}"
                )
                if config.get("user"):
                    server.resource.credentials = (config.get("user"), config.get("password"))
                server.version()
                return True
            
            elif ds_type == DataSourceType.SQLITE:
                conn = sqlite3.connect(config.get("database_path") or config.get("database"))
                conn.close()
                return True
            
            # File-based sources (CSV, Excel, JSON, Parquet) don't need connection testing
            elif ds_type in [DataSourceType.CSV, DataSourceType.EXCEL, DataSourceType.JSON_FILE, DataSourceType.PARQUET]:
                return True
            
            return True
        except Exception as e:
            print(f"Connection test failed for {ds_type}: {str(e)}")
            return False
    
    async def get_schema(self, ds_type: DataSourceType, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get schema information from a data source"""
        tables = []
        
        try:
            if ds_type in [DataSourceType.POSTGRESQL, DataSourceType.TIMESCALEDB]:
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
            
            elif ds_type in [DataSourceType.MYSQL, DataSourceType.MARIADB]:
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
            
            elif ds_type == DataSourceType.MSSQL:
                if MSSQL_AVAILABLE:
                    conn = pymssql.connect(
                        server=config.get("host"),
                        port=config.get("port", 1433),
                        database=config.get("database"),
                        user=config.get("user"),
                        password=config.get("password")
                    )
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        SELECT TABLE_NAME 
                        FROM INFORMATION_SCHEMA.TABLES 
                        WHERE TABLE_TYPE = 'BASE TABLE'
                    """)
                    table_names = cursor.fetchall()
                    
                    for (table_name,) in table_names:
                        cursor.execute("""
                            SELECT COLUMN_NAME, DATA_TYPE 
                            FROM INFORMATION_SCHEMA.COLUMNS 
                            WHERE TABLE_NAME = ?
                        """, (table_name,))
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
            
            elif ds_type == DataSourceType.REDSHIFT:
                # Redshift uses PostgreSQL protocol
                conn = psycopg2.connect(
                    host=config.get("host"),
                    port=config.get("port", 5439),
                    database=config.get("database"),
                    user=config.get("user"),
                    password=config.get("password")
                )
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                """)
                table_names = cursor.fetchall()
                
                for (table_name,) in table_names:
                    cursor.execute(f"""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = '{table_name}'
                    """)
                    columns = cursor.fetchall()
                    
                    tables.append({
                        "name": table_name,
                        "columns": [{"name": col[0], "type": col[1]} for col in columns]
                    })
                
                conn.close()
            
            elif ds_type == DataSourceType.CLICKHOUSE:
                if CLICKHOUSE_AVAILABLE:
                    client = clickhouse_connect.get_client(
                        host=config.get("host"),
                        port=config.get("port", 8123),
                        username=config.get("user"),
                        password=config.get("password"),
                        database=config.get("database", "default")
                    )
                    
                    result = client.query("SHOW TABLES")
                    table_names = [row[0] for row in result.result_rows]
                    
                    for table_name in table_names:
                        result = client.query(f"DESCRIBE TABLE {table_name}")
                        columns = [{"name": row[0], "type": row[1]} for row in result.result_rows]
                        
                        tables.append({
                            "name": table_name,
                            "columns": columns
                        })
            
            elif ds_type == DataSourceType.SNOWFLAKE:
                if SNOWFLAKE_AVAILABLE:
                    conn = snowflake_connect(
                        user=config.get("user"),
                        password=config.get("password"),
                        account=config.get("account"),
                        warehouse=config.get("warehouse"),
                        database=config.get("database"),
                        schema=config.get("schema", "PUBLIC")
                    )
                    cursor = conn.cursor()
                    
                    cursor.execute("SHOW TABLES")
                    table_names = cursor.fetchall()
                    
                    for row in table_names:
                        table_name = row[1]  # Table name is in the second column
                        cursor.execute(f"DESCRIBE TABLE {table_name}")
                        columns = cursor.fetchall()
                        
                        tables.append({
                            "name": table_name,
                            "columns": [{"name": col[0], "type": col[1]} for col in columns]
                        })
                    
                    conn.close()
            
            elif ds_type == DataSourceType.ELASTICSEARCH:
                if ELASTICSEARCH_AVAILABLE:
                    es = Elasticsearch(
                        [f"{config.get('host')}:{config.get('port', 9200)}"],
                        basic_auth=(config.get("user"), config.get("password")) if config.get("user") else None
                    )
                    
                    # Get all indices
                    indices = es.indices.get_alias(index="*")
                    
                    for index_name in indices.keys():
                        if not index_name.startswith('.'):  # Skip system indices
                            # Get mapping to infer schema
                            mapping = es.indices.get_mapping(index=index_name)
                            properties = mapping[index_name]["mappings"].get("properties", {})
                            
                            columns = [{"name": field, "type": props.get("type", "unknown")} 
                                     for field, props in properties.items()]
                            
                            tables.append({
                                "name": index_name,
                                "columns": columns
                            })
            
            elif ds_type == DataSourceType.CASSANDRA:
                if CASSANDRA_AVAILABLE:
                    cluster = Cluster([config.get("host")], port=config.get("port", 9042))
                    session = cluster.connect()
                    
                    # Get keyspaces
                    keyspace = config.get("keyspace", "system")
                    session.set_keyspace(keyspace)
                    
                    # Get tables in keyspace
                    rows = session.execute(f"""
                        SELECT table_name 
                        FROM system_schema.tables 
                        WHERE keyspace_name = '{keyspace}'
                    """)
                    
                    for row in rows:
                        table_name = row.table_name
                        
                        # Get columns
                        col_rows = session.execute(f"""
                            SELECT column_name, type 
                            FROM system_schema.columns 
                            WHERE keyspace_name = '{keyspace}' AND table_name = '{table_name}'
                        """)
                        
                        columns = [{"name": col_row.column_name, "type": col_row.type} 
                                 for col_row in col_rows]
                        
                        tables.append({
                            "name": table_name,
                            "columns": columns
                        })
                    
                    cluster.shutdown()
            
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
            print(f"Schema retrieval failed for {ds_type}: {str(e)}")
        
        return tables