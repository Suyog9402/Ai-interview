import logging
from typing import Dict, Any
from app.workflows.state import InterviewPipelineState
from app.services.transcription import get_transcriber
from app.core.exceptions import TranscriptionException

logger = logging.getLogger(__name__)


async def transcribe_node(state: InterviewPipelineState) -> Dict[str, Any]:
    """
    Transcribe recording.
    
    Args:
        state: Current workflow state
    
    Returns:
        Updated state with transcript data
    """
    try:
        recording_path = state.get("recording_path")
        if not recording_path:
            return {
                **state,
                "error_message": "Recording path not found",
                "should_continue": False
            }
        
        transcriber = get_transcriber()
        transcript_data = await transcriber.transcribe_file(
            file_path=recording_path,
            enable_diarization=True
        )
        
        return {
            **state,
            "transcript_data": transcript_data,
            "transcription_complete": True,
            "should_continue": True
        }
        
    except TranscriptionException as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        return {
            **state,
            "error_message": f"Transcription failed: {str(e)}",
            "should_continue": False
        }
    except Exception as e:
        logger.error(f"Unexpected error in transcription: {e}", exc_info=True)
        return {
            **state,
            "error_message": f"Unexpected error: {str(e)}",
            "should_continue": False
        }


async def check_quality_node(state: InterviewPipelineState) -> Dict[str, Any]:
    """
    Check transcription quality.
    
    Args:
        state: Current workflow state
    
    Returns:
        Updated state with quality assessment
    """
    try:
        transcript_data = state.get("transcript_data")
        if not transcript_data:
            return {
                **state,
                "quality_issues": ["No transcript data available"],
                "should_continue": False
            }
        
        quality_score = transcript_data.get("quality_score", 0.0)
        quality_threshold = 0.7
        
        quality_issues = []
        if quality_score < quality_threshold:
            quality_issues.append(f"Low quality score: {quality_score:.2f} < {quality_threshold}")
        
        # Check for empty transcript
        if not transcript_data.get("transcript_json", {}).get("text"):
            quality_issues.append("Empty transcript")
        
        return {
            **state,
            "quality_issues": quality_issues,
            "should_continue": len(quality_issues) == 0
        }
        
    except Exception as e:
        logger.error(f"Error checking quality: {e}", exc_info=True)
        return {
            **state,
            "quality_issues": [f"Quality check error: {str(e)}"],
            "should_continue": False
        }


async def retranscribe_node(state: InterviewPipelineState) -> Dict[str, Any]:
    """
    Retranscribe recording if quality is low.
    
    Args:
        state: Current workflow state
    
    Returns:
        Updated state with new transcript
    """
    try:
        retry_count = state.get("retry_count", 0)
        max_retries = 2
        
        if retry_count >= max_retries:
            return {
                **state,
                "error_message": f"Max retries ({max_retries}) reached for transcription",
                "should_continue": False
            }
        
        # Retry transcription
        recording_path = state.get("recording_path")
        transcriber = get_transcriber()
        transcript_data = await transcriber.transcribe_file(
            file_path=recording_path,
            enable_diarization=True
        )
        
        return {
            **state,
            "transcript_data": transcript_data,
            "transcription_complete": True,
            "retry_count": retry_count + 1,
            "quality_issues": [],  # Clear previous issues
            "should_continue": True
        }
        
    except Exception as e:
        logger.error(f"Error in retranscription: {e}", exc_info=True)
        return {
            **state,
            "error_message": f"Retranscription failed: {str(e)}",
            "should_continue": False
        }

