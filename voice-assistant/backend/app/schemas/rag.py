from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class CitationLocation(BaseModel):
    chunk_id: Optional[str] = None
    timestamp: Optional[float] = None
    jd_section: Optional[str] = None
    resume_section: Optional[str] = None
    transcript_segment: Optional[int] = None


class Citation(BaseModel):
    source: str
    location: CitationLocation
    confidence: float
    page_content: Optional[str] = None


class RAGQuery(BaseModel):
    query: str
    candidate_id: Optional[int] = None
    source_types: Optional[List[str]] = None  # ["resume", "transcript", "jd"]
    filters: Optional[Dict[str, Any]] = None
    top_k: Optional[int] = None


class RAGResult(BaseModel):
    document_content: str
    citation: Citation
    score: float
    source: str


class RAGResponse(BaseModel):
    query: str
    results: List[RAGResult]
    total_results: int

