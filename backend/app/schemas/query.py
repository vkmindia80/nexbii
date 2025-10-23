from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class QueryBase(BaseModel):
    name: str
    description: Optional[str] = None
    datasource_id: str
    query_type: str  # 'visual' or 'sql'
    query_config: Optional[Dict[str, Any]] = None
    sql_query: Optional[str] = None

class QueryCreate(QueryBase):
    pass

class QueryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    datasource_id: Optional[str] = None
    query_type: Optional[str] = None
    query_config: Optional[Dict[str, Any]] = None
    sql_query: Optional[str] = None

class QueryResponse(QueryBase):
    id: str
    created_by: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class QueryExecute(BaseModel):
    query_id: Optional[str] = None
    datasource_id: Optional[str] = None
    sql_query: Optional[str] = None
    limit: Optional[int] = 1000

class QueryResult(BaseModel):
    columns: list[str]
    rows: list[list[Any]]
    total_rows: int
    execution_time: float