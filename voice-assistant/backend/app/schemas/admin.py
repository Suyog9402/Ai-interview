from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class AdminUserBase(BaseModel):
    username: str
    email: str


class AdminUserCreate(AdminUserBase):
    password: str


class AdminUserResponse(AdminUserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AdminSettingBase(BaseModel):
    setting_name: str
    setting_value: Dict[str, Any]


class AdminSettingCreate(AdminSettingBase):
    jd_id: Optional[int] = None


class AdminSettingUpdate(BaseModel):
    setting_value: Dict[str, Any]


class AdminSettingResponse(AdminSettingBase):
    id: int
    jd_id: Optional[int] = None
    admin_id: int
    version: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MatchingConfig(BaseModel):
    """Matching configuration schema"""
    weights: Dict[str, float]
    threshold: float
    hard_filter_enabled: bool = True


class AuditLogResponse(BaseModel):
    id: int
    admin_id: int
    action_type: str
    resource_type: str
    resource_id: Optional[int] = None
    changes: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

