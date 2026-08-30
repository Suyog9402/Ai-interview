import logging
from typing import Dict, Any
from app.workflows.state import InterviewPipelineState
from app.services.storage import get_storage
from app.core.exceptions import StorageException

logger = logging.getLogger(__name__)


async def store_recording_node(state: InterviewPipelineState) -> Dict[str, Any]:
    """
    Store recording file in object storage.
    
    Args:
        state: Current workflow state
    
    Returns:
        Updated state
    """
    try:
        # This node expects recording to already be uploaded via API
        # We just verify it exists and get the path
        recording_id = state.get("recording_id")
        if not recording_id:
            return {
                **state,
                "error_message": "Recording ID not provided",
                "should_continue": False
            }
        
        # In a real implementation, we'd fetch recording from DB and verify storage
        # For now, we assume recording is already stored
        
        return {
            **state,
            "recording_stored": True,
            "should_continue": True
        }
        
    except Exception as e:
        logger.error(f"Error storing recording: {e}", exc_info=True)
        return {
            **state,
            "error_message": f"Failed to store recording: {str(e)}",
            "should_continue": False
        }


async def load_resume_node(state: InterviewPipelineState) -> Dict[str, Any]:
    """
    Load resume data for candidate.
    
    Args:
        state: Current workflow state
    
    Returns:
        Updated state with resume data
    """
    try:
        from sqlalchemy.orm import Session
        from app.db.database import get_db
        from app.models.candidate import Resume
        
        candidate_id = state.get("candidate_id")
        
        # Get database session (simplified - in production use dependency injection)
        db = next(get_db())
        
        # Get latest resume for candidate
        resume = db.query(Resume).filter(
            Resume.candidate_id == candidate_id
        ).order_by(Resume.created_at.desc()).first()
        
        if not resume:
            return {
                **state,
                "error_message": "No resume found for candidate",
                "should_continue": False
            }
        
        # Resume data should already be extracted and stored
        resume_data = resume.extracted_data or {}
        
        return {
            **state,
            "extracted_resume_data": resume_data,
            "should_continue": True
        }
        
    except Exception as e:
        logger.error(f"Error loading resume: {e}", exc_info=True)
        return {
            **state,
            "error_message": f"Failed to load resume: {str(e)}",
            "should_continue": False
        }

