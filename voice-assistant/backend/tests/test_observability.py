"""
Unit Tests for Pipeline Telemetry & Observability
Verifies stage timing measurements, structured logging, and token estimation with 0 API calls.
"""
import time
import pytest
from app.core.observability import PipelineTimer, TokenEstimator

def test_pipeline_timer_stage_measurement():
    timer = PipelineTimer(workflow_id="test-wf-123")
    
    with timer.time_stage("transcription"):
        time.sleep(0.02)  # Simulate 20ms work
        
    with timer.time_stage("rag_retrieval"):
        time.sleep(0.01)  # Simulate 10ms work
        
    summary = timer.finish()
    
    assert summary["workflow_id"] == "test-wf-123"
    assert "transcription" in summary["stage_latencies_ms"]
    assert "rag_retrieval" in summary["stage_latencies_ms"]
    assert summary["stage_latencies_ms"]["transcription"] >= 15.0
    assert summary["total_latency_ms"] >= 30.0

def test_token_estimator_calculations():
    prompt = "You are a technical interviewer assessing candidate answers."
    completion = '{"score": 85, "quality": "excellent"}'
    
    res = TokenEstimator.estimate_cost("gpt-4o-mini", prompt, completion)
    
    assert res["prompt_tokens"] > 0
    assert res["completion_tokens"] > 0
    assert res["total_tokens"] == res["prompt_tokens"] + res["completion_tokens"]
    assert res["estimated_cost_usd"] > 0.0
