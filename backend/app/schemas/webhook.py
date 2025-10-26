from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, List
from datetime import datetime

# Available webhook events
AVAILABLE_EVENTS = [
    "datasource.created",
    "datasource.updated",
    "datasource.deleted",
    "query.created",
    "query.updated",
    "query.deleted",
    "query.executed",
    "dashboard.created",
    "dashboard.updated",
    "dashboard.deleted",
    "dashboard.viewed",
    "alert.triggered",
    "alert.resolved",
    "export.completed",
    "user.created",
    "user.updated",
    "user.deleted",
]

class WebhookBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    url: str = Field(..., min_length=1)
    events: List[str] = Field(default_factory=list)
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_backoff_seconds: int = Field(default=60, ge=10, le=3600)
    
    @validator('events')
    def validate_events(cls, v):
        """Validate that all events are valid"""
        if not v:
            raise ValueError("At least one event is required")
        
        invalid_events = [event for event in v if event not in AVAILABLE_EVENTS]
        if invalid_events:
            raise ValueError(f"Invalid events: {', '.join(invalid_events)}")
        
        return v
    
    @validator('url')
    def validate_url(cls, v):
        """Validate webhook URL"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v


class WebhookCreate(WebhookBase):
    """Schema for creating a new webhook"""
    secret: Optional[str] = Field(None, min_length=16, max_length=128)


class WebhookUpdate(BaseModel):
    """Schema for updating a webhook"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    url: Optional[str] = None
    events: Optional[List[str]] = None
    is_active: Optional[bool] = None
    max_retries: Optional[int] = Field(None, ge=0, le=10)
    retry_backoff_seconds: Optional[int] = Field(None, ge=10, le=3600)
    
    @validator('events')
    def validate_events(cls, v):
        """Validate that all events are valid"""
        if v is not None:
            if not v:
                raise ValueError("At least one event is required")
            
            invalid_events = [event for event in v if event not in AVAILABLE_EVENTS]
            if invalid_events:
                raise ValueError(f"Invalid events: {', '.join(invalid_events)}")
        
        return v
    
    @validator('url')
    def validate_url(cls, v):
        """Validate webhook URL"""
        if v is not None and not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v


class WebhookResponse(BaseModel):
    """Schema for webhook response"""
    id: str
    name: str
    description: Optional[str]
    url: str
    events: List[str]
    is_active: bool
    max_retries: int
    retry_backoff_seconds: int
    total_deliveries: int
    successful_deliveries: int
    failed_deliveries: int
    last_triggered_at: Optional[datetime]
    last_success_at: Optional[datetime]
    last_failure_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class WebhookDeliveryResponse(BaseModel):
    """Schema for webhook delivery log"""
    id: str
    webhook_id: str
    event_type: str
    status: str
    attempt_count: int
    max_attempts: int
    response_status_code: Optional[int]
    response_time_ms: Optional[int]
    error_message: Optional[str]
    next_retry_at: Optional[datetime]
    created_at: datetime
    delivered_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class WebhookTestRequest(BaseModel):
    """Schema for testing a webhook"""
    event_type: str = Field(default="test.webhook", description="Event type for testing")
    test_data: Optional[dict] = Field(default_factory=dict, description="Test payload data")


class WebhookTestResponse(BaseModel):
    """Response from testing a webhook"""
    success: bool
    status_code: Optional[int]
    response_time_ms: Optional[int]
    response_body: Optional[str]
    error_message: Optional[str]


class WebhookEventInfo(BaseModel):
    """Information about available webhook events"""
    event: str
    description: str
    category: str


class WebhookEventsResponse(BaseModel):
    """Response with all available events"""
    events: List[WebhookEventInfo]


class WebhookStatsResponse(BaseModel):
    """Webhook statistics"""
    webhook_id: str
    webhook_name: str
    total_deliveries: int
    successful_deliveries: int
    failed_deliveries: int
    success_rate: float
    avg_response_time_ms: Optional[float]
    deliveries_last_24h: int
    deliveries_last_7d: int
    deliveries_last_30d: int
    recent_deliveries: List[WebhookDeliveryResponse]
