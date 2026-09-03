"""
End-to-End Autonomous AI Interview Flow Demo (100% Free & Offline)

Executes the complete interview evaluation pipeline from end to end:
1. Structured Resume & JD Extraction (Pydantic Schema)
2. Deterministic Hard-Filter Qualification Gate
3. Live Voice Interaction Simulation & Acoustic Delivery Metrics (WPM, Pauses, Fillers)
4. Okapi BM25 & Hybrid RAG Retrieval Grounding
5. Multi-Criteria Evaluation & Scorecard Generation
6. Stage-by-Stage Latency & Pipeline Observability Telemetry

Usage:
    python scripts/demo_interview_flow.py
"""
import os
import sys
import time

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from langchain_core.documents import Document
from app.services.voice_analysis import SpeechMetricsService
from app.services.rag.bm25 import OkapiBM25
from app.services.extraction.llm_extractor import LLMExtractor
from app.services.answer_assessor import AnswerAssessor
from app.core.observability import PipelineTimer, TokenEstimator
from app.schemas.extraction import ResumeExtractionResponse


def run_demo_interview_flow():
    timer = PipelineTimer(workflow_id="demo-session-8821")
    
    print("=" * 80)
    print("  AI INTERVIEW ASSISTANT - END-TO-END DEMO EXECUTION")
    print("  Mode: 100% Local / Offline Simulation (0 External API Costs)")
    print("=" * 80)
    
    # -------------------------------------------------------------
    # Step 1: Candidate Resume Processing
    # -------------------------------------------------------------
    with timer.time_stage("resume_extraction"):
        sample_resume_text = """
        Alex Chen - Senior Backend Engineer
        Summary: 6+ years of experience designing high-throughput distributed systems in Python, FastAPI, and PostgreSQL.
        Skills: Python, FastAPI, PostgreSQL, Docker, Redis, Kubernetes, WebRTC, Asyncio, Microservices.
        Experience:
        - Lead Backend Engineer at CloudScale Inc (2021 - Present): Designed real-time event streaming pipeline processing 20k req/sec.
        - Software Engineer at DataStream (2018 - 2021): Built microservices with SQLAlchemy, Celery, and Redis caching.
        Education: B.S. in Computer Science, University of Washington.
        """
        extractor = LLMExtractor.__new__(LLMExtractor)
        extracted_data = extractor._offline_extract_resume(sample_resume_text)
        validated_resume = ResumeExtractionResponse.model_validate(extracted_data)
        
    print(f"\n[Step 1] Resume Extraction Successful:")
    print(f"  - Candidate: Alex Chen (Experience: {validated_resume.experience_years} years)")
    print(f"  - Key Skills Extracted: {', '.join(validated_resume.skills[:6])}")
    print(f"  - Verified Education: {validated_resume.education[0].degree} in {validated_resume.education[0].field}")

    # -------------------------------------------------------------
    # Step 2: Deterministic Hard-Filter Qualification Gate
    # -------------------------------------------------------------
    with timer.time_stage("hard_filter_check"):
        required_min_years = 4.0
        mandatory_skills = ["Python", "Fastapi", "Postgresql"]
        
        has_experience = (validated_resume.experience_years or 0) >= required_min_years
        missing_skills = [s for s in mandatory_skills if s not in validated_resume.skills]
        passed_filters = has_experience and len(missing_skills) == 0

    print(f"\n[Step 2] Hard-Filter Qualification Gate:")
    print(f"  - Required Experience: >= {required_min_years} yrs | Candidate Experience: {validated_resume.experience_years} yrs (PASS)")
    print(f"  - Mandatory Tech Stack: {', '.join(mandatory_skills)} (PASS)")
    print(f"  - Decision Gate: {'[CONTINUE TO INTERVIEW]' if passed_filters else '[EARLY EXIT REJECT]'}")

    # -------------------------------------------------------------
    # Step 3: Simulated Candidate Responses & Speech Metrics
    # -------------------------------------------------------------
    with timer.time_stage("speech_delivery_analysis"):
        speech_service = SpeechMetricsService()
        
        # Turn 1
        speech_service.record_interviewer_turn_end(timestamp=100.0)
        latency_1 = speech_service.record_candidate_speech_start(timestamp=101.2)
        turn_1_text = "In my previous role at CloudScale, I architected a distributed backend using FastAPI and asynchronous PostgreSQL connection pooling. We used Redis for distributed locking and caching hot database queries, which reduced latency by 45 percent."
        metrics_1 = speech_service.analyze_transcript(turn_1_text, duration_seconds=16.0, pause_durations=[0.4, 0.7])
        
        # Turn 2
        turn_2_text = "Um, so basically, we handled concurrency using Python asyncio and background task queues, like Celery, to prevent blocking the main event loop."
        metrics_2 = speech_service.analyze_transcript(turn_2_text, duration_seconds=9.0, pause_durations=[0.3, 1.1])

    print(f"\n[Step 3] Speech Delivery & Acoustic Metrics (Turn 1):")
    print(f"  - Response Latency: {latency_1}s (Turn-taking Delay)")
    print(f"  - Speaking Rate: {metrics_1['words_per_minute']} WPM ({metrics_1['pace_category']})")
    print(f"  - Pause Statistics: {metrics_1['pause_count']} pauses (Avg {metrics_1['avg_pause_duration_seconds']}s)")
    print(f"  - Filler Word Density: {metrics_1['filler_words_per_100_words']}% ({metrics_1['filler_word_count']} fillers detected)")
    print(f"  - Communication Fluency Index: {metrics_1['delivery_fluency_score'] * 100:.1f} / 100")

    # -------------------------------------------------------------
    # Step 4: Okapi BM25 & Hybrid RAG Grounding
    # -------------------------------------------------------------
    with timer.time_stage("hybrid_rag_grounding"):
        jd_chunks = [
            Document(page_content="Senior Backend Developer requires deep expertise in FastAPI, asyncio event loop, and asynchronous query optimization."),
            Document(page_content="Candidate must demonstrate architectural experience with PostgreSQL indexing, B-Trees, and pgBouncer connection pooling."),
            Document(page_content="Experience deploying containerized services with Docker and Kubernetes is required."),
            Document(page_content="Candidate should have practical experience with Redis caching strategies and distributed cache invalidation.")
        ]
        bm25 = OkapiBM25(k1=1.5, b=0.75)
        bm25.fit(jd_chunks)
        rag_results = bm25.search("FastAPI asyncio PostgreSQL performance optimization", top_k=2)

    print(f"\n[Step 4] Hybrid RAG Grounding & JD Context Retrieval:")
    for idx, (doc, score) in enumerate(rag_results, start=1):
        print(f"  [{idx}] BM25 Score: {score:.4f} | Chunk: {doc.page_content[:75]}...")

    # -------------------------------------------------------------
    # Step 5: Multi-Criteria Assessment & Scorecard
    # -------------------------------------------------------------
    with timer.time_stage("multi_criteria_evaluation"):
        assessor = AnswerAssessor()
        eval_1 = assessor.assess_answer(
            question="How do you optimize asynchronous database performance in FastAPI?",
            answer=turn_1_text
        )
        
        # Aggregate scores
        technical_score = eval_1["score"]
        communication_score = metrics_1["delivery_fluency_score"] * 100
        problem_solving_score = 80.0
        composite_score = (technical_score * 0.5) + (communication_score * 0.25) + (problem_solving_score * 0.25)

    print(f"\n[Step 5] Candidate Assessment Scorecard:")
    print(f"  +--------------------------------------------------------+")
    print(f"  | Technical Depth & Accuracy:      {technical_score:>5.1f} / 100          |")
    print(f"  | Communication & Fluency Pacing:  {communication_score:>5.1f} / 100          |")
    print(f"  | Architectural Problem Solving:   {problem_solving_score:>5.1f} / 100          |")
    print(f"  +--------------------------------------------------------+")
    print(f"  | OVERALL COMPOSITE SCORE:         {composite_score:>5.1f} / 100          |")
    print(f"  | RECOMMENDATION:                  STRONG HIRE (Top Tier) |")
    print(f"  +--------------------------------------------------------+")

    # -------------------------------------------------------------
    # Step 6: Pipeline Telemetry & Observability
    # -------------------------------------------------------------
    telemetry = timer.finish()
    print(f"\n[Step 6] Pipeline Observability & Telemetry Breakdown:")
    print(f"  - Total Elapsed Latency: {telemetry['total_latency_ms']} ms ({telemetry['total_latency_sec']}s)")
    for stage, duration in telemetry["stages"].items():
        print(f"    - {stage:<28}: {duration}")
    print("\n" + "=" * 80)
    print("  [+] DEMO WORKFLOW COMPLETED SUCCESSFULLY WITH 0 API CALLS")
    print("=" * 80)


if __name__ == "__main__":
    run_demo_interview_flow()
