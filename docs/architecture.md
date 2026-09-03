# Technical Architecture Specification

## 1. System Overview

The **AI Interview Assistant** is a distributed, real-time technical assessment platform designed to conduct interactive voice interviews, stream audio over WebRTC, parse multi-modal telemetry (speech pacing, pause statistics, facial attention), and orchestrate automated evaluations via cyclical state-machine graphs.

```text
                                END-TO-END ARCHITECTURE
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Next.js 14 Frontend UI                                 │
│      Candidate Portal • WebRTC Audio Client • Face Tracking WS • Admin Scorecards      │
└───────────────────────────┬────────────────────────────────┬───────────────────────────┘
                            │ REST / JSON (Port 8000)        │ WebRTC / WSS
                            ▼                                ▼
┌────────────────────────────────────────┐       ┌───────────────────────────────────────┐
│        FastAPI Application Server      │       │        LiveKit Voice Agent Room       │
│  - JWT Auth & RBAC Security            │       │  - OpenAI Realtime (gpt-4o)           │
│  - Candidate & JD CRUD Services        │       │  - Silero VAD (Turn Detection)        │
│  - Face Attention WS Handler           │       │  - Adaptive Question Manager          │
│  - Pipeline Telemetry & Observability  │       │  - Objective Speech Delivery Metrics  │
└───────────────────┬────────────────────┘       └───────────────────┬───────────────────┘
                    │                                                │
                    │ Post-Interview Trigger                         │ Audio Recording
                    ▼                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                             LangGraph Evaluation Pipeline                              │
│                                                                                        │
│  [START] ──► [Store Audio] ──► [Whisper STT] ──► [Quality Gate]                        │
│                                                         │                              │
│                                                   (Retry Loop)                         │
│                                                         ▼                              │
│  [Generate Scorecard] ◄── [Deterministic Hard Filter] ◄── [Resume/Transcript Extract] │
│           ▲                            │ (Passed)                                      │
│           │ (Failed: Early Exit)       ▼                                               │
│           └────────────────── [Hybrid RAG (ChromaDB + Okapi BM25)]                     │
│                                        │                                               │
│                                        ▼                                               │
│                           [Multi-Agent LLM Evaluation]                                 │
│                    (Technical Depth, Problem Solving, Communication)                   │
└───────────────────────────┬────────────────────────────────┬───────────────────────────┘
                            │                                │
                            ▼                                ▼
                 ┌──────────────────────┐         ┌──────────────────────┐
                 │    PostgreSQL DB     │         │   ChromaDB Vector    │
                 │ (Relational / ACID)  │         │ (Dense Embeddings)   │
                 └──────────────────────┘         └──────────────────────┘
```

---

## 2. Core Subsystems

### A. Real-Time Voice Streaming Layer
- **Protocol**: Bidirectional WebRTC streaming managed by **LiveKit Agents SDK**.
- **Voice Activity Detection (VAD)**: Server-side Silero VAD with noise-cancellation filtering to enable natural interruptions and sub-300ms turn-taking.
- **Speech Delivery Metrics Engine**: Quantifies Words Per Minute (WPM), hesitation pause duration, filler-word density, and response latency without pseudo-psychological emotion claims.

### B. Cyclical LangGraph State Machine
- **Engine**: LangGraph `StateGraph` compiled with in-memory checkpointers.
- **Fail-Safe Loops**: Conditional routing dynamically retries low-quality transcriptions up to a configurable maximum before degrading gracefully.
- **Cost-Optimizing Gates**: Deterministic hard filters verify non-negotiable criteria (e.g. required language, minimum years of experience) *before* invoking expensive multi-agent LLM evaluation prompts.

### C. Hybrid Retrieval (RAG) & Matching Engine
- **Vector Retrieval**: Dense semantic similarity search over ChromaDB embeddings (`text-embedding-3-small`).
- **Lexical Retrieval**: Pure-Python Okapi BM25 algorithm ($k_1 = 1.5, b = 0.75$) with Inverse Document Frequency and document length normalization.
- **Combination Function**:
  $$\text{Score}_{\text{hybrid}} = \alpha \cdot \text{Score}_{\text{vector}} + (1 - \alpha) \cdot \text{Score}_{\text{BM25}}$$

### D. Relational Data & Administration
- **Transactional Persistence**: PostgreSQL storing candidate records, Q&A pairs, evaluation scorecards, and audit logs.
- **Admin Dashboard**: Next.js 14 interface featuring candidate rankings, side-by-side scorecard comparisons, radar charts, and role-based access controls.
