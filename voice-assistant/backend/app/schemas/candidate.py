from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class CandidateBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None


class CandidateCreate(CandidateBase):
    user_id: int


class CandidateUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None


class CandidateResponse(CandidateBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ResumeBase(BaseModel):
    file_path: str
    file_version: int = 1


class ResumeCreate(BaseModel):
    candidate_id: int
    file_path: str


class ResumeResponse(ResumeBase):
    id: int
    candidate_id: int
    extracted_data: Optional[dict] = None
    raw_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

