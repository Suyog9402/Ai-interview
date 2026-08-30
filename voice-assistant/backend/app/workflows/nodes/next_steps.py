import logging
from typing import Dict, Any
from app.workflows.state import InterviewPipelineState
from app.services.memory.manager import MemoryManager
from sqlalchemy.orm import Session
from app.db.database import get_db

logger = logging.getLogger(__name__)


async def update_memory_node(state: InterviewPipelineState) -> Dict[str, Any]:
    """
    Update memory with interview results.
    
    Args:
        state: Current workflow state
    
    Returns:
        Updated state
    """
    try:
        candidate_id = state.get("candidate_id")
        session_id = state.get("session_id")
        
        if not candidate_id or not session_id:
            return {
                **state,
                "memory_updated": True,  # Don't block on memory update failure
                "should_continue": True
            }
        
        # Get memory manager
        db = next(get_db())
        memory_manager = MemoryManager(db)
        
        # Get working memory
        working_memory = memory_manager.get_working_memory(session_id)
        
        # Update with extracted data
        resume_data = state.get("extracted_resume_data", {})
        transcript_data = state.get("extracted_transcript_data", {})
        match_result = state.get("match_result", {})
        
        # Update skill coverage
        if resume_data.get("skills"):
            for skill in resume_data["skills"]:
                working_memory.update_skill_coverage(skill, True, "resume")
        
        if transcript_data.get("skills"):
            for skill in transcript_data["skills"]:
                working_memory.update_skill_coverage(skill, True, "transcript")
        
        # Add strengths/weaknesses from match result
        if match_result.get("score_breakdown"):
            for dimension, score in match_result["score_breakdown"].items():
                if score >= 0.8:
                    working_memory.add_strength(f"Strong {dimension}", f"Score: {score:.2f}")
                elif score < 0.5:
                    working_memory.add_weakness(f"Weak {dimension}", f"Score: {score:.2f}")
        
        # Consolidate to long-term memory
        await memory_manager.consolidate_session(candidate_id, session_id)
        
        return {
            **state,
            "memory_updated": True,
            "should_continue": True
        }
        
    except Exception as e:
        logger.error(f"Error updating memory: {e}", exc_info=True)
        # Don't block workflow on memory update failure
        return {
            **state,
            "memory_updated": True,
            "should_continue": True
        }


async def next_steps_node(state: InterviewPipelineState) -> Dict[str, Any]:
    """
    Generate next steps based on match results.
    
    Args:
        state: Current workflow state
    
    Returns:
        Updated state with next steps
    """
    try:
        match_result = state.get("match_result", {})
        
        if not match_result:
            return {
                **state,
                "next_steps": {"next_steps": [], "recommended_actions": []}
            }
        
        weighted_score = match_result.get("weighted_score", 0.0)
        threshold_passed = match_result.get("threshold_passed", False)
        hard_filter_passed = match_result.get("hard_filter_passed", False)
        
        next_steps = []
        
        if not hard_filter_passed:
            next_steps.append({
                "action": "reject",
                "priority": "high",
                "reason": "Failed hard filters (must-have requirements not met)",
                "details": match_result.get("hard_filter_reasons", [])
            })
        elif not threshold_passed:
            next_steps.append({
                "action": "reject",
                "priority": "high",
                "reason": f"Match score {weighted_score:.1%} below threshold",
                "details": []
            })
        elif weighted_score >= 0.8:
            next_steps.append({
                "action": "schedule_interview",
                "priority": "high",
                "reason": f"Strong match: {weighted_score:.1%}",
                "details": []
            })
        elif weighted_score >= 0.65:
            next_steps.append({
                "action": "technical_assessment",
                "priority": "medium",
                "reason": f"Good match: {weighted_score:.1%}, verify technical skills",
                "details": []
            })
        else:
            next_steps.append({
                "action": "review",
                "priority": "low",
                "reason": f"Moderate match: {weighted_score:.1%}, requires review",
                "details": []
            })
        
        # Add skill-specific recommendations
        evidence_map = match_result.get("evidence_map", {})
        if evidence_map:
            # Identify gaps
            score_breakdown = match_result.get("score_breakdown", {})
            for dimension, score in score_breakdown.items():
                if score < 0.6:
                    next_steps.append({
                        "action": "skill_development",
                        "dimension": dimension,
                        "priority": "low",
                        "reason": f"Low {dimension} score: {score:.1%}"
                    })
        
        return {
            **state,
            "next_steps": {
                "next_steps": next_steps,
                "recommended_actions": next_steps
            },
            "should_continue": True
        }
        
    except Exception as e:
        logger.error(f"Error generating next steps: {e}", exc_info=True)
        return {
            **state,
            "next_steps": {"next_steps": [], "recommended_actions": []},
            "should_continue": True
        }

