from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, Field, ValidationError
from app.core.llm_provider import get_chat_llm
from langchain_core.prompts import ChatPromptTemplate
import os
import logging
import json
import re

logger = logging.getLogger(__name__)


class AnswerAssessmentResult(BaseModel):
    """Pydantic schema for structured answer assessment."""
    score: float = Field(default=50.0, ge=0.0, le=100.0)
    quality: Literal["excellent", "good", "fair", "poor"] = "fair"
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    topics_covered: List[str] = Field(default_factory=list)
    needs_followup: bool = False
    answer_felt_interesting: bool = False


class AnswerAssessor:
    """Assesses answer quality using LLM with Pydantic structured output validation."""
    
    def __init__(self):
        self.model = get_chat_llm(temperature=0.3, prefer="groq")
    
    def assess_answer(
        self, 
        question: str, 
        answer: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Assess candidate answer quality with structured schema validation and safe fallback."""
        if not self.model or not answer or not answer.strip():
            return self._simple_assess(answer or "")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical interviewer assessing candidate answers.

Analyze the answer and provide:
1. Quality score (0-100)
2. Quality level (excellent/good/fair/poor)
3. Strengths (list)
4. Weaknesses (list)
5. Topics covered (list)
6. Whether follow-up is needed (boolean)
7. answer_felt_interesting (boolean): true ONLY when the answer is excellent or good AND includes a concrete example, real project, or specific story (not generic).

Be strict but fair:
- Excellent (80-100): Deep understanding, concrete implementation experience, architecture trade-offs.
- Good (60-79): Solid understanding, clear explanation.
- Fair (40-59): Basic theoretical knowledge, lacks depth.
- Poor (0-39): Inaccurate or vague.

Return ONLY a valid JSON object matching this schema:
{
    "score": <0-100>,
    "quality": "<excellent|good|fair|poor>",
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "topics_covered": ["topic1", "topic2"],
    "needs_followup": <true|false>,
    "answer_felt_interesting": <true|false>
}"""),
            ("user", f"""Question: {question}

Answer: {answer}

Context: {context or 'None'}

Assess this answer and return JSON.""")
        ])
        
        content = ""
        try:
            response = self.model.invoke(prompt.format_messages())
            content = (getattr(response, "content", None) or str(response)).strip()
            
            # Clean markdown code fences safely using regex
            clean_json = re.sub(r"^```(?:json)?\s*", "", content, flags=re.MULTILINE)
            clean_json = re.sub(r"\s*```$", "", clean_json, flags=re.MULTILINE).strip()
            
            # Extract outermost JSON object
            json_match = re.search(r"\{.*\}", clean_json, re.DOTALL)
            if json_match:
                clean_json = json_match.group(0)
            
            raw_dict = json.loads(clean_json)
            validated = AnswerAssessmentResult.model_validate(raw_dict)
            return validated.model_dump()
            
        except (json.JSONDecodeError, ValidationError, Exception) as e:
            logger.warning(f"Answer assessor schema parse error: {e}. Falling back to deterministic assessment.")
            return self._simple_assess(answer)
    
    def _simple_assess(self, answer: str) -> Dict[str, Any]:
        """Deterministic offline assessment when LLM is offline or output is malformed."""
        answer_lower = (answer or "").lower()
        words = re.findall(r"\b[\w'-]+\b", answer_lower)
        length = len(words)
        
        if length < 8:
            return {
                "score": 25.0,
                "quality": "poor",
                "strengths": [],
                "weaknesses": ["Answer too brief or incomplete"],
                "topics_covered": [],
                "needs_followup": True,
                "answer_felt_interesting": False,
            }
        
        # Technical term check
        tech_terms = [
            "database", "api", "cache", "async", "redis", "postgresql", "docker",
            "microservices", "pipeline", "performance", "indexing", "latency"
        ]
        found = [t for t in tech_terms if t in answer_lower]
        
        if length > 40 and len(found) >= 2:
            return {
                "score": 75.0,
                "quality": "good",
                "strengths": ["Structured explanation", f"Referenced concepts: {', '.join(found[:3])}"],
                "weaknesses": [],
                "topics_covered": found,
                "needs_followup": False,
                "answer_felt_interesting": True,
            }
        elif length >= 15:
            return {
                "score": 60.0,
                "quality": "fair",
                "strengths": ["Clear communication"],
                "weaknesses": ["Could include more specific architectural examples"],
                "topics_covered": found,
                "needs_followup": True,
                "answer_felt_interesting": False,
            }
        else:
            return {
                "score": 45.0,
                "quality": "fair",
                "strengths": [],
                "weaknesses": ["Basic response, lacks depth"],
                "topics_covered": found,
                "needs_followup": True,
                "answer_felt_interesting": False,
            }
