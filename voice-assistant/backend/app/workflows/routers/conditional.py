from typing import Literal
from app.workflows.state import InterviewPipelineState


def should_retranscribe(state: InterviewPipelineState) -> Literal["retry", "continue"]:
    """
    Determine if transcription should be retried based on quality.
    
    Args:
        state: Current workflow state
    
    Returns:
        "retry" to retranscribe, "continue" to proceed
    """
    quality_issues = state.get("quality_issues", [])
    retry_count = state.get("retry_count", 0)
    max_retries = 2
    
    if quality_issues and retry_count < max_retries:
        return "retry"
    
    return "continue"


def should_continue_after_filters(state: InterviewPipelineState) -> Literal["stop", "continue"]:
    """
    Determine if workflow should continue after hard filter check.
    
    Args:
        state: Current workflow state
    
    Returns:
        "stop" to end workflow, "continue" to proceed
    """
    should_continue = state.get("should_continue", False)
    
    if should_continue:
        return "continue"
    
    return "stop"

