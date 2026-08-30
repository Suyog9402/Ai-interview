from typing import Dict, List, Any
from datetime import datetime


class EvidenceTracker:
    """Tracks evidence for skills and requirements from resume and transcript"""
    
    def __init__(self):
        self.evidence_map: Dict[str, List[Dict[str, Any]]] = {}
    
    def add_evidence(
        self,
        skill: str,
        source: str,  # "resume" or "transcript"
        location: Dict[str, Any],  # chunk_id, timestamp, etc.
        confidence: float
    ) -> None:
        """
        Add evidence for a skill.
        
        Args:
            skill: Skill name
            source: Source of evidence ("resume" or "transcript")
            location: Location information (chunk_id, timestamp, etc.)
            confidence: Confidence score (0-1)
        """
        if skill not in self.evidence_map:
            self.evidence_map[skill] = []
        
        self.evidence_map[skill].append({
            "source": source,
            "location": location,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_evidence(self, skill: str) -> List[Dict[str, Any]]:
        """
        Get all evidence for a skill.
        
        Args:
            skill: Skill name
        
        Returns:
            List of evidence dictionaries
        """
        return self.evidence_map.get(skill, [])
    
    def has_evidence(self, skill: str) -> bool:
        """
        Check if there is evidence for a skill.
        
        Args:
            skill: Skill name
        
        Returns:
            True if evidence exists
        """
        return skill in self.evidence_map and len(self.evidence_map[skill]) > 0
    
    def get_evidence_map(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get the complete evidence map.
        
        Returns:
            Dictionary mapping skills to evidence lists
        """
        return self.evidence_map.copy()
    
    def get_best_evidence(self, skill: str) -> Dict[str, Any] | None:
        """
        Get the best (highest confidence) evidence for a skill.
        
        Args:
            skill: Skill name
        
        Returns:
            Best evidence dictionary or None
        """
        evidence_list = self.get_evidence(skill)
        if not evidence_list:
            return None
        
        return max(evidence_list, key=lambda x: x.get("confidence", 0.0))
    
    def get_all_skills(self) -> List[str]:
        """
        Get list of all skills with evidence.
        
        Returns:
            List of skill names
        """
        return list(self.evidence_map.keys())

