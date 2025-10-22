from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from ..models.datasource import DataSourceType

class DataSourceBase(BaseModel):
    name: str
    type: DataSourceType
    connection_config: Dict[str, Any]

class DataSourceCreate(DataSourceBase):
    pass

class DataSourceResponse(DataSourceBase):
    id: str
    created_by: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class DataSourceTest(BaseModel):
    type: DataSourceType
    connection_config: Dict[str, Any]

class SchemaResponse(BaseModel):
    tables: list[Dict[str, Any]]