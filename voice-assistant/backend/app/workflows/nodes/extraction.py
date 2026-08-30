import logging
from typing import Dict, Any
from app.workflows.state import InterviewPipelineState
from app.services.extraction import get_extractor
from app.core.exceptions import ExtractionException

logger = logging.getLogger(__name__)


async def extract_data_node(state: InterviewPipelineState) -> Dict[str, Any]:
    """
    Extract structured data from transcript and resume.
    
    Args:
        state: Current workflow state
    
    Returns:
        Updated state with extracted data
    """
    try:
        extractor = get_extractor()
        
        # Extract from transcript
        transcript_data = state.get("transcript_data")
        extracted_transcript_data = {}
        
        if transcript_data:
            extracted_transcript_data = await extractor.extract_from_transcript(
                transcript_data=transcript_data
            )
        
        # Resume data should already be extracted (from load_resume_node)
        # But we can re-extract if needed
        
        return {
            **state,
            "extracted_transcript_data": extracted_transcript_data,
            "extraction_complete": True,
            "should_continue": True
        }
        
    except ExtractionException as e:
        logger.error(f"Extraction error: {e}", exc_info=True)
        return {
            **state,
            "error_message": f"Extraction failed: {str(e)}",
            "should_continue": False
        }
    except Exception as e:
        logger.error(f"Unexpected error in extraction: {e}", exc_info=True)
        return {
            **state,
            "error_message": f"Unexpected error: {str(e)}",
            "should_continue": False
        }

