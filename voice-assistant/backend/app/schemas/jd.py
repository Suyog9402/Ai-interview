from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class JDRequirement(BaseModel):
    must_have_skills: List[str] = []
    nice_to_have_skills: List[str] = []
    must_have_tools: List[str] = []
    min_experience_years: float = 0.0
    required_qualifications: List[str] = []
    project_requirements: List[Dict[str, Any]] = []
    role_requirements: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []


class JDVersionBase(BaseModel):
    version_number: int
    content: str
    requirements: Optional[Dict[str, Any]] = None
    is_active: bool = False


class JDVersionCreate(JDVersionBase):
    jd_id: int


class JDVersionResponse(JDVersionBase):
    id: int
    jd_id: int
    admin_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class JDBase(BaseModel):
    title: str
    description: Optional[str] = None


class JDCreate(JDBase):
    content: str
    requirements: Optional[Dict[str, Any]] = None


class JDUpdate(JDBase):
    content: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None


class JDResponse(JDBase):
    id: int
    current_version_id: Optional[int] = None
    admin_id: int
    created_at: datetime
    updated_at: datetime
    current_version: Optional[JDVersionResponse] = None
    versions: Optional[List[JDVersionResponse]] = None
    
    class Config:
        from_attributes = True

