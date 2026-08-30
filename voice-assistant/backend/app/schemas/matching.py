from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class EvidenceLocation(BaseModel):
    chunk_id: Optional[str] = None
    timestamp: Optional[float] = None
    jd_section: Optional[str] = None
    resume_section: Optional[str] = None
    transcript_segment: Optional[int] = None


class EvidenceItem(BaseModel):
    source: str  # "resume" or "transcript"
    location: EvidenceLocation
    confidence: float
    timestamp: str


class MatchResultBase(BaseModel):
    hard_filter_passed: bool
    hard_filter_reasons: Optional[List[str]] = None
    weighted_score: float
    score_breakdown: Optional[Dict[str, float]] = None
    evidence_map: Optional[Dict[str, List[EvidenceItem]]] = None
    explanation: Optional[str] = None
    threshold_passed: bool


class MatchResultResponse(MatchResultBase):
    id: int
    candidate_id: int
    jd_id: int
    session_id: Optional[str] = None
    settings_version_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class MatchRequest(BaseModel):
    candidate_id: int
    jd_id: int
    session_id: Optional[str] = None

