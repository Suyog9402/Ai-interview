import logging
from typing import Dict, Any
from app.workflows.state import InterviewPipelineState
from app.services.matching.engine import MatchingEngine
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.exceptions import MatchingException

logger = logging.getLogger(__name__)


async def matching_node(state: InterviewPipelineState) -> Dict[str, Any]:
    """
    Run matching engine to match candidate to JD.
    
    Args:
        state: Current workflow state
    
    Returns:
        Updated state with match result
    """
    try:
        candidate_id = state.get("candidate_id")
        jd_id = state.get("jd_id")
        session_id = state.get("session_id")
        
        if not jd_id:
            return {
                **state,
                "error_message": "JD ID not provided",
                "should_continue": False
            }
        
        resume_data = state.get("extracted_resume_data", {})
        transcript_data = state.get("extracted_transcript_data", {})
        
        # Get database session
        db = next(get_db())
        matching_engine = MatchingEngine(db)
        
        # Run matching
        match_result_obj = await matching_engine.match_candidate_to_jd(
            candidate_id=candidate_id,
            jd_id=jd_id,
            resume_data=resume_data,
            transcript_data=transcript_data,
            session_id=session_id
        )
        
        # Convert to dictionary
        match_result = {
            "id": match_result_obj.id,
            "hard_filter_passed": match_result_obj.hard_filter_passed,
            "hard_filter_reasons": match_result_obj.hard_filter_reasons,
            "weighted_score": match_result_obj.weighted_score,
            "score_breakdown": match_result_obj.score_breakdown,
            "evidence_map": match_result_obj.evidence_map,
            "explanation": match_result_obj.explanation,
            "threshold_passed": match_result_obj.threshold_passed
        }
        
        return {
            **state,
            "match_result": match_result,
            "matching_complete": True,
            "should_continue": True
        }
        
    except MatchingException as e:
        logger.error(f"Matching error: {e}", exc_info=True)
        return {
            **state,
            "error_message": f"Matching failed: {str(e)}",
            "should_continue": False
        }
    except Exception as e:
        logger.error(f"Unexpected error in matching: {e}", exc_info=True)
        return {
            **state,
            "error_message": f"Unexpected error: {str(e)}",
            "should_continue": False
        }


async def hard_filter_check_node(state: InterviewPipelineState) -> Dict[str, Any]:
    """
    Check if hard filters passed and determine if workflow should continue.
    
    Args:
        state: Current workflow state
    
    Returns:
        Updated state with continuation decision
    """
    try:
        match_result = state.get("match_result")
        if not match_result:
            return {
                **state,
                "should_continue": False,
                "error_message": "Match result not available"
            }
        
        hard_filter_passed = match_result.get("hard_filter_passed", False)
        threshold_passed = match_result.get("threshold_passed", False)
        
        # Continue only if both hard filters and threshold passed
        should_continue = hard_filter_passed and threshold_passed
        
        return {
            **state,
            "should_continue": should_continue
        }
        
    except Exception as e:
        logger.error(f"Error in hard filter check: {e}", exc_info=True)
        return {
            **state,
            "should_continue": False,
            "error_message": f"Hard filter check failed: {str(e)}"
        }

