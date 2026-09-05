# AI Interview Platform - Backend & Voice Agent Service

FastAPI application backend, LiveKit WebRTC real-time voice agent worker, and LangGraph evaluation engine for the AI Voice Interview platform.

---

## 🏗️ Architecture & Component Overview

- **FastAPI REST & WebSocket Server (`app/`)**: Provides REST endpoints for authentication (JWT/RBAC), candidate management, job descriptions, real-time computer vision face proctoring WebSockets, and evaluation pipelines.
- **LiveKit Voice Agent Worker (`app.py`)**: Real-time WebRTC voice agent leveraging Deepgram Nova-2 STT, Groq LPU inference (`qwen/qwen-2.5-32b` / `qwen3.8-27b`), Deepgram Aura TTS, Silero VAD turn detection, and server-side interruption handling.
- **LangGraph Evaluation Engine (`app/services/interview_service.py`)**: Cyclic StateGraph workflow executing quality gates, deterministic hard filters, structured Q&A extraction, and multi-criteria scoring rubrics.
- **Hybrid RAG & Candidate Matching (`app/services/rag/`, `app/services/matching/`)**: ChromaDB vector store + pure-Python Okapi BM25 ranking fused via Reciprocal Rank Fusion (RRF).
- **Speech Metrics Engine (`app/services/voice_analysis.py`)**: Objective calculation of WPM, response latency, hesitation pause statistics, and filler-word density.
- **Resilient Multi-Provider LLM Router (`app/core/llm_provider.py`)**: Fallback chain prioritizing Groq -> Gemini 2.5 Flash -> OpenAI -> Offline Rule Mock.

---

## 🚀 Setup & Execution

### 1. Install Dependencies
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Ensure your API keys (LiveKit, Groq, Deepgram, Gemini) are configured.

### 3. Run FastAPI Application Server
```bash
# In development mode with auto-reload:
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger API documentation: `http://localhost:8000/docs`

### 4. Run LiveKit Real-Time Voice Agent
```bash
# In development mode:
python app.py dev

# In production worker mode:
python app.py start
```

---

## 🧪 Testing & Validation Suite

All test suites and benchmarks run **100% offline, deterministic, and secretless**:

```bash
# Run complete pytest test suite (18 unit/integration tests)
python -m pytest tests/ -v

# Run flake8 syntax & lint check
flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics

# Run offline RAG retrieval benchmark
python scripts/evaluate_rag.py
```

---

## 🛠️ CLI & Management Scripts

```bash
# Admin user management
python scripts/manage_admin.py list
python scripts/manage_admin.py create <username> <password> <email>
python scripts/manage_admin.py reset <username> <new_password>

# Test end-to-end interview simulation flow
python scripts/demo_interview_flow.py

# Inspect results and speech analytics
python scripts/check_interview_results.py
```