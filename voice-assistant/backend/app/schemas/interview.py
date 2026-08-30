from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ConversationMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None

class InterviewSessionCreate(BaseModel):
    session_id: str
    conversation: List[ConversationMessage]
    questions: List[str]
    answers: List[str]

class InterviewResultResponse(BaseModel):
    session_id: str
    user_id: int
    total_score: int
    max_score: int
    percentage: float
    questions_evaluated: int
    overall_analysis: str
    detailed_feedback: List[Dict[str, Any]]
    strengths: List[str]
    areas_for_improvement: List[str]
    recommendations: List[str]
    transcript: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: datetime

class InterviewHistoryItem(BaseModel):
    session_id: str
    total_score: int
    max_score: int
    percentage: float
    created_at: datetime 