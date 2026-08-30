import logging
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from app.workflows.state import InterviewPipelineState
from app.workflows.nodes.storage import store_recording_node, load_resume_node
from app.workflows.nodes.transcription import transcribe_node, check_quality_node, retranscribe_node
from app.workflows.nodes.extraction import extract_data_node
from app.workflows.nodes.matching import matching_node, hard_filter_check_node
from app.workflows.nodes.rag_query import rag_query_node
from app.workflows.nodes.next_steps import next_steps_node, update_memory_node
from app.workflows.routers.conditional import should_retranscribe, should_continue_after_filters

logger = logging.getLogger(__name__)


def build_interview_pipeline():
    """
    Build the LangGraph interview pipeline workflow.
    
    Returns:
        Compiled LangGraph workflow
    """
    workflow = StateGraph(InterviewPipelineState)
    
    # Add nodes
    workflow.add_node("store_recording", store_recording_node)
    workflow.add_node("transcribe", transcribe_node)
    workflow.add_node("check_transcription_quality", check_quality_node)
    workflow.add_node("retranscribe", retranscribe_node)
    workflow.add_node("extract_structured_data", extract_data_node)
    workflow.add_node("load_resume", load_resume_node)
    workflow.add_node("run_matching", matching_node)
    workflow.add_node("check_hard_filters", hard_filter_check_node)
    workflow.add_node("run_rag_query", rag_query_node)
    workflow.add_node("update_memory", update_memory_node)
    workflow.add_node("generate_next_steps", next_steps_node)
    
    # Define edges
    workflow.add_edge(START, "store_recording")
    workflow.add_edge("store_recording", "transcribe")
    workflow.add_edge("transcribe", "check_transcription_quality")
    
    # Conditional: quality check
    workflow.add_conditional_edges(
        "check_transcription_quality",
        should_retranscribe,
        {
            "retry": "retranscribe",
            "continue": "extract_structured_data"
        }
    )
    
    workflow.add_edge("retranscribe", "check_transcription_quality")
    workflow.add_edge("extract_structured_data", "load_resume")
    workflow.add_edge("load_resume", "run_matching")
    workflow.add_edge("run_matching", "check_hard_filters")
    
    # Conditional: hard filters
    workflow.add_conditional_edges(
        "check_hard_filters",
        should_continue_after_filters,
        {
            "stop": "generate_next_steps",  # Still generate next steps even if stopped
            "continue": "run_rag_query"
        }
    )
    
    workflow.add_edge("run_rag_query", "update_memory")
    workflow.add_edge("update_memory", "generate_next_steps")
    workflow.add_edge("generate_next_steps", END)
    
    # Compile workflow
    return workflow.compile(checkpointer=MemorySaver())

