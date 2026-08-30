from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class RoleData(BaseModel):
    title: str
    company: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class ProjectData(BaseModel):
    name: str
    description: Optional[str] = None
    technologies: List[str] = []
    duration: Optional[str] = None
    achievements: List[str] = []


class AchievementData(BaseModel):
    title: str
    description: Optional[str] = None
    metrics: Optional[str] = None
    date: Optional[str] = None


class EducationData(BaseModel):
    degree: str
    institution: Optional[str] = None
    field: Optional[str] = None
    graduation_date: Optional[str] = None
    gpa: Optional[str] = None


class ExtractedDataBase(BaseModel):
    skills: List[str] = []
    tools: List[str] = []
    experience_years: Optional[float] = None
    roles: List[RoleData] = []
    projects: List[ProjectData] = []
    achievements: List[AchievementData] = []
    education: List[EducationData] = []
    companies: List[str] = []
    dates: Optional[Dict[str, str]] = None


class ResumeExtractionResponse(ExtractedDataBase):
    """Extracted data from resume"""
    pass


class TranscriptExtractionResponse(ExtractedDataBase):
    """Extracted data from transcript"""
    transcript_timestamps: Optional[List[Dict[str, Any]]] = None

