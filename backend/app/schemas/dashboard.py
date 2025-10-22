from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class DashboardBase(BaseModel):
    name: str
    description: Optional[str] = None
    layout: Optional[Dict[str, Any]] = None
    widgets: Optional[list[Dict[str, Any]]] = []
    filters: Optional[Dict[str, Any]] = None
    is_public: bool = False

class DashboardCreate(DashboardBase):
    pass

class DashboardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    layout: Optional[Dict[str, Any]] = None
    widgets: Optional[list[Dict[str, Any]]] = None
    filters: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None

class DashboardResponse(DashboardBase):
    id: str
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True