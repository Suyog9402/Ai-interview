"""
Unit & Failure-Path Tests for LangGraph AI Interview Pipeline
Tests conditional router transitions, retry loops, hard-filter disqualification,
and fallback behavior with 0 external API calls.
"""
import pytest
from app.workflows.routers.conditional import should_retranscribe, should_continue_after_filters
from app.services.answer_assessor import AnswerAssessor
from app.services.extraction.llm_extractor import LLMExtractor

def test_transcription_quality_failure_triggers_retry():
    """When quality issues exist and retries < max, workflow routes to retranscribe."""
    state = {
        "quality_issues": ["low_word_count", "high_background_noise"],
        "retry_count": 0,
        "is_acceptable": False
    }
    decision = should_retranscribe(state)
    assert decision == "retry"

def test_transcription_max_retries_exhaustion_guards_loop():
    """When retries exceed max_retries, workflow continues to fallback extraction."""
    state = {
        "quality_issues": ["low_word_count"],
        "retry_count": 2,  # max_retries reached
        "is_acceptable": False
    }
    decision = should_retranscribe(state)
    assert decision == "continue"

def test_transcription_clean_quality_continues():
    """When no quality issues exist, workflow proceeds immediately to extraction."""
    state = {
        "quality_issues": [],
        "retry_count": 0,
        "is_acceptable": True
    }
    decision = should_retranscribe(state)
    assert decision == "continue"

def test_hard_filter_disqualification_terminates_early():
    """When candidate fails hard filters, workflow stops before expensive LLM evaluation."""
    state = {
        "should_continue": False,
        "passed_filters": False,
        "missing_critical_skills": ["Python", "PostgreSQL"]
    }
    decision = should_continue_after_filters(state)
    assert decision == "stop"

def test_hard_filter_passed_continues():
    """When candidate passes hard filters, workflow proceeds to RAG & evaluation."""
    state = {
        "should_continue": True,
        "passed_filters": True,
        "missing_critical_skills": []
    }
    decision = should_continue_after_filters(state)
    assert decision == "continue"

def test_answer_assessor_fallback_on_empty():
    """AnswerAssessor gracefully handles empty or whitespace input without errors."""
    assessor = AnswerAssessor()
    res = assessor.assess_answer("What is async/await?", "")
    assert res["quality"] == "poor"
    assert res["score"] <= 30.0
    assert res["needs_followup"] is True

def test_offline_extractor_fallback_regex():
    """LLMExtractor offline fallback extracts known technical keywords deterministically."""
    extractor = LLMExtractor.__new__(LLMExtractor)
    text = "Senior Python engineer with 5 years experience in FastAPI, Docker, and PostgreSQL databases."
    res = extractor._offline_extract_resume(text)
    
    assert "Python" in res["skills"]
    assert "Fastapi" in res["skills"]
    assert "Postgresql" in res["skills"]
    assert res["experience_years"] == 5.0
