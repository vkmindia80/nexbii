from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class EmailConfigBase(BaseModel):
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = None
    mock_email: bool = True

class EmailConfigCreate(EmailConfigBase):
    pass

class EmailConfigResponse(BaseModel):
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = None
    mock_email: bool = True
    # Note: We don't return the password
    
    class Config:
        from_attributes = True

class SlackConfigBase(BaseModel):
    slack_webhook_url: Optional[str] = None
    mock_slack: bool = True
    
    @validator('slack_webhook_url')
    def validate_webhook_url(cls, v):
        if v and not (v.startswith('https://hooks.slack.com/') or v.startswith('http://') or v.startswith('https://')):
            raise ValueError('Invalid webhook URL format')
        return v

class SlackConfigCreate(SlackConfigBase):
    pass

class SlackConfigResponse(BaseModel):
    slack_webhook_url: Optional[str] = None
    mock_slack: bool = True
    
    class Config:
        from_attributes = True

class IntegrationResponse(BaseModel):
    id: str
    email_config: EmailConfigResponse
    slack_config: SlackConfigResponse
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TestEmailRequest(BaseModel):
    test_email: EmailStr

class TestSlackRequest(BaseModel):
    test_message: Optional[str] = "Test message from NexBII"
