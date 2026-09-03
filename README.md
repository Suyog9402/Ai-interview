# AI Voice Interview Platform & Technical Evaluation System

[![CI Pipeline](https://github.com/Suyog9402/Ai-interview/actions/workflows/ci.yml/badge.svg)](https://github.com/Suyog9402/Ai-interview/actions)
![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi)
![Next.js 15](https://img.shields.io/badge/Next.js-15%20App%20Router-black?logo=next.js)
![LiveKit](https://img.shields.io/badge/LiveKit-WebRTC%20Agent-0080FF?logo=livekit)
![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph%20Workflow-FF6F00)
![PostgreSQL / SQLite](https://img.shields.io/badge/Database-PostgreSQL%20%7C%20SQLite-336791?logo=postgresql)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-orange)
![Tests](https://img.shields.io/badge/Tests-Pytest%2018%2F18%20Passing-brightgreen)

An autonomous, full-stack AI interview platform that conducts real-time technical voice interviews over WebRTC, calculates objective speech delivery metrics (WPM, response latency, pause statistics, filler-word density), performs real-time face attention proctoring, and evaluates candidate technical competency using **Hybrid RAG (ChromaDB + pure-Python Okapi BM25)**, **Pydantic v2 structured schemas**, and a **multi-criteria LLM evaluation pipeline**.

---

## 🏗️ System Architecture

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

## 🌟 Key Features & Implementation Reality

| Capability | Engineering Implementation in Code | Location |
| :--- | :--- | :--- |
| **Real-Time Voice Agent** | LiveKit Agents SDK (1.3.12) with Deepgram Nova-2 STT, Groq LPU LLM inference (`qwen/qwen3.8-27b`), Deepgram Aura TTS, Silero VAD, and LiveKit Cloud Background Voice Cancellation. | `voice-assistant/backend/app.py` |
| **Adaptive Question State Machine** | 6-Phase State Machine: `INTRODUCTION` -> `RESUME_VALIDATION` -> `CORE_TECHNICAL` -> `DEEP_DIVE` -> `BEHAVIORAL` -> `CANDIDATE_QA`. Probes candidate answers and tracks topics to avoid repetition. | `app/services/adaptive_question_manager.py` |
| **Hybrid RAG Retrieval** | Combines ChromaDB dense vector similarity (Google `text-embedding-004` / OpenAI) with pure-Python Okapi BM25 ($k_1=1.5, b=0.75$) via Reciprocal Rank Fusion ($k=60$) & normalized linear fusion. | `app/services/rag_service.py`<br>`app/services/rag/` |
| **Resume & JD Matching Engine** | 2-Stage matching: (1) Deterministic Hard-Filter checking (must-have skills, minimum experience), (2) Multi-factor weighted scoring (Skills 35%, Experience 25%, Projects 25%, Domain 15%). | `app/services/matching/` |
| **Multi-Criteria Evaluation Pipeline** | Structured Q&A extraction and rubric-based evaluation scoring technical accuracy, completeness, and clarity on a 0–100 scale with strengths, areas for improvement, and recommendations. | `app/services/interview_service.py` |
| **Objective Speech Delivery Metrics** | Calculates quantifiable pacing: Words Per Minute (WPM), response latency, pause count/duration, and filler-word density per 100 words. (Avoids unscientific psychological claims). | `app/services/voice_analysis.py` |
| **Computer Vision Anti-Cheating** | WebSocket stream (`/api/v1/face-detection/ws`) monitoring MediaPipe 468 FaceMesh: Head pose (yaw/pitch), Eye Aspect Ratio (EAR) for gaze, multi-face presence, and mobile phone detection. | `app/api/face_detection.py`<br>`frontend/components/face-detection/` |
| **Multi-Provider Resilient Router** | Priority-based LLM fallback chain designed to reduce failures during individual provider outages or rate limits: Primary Groq -> Fallback Gemini 2.5 Flash -> Fallback OpenAI -> Offline Rule Mock. | `app/core/llm_provider.py` |
| **Admin & Governance Dashboard** | Recruiter candidate leaderboard, JD version snapshots, CSV/JSON audit logs, and match score analytics. | `app/api/admin.py`<br>`frontend/app/admin/` |

---

## 🎙️ Real-Time Voice Conversational Streaming Architecture

The voice assistant architecture is designed for low-latency conversational streaming using:
* **Turn Detection**: Server-side Silero Voice Activity Detection (VAD).
* **Streaming STT**: Deepgram Nova-2 with WebSocket streaming.
* **Low-Latency LLM**: Groq LPU inference (`qwen/qwen3.8-27b`).
* **Streaming TTS**: Deepgram Aura neural text-to-speech.

> **Engineering Note**: The system architecture is built for rapid turn-taking and natural streaming. The repository does not currently contain a production end-to-end latency benchmark across live networks.

### Interruption Handling
When a candidate speaks while the AI interviewer is responding, Silero VAD detects incoming audio on the WebRTC stream. The agent triggers an interruption event, cancels the active TTS audio buffer, and transitions immediately to listening mode.

---

## 📊 Hybrid RAG Architecture & Offline Validation Benchmark

### Ingestion & Chunking
* **Chunk Size**: 500 characters
* **Chunk Overlap**: 100 characters (preserves requirement context across boundaries)
* **Dense Vector Index**: ChromaDB (`./db/chroma_db_v2`) using Google `text-embedding-004` (768 dimensions) or OpenAI embeddings
* **Sparse Lexical Index**: Pure-Python Okapi BM25 ($k_1 = 1.5, b = 0.75$) with Inverse Document Frequency (IDF) normalization
* **Rank Fusion (RRF)**: Reciprocal Rank Fusion ($k = 60$) combines rankings from both retrieval strategies and avoids the need to compare incompatible raw score distributions ($k=60$ acts as a rank-smoothing parameter).
* **Reranker Interface**: `SimpleReranker` is implemented as an extensible interface hook with query term-overlap scoring.

### Offline Validation Benchmark (`python scripts/evaluate_rag.py`)
Tested against 20 technical domain queries over 20 architectural document chunks:

| Retrieval Strategy | Recall@1 | Recall@3 | Recall@5 | Precision@1 | MRR |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **1. Dense Vector Search** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| **2. Okapi BM25 Lexical** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| **3. Hybrid Search ($\alpha = 0.5$)** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |

> **Scope Note**: This is an offline, deterministic validation benchmark designed to test ranking correctness and verify hybrid fusion math without consuming external API credits. It validates the code implementation and benchmark harness, but does not claim statistical superiority across arbitrary real-world corpora.

---

## 🏛️ Architecture Decision Records (ADRs)

* [ADR-001: Why LiveKit WebRTC Over Raw WebSockets](docs/decisions/ADR-001-why-livekit-webrtc.md)
* [ADR-002: Why LangGraph StateGraphs Over Linear Chains](docs/decisions/ADR-002-why-langgraph.md)
* [ADR-003: Why PostgreSQL / SQLite + ChromaDB Hybrid Persistence](docs/decisions/ADR-003-why-postgresql-and-chromadb.md)
* [ADR-004: Why Deterministic Hard-Filtering Precedes LLM Evaluation](docs/decisions/ADR-004-why-deterministic-hard-filters.md)
* [ADR-005: Why Hybrid Retrieval (Vector + Okapi BM25)](docs/decisions/ADR-005-why-hybrid-retrieval.md)
* [Known Limitations & Engineering Transparency](docs/known-limitations.md)

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
* Python 3.11 or 3.12
* Node.js 18+ & npm
* (Optional for live voice) LiveKit Cloud account, Groq API key, Deepgram API key, Gemini API key

### 2. Environment Configuration

```bash
# Clone the repository
git clone https://github.com/Suyog9402/Ai-interview.git
cd Ai-interview/voice-assistant

# Setup Backend Environment
cp backend/.env.example backend/.env

# Setup Frontend Environment
cp frontend/.env.example frontend/.env.local
```

### 3. Running Backend Services

```bash
cd voice-assistant/backend

# Install dependencies
pip install -r requirements.txt

# Start FastAPI backend (Port 8000)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Start LiveKit Voice Agent Worker (in a separate terminal)
python app.py dev
```

### 4. Running Frontend Client

```bash
cd voice-assistant/frontend

# Install dependencies
npm install

# Start Next.js development server (Port 3000)
npm run dev
```

Open your browser at **`http://localhost:3000`**.

---

## 🧪 Testing & CI/CD Pipeline

The test suite is **100% offline, deterministic, and secretless**. No external API keys or network calls are required to run tests.

```bash
cd voice-assistant/backend

# Run complete pytest test suite (18 tests)
python -m pytest tests/ -v

# Run flake8 linter check (0 errors)
flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics

# Run offline RAG retrieval evaluation benchmark
python scripts/evaluate_rag.py
```

### Automated GitHub Actions CI
Every commit and pull request to `main` triggers automated CI checks verifying:
1. Python syntax & flake8 linting (0 errors)
2. Pytest unit & workflow test suite (18/18 passed)
3. Offline RAG benchmark execution
4. Next.js frontend TypeScript typecheck & production build

---

## 🔒 Security & Privacy Practices

* **Zero Hardcoded Secrets**: All API keys and secrets are loaded from local `.env` files explicitly ignored by `.gitignore`.
* **Password Hashing**: Passwords stored using salted `bcrypt` hashes.
* **Token Authentication**: Stateless `JWT` tokens with `HS256` signatures and expiration limits.
* **Prompt Injection Guardrails**: Candidate transcripts are partitioned into structured user roles within `ChatPromptTemplate`, preventing system instruction overrides.
* **CORS Whitelist**: FastAPI endpoints restricted to authorized frontend origins.

---

## 📄 License & Contact

Distributed under the MIT License. Developed for technical assessment, recruiter workflow automation, and conversational AI engineering.
