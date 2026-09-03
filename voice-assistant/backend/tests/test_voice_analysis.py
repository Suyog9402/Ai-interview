"""
Unit Tests for Speech Delivery Metrics & Fluency Analysis
Verifies WPM, pause statistics, filler words, latency, and objective scoring with 0 API calls.
"""
import pytest
from app.services.voice_analysis import SpeechMetricsService

def test_speech_metrics_normal_pace():
    service = SpeechMetricsService()
    text = "In my previous project I architected a distributed backend service using FastAPI and PostgreSQL with Redis caching for performance."
    
    # 19 words over 10 seconds -> 114.0 WPM
    res = service.analyze_transcript(text, duration_seconds=10.0)
    
    assert res["speaking"] is True
    assert res["word_count"] == 19
    assert res["words_per_minute"] == 114.0
    assert "Optimal" in res["pace_category"]
    assert res["filler_word_count"] == 0
    assert res["delivery_fluency_score"] >= 0.85

def test_speech_metrics_filler_words_detection():
    service = SpeechMetricsService()
    text = "Um, so basically, like, we used, you know, Docker containers and, like, Kubernetes for deployment."
    
    res = service.analyze_transcript(text, duration_seconds=10.0)
    
    assert res["filler_word_count"] >= 4
    assert "like" in res["filler_breakdown"]
    assert "um" in res["filler_breakdown"]
    assert res["filler_words_per_100_words"] > 10.0
    # Fluency score should be penalized for high filler density
    assert res["delivery_fluency_score"] < 0.85

def test_speech_metrics_response_latency():
    service = SpeechMetricsService()
    service.record_interviewer_turn_end(timestamp=100.0)
    latency = service.record_candidate_speech_start(timestamp=101.45)
    
    assert latency == 1.45
    assert service.get_analysis_state()["response_latency_seconds"] == 1.45

def test_speech_metrics_pause_statistics():
    service = SpeechMetricsService()
    text = "I designed the relational schema and optimized indexes."
    pauses = [0.5, 1.2, 0.8]
    
    res = service.analyze_transcript(text, duration_seconds=8.0, pause_durations=pauses)
    
    assert res["pause_count"] == 3
    assert res["avg_pause_duration_seconds"] == round((0.5 + 1.2 + 0.8) / 3, 2)
    assert 0.0 < res["speaking_ratio"] < 1.0

def test_speech_metrics_empty_input():
    service = SpeechMetricsService()
    res = service.analyze_transcript("")
    
    assert res["speaking"] is False
    assert res["word_count"] == 0
    assert res["words_per_minute"] == 0.0
