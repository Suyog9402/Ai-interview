# Technical Architecture Specification

## 1. System Overview

The **AI Interview Assistant** is a distributed, real-time technical assessment platform designed to conduct interactive voice interviews, stream audio over WebRTC, parse multi-modal telemetry (speech pacing, pause statistics, facial attention), and orchestrate automated evaluations via cyclical state-machine graphs.

```text
                                END-TO-END ARCHITECTURE
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Next.js 15 Frontend UI                                 │
│      Candidate Portal • WebRTC Audio Client • Face Tracking WS • Admin Scorecards      │
└───────────────────────────┬────────────────────────────────┬───────────────────────────┘
                            │ REST / JSON (Port 8000)        │ WebRTC / WSS
                            ▼                                ▼
┌────────────────────────────────────────┐       ┌───────────────────────────────────────┐
│        FastAPI Application Server      │       │        LiveKit Voice Agent Room       │
│  - JWT Auth & RBAC Security            │       │  - STT: Deepgram Nova-2               │
│  - Candidate & JD CRUD Services        │       │  - LLM: Groq (Qwen 2.5 27B) / Gemini  │
│  - Face Attention WS Handler           │       │  - TTS: Deepgram Aura Asteria         │
│  - Pipeline Telemetry & Observability  │       │  - Silero VAD (Turn Detection)        │
└───────────────────┬────────────────────┘       └───────────────────┬───────────────────┘
                    │                                                │
                    │ Post-Interview Trigger                         │ Audio / Transcript
                    ▼                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        LangGraph / Evaluation Pipeline                                 │
│                                                                                        │
│  [START] ──► [Store Recording] ──► [Transcribe] ──► [Quality Gate]                    │
│                                                         │                              │
│                                                   (Retry Loop)                         │
│                                                         ▼                              │
│  [Generate Next Steps] ◄── [Check Hard Filters] ◄── [Extract Structured Data]          │
│           ▲                            │ (Passed)                                      │
│           │ (Disqualified: Early Exit) ▼                                               │
│           └────────────────── [Hybrid RAG (ChromaDB + Okapi BM25)]                     │
│                                        │                                               │
│                                        ▼                                               │
│                     [Multi-Criteria LLM Evaluation Pipeline]                           │
│                 (Technical Accuracy, Completeness, Clarity, Rubrics)                   │
└───────────────────────────┬────────────────────────────────┬───────────────────────────┘
                            │                                │
                            ▼                                ▼
                 ┌──────────────────────┐         ┌──────────────────────┐
                 │ PostgreSQL / SQLite  │         │   ChromaDB Vector    │
                 │ (Relational / ACID)  │         │ (Dense Embeddings)   │
                 └──────────────────────┘         └──────────────────────┘
```

---

## 2. Core Subsystems

### A. Real-Time Voice Streaming Layer
- **Protocol**: Bidirectional WebRTC streaming managed by **LiveKit Agents SDK**.
- **Speech Stack**: Deepgram Nova-2 streaming STT, Groq LPU high-speed LLM inference (`qwen/qwen3.8-27b`), Deepgram Aura neural TTS, and Silero VAD with noise-cancellation filtering to enable natural interruptions and sub-500ms conversational turn-taking.
- **Speech Delivery Metrics Engine**: Quantifies Words Per Minute (WPM), hesitation pause duration, filler-word density, and response latency without unscientific psychological claims.

### B. Cyclical LangGraph State Machine
- **Engine**: LangGraph `StateGraph` compiled with in-memory checkpointers.
- **Fail-Safe Loops**: Conditional routing dynamically retries low-quality transcriptions up to a configurable maximum retry limit before degrading gracefully.
- **Cost-Optimizing Gates**: Deterministic hard filters verify non-negotiable criteria (e.g. required language, minimum years of experience) *before* invoking expensive LLM evaluation prompts.

### C. Hybrid Retrieval (RAG) & Matching Engine
- **Vector Retrieval**: Dense semantic similarity search over ChromaDB embeddings (Google `text-embedding-004` / OpenAI embeddings).
- **Lexical Retrieval**: Pure-Python Okapi BM25 algorithm ($k_1 = 1.5, b = 0.75$) with Inverse Document Frequency and document length normalization.
- **Combination Function**: Reciprocal Rank Fusion ($k = 60$) and Min-Max normalized scoring:
  $$\text{Score}_{\text{hybrid}} = \alpha \cdot \text{Score}_{\text{vector}} + (1 - \alpha) \cdot \text{Score}_{\text{BM25}}$$

### D. Relational Data & Administration
- **Transactional Persistence**: PostgreSQL (production) / SQLite (development) storing candidate records, Q&A pairs, evaluation scorecards, and audit logs.
- **Admin Dashboard**: Next.js 15 interface featuring candidate rankings, side-by-side scorecard comparisons, radar charts, and role-based access controls.
