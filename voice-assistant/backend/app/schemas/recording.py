from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class RecordingBase(BaseModel):
    session_id: str
    file_path: str
    video_url: Optional[str] = None  # HTTP URL to access file
    format: str  # "audio" or "video"
    duration_seconds: Optional[float] = None
    file_size_bytes: Optional[int] = None
    storage_provider: str = "local"


class RecordingCreate(BaseModel):
    candidate_id: int
    session_id: str
    format: str


class RecordingResponse(RecordingBase):
    id: int
    candidate_id: int
    file_version: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TranscriptSegment(BaseModel):
    id: Optional[int] = None
    start: float
    end: float
    text: str
    confidence: Optional[float] = None
    speaker: Optional[str] = None


class DiarizationData(BaseModel):
    speakers: List[str]
    segments: List[Dict[str, Any]]


class TranscriptBase(BaseModel):
    transcript_json: Dict[str, Any]
    diarization_data: Optional[Dict[str, Any]] = None
    confidence_scores: Optional[List[float]] = None
    segments: Optional[List[TranscriptSegment]] = None
    quality_score: Optional[float] = None


class TranscriptResponse(TranscriptBase):
    id: int
    recording_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProcessingRequest(BaseModel):
    candidate_id: int
    session_id: str
    jd_id: Optional[int] = None


class ProcessingResponse(BaseModel):
    session_id: str
    status: str  # "processing", "completed", "failed"
    current_stage: Optional[str] = None
    error_message: Optional[str] = None
    match_result_id: Optional[int] = None
    next_steps: Optional[Dict[str, Any]] = None

