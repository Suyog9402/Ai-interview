import logging
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.jd import JobDescription, JDVersion
from app.models.matching import MatchResult, EvidenceTracking
from app.models.admin import AdminSetting
from app.services.matching.hard_filters import check_hard_filters
from app.services.matching.weighted_scoring import calculate_weighted_score
from app.services.matching.evidence_tracker import EvidenceTracker
from app.services.matching.explanation_generator import generate_explanation
from app.core.config import settings
from app.core.exceptions import MatchingException

logger = logging.getLogger(__name__)


class MatchingEngine:
    """Main matching engine that orchestrates hard filters and weighted scoring"""
    
    def __init__(self, db: Session):
        """
        Initialize matching engine.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def match_candidate_to_jd(
        self,
        candidate_id: int,
        jd_id: int,
        resume_data: Dict[str, Any],
        transcript_data: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> MatchResult:
        """
        Match candidate to job description.
        
        Args:
            candidate_id: Candidate ID
            jd_id: Job description ID
            resume_data: Extracted resume data
            transcript_data: Extracted transcript data
            session_id: Optional session ID
        
        Returns:
            MatchResult database object
        """
        try:
            # Load JD and requirements
            jd = self.db.query(JobDescription).filter(JobDescription.id == jd_id).first()
            if not jd:
                raise MatchingException(f"Job description {jd_id} not found")
            
            # Get active JD version
            jd_version = self.db.query(JDVersion).filter(
                JDVersion.jd_id == jd_id,
                JDVersion.is_active == True
            ).first()
            
            if not jd_version:
                raise MatchingException(f"No active version found for JD {jd_id}")
            
            jd_requirements = jd_version.requirements or {}
            
            # Get admin settings for this JD (or global defaults)
            admin_settings = self._get_matching_settings(jd_id)
            weights = admin_settings.get("weights", self._get_default_weights())
            threshold = admin_settings.get("threshold", settings.matching_default_threshold)
            hard_filter_enabled = admin_settings.get("hard_filter_enabled", settings.matching_hard_filter_enabled)
            
            # Initialize evidence tracker
            evidence_tracker = EvidenceTracker()
            
            # Step 1: Hard filters
            hard_filter_passed = True
            hard_filter_reasons = []
            
            if hard_filter_enabled:
                hard_filter_passed, hard_filter_reasons = check_hard_filters(
                    jd_requirements=jd_requirements,
                    resume_data=resume_data,
                    transcript_data=transcript_data,
                    settings=admin_settings
                )
            
            # Step 2: Weighted scoring (only if hard filters passed or disabled)
            weighted_score = 0.0
            score_breakdown = {}
            evidence_map = {}
            
            if hard_filter_passed or not hard_filter_enabled:
                weighted_score, score_breakdown, evidence_map = calculate_weighted_score(
                    jd_requirements=jd_requirements,
                    resume_data=resume_data,
                    transcript_data=transcript_data,
                    weights=weights,
                    evidence_tracker=evidence_tracker
                )
            
            # Check threshold
            threshold_passed = weighted_score >= threshold
            
            # Generate explanation
            match_result_dict = {
                "weighted_score": weighted_score,
                "score_breakdown": score_breakdown,
                "evidence_map": evidence_map,
                "hard_filter_passed": hard_filter_passed,
                "hard_filter_reasons": hard_filter_reasons,
                "threshold_passed": threshold_passed
            }
            
            explanation = generate_explanation(
                match_result=match_result_dict,
                jd_requirements=jd_requirements,
                candidate_data={**resume_data, **transcript_data}
            )
            
            # Get settings version ID
            settings_version_id = self._get_settings_version_id(jd_id)
            
            # Create or update match result
            existing_result = self.db.query(MatchResult).filter(
                MatchResult.candidate_id == candidate_id,
                MatchResult.jd_id == jd_id,
                MatchResult.session_id == session_id
            ).first()
            
            if existing_result:
                # Update existing
                existing_result.hard_filter_passed = hard_filter_passed
                existing_result.hard_filter_reasons = hard_filter_reasons
                existing_result.weighted_score = weighted_score
                existing_result.score_breakdown = score_breakdown
                existing_result.evidence_map = evidence_map
                existing_result.explanation = explanation
                existing_result.threshold_passed = threshold_passed
                existing_result.settings_version_id = settings_version_id
                
                self.db.add(existing_result)
                self.db.flush()
                match_result = existing_result
            else:
                # Create new
                match_result = MatchResult(
                    candidate_id=candidate_id,
                    jd_id=jd_id,
                    session_id=session_id,
                    hard_filter_passed=hard_filter_passed,
                    hard_filter_reasons=hard_filter_reasons,
                    weighted_score=weighted_score,
                    score_breakdown=score_breakdown,
                    evidence_map=evidence_map,
                    explanation=explanation,
                    threshold_passed=threshold_passed,
                    settings_version_id=settings_version_id
                )
                self.db.add(match_result)
                self.db.flush()
            
            # Store evidence tracking
            self._store_evidence_tracking(match_result.id, evidence_map)
            
            self.db.commit()
            self.db.refresh(match_result)
            
            logger.info(
                f"Match completed: candidate={candidate_id}, jd={jd_id}, "
                f"score={weighted_score:.2f}, passed={threshold_passed}"
            )
            
            return match_result
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Matching error: {e}", exc_info=True)
            raise MatchingException(f"Failed to match candidate to JD: {str(e)}")
    
    def _get_matching_settings(self, jd_id: Optional[int]) -> Dict[str, Any]:
        """Get matching settings for JD (or global defaults)"""
        # Try JD-specific settings first
        if jd_id:
            jd_setting = self.db.query(AdminSetting).filter(
                AdminSetting.jd_id == jd_id,
                AdminSetting.setting_name == "matching_config"
            ).order_by(AdminSetting.version.desc()).first()
            
            if jd_setting:
                return jd_setting.setting_value
        
        # Try global settings
        global_setting = self.db.query(AdminSetting).filter(
            AdminSetting.jd_id == None,
            AdminSetting.setting_name == "matching_config"
        ).order_by(AdminSetting.version.desc()).first()
        
        if global_setting:
            return global_setting.setting_value
        
        # Return defaults
        return {
            "weights": self._get_default_weights(),
            "threshold": settings.matching_default_threshold,
            "hard_filter_enabled": settings.matching_hard_filter_enabled
        }
    
    def _get_default_weights(self) -> Dict[str, float]:
        """Get default weight configuration"""
        return {
            "skills": 0.30,
            "experience": 0.20,
            "tools": 0.15,
            "education": 0.10,
            "projects": 0.15,
            "roles": 0.10
        }
    
    def _get_settings_version_id(self, jd_id: Optional[int]) -> Optional[int]:
        """Get the settings version ID used for this match"""
        if jd_id:
            setting = self.db.query(AdminSetting).filter(
                AdminSetting.jd_id == jd_id,
                AdminSetting.setting_name == "matching_config"
            ).order_by(AdminSetting.version.desc()).first()
            if setting:
                return setting.id
        
        setting = self.db.query(AdminSetting).filter(
            AdminSetting.jd_id == None,
            AdminSetting.setting_name == "matching_config"
        ).order_by(AdminSetting.version.desc()).first()
        
        return setting.id if setting else None
    
    def _store_evidence_tracking(
        self,
        match_result_id: int,
        evidence_map: Dict[str, Any]
    ) -> None:
        """Store evidence tracking records"""
        # Delete existing evidence for this match
        self.db.query(EvidenceTracking).filter(
            EvidenceTracking.match_result_id == match_result_id
        ).delete()
        
        # Store new evidence
        for skill, evidence_list in evidence_map.items():
            for evidence in evidence_list:
                evidence_tracking = EvidenceTracking(
                    match_result_id=match_result_id,
                    skill_name=skill,
                    evidence_type=evidence.get("source", "unknown"),
                    source_location=evidence.get("location", {}),
                    confidence=evidence.get("confidence", 0.0)
                )
                self.db.add(evidence_tracking)

