from typing import TypedDict, List, Dict, Any, Optional, Annotated
from operator import add


class InterviewPipelineState(TypedDict):
    """State schema for the interview pipeline workflow"""
    
    # Input
    candidate_id: int
    session_id: str
    recording_id: Optional[int]
    jd_id: Optional[int]
    
    # Processing stages
    recording_stored: bool
    transcription_complete: bool
    extraction_complete: bool
    matching_complete: bool
    rag_complete: bool
    memory_updated: bool
    
    # Data
    recording_path: Optional[str]
    transcript_data: Optional[Dict[str, Any]]
    extracted_resume_data: Optional[Dict[str, Any]]
    extracted_transcript_data: Optional[Dict[str, Any]]
    match_result: Optional[Dict[str, Any]]
    rag_results: Optional[List[Dict[str, Any]]]
    next_steps: Optional[Dict[str, Any]]
    
    # Control flow
    should_continue: bool
    error_message: Optional[str]
    quality_issues: Annotated[List[str], add]
    retry_count: int
    
    # Metadata
    processing_metadata: Dict[str, Any]

