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
![License](https://img.shields.io/badge/License-MIT-green)

An enterprise-grade, autonomous AI technical interview platform that conducts real-time conversational voice interviews over WebRTC, calculates objective speech delivery metrics (WPM, response latency, pause statistics, filler-word density), performs real-time face attention proctoring, and evaluates candidate technical competency using **Hybrid RAG (ChromaDB dense vectors + pure-Python Okapi BM25)**, **Pydantic v2 structured schemas**, and a **multi-criteria LangGraph evaluation workflow**.

---

## 📑 Table of Contents

- [System Architecture](#-system-architecture)
- [Core Feature Matrix](#-core-feature-matrix)
- [Key Engineering Pillars](#-key-engineering-pillars)
  - [1. Real-Time WebRTC Voice Agent](#1-real-time-webrtc-voice-agent)
  - [2. LangGraph Multi-Criteria Evaluation Pipeline](#2-langgraph-multi-criteria-evaluation-pipeline)
  - [3. Hybrid RAG & Benchmark Harness](#3-hybrid-rag--benchmark-harness)
  - [4. Computer Vision Face Proctoring](#4-computer-vision-face-proctoring)
  - [5. Objective Speech Metrics Engine](#5-objective-speech-metrics-engine)
  - [6. Admin & Recruiter Governance Panel](#6-admin--recruiter-governance-panel)
- [Deep-Dive Documentation Index](#-deep-dive-documentation-index)
- [Directory Structure](#-directory-structure)
- [Quickstart & Local Setup](#-quickstart--local-setup)
  - [Option A: Native Development](#option-a-native-development)
  - [Option B: Docker Compose](#option-b-docker-compose)
- [Environment Variables Guide](#-environment-variables-guide)
- [Offline Verification & Benchmarks](#-offline-verification--benchmarks)
- [Admin & Automation CLI Tools](#-admin--automation-cli-tools)
- [Security, Privacy & Guardrails](#-security-privacy--guardrails)
- [License](#-license)

---

## 🏗️ System Architecture

```text
                                 END-TO-END SYSTEM ARCHITECTURE
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Next.js 15 Frontend UI                                 │
│      Candidate Portal • WebRTC Audio Client • Face Tracking WS • Admin Scorecards      │
└───────────────────────────┬────────────────────────────────┬───────────────────────────┘
                            │ REST / JSON (Port 8000)        │ WebRTC / WSS
                            ▼                                ▼
┌────────────────────────────────────────┐       ┌───────────────────────────────────────┐
│        FastAPI Application Server      │       │        LiveKit Voice Agent Worker     │
│  - JWT Auth & RBAC Security            │       │  - STT: Deepgram Nova-2               │
│  - Candidate & JD CRUD Services        │       │  - LLM: Groq (Qwen 2.5 32B) / Gemini  │
│  - Face Attention WS Handler           │       │  - TTS: Deepgram Aura Asteria         │
│  - Pipeline Telemetry & Observability  │       │  - Silero VAD (Turn Detection)        │
└───────────────────┬────────────────────┘       └───────────────────┬───────────────────┘
                    │                                                │
                    │ Post-Interview Evaluation                      │ Audio / Transcript
                    ▼                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        LangGraph Technical Evaluation Pipeline                         │
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
│                     [Multi-Criteria LLM Evaluation Engine]                             │
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

## 🌟 Core Feature Matrix

| Capability | Engineering Implementation | Location |
| :--- | :--- | :--- |
| **Real-Time Voice Agent** | LiveKit Agents SDK (1.3.12) with Deepgram Nova-2 STT, Groq LPU inference (`qwen/qwen-2.5-32b-instruct` / `qwen3.8-27b`), Deepgram Aura TTS, Silero VAD, and server-side interruption handling. | `voice-assistant/backend/app.py` |
| **Adaptive Question Flow** | 6-Phase State Machine: `INTRODUCTION` -> `RESUME_VALIDATION` -> `CORE_TECHNICAL` -> `DEEP_DIVE` -> `BEHAVIORAL` -> `CANDIDATE_QA`. Tracks covered topics and dynamically adjusts follow-ups. | `app/services/adaptive_question_manager.py` |
| **Hybrid RAG Retrieval** | Combines ChromaDB dense vector similarity (`text-embedding-004` / OpenAI) with pure-Python Okapi BM25 ($k_1=1.5, b=0.75$) via Reciprocal Rank Fusion ($k=60$) and linear fusion. | `app/services/rag_service.py`<br>`app/services/rag/` |
| **Multi-Criteria Evaluation** | LangGraph StateGraph pipeline enforcing structured Q&A extraction, deterministic hard filtering, rubric evaluations (0–100 scale), and actionable recommendations. | `app/services/interview_service.py`<br>`app/services/matching/` |
| **Speech Delivery Metrics** | Quantifiable pacing analysis: Words Per Minute (WPM), response latency, pause count/durations, and filler-word density per 100 words. | `app/services/voice_analysis.py` |
| **Computer Vision Proctoring** | WebSocket stream (`/api/v1/face-detection/ws`) monitoring MediaPipe 468 FaceMesh: Head pose (yaw/pitch), Eye Aspect Ratio (EAR) for gaze, multi-face presence, and mobile phone detection. | `app/api/face_detection.py`<br>`frontend/components/face-detection/` |
| **Multi-Provider LLM Router** | Priority fallback chain for zero-downtime inference: Primary Groq -> Fallback Gemini 2.5 Flash -> Fallback OpenAI -> Offline Rule Mock. | `app/core/llm_provider.py` |
| **Admin & Governance Dashboard** | Recruiter candidate leaderboard, JD version snapshots, CSV/JSON audit logs, and match score analytics. | `app/api/admin.py`<br>`frontend/app/admin/` |

---

## 🔬 Key Engineering Pillars

### 1. Real-Time WebRTC Voice Agent
- **Sub-Second Latency Pipeline**: Deepgram Nova-2 WebSocket STT $\rightarrow$ Groq LPU token streaming $\rightarrow$ Deepgram Aura WebSocket TTS.
- **Silero Turn Detection & Interruption**: Detects candidate speech mid-answer, cancels active TTS output buffers, and immediately transitions into listening state.
- **Adaptive Phase Control**: Contextual interview progression spanning resume verification, system design, core coding principles, deep dives, behavioral scenarios, and candidate Q&A.

### 2. LangGraph Multi-Criteria Evaluation Pipeline
- **StateGraph Architecture**: Deterministic, cyclic state machine with validation retry loops, quality gate inspection, hard-filter disqualification checks, and structured extraction.
- **Zero Hallucination Rubric**: Grounded by retrieved Job Description criteria and standard answer keys via Hybrid RAG.

### 3. Hybrid RAG & Benchmark Harness
- **Dense Vector Search**: ChromaDB with Google `text-embedding-004` (768-dim) or OpenAI embeddings.
- **Sparse Lexical Search**: Custom pure-Python Okapi BM25 ($k_1=1.5, b=0.75$) with inverse document frequency normalization.
- **Fusion**: Reciprocal Rank Fusion ($RRF score = \sum \frac{1}{k + rank_i}, k=60$) for scale-invariant ranking.
- **Offline Benchmark**: Built-in benchmark suite (`scripts/evaluate_rag.py`) testing Recall@k, Precision@k, and MRR.

### 4. Computer Vision Face Proctoring
- **Client-Side Face Mesh**: MediaPipe 468-landmark tracking running directly in the browser via WebAssembly/Canvas.
- **WebSocket Telemetry**: Streams real-time EAR (gaze tracking), head pose orientation angles, and presence alerts to the FastAPI server for cheat audit logs.

### 5. Objective Speech Metrics Engine
- **Delivery Assessment**: Pure mathematical computation of speech rate (WPM), hesitation pause lengths, response latency, and filler-word occurrences (`um`, `uh`, `like`, `you know`).

---

## 📚 Deep-Dive Documentation Index

| Documentation Guide | Focus Area | Link |
| :--- | :--- | :--- |
| **Mastery & Architecture Guide (24 Chapters)** | Comprehensive architecture, deep-dive theory, implementation mechanics, and viva/defense Q&A. | [PROJECT_INTERVIEW_MASTERY_DOCUMENT.md](PROJECT_INTERVIEW_MASTERY_DOCUMENT.md) |
| **LangGraph Pipeline Guide** | Complete StateGraph design, state schemas, node transitions, quality gates, and evaluation rubrics. | [LANGGRAPH_DOCUMENTATION.md](LANGGRAPH_DOCUMENTATION.md) |
| **Admin Panel & Governance Guide** | RBAC security, JWT authentication, candidate management, audit logs, and recruiter scorecards. | [ADMIN_PANEL_DOCUMENTATION.md](ADMIN_PANEL_DOCUMENTATION.md) |
| **Architecture Decisions (ADRs)** | Technical justifications for LiveKit, LangGraph, Hybrid RAG, and Postgres/ChromaDB persistence. | [docs/decisions/](docs/decisions/) |
| **Known Limitations & Transparency** | Honest disclosure of edge cases, offline benchmarks, and production scaling considerations. | [docs/known-limitations.md](docs/known-limitations.md) |

---

## 📁 Directory Structure

```text
ai-interview-main/
├── docs/                                # Architecture Decision Records (ADRs) & Specs
│   ├── architecture.md
│   ├── known-limitations.md
│   └── decisions/
│       ├── ADR-001-why-livekit-webrtc.md
│       ├── ADR-002-why-langgraph.md
│       ├── ADR-003-why-postgresql-and-chromadb.md
│       ├── ADR-004-why-deterministic-hard-filters.md
│       └── ADR-005-why-hybrid-retrieval.md
├── voice-assistant/
│   ├── docker-compose.yml               # Multi-service deployment definition
│   ├── backend/                         # FastAPI & LiveKit Backend
│   │   ├── app.py                       # LiveKit Voice Agent Worker
│   │   ├── main.py                      # FastAPI App Entry Point
│   │   ├── requirements.txt             # Backend dependencies
│   │   ├── app/
│   │   │   ├── api/                     # REST & WebSocket Endpoints (auth, admin, interview, face)
│   │   │   ├── core/                    # Security, DB configs, Multi-provider LLM router
│   │   │   ├── models/                  # SQLAlchemy ORM Models
│   │   │   ├── schemas/                 # Pydantic v2 DTOs & Schemas
│   │   │   └── services/                # Business logic (RAG, Matching, Voice, LangGraph)
│   │   │       ├── matching/            # Multi-factor matching engine
│   │   │       ├── rag/                 # BM25 + Vector Hybrid Retrieval
│   │   │       └── transcription/       # Realtime transcription engines
│   │   ├── scripts/                     # Evaluation benchmarks, admin CLI, demo scripts
│   │   └── tests/                       # Pytest test suite (18 deterministic tests)
│   └── frontend/                        # Next.js 15 App Router Frontend
│       ├── app/                         # App Router pages (interview, admin, candidate portal)
│       ├── components/                  # UI components, WebRTC voice visualizer, Face proctoring
│       ├── hooks/                       # Custom React hooks (LiveKit audio, WebSocket face detection)
│       ├── lib/                         # Client utilities & API client
│       └── package.json                 # Frontend dependencies
├── ADMIN_PANEL_DOCUMENTATION.md         # Admin panel design & API guide
├── LANGGRAPH_DOCUMENTATION.md           # LangGraph evaluation pipeline guide
├── PROJECT_INTERVIEW_MASTERY_DOCUMENT.md# 24-Chapter comprehensive mastery documentation
└── README.md                            # Main project documentation
```

---

## 🚀 Quickstart & Local Setup

### Option A: Native Development

#### 1. Prerequisites
- **Python**: 3.11 or 3.12
- **Node.js**: 18+ (Node 20+ recommended) & npm / pnpm
- **API Keys** (Optional for offline mock/tests, required for live voice):
  - LiveKit Cloud URL, API Key, API Secret
  - Groq API Key, Deepgram API Key, or Google Gemini API Key

#### 2. Backend Setup
```bash
cd voice-assistant/backend

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

#### 3. Start Backend Services
```bash
# Terminal 1: Start FastAPI REST Server (Port 8000)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Start LiveKit Real-Time Voice Agent Worker
python app.py dev
```
*API documentation and Swagger UI are available at: `http://localhost:8000/docs`*

#### 4. Frontend Setup & Run
```bash
cd voice-assistant/frontend

# Configure environment
cp .env.example .env.local

# Install dependencies
npm install

# Start Next.js Development Server (Port 3000)
npm run dev
```
*Candidate & Admin portal accessible at: `http://localhost:3000`*

---

### Option B: Docker Compose

Spin up PostgreSQL, FastAPI Backend, LiveKit Agent Worker, and Next.js Frontend with a single command:

```bash
cd voice-assistant
cp backend/.env.example backend/.env
docker compose up --build
```

---

## ⚙️ Environment Variables Guide

Key configuration variables in `voice-assistant/backend/.env`:

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./db/interview_assistant.db` or PostgreSQL |
| `JWT_SECRET_KEY` | Secret key for JWT session tokens | `your-secret-key-min-32-chars` |
| `LIVEKIT_URL` | LiveKit WebRTC server endpoint | `wss://your-project.livekit.cloud` |
| `LIVEKIT_API_KEY` | LiveKit API Key | `APInonprod...` |
| `LIVEKIT_API_SECRET`| LiveKit API Secret | `secret...` |
| `GROQ_API_KEY` | Primary LLM Provider (Groq LPU) | `gsk_...` |
| `DEEPGRAM_API_KEY` | Deepgram STT (Nova-2) & TTS (Aura) | `dg_...` |
| `GEMINI_API_KEY` | Secondary LLM Fallback Provider | `AIza...` |
| `OPENAI_API_KEY` | Tertiary LLM / Embeddings Provider | `sk-...` |

---

## 🧪 Offline Verification & Benchmarks

The entire test suite and benchmark harness run **100% offline, deterministic, and secretless**:

```bash
cd voice-assistant/backend

# 1. Run Complete Pytest Suite (18/18 Unit & Integration Tests)
python -m pytest tests/ -v

# 2. Run Flake8 Code Quality & Syntax Linter (0 errors)
flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics

# 3. Run Offline Hybrid RAG Evaluation Benchmark
python scripts/evaluate_rag.py
```

### RAG Retrieval Benchmark Results
Tested against 20 technical domain queries over 20 architectural document chunks:

| Retrieval Strategy | Recall@1 | Recall@3 | Recall@5 | Precision@1 | MRR |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Dense Vector Search** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| **Okapi BM25 Lexical** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| **Hybrid Search ($\alpha = 0.5$)** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |

---

## 🛠️ Admin & Automation CLI Tools

Helpful utility scripts located in `voice-assistant/backend/scripts/`:

```bash
# Manage Admin Users
python scripts/manage_admin.py list
python scripts/manage_admin.py create <username> <password> <email>
python scripts/manage_admin.py reset <username> <new_password>

# Simulate an End-to-End Interview Flow (Offline Mock)
python scripts/demo_interview_flow.py

# Inspect Latest Interview Results and Telemetry
python scripts/check_interview_results.py

# Re-generate 24-Chapter Mastery Documentation
python scripts/build_full_document.py
```

---

## 🔒 Security, Privacy & Guardrails

- **Zero Hardcoded Secrets**: All credentials managed via `.env` files protected by `.gitignore`.
- **Stateless JWT & RBAC**: Role-based access control separating Candidates, Interviewers, and Admins.
- **Safe Password Hashing**: Salted `bcrypt` hashing for all administrative and user credentials.
- **Prompt Injection Defense**: Transcripts and user inputs are strictly encapsulated in structured schema fields, preventing system prompt overrides.
- **CORS Whitelist**: Secure cross-origin resource sharing policies for authorized origins.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.
