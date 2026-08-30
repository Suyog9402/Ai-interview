import logging
from typing import Dict, Any
from app.workflows.state import InterviewPipelineState
from app.services.rag import get_rag_service
from app.core.exceptions import RAGException

logger = logging.getLogger(__name__)


async def rag_query_node(state: InterviewPipelineState) -> Dict[str, Any]:
    """
    Perform RAG query to retrieve relevant context.
    
    Args:
        state: Current workflow state
    
    Returns:
        Updated state with RAG results
    """
    try:
        # Only run RAG if matching passed
        if not state.get("should_continue", False):
            return {
                **state,
                "rag_complete": True,
                "rag_results": []
            }
        
        # Build query from match result and candidate data
        match_result = state.get("match_result", {})
        resume_data = state.get("extracted_resume_data", {})
        transcript_data = state.get("extracted_transcript_data", {})
        
        # Create query based on gaps or strengths
        query_parts = []
        
        if match_result.get("hard_filter_reasons"):
            query_parts.append(" ".join(match_result["hard_filter_reasons"][:3]))
        
        # Add skill gaps
        evidence_map = match_result.get("evidence_map", {})
        if evidence_map:
            query_parts.append("skills and experience")
        
        query = " ".join(query_parts) if query_parts else "candidate qualifications and experience"
        
        # Perform RAG retrieval
        rag_service = get_rag_service()
        candidate_id = state.get("candidate_id")
        
        rag_results = await rag_service.retrieve(
            query=query,
            source_types=["resume", "transcript", "jd"],
            filters={"candidate_id": candidate_id} if candidate_id else None
        )
        
        return {
            **state,
            "rag_results": rag_results,
            "rag_complete": True,
            "should_continue": True
        }
        
    except RAGException as e:
        logger.error(f"RAG error: {e}", exc_info=True)
        return {
            **state,
            "error_message": f"RAG query failed: {str(e)}",
            "rag_complete": True,  # Don't block workflow on RAG failure
            "rag_results": [],
            "should_continue": True
        }
    except Exception as e:
        logger.error(f"Unexpected error in RAG: {e}", exc_info=True)
        return {
            **state,
            "error_message": f"Unexpected RAG error: {str(e)}",
            "rag_complete": True,
            "rag_results": [],
            "should_continue": True
        }

