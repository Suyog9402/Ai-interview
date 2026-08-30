from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class WorkingMemory:
    """Working memory for current interview session (ephemeral)"""
    
    def __init__(self, session_id: str):
        """
        Initialize working memory for a session.
        
        Args:
            session_id: Session identifier
        """
        self.session_id = session_id
        self.memory: Dict[str, Any] = {
            "current_context": {},
            "skill_coverage": {},
            "candidate_profile": {
                "strengths": [],
                "weaknesses": [],
                "experience_indicators": []
            },
            "voice_analysis_buffer": [],
            "conversation_state": []
        }
        self.created_at = datetime.now()
        self.ttl_hours = settings.memory_working_ttl_hours
    
    def update_current_context(
        self,
        question: Optional[str] = None,
        answer: Optional[str] = None,
        conversation_state: Optional[Dict] = None
    ) -> None:
        """Update current conversation context"""
        if question:
            self.memory["current_context"]["current_question"] = question
        if answer:
            self.memory["current_context"]["current_answer"] = answer
        if conversation_state:
            self.memory["current_context"].update(conversation_state)
    
    def update_skill_coverage(self, skill: str, covered: bool, source: str) -> None:
        """Update skill coverage map"""
        if "skill_coverage" not in self.memory:
            self.memory["skill_coverage"] = {}
        
        self.memory["skill_coverage"][skill] = {
            "covered": covered,
            "source": source,
            "timestamp": datetime.now().isoformat()
        }
    
    def add_strength(self, strength: str, evidence: Optional[str] = None) -> None:
        """Add identified strength"""
        self.memory["candidate_profile"]["strengths"].append({
            "strength": strength,
            "evidence": evidence,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_weakness(self, weakness: str, evidence: Optional[str] = None) -> None:
        """Add identified weakness"""
        self.memory["candidate_profile"]["weaknesses"].append({
            "weakness": weakness,
            "evidence": evidence,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_voice_metric(self, metric: Dict[str, Any]) -> None:
        """Add voice analysis metric"""
        self.memory["voice_analysis_buffer"].append({
            **metric,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_memory(self) -> Dict[str, Any]:
        """Get complete working memory"""
        return self.memory.copy()
    
    def is_expired(self) -> bool:
        """Check if working memory has expired"""
        age = datetime.now() - self.created_at
        return age > timedelta(hours=self.ttl_hours)
    
    def get_covered_skills(self) -> List[str]:
        """Get list of covered skills"""
        coverage = self.memory.get("skill_coverage", {})
        return [skill for skill, data in coverage.items() if data.get("covered", False)]
    
    def get_uncovered_skills(self, required_skills: List[str]) -> List[str]:
        """Get list of uncovered required skills"""
        covered = set(self.get_covered_skills())
        return [skill for skill in required_skills if skill.lower() not in [s.lower() for s in covered]]

