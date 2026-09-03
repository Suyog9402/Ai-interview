# Interview Assistant Backend

FastAPI application backend and LiveKit voice agent service for the AI Interview Assistant platform.

## Architecture

- **FastAPI Backend (`app/`)**: Provides REST endpoints for authentication (JWT/RBAC), candidate management, job descriptions, face detection WebSockets, and LangGraph evaluation pipelines.
- **LiveKit Voice Agent (`app.py`)**: Real-time WebRTC voice agent interfacing with OpenAI Realtime API (`gpt-4o-realtime-preview`) and Silero VAD.
- **RAG & Hybrid Matching (`app/services/rag/`)**: ChromaDB vector store + pure-Python Okapi BM25 ranking.
- **Speech Metrics Engine (`app/services/voice_analysis.py`)**: Local calculation of WPM, response latency, pause statistics, and filler-word density.

## Setup & Execution

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Run FastAPI Application Server
```bash
python main.py
# Or with uvicorn:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API docs available at: `http://localhost:8000/docs`

### 4. Run LiveKit Real-Time Voice Agent
```bash
# In development mode:
python app.py dev

# In production worker mode:
python app.py start
```

### 5. Run Offline Test Suite & RAG Benchmark (100% Free)
```bash
# Run full pytest test suite
python -m pytest tests/ -v

# Run offline RAG retrieval benchmark
python scripts/evaluate_rag.py
```

## Admin Tooling
```bash
# List all admin users
python scripts/manage_admin.py list

# Reset admin password
python scripts/manage_admin.py reset <username> <new_password>
```