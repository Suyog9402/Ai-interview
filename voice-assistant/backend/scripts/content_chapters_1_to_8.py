"""
Chapters 1 to 8 of the Project Interview Mastery Document
"""

CHAPTER_1 = """# 1. Codebase Audit & Truth Table

A rigorous, file-by-file inspection of the repository reveals the exact implementation state of every component:

| Component / Feature | Implementation State | Actual Code Files & Symbols | Engineering Reality & Technical Truth |
| :--- | :--- | :--- | :--- |
| **Real-Time Voice Agent (STT/LLM/TTS)** | **Fully Implemented** | `voice-assistant/backend/app.py`<br>`AgentSession`, `Silero.VAD`, `Deepgram.STT`, `Groq.LLM` | Uses LiveKit Agents SDK 1.3.12 with Deepgram Nova-2 STT, Groq Qwen 2.5 27B LLM (`qwen/qwen3.8-27b`), Deepgram Aura TTS (`aura-asteria-en`), and Silero VAD. Noise suppression via LiveKit Cloud BVC. |
| **Adaptive Question Manager** | **Fully Implemented** | `app/services/adaptive_question_manager.py`<br>`AdaptiveQuestionManager`, `InterviewPhase` | Manages 6 distinct interview phases: `INTRODUCTION`, `RESUME_VALIDATION`, `CORE_TECHNICAL`, `DEEP_DIVE`, `BEHAVIORAL`, `CANDIDATE_QA`. Tracks user answers, assesses answer quality, and adapts questions dynamically. |
| **Resume Parsing & Skill Extraction** | **Fully Implemented** | `app/api/resume.py`<br>`app/services/extraction/llm_extractor.py`<br>`pdfplumber`, `PyPDF2`, `fitz` | Extracts text from PDF/DOCX using multi-engine fallback. Parses skills, work experience, projects, education using Groq/Gemini structured extraction with regex fallback. |
| **Job Description Matching Engine** | **Fully Implemented** | `app/services/matching/engine.py`<br>`app/services/matching/hard_filters.py`<br>`app/services/matching/weighted_scoring.py` | Multi-stage pipeline: Hard-filter disqualification (must-have skills, min experience, degree) followed by weighted multi-factor scoring (Skills: 35%, Experience: 25%, Projects: 25%, Domain: 15%) and natural language explanation generation. |
| **RAG & Hybrid Search Pipeline** | **Fully Implemented** | `app/services/rag_service.py`<br>`app/services/rag/bm25.py`<br>`app/services/rag/hybrid_retrieval.py` | ChromaDB vector store (`./db/chroma_db_v2`) combined with BM25 sparse keyword index via Reciprocal Rank Fusion (RRF, $k=60$). Embeddings via Google Generative AI (`models/text-embedding-004`) or OpenAI. |
| **Multi-Provider LLM Router** | **Fully Implemented** | `app/core/llm_provider.py`<br>`get_chat_llm`, `get_fast_llm` | Priority router: Primary Groq -> Fallback Gemini 2.5 Flash -> Fallback OpenAI -> Offline Rule Mock. Ensures zero downtime even during provider API outages. |
| **Computer Vision Anti-Cheating & Proctoring** | **Fully Implemented** | `app/api/face_detection.py`<br>`frontend/components/face-detection/` | Real-time WebSocket (`/api/v1/face-detection/ws`) tracking MediaPipe 468-point FaceMesh: Head pose (yaw/pitch), Eye Aspect Ratio (EAR) for gaze, emotion detection (CNN), multiple face detection, and mobile phone detection (MobileNet SSD). |
| **Post-Interview AI Evaluation** | **Fully Implemented** | `app/services/interview_service.py`<br>`app/api/interview.py`<br>`POST /api/v1/interview/evaluate` | LLM-powered structured extraction of Q&A pairs from conversation transcript, scoring each question 0-100 across technical accuracy, completeness, clarity, and producing an overall evaluation with strengths, weaknesses, and recommendations. |
| **Admin Dashboard & Audit Logs** | **Fully Implemented** | `app/api/admin.py`<br>`app/services/admin_service.py`<br>`frontend/app/admin/` | Candidate leaderboard, JD version control, CSV/JSON audit log export, system configuration manager, and match score analytics. |
| **LangGraph Pipeline Workflow** | **Partially Implemented** | `app/workflows/interview_pipeline.py`<br>`app/workflows/nodes/` | Full Node/StateGraph structure defined (`extraction`, `matching`, `rag_query`, `next_steps`, `storage`) with unit tests; primary runtime currently invokes service classes directly for minimal latency overhead. |
| **Azure Realtime Transcriber** | **Stub / Reserved Abstraction** | `app/services/transcription/azure_realtime.py` | Clean abstract interface inheriting from `BaseTranscriber`; stubbed to raise `NotImplementedError` while preserving polymorphic provider hierarchy. |
| **Distributed Task Queue (Celery/Redis)** | **Missing / Future Roadmap** | N/A | Evaluation runs asynchronously in-process via FastAPI ASGI event loop; production roadmap includes moving heavy video processing to Celery/Redis. |
"""

CHAPTER_2 = """# 2. Project Overview & Interview Pitches

### Problem Being Solved
Traditional technical screening interviews suffer from high human recruiter costs, human interviewer fatigue, subjective grading biases, scheduling bottlenecks (taking 2–3 weeks per candidate), and inability to rigorously verify candidate resume claims in real-time.

### Solution Architecture
An end-to-end, multi-modal autonomous AI Voice Interview Platform that:
1. Ingests candidate resumes and automatically matches them against rich Job Descriptions using a hybrid RAG engine and multi-factor weighted scoring.
2. Conducts natural, real-time, low-latency (<500ms audio-to-audio) conversational voice interviews powered by LiveKit WebRTC, Deepgram STT/TTS, Silero VAD, and Groq LPUs.
3. Performs real-time computer vision proctoring (head pose, gaze estimation, eye tracking, multi-face presence, and forbidden object detection).
4. Generates comprehensive technical evaluations with question-by-question scoring, strength/weakness breakdowns, and recruiter audit trails.

---

### 30-Second Interview Explanation
> "I built an autonomous real-time AI technical interviewing platform that conducts live, conversational voice interviews over WebRTC with sub-500ms voice latency. It uses a hybrid RAG pipeline combining ChromaDB dense search with BM25 keyword retrieval to dynamically tailor questions to job descriptions and candidate resumes. It runs real-time computer vision anti-cheating proctoring via MediaPipe and automatically scores candidate technical depth across multiple interview phases with Groq and Gemini LLM provider routing."

---

### 1-Minute Interview Explanation
> "This project solves the technical hiring bottleneck by creating an intelligent, multi-modal interviewer. 
> 
> On the frontend, candidates upload their resume in Next.js 15, which matches them against job requirements using our weighted scoring engine and hard-filter disqualifiers. 
> 
> When the live interview begins, we establish a WebRTC audio-video session through LiveKit Cloud. Our Python AI agent worker uses Silero VAD to detect turn-taking, Deepgram Nova-2 for real-time speech-to-text, Groq LPU inference running Qwen 2.5 27B to reason and select adaptive technical questions from our ChromaDB RAG vector store, and Deepgram Aura for ultra-low latency text-to-speech. 
> 
> Concurrently, our vision pipeline monitors candidate attention, head pose angles, and presence using MediaPipe FaceMesh over WebSockets. Once completed, the platform evaluates the conversation transcript into actionable technical scorecards stored in SQLite/PostgreSQL with full recruiter analytics."

---

### 3-Minute Interview Explanation
> "In technical hiring, human interviewers often lack the time or domain breadth to conduct deep, consistent first-round technical screens. I designed and engineered a full-stack, real-time AI Voice Interview Platform to automate this entire pipeline.
> 
> The architecture is divided into four synchronized layers:
> 
> 1. **Ingestion & Matching Layer**: Resumes and Job Descriptions are parsed via multi-engine PDF extractors and converted into structured profiles. We index them into ChromaDB using Google text-embedding-004 and maintain an in-memory BM25 sparse index. When matching a candidate to a role, we compute Reciprocal Rank Fusion scores across dense semantic vectors and keyword tokens, then apply hard constraint filters (must-have skills, experience thresholds) before calculating a multi-factor weighted match score.
> 
> 2. **Real-Time Voice Agent Layer**: To make AI conversation feel human, audio latency must be under 600 milliseconds. We use LiveKit WebRTC connected to an autonomous Python agent worker. The worker utilizes Silero VAD for voice activity detection, Deepgram Nova-2 STT for streaming transcription, Groq's high-speed inference engine for LLM generation, and Deepgram Aura for speech synthesis. An `AdaptiveQuestionManager` dynamically transitions the candidate through 6 phases: Introduction, Resume Validation, Core Technical, Deep Dive, Behavioral, and Candidate Q&A.
> 
> 3. **Proctoring & Vision Layer**: A separate computer vision WebSocket stream processes webcam frames through MediaPipe 468-point FaceMesh and MobileNet SSD to compute Eye Aspect Ratio (EAR), head yaw and pitch, emotion classification, multi-face presence (preventing proxy candidates), and phone detection.
> 
> 4. **Evaluation & Governance Layer**: Upon session completion, the conversation is extracted into paired questions and answers. An LLM evaluation pipeline assesses technical precision, completeness, and clarity on a 0–100 scale, generating structured recruiter scorecards and persisting audit trails in our database.
> 
> The entire backend is built on FastAPI with resilient fallback routing across Groq, Gemini, and OpenAI, backed by 18 automated unit tests and an offline RAG benchmark harness."
"""

CHAPTER_3 = """# 3. Complete Architecture & Component Deep Dive

```
+-----------------------------------------------------------------------------------+
|                            NEXT.JS 15 FRONTEND (Client)                          |
|  [Resume Upload]     [Job Matcher]     [LiveKit WebRTC Audio/Video]     [Scorecard] |
|  - TypeScript        - Tailwind CSS    - MediaPipe FaceMesh Proctoring  - Radix UI  |
+----------------------------------------+------------------------------------------+
                                         | (REST & WebSockets)
                                         v
+-----------------------------------------------------------------------------------+
|                              FASTAPI BACKEND (Port 8000)                          |
|  [Auth & Users]   [Resume Parser]   [JD Manager]   [Matching Engine]   [CV Service]|
|  - FastAPI ASGI   - Pydantic v2     - SQLite/PG    - WebSocket Router  - Admin API |
+------------------+---------------------+-------------------+----------------------+
                   |                     |                   |
                   v                     v                   v
+------------------------+ +-----------------------+ +------------------------------+
| RAG RETRIEVAL ENGINE   | | LLM ROUTER & PROVIDER | | LIVEKIT AI VOICE WORKER      |
| - ChromaDB (Dense)     | | - Primary: Groq LPU   | | (LiveKit Agents SDK 1.3.12)  |
| - BM25 Index (Sparse)  | | - Backup: Gemini 2.5  | | - Silero VAD (Turn-taking)   |
| - Reciprocal Rank Fuse | | - Fallback: OpenAI    | | - Deepgram Nova-2 (STT)      |
| - Citation Tracker     | | - Offline Rule Engine | | - Deepgram Aura Asteria(TTS) |
+------------------------+ +-----------------------+ +------------------------------+
```

### Component Breakdown & Design Rationale

#### 1. Next.js 15 Frontend (`voice-assistant/frontend`)
* **What is it?**: A responsive React 18 / Next.js 15 App Router web application.
* **Why does it exist?**: Provides candidates with an intuitive interface for resume uploading, role selection, WebRTC voice/video interaction, and detailed evaluation scorecards.
* **Responsibilities**: Media device management (microphone, webcam permissions), WebRTC connection establishment via `@livekit/components-react`, client-side face landmark rendering, and post-session scorecard visualization.
* **Inputs/Outputs**: Receives candidate PDF files, camera streams, and audio; produces REST API payloads and WebRTC media tracks.
* **Failure Impact if Removed**: Candidates have no UI to interact with the platform.

#### 2. FastAPI Backend Core (`voice-assistant/backend/app/main.py`)
* **What is it?**: An asynchronous high-performance Python web framework running on Uvicorn ASGI.
* **Why does it exist?**: Coordinates business logic, database transactions, RAG queries, WebSocket computer vision processing, and LLM evaluation endpoints.
* **Responsibilities**: Request validation via Pydantic v2 schemas, database session management (`get_db`), authentication token verification, and serving REST endpoints.
* **Design Decision**: Async ASGI allows handling thousands of concurrent lightweight I/O operations (like database queries and WebSocket frame reception) on a single Python process.

#### 3. LiveKit Real-Time AI Agent Worker (`voice-assistant/backend/app.py`)
* **What is it?**: An autonomous background daemon worker built on the `livekit-agents` 1.3.12 framework.
* **Why does it exist?**: Operates the real-time voice loop independently from HTTP request-response lifecycles.
* **Responsibilities**: Joins the WebRTC room upon candidate connection, receives candidate audio tracks, performs voice activity detection (VAD), invokes STT, prompts Groq LLM with conversation history and adaptive interview state, synthesizes speech via TTS, and streams audio back over WebRTC.
* **Why designed this way?**: Decoupling real-time audio WebRTC transport into a dedicated worker keeps HTTP API endpoints fast, non-blocking, and crash-resilient.

#### 4. Hybrid RAG & Vector Engine (`app/services/rag_service.py`)
* **What is it?**: Dual-index retrieval system combining ChromaDB dense vector store and in-memory BM25 sparse keyword store.
* **Why does it exist?**: Overcomes semantic drift and exact keyword mismatches (e.g. searching for specific framework versions or technical acronyms like "ASGI", "VAD", "BVC").
* **Responsibilities**: Chunking Job Descriptions (500 chars, 100 overlap), generating embeddings, calculating BM25 term frequencies, and fusing results with Reciprocal Rank Fusion ($k=60$).

#### 5. Multi-Provider LLM Router (`app/core/llm_provider.py`)
* **What is it?**: A resilience wrapper that provides unified `BaseChatModel` instances across multiple AI vendors.
* **Why does it exist?**: Single-provider architectures suffer from severe outage risks and rate-limit throttling during peak traffic.
* **Responsibilities**: Dynamically falls back from Groq (`qwen/qwen3.8-27b`) -> Google Gemini (`gemini-2.5-flash`) -> OpenAI (`gpt-4o-mini`) -> Offline Mock Extractor.
"""

CHAPTER_4 = """# 4. End-to-End Workflows

### Workflow 1: Resume Upload, Ingestion & Parsing
```
Candidate -> [Upload PDF] -> Frontend (/resume)
  -> POST /api/v1/resume/upload -> FastAPI (app/api/resume.py)
  -> Multi-Engine Text Extraction (pdfplumber -> PyPDF2 -> PyMuPDF fitz)
  -> LLM Extraction (app/services/extraction/llm_extractor.py)
  -> Pydantic ResumeData Schema Validation
  -> SQLAlchemy Database Insertion (Candidate, Resume tables)
  -> Candidate Profile Response -> Frontend Display
```
* **Step Details**:
  1. `resume.py:upload_resume()` receives `multipart/form-data`.
  2. Text extracted via fallback chain: `pdfplumber` (preserves tables) -> `PyPDF2` (standard text) -> `fitz` (scanned fallback).
  3. Structured extraction prompt sent to Groq/Gemini requesting JSON fields: `skills`, `experience_years`, `projects`, `education`.
  4. If LLM unavailable, offline regex heuristic extractor extracts emails, phone numbers, and known keyword lists.
  5. Candidate saved to DB and returned with status `200 OK`.

---

### Workflow 2: Job Description Matching & Recommendation
```
Frontend -> GET /api/v1/matching/recommendations?candidate_id=1
  -> FastAPI (app/api/matching.py) -> MatchingEngine (app/services/matching/engine.py)
  -> 1. HardFilterEvaluator (app/services/matching/hard_filters.py)
        - Must-have skills, minimum experience, degree check
        - Early disqualification flag if hard constraint violated
  -> 2. Hybrid RAG Search (rag_service.py) -> Extract role-specific context
  -> 3. WeightedScoringEngine (app/services/matching/weighted_scoring.py)
        - Skills Match (35%) + Experience (25%) + Projects (25%) + Domain (15%)
  -> 4. ExplanationGenerator (app/services/matching/explanation_generator.py)
  -> MatchResult DB Record -> Frontend Card Grid with match percentage & breakdown
```

---

### Workflow 3: Live WebRTC Voice Interview Session
```
Candidate -> [Start Interview] -> Frontend (/interview)
  -> LiveKit Cloud WebRTC Room Creation (wss://ai-interview-3f297yze.livekit.cloud)
  -> Agent Worker (backend/app.py) detects Room Event & joins
  -> Silero VAD detects speech onset -> Deepgram Nova-2 STT streams transcript
  -> AgentSession triggers on_user_speech_committed
  -> AdaptiveQuestionManager (adaptive_question_manager.py) determines active phase:
     [INTRO -> RESUME_CHECK -> CORE_TECH -> DEEP_DIVE -> BEHAVIORAL -> CANDIDATE_QA]
  -> RAG Context retrieved from selected JD (selected_jd.txt)
  -> Groq LPU (qwen/qwen3.8-27b) generates contextual conversational response
  -> Deepgram Aura TTS synthesizes audio -> LiveKit Cloud BVC cancels noise
  -> Audio Track streamed over WebRTC to Candidate Headset (<450ms total latency)
```

---

### Workflow 4: Real-Time Computer Vision Proctoring
```
Webcam Frame (Browser) -> WebSocket Stream -> /api/v1/face-detection/ws
  -> VideoProcessor (app/api/face_detection.py)
  -> MediaPipe FaceMesh (468 3D landmarks)
  -> 1. Head Pose Estimation (SolvePnP on 2D/3D facial points -> Yaw, Pitch, Roll)
  -> 2. Eye Aspect Ratio (EAR) Calculation -> Gaze direction & blink frequency
  -> 3. Multi-Face Counter (Haar/DNN cascade -> flags proxy interviewers)
  -> 4. MobileNet SSD Object Detector (flags mobile phones & books)
  -> JSON Analysis Frame pushed back over WebSocket -> Real-time warning HUD on UI
```

---

### Workflow 5: Post-Interview Evaluation & Scorecard Generation
```
Candidate/Interviewer -> [End Call] -> Frontend (/result)
  -> POST /api/v1/interview/evaluate (app/api/interview.py)
  -> InterviewService.evaluate_session() (app/services/interview_service.py)
  -> LLM Q&A Extraction from conversation transcript
  -> Strict Question-by-Question Rubric Evaluation (0-100 score + feedback)
  -> Aggregation: Total Score, Percentage, Strengths, Weaknesses, Recommendations
  -> Database Commit (InterviewResult, QAPair tables)
  -> Response returned -> Frontend renders interactive scorecard & radar charts
```
"""

CHAPTER_5 = """# 5. Technology & Concept Inventory

### 1. WebRTC & LiveKit Cloud
* **What is it?**: Web Real-Time Communication protocol providing peer-to-peer and Selective Forwarding Unit (SFU) audio/video streaming with ultra-low latency (<200ms transport).
* **Where used?**: Frontend `@livekit/components-react` and backend `voice-assistant/backend/app.py`.
* **Why used?**: Standard HTTP polling or WebSockets introduces jitter, buffering, and packet queuing unacceptable for natural voice conversation. WebRTC uses UDP/SRTP for real-time media delivery.
* **Internals**: LiveKit manages ICE negotiation, STUN/TURN traversal, adaptive bitrate streaming, and audio track multiplexing.

### 2. Silero Voice Activity Detection (VAD)
* **What is it?**: Lightweight deep learning model (~1MB) trained on 50,000+ hours of speech to detect human voice presence in raw audio chunks.
* **Where used?**: `backend/app.py` via `silero.VAD.load()`.
* **Why used?**: Determines exact boundaries when the candidate starts and stops speaking. Without VAD, the AI agent would either interrupt the candidate mid-sentence or wait in awkward silence.
* **Alternatives**: WebRTC energy thresholding (poor in noisy rooms), WebRTC VAD (less accurate).

### 3. Deepgram Nova-2 STT & Aura TTS
* **What is it?**: High-accuracy streaming speech recognition and neural text-to-speech engine optimized for conversational AI.
* **Where used?**: `backend/app.py` via `deepgram.STT(model="nova-2")` and `deepgram.TTS(model="aura-asteria-en")`.
* **Why used?**: Nova-2 provides word error rates (WER) under 7% with streaming latency under 200ms. Aura delivers natural conversational prosody without robotic pauses.
* **Trade-off**: Requires commercial API key vs self-hosted Whisper (which requires dedicated GPU compute).

### 4. Groq Language Processing Units (LPU)
* **What is it?**: Specialized tensor-streaming hardware designed specifically for deterministic, ultra-high throughput LLM inference (500+ tokens/sec).
* **Where used?**: `app/core/llm_provider.py` and `app.py` (`qwen/qwen3.8-27b`).
* **Why used?**: Standard GPU cloud providers take 1.5 to 3 seconds for Time-To-First-Token (TTFT). Groq delivers TTFT in under 150ms, enabling sub-500ms voice conversational loops.

### 5. Hybrid Search: Dense ChromaDB + Sparse BM25 via Reciprocal Rank Fusion (RRF)
* **What is it?**: Combining semantic vector similarity with probabilistic keyword matching.
* **Where used?**: `app/services/rag/hybrid_retrieval.py` and `app/services/rag_service.py`.
* **Formula**:
  $$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + rank_m(d)} \quad (k = 60)$$
* **Why used?**: Dense embeddings understand conceptual similarity but fail on exact technical acronyms (e.g. "OAuth2", "CI/CD", "PostgreSQL 16"). BM25 ensures exact keywords match while ChromaDB captures semantics.
"""

CHAPTER_6 = """# 6. AI/ML Deep Dive & Agent Architecture

### LiveKit Agent Session Lifecycle
The AI Voice Agent (`voice-assistant/backend/app.py`) operates as an event-driven state machine:
```
1. Worker Boot: cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
2. Room Connect: ctx.connect() -> Joins WebRTC room as participant
3. Audio Ingestion: RoomInputOptions(noise_cancellation=noise_cancellation.BVC())
4. Audio Event: Silero VAD detects candidate speech stop
5. Pipeline Trigger: Deepgram Nova-2 -> transcript string
6. State Evaluation: AdaptiveQuestionManager determines next technical phase
7. Generation: Groq LLM streams response tokens
8. Speech Synthesis: Deepgram Aura converts token chunks to PCM audio frames
9. Output Streaming: LiveKit AudioSource sends audio packets to WebRTC track
```

### Adaptive Questioning State Machine
The `AdaptiveQuestionManager` (`app/services/adaptive_question_manager.py`) tracks:
* **Current Phase**: `INTRODUCTION` (1 Q) -> `RESUME_VALIDATION` (2 Qs) -> `CORE_TECHNICAL` (3-4 Qs) -> `DEEP_DIVE` (2 Qs) -> `BEHAVIORAL` (1-2 Qs) -> `CANDIDATE_QA`.
* **Answer Quality Assessment**: Evaluates length, technical keyword density, and confidence. If answer is short or vague, transitions to follow-up probe; if answer is comprehensive, advances topic.
* **Topic Duplication Guard**: Checks previously covered topics in SQLite database to ensure the AI never repeats questions asked in prior sessions with the same candidate.

### Prompt Engineering & System Instructions
The system prompt enforces strict interviewer personas:
* Professional, encouraging yet rigorous technical evaluation tone.
* Concise verbal outputs: Prohibits markdown formatting, bullet points, or code blocks in spoken responses (since speech synthesizers read asterisks and brackets awkwardly).
* Single-question constraint: Instructs the LLM to ask exactly one clear question at a time.
"""

CHAPTER_7 = """# 7. RAG (Retrieval-Augmented Generation) Deep Dive

```
+----------------------------------------------------------------------------------+
|                              DOCUMENT INGESTION STAGE                            |
|  Job Description (.txt / .pdf) -> Text Cleaning -> RecursiveCharacterTextSplitter|
|  - Chunk Size: 500 characters                                                    |
|  - Chunk Overlap: 100 characters                                                 |
|  - Separators: ["\n\n", "\n", " ", ""]                                           |
+----------------------------------------+-----------------------------------------+
                                         |
                                         v
+----------------------------------------------------------------------------------+
|                              DUAL INDEXING STAGE                                 |
|  [Dense Index]                                 [Sparse Index]                    |
|  - Google text-embedding-004 (768 dim)         - BM25 Okapi Indexer              |
|  - Stored in Persistent ChromaDB               - In-Memory Document Tokenizer    |
|    (./db/chroma_db_v2)                           (Term Frequencies & IDF Table)  |
+----------------------------------------+-----------------------------------------+
                                         |
                                         v
+----------------------------------------------------------------------------------+
|                              QUERY & RETRIEVAL STAGE                             |
|  Query: "What are the core technical requirements for this backend role?"        |
|  - ChromaDB Semantic Search: Top-K = 4 candidates                               |
|  - BM25 Keyword Search: Top-K = 4 candidates                                     |
|  - Reciprocal Rank Fusion (RRF): Merge & score ranks with k=60                   |
|  - Citation Tracking: Attach source metadata (JD filename, section, chunk index) |
+----------------------------------------+-----------------------------------------+
```

### RAG Engineering Decisions & Defense:
1. **Why 500-Character Chunk Size with 100 Overlap?**
   * Job description requirements and skill sections are typically 2–4 sentences long. Chunks of 1500+ characters introduce noise and dilute vector similarity. 500 characters isolate single competencies (e.g. "Experience with FastAPI, SQLAlchemy, and Docker") while 100-character overlap prevents boundary truncation.
2. **Why Reciprocal Rank Fusion ($k=60$)?**
   * Dense vector cosine scores and BM25 scores have different mathematical scales. Normalizing them directly often causes dense scores to overpower sparse scores. RRF scores items strictly based on their rank positions across both lists, providing mathematically stable hybrid retrieval.
3. **How Hallucinations are Controlled**:
   * Prompts explicitly instruct the LLM: *"Base interview questions strictly on the provided Job Description context and candidate resume. Do not invent company technologies."*
"""

CHAPTER_8 = """# 8. Model & Provider Routing Decisions

| Provider / Model | Primary Role | Latency (TTFT) | Context Window | Selection Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Groq / Qwen 2.5 27B** (`qwen/qwen3.8-27b`) | Real-time Voice Agent & LLM Extraction | **~120ms** | 32,768 tokens | Exceptional reasoning and speed on Groq LPUs; delivers sub-500ms total conversational loop. |
| **Google Gemini 2.5 Flash** (`gemini-2.5-flash`) | Fallback LLM & Complex Ingestion | **~450ms** | 1,000,000 tokens | Massive context window for multi-page documents; reliable JSON structured outputs. |
| **Google text-embedding-004** | RAG Vector Embeddings | **~80ms** | 2,048 tokens | High retrieval accuracy (MTEB benchmark leader), native 768 dimensions, low cost. |
| **OpenAI GPT-4o-mini** | Secondary Fallback | **~600ms** | 128,000 tokens | Industry baseline fallback if both Groq and Gemini experience outages. |
| **Deepgram Nova-2** | Streaming STT | **~150ms** | Audio Stream | Lowest word error rate for technical and domain-specific terminology. |
| **Deepgram Aura** | Real-time TTS | **~180ms** | Text Stream | Natural conversational flow, low latency streaming audio buffers. |

### Routing & Fallback Logic (`app/core/llm_provider.py`):
```python
def get_chat_llm(temperature=0.3, prefer="groq"):
    if prefer == "groq" and os.getenv("GROQ_API_KEY"):
        return ChatGroq(model_name=os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"), ...)
    elif os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        return ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), ...)
    elif os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model_name=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), ...)
    else:
        return FallbackMockLLM()
```
"""

print("Chapters 1 to 8 loaded.")
