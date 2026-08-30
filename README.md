# AI Interview Assistant - Complete Documentation

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Frontend (Next.js)](#frontend-nextjs)
6. [Backend (FastAPI)](#backend-fastapi)
7. [LiveKit Agent](#livekit-agent)
8. [Database Schema](#database-schema)
9. [Workflows (LangGraph)](#workflows-langgraph)
10. [Services](#services)
11. [API Endpoints](#api-endpoints)
12. [Setup Instructions](#setup-instructions)
13. [Configuration](#configuration)
14. [Workflow Details](#workflow-details)
15. [Deployment](#deployment)

---

## 🎯 Project Overview

This is a **production-grade AI-powered interview assistant** that conducts automated technical interviews using:

- **Real-time voice interaction** via LiveKit
- **Advanced AI evaluation** using multi-agent LangGraph workflows
- **JD-focused assessment** with agentic RAG for accurate matching
- **Real-time voice analysis** for confidence, nervousness, and speech patterns
- **Comprehensive memory system** for context-aware evaluations
- **Face detection and attention monitoring** for proctoring

### Key Features

- ✅ **JD-Focused Interviews**: Questions and evaluation based on specific job descriptions
- ✅ **Multi-Agent Evaluation**: Parallel specialized agents for technical accuracy, communication, problem-solving, depth, and practical application
- ✅ **Real-time Voice Analysis**: Leverages OpenAI Realtime API for live voice characteristics analysis
- ✅ **Advanced Workflows**: LangGraph-based pipeline with parallel processing and looping
- ✅ **Memory Integration**: Dual memory system (working + long-term) for context retention
- ✅ **Production Ready**: Security, logging, monitoring, error handling, and best practices

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   React UI   │  │  LiveKit SDK │  │  Face Detection WS   │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/WebSocket
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                    Backend (FastAPI)                             │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  API Routes: auth, interview, candidates, recordings,   │    │
│  │  jds, matching, rag, admin, face_detection              │    │
│  └──────────────────────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  Services Layer                                           │    │
│  │  - Interview Service (Agentic Evaluator)                 │    │
│  │  - RAG Service (Hybrid Retrieval + Reranking)            │    │
│  │  - Matching Engine (Hard Filters + Weighted Scoring)     │    │
│  │  - Memory Manager (Working + Long-term)                  │    │
│  │  - Storage, Transcription, Extraction                   │    │
│  └──────────────────────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  Workflows (LangGraph)                                    │    │
│  │  - Interview Pipeline (Storage → Transcription →        │    │
│  │    Extraction → Matching → RAG → Next Steps)           │    │
│  └──────────────────────────────────────────────────────────┘    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ PostgreSQL + ChromaDB
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                    Database Layer                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐    │
│  │  PostgreSQL  │  │  ChromaDB    │  │  File Storage        │    │
│  │  (SQLAlchemy) │  │  (Vectors)  │  │  (Local/Cloud)       │    │
│  └──────────────┘  └──────────────┘  └──────────────────────┘    │
└───────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    LiveKit Agent (app.py)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  OpenAI Realtime Model (gpt-4o-realtime-preview)          │  │
│  │  - Voice-to-Text                                           │  │
│  │  - Real-time Voice Analysis                                │  │
│  │  - Turn Detection (Server VAD)                             │  │
│  │  - Interview Questions (JD-based)                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Interview Initiation**:
   - Frontend connects to LiveKit room
   - LiveKit agent (`app.py`) joins the room
   - Agent loads JD-specific questions
   - Interview begins with real-time voice interaction

2. **During Interview**:
   - Real-time audio → OpenAI Realtime API → Transcription + Voice Analysis
   - Face detection WebSocket → Attention monitoring
   - Q&A pairs stored in real-time

3. **Post-Interview**:
   - Recording uploaded to storage
   - LangGraph workflow processes:
     - Transcription (OpenAI Whisper)
     - Resume extraction (LLM-based)
     - JD matching (Hard filters + Weighted scoring)
     - RAG context retrieval
     - Multi-agent evaluation
   - Results stored in database

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14+ (React 18+)
- **Language**: TypeScript
- **UI Components**: 
  - LiveKit Components (React)
  - shadcn/ui
  - Tailwind CSS
- **State Management**: React Context + Hooks
- **Real-time Communication**: LiveKit JavaScript SDK
- **HTTP Client**: Fetch API

### Backend
- **Framework**: FastAPI (Python 3.12+)
- **ASGI Server**: Uvicorn
- **Database ORM**: SQLAlchemy 2.0+
- **Database**: PostgreSQL
- **Vector Store**: ChromaDB
- **Migrations**: Alembic

### AI & ML
- **LLM**: OpenAI GPT-4o (Realtime + Standard)
- **Embeddings**: OpenAI `text-embedding-3-small`
- **Voice Processing**: OpenAI Realtime API
- **Transcription**: OpenAI Whisper
- **Orchestration**: LangGraph
- **RAG Framework**: LangChain

### Real-time Communication
- **Platform**: LiveKit
- **Protocol**: WebRTC
- **Agent Framework**: LiveKit Agents SDK

### Additional Services
- **Face Detection**: MediaPipe (with OpenCV fallback)
- **Image Processing**: OpenCV
- **Security**: 
  - JWT (python-jose)
  - bcrypt (password hashing)
- **Validation**: Pydantic V2

---

## 📁 Project Structure

```
interview/
├── voice-assistant/
│   ├── frontend/                    # Next.js frontend
│   │   ├── app/                      # Next.js app router
│   │   │   ├── (app)/               # Protected routes
│   │   │   ├── api/                 # API routes (token server)
│   │   │   ├── components/          # React components
│   │   │   ├── interview/           # Interview page
│   │   │   ├── jobs/                # Job listings
│   │   │   ├── login/                # Login page
│   │   │   ├── signup/              # Signup page
│   │   │   └── resume/              # Resume upload
│   │   ├── components/              # Shared components
│   │   │   ├── livekit/             # LiveKit components
│   │   │   ├── face-detection/      # Face detection UI
│   │   │   ├── interview/           # Interview components
│   │   │   └── ui/                  # UI components (shadcn)
│   │   ├── hooks/                   # React hooks
│   │   ├── lib/                     # Utilities
│   │   └── package.json
│   │
│   └── backend/                      # FastAPI backend
│       ├── app/
│       │   ├── api/                 # API routes
│       │   │   ├── auth.py          # Authentication
│       │   │   ├── interview.py     # Interview endpoints
│       │   │   ├── candidates.py    # Candidate management
│       │   │   ├── recordings.py    # Recording uploads
│       │   │   ├── jds.py           # Job description CRUD
│       │   │   ├── matching.py      # Match results
│       │   │   ├── rag.py           # RAG queries
│       │   │   ├── admin.py         # Admin endpoints
│       │   │   └── face_detection.py # Face detection WS
│       │   │
│       │   ├── core/                # Core configuration
│       │   │   ├── config.py        # Settings (Pydantic)
│       │   │   ├── security.py      # JWT, password hashing
│       │   │   └── exceptions.py   # Custom exceptions
│       │   │
│       │   ├── db/                  # Database
│       │   │   └── database.py      # SQLAlchemy setup
│       │   │
│       │   ├── models/              # SQLAlchemy models
│       │   │   ├── user.py
│       │   │   ├── candidate.py
│       │   │   ├── jd.py
│       │   │   ├── recording.py
│       │   │   ├── matching.py
│       │   │   ├── memory.py
│       │   │   └── admin.py
│       │   │
│       │   ├── schemas/             # Pydantic schemas
│       │   │   ├── user.py
│       │   │   ├── candidate.py
│       │   │   ├── interview.py
│       │   │   ├── jd.py
│       │   │   ├── matching.py
│       │   │   └── rag.py
│       │   │
│       │   ├── services/            # Business logic
│       │   │   ├── interview_service.py      # Interview evaluation
│       │   │   ├── rag_service.py            # RAG operations
│       │   │   ├── voice_analysis.py         # Voice analysis
│       │   │   ├── user_service.py          # User management
│       │   │   │
│       │   │   ├── evaluation/              # Evaluation agents
│       │   │   │   └── agentic_evaluator.py  # Multi-agent evaluator
│       │   │   │
│       │   │   ├── storage/                  # Storage interfaces
│       │   │   │   ├── base.py
│       │   │   │   ├── local.py
│       │   │   │   └── (azure_blob, aws_s3, gcp_storage)
│       │   │   │
│       │   │   ├── transcription/           # Transcription services
│       │   │   │   ├── base.py
│       │   │   │   └── openai_realtime.py
│       │   │   │
│       │   │   ├── extraction/              # Data extraction
│       │   │   │   └── llm_extractor.py
│       │   │   │
│       │   │   ├── matching/                # JD matching engine
│       │   │   │   ├── engine.py
│       │   │   │   ├── hard_filters.py
│       │   │   │   ├── weighted_scoring.py
│       │   │   │   ├── evidence_tracker.py
│       │   │   │   └── explanation_generator.py
│       │   │   │
│       │   │   ├── vector_stores/           # Vector databases
│       │   │   │   ├── base.py
│       │   │   │   └── chroma.py
│       │   │   │
│       │   │   ├── rag/                     # RAG components
│       │   │   │   ├── hybrid_retrieval.py
│       │   │   │   ├── reranker.py
│       │   │   │   └── citation_tracker.py
│       │   │   │
│       │   │   ├── memory/                  # Memory system
│       │   │   │   ├── manager.py
│       │   │   │   ├── working_memory.py
│       │   │   │   ├── long_term_memory.py
│       │   │   │   └── retrieval.py
│       │   │   │
│       │   │   └── interfaces/              # Service interfaces
│       │   │       ├── storage.py
│       │   │       ├── transcriber.py
│       │   │       ├── extractor.py
│       │   │       ├── vector_store.py
│       │   │       └── reranker.py
│       │   │
│       │   └── workflows/                   # LangGraph workflows
│       │       ├── interview_pipeline.py    # Main pipeline
│       │       ├── state.py                 # Workflow state
│       │       ├── nodes/                   # Workflow nodes
│       │       │   ├── storage.py
│       │       │   ├── transcription.py
│       │       │   ├── extraction.py
│       │       │   ├── matching.py
│       │       │   ├── rag_query.py
│       │       │   └── next_steps.py
│       │       └── routers/                 # Conditional routing
│       │           └── conditional.py
│       │
│       ├── app.py                          # LiveKit agent entrypoint
│       ├── main.py                         # FastAPI entrypoint
│       ├── requirements.txt                # Python dependencies
│       └── alembic/                        # Database migrations
│
└── README.md                               # This file
```

---

## 🎨 Frontend (Next.js)

### Architecture

The frontend is built with **Next.js 14+** using the App Router pattern. It provides:

- **Real-time interview interface** with LiveKit integration
- **Face detection monitoring** via WebSocket
- **Authentication** (login/signup)
- **Resume upload** functionality
- **Job listing** and selection
- **Interview results** display

### Key Components

#### 1. **Interview Assistant** (`components/interview-assistant.tsx`)
- Main interview interface
- LiveKit room connection
- Real-time audio/video handling
- Transcription display
- Q&A tracking

#### 2. **LiveKit Components** (`components/livekit/`)
- Room connection management
- Audio/video track handling
- Participant management
- Connection state management

#### 3. **Face Detection** (`components/face-detection/`)
- WebSocket connection to backend
- Real-time frame capture and sending
- Attention monitoring display
- Proctoring alerts

#### 4. **Authentication** (`components/auth/`)
- Login form
- Signup form
- JWT token management
- Protected route handling

### Key Hooks

- `useRoomConnection.ts`: Manages LiveKit room connection
- `useChatAndTranscription.ts`: Handles chat and transcription
- `useAttentionMonitor.ts`: Monitors attention metrics
- `useConnectionDetails.ts`: Tracks connection details

### API Integration

The frontend communicates with the backend via:
- **REST API**: `/api/v1/*` endpoints
- **WebSocket**: `/face-detection/ws/{client_id}` for face detection
- **LiveKit**: Direct WebRTC connection for audio/video

### Token Server

The frontend includes a token server (`app/api/token/route.ts`) that generates LiveKit access tokens for authenticated users.

---

## ⚙️ Backend (FastAPI)

### Architecture

The backend is a **FastAPI** application that provides:

- **RESTful API** for all operations
- **WebSocket endpoints** for real-time features
- **Service layer** for business logic
- **Database models** with SQLAlchemy
- **Workflow orchestration** with LangGraph

### Entry Point

**File**: `backend/main.py`

```python
from fastapi import FastAPI
from app.api import api_router

app = FastAPI(title="Interview Assistant API")
app.include_router(api_router, prefix="/api/v1")
```

**Run**: `uvicorn main:app --reload`

### API Routes

All routes are prefixed with `/api/v1`:

#### Authentication (`/api/v1/auth`)
- `POST /signup`: User registration
- `POST /login`: User authentication (returns JWT)

#### Interview (`/api/v1/interview`)
- `POST /evaluate`: Evaluate interview session
- `GET /history`: Get interview history
- `GET /{session_id}`: Get specific interview result

#### Candidates (`/api/v1/candidates`)
- `GET /`: List candidates
- `GET /{candidate_id}`: Get candidate details
- `POST /`: Create candidate

#### Recordings (`/api/v1/recordings`)
- `POST /upload`: Upload interview recording
- `GET /{recording_id}`: Get recording details

#### Job Descriptions (`/api/v1/jds`)
- `GET /`: List JDs (admin only)
- `POST /`: Create JD (admin only)
- `PUT /{jd_id}`: Update JD (admin only)
- `DELETE /{jd_id}`: Delete JD (admin only)
- `POST /{jd_id}/select`: Select JD for interview

#### Matching (`/api/v1/matching`)
- `GET /{candidate_id}/{jd_id}`: Get match result

#### RAG (`/api/v1/rag`)
- `POST /query`: Query RAG system

#### Face Detection (`/face-detection`)
- `WebSocket /ws/{client_id}`: Real-time face detection

### Core Services

#### 1. **Interview Service** (`services/interview_service.py`)
- Orchestrates interview evaluation
- Integrates with `AgenticEvaluator`
- Converts evaluation results to response format
- Persists results to database

#### 2. **Agentic Evaluator** (`services/evaluation/agentic_evaluator.py`)
- Multi-agent LangGraph workflow
- Parallel evaluation agents:
  - Technical Accuracy
  - Communication Clarity
  - Problem-Solving Approach
  - Depth of Knowledge
  - Practical Application
- Consensus validation
- Final report generation

#### 3. **RAG Service** (`services/rag_service.py`)
- Loads job descriptions into vector store
- Processes resumes
- Matches resumes with JDs
- Provides context for evaluation

#### 4. **Matching Engine** (`services/matching/`)
- Hard filters (must-have requirements)
- Weighted scoring (nice-to-have requirements)
- Evidence tracking
- Explanation generation

#### 5. **Memory Manager** (`services/memory/manager.py`)
- Working memory (session-specific)
- Long-term memory (persistent)
- Memory retrieval and storage

### Database Models

#### User Models
- `User`: Basic user account
- `AdminUser`: Admin accounts

#### Candidate Models
- `Candidate`: Candidate profile
- `Resume`: Resume files and extracted data

#### Interview Models
- `InterviewResult`: Interview evaluation results
- `QAPair`: Question-answer pairs

#### JD Models
- `JobDescription`: Job description metadata
- `JDVersion`: Versioned JD content

#### Recording Models
- `Recording`: Audio/video recordings
- `Transcript`: Transcription data

#### Matching Models
- `MatchResult`: JD-candidate matching results
- `EvidenceTracking`: Evidence for matching

#### Memory Models
- `MemoryStore`: Memory storage

---

## 🎤 LiveKit Agent

### Entry Point

**File**: `backend/app.py`

This is the **LiveKit agent** that handles real-time voice interviews.

### Architecture

```python
async def entrypoint(ctx: JobContext):
    # Load JD-specific questions
    session_questions = get_random_interview_questions()
    
    # Set up OpenAI Realtime Model
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            model="gpt-4o-realtime-preview",
            turn_detection=TurnDetection(...)
        )
    )
    
    # Start interview agent
    await session.start(
        agent=Assistant(session_questions, role_description),
        room=ctx.room
    )
```

### Key Features

1. **JD-Based Questions**: Loads questions from `interview_questions/` based on selected JD
2. **Real-time Voice**: Uses OpenAI Realtime API for natural conversation
3. **Turn Detection**: Server-side VAD (Voice Activity Detection)
4. **Noise Cancellation**: LiveKit Cloud BVC (if available)
5. **Metrics Collection**: Tracks usage and performance

### Question Loading

Questions are loaded from files in `interview_questions/` directory:
- Format: `{role}_{level}.txt` (e.g., `backend_developer_senior.txt`)
- Selected JD is read from `selected_jd.txt` or `INTERVIEW_JD_SOURCE` env var

### Assistant Class

The `Assistant` class (defined in `app.py`) handles:
- Interview flow
- Question asking
- Answer collection
- Follow-up questions (minimal)
- Session management

### Running the Agent

```bash
# Set environment variables
export LIVEKIT_URL=wss://your-livekit-server.com
export LIVEKIT_API_KEY=your-api-key
export LIVEKIT_API_SECRET=your-api-secret
export OPENAI_API_KEY=your-openai-key

# Run agent
python app.py dev
```

---

## 🗄️ Database Schema

### Core Tables

#### Users & Authentication
- **users**: User accounts
  - `id`, `email`, `hashed_password`, `created_at`
- **admin_users**: Admin accounts
  - `id`, `username`, `email`, `hashed_password`, `is_active`

#### Candidates
- **candidates**: Candidate profiles
  - `id`, `user_id`, `email`, `full_name`, `phone`
- **resumes**: Resume files
  - `id`, `candidate_id`, `file_path`, `extracted_data`, `raw_text`

#### Job Descriptions
- **job_descriptions**: JD metadata
  - `id`, `title`, `description`, `current_version_id`, `admin_id`
- **jd_versions**: Versioned JD content
  - `id`, `jd_id`, `version_number`, `content`, `requirements`, `is_active`

#### Interviews
- **interview_results**: Evaluation results
  - `id`, `user_id`, `session_id`, `total_score`, `overall_analysis`, `detailed_feedback`
- **qa_pairs**: Q&A pairs
  - `id`, `user_id`, `session_id`, `question`, `answer`, `score`

#### Recordings
- **recordings**: Audio/video files
  - `id`, `candidate_id`, `session_id`, `file_path`, `format`, `duration_seconds`
- **transcripts**: Transcription data
  - `id`, `recording_id`, `transcript_json`, `diarization_data`, `confidence_scores`

#### Matching
- **match_results**: JD-candidate matching
  - `id`, `candidate_id`, `jd_id`, `hard_filter_passed`, `weighted_score`, `threshold_passed`
- **evidence_tracking**: Evidence for matching
  - `id`, `match_result_id`, `skill_name`, `evidence_type`, `confidence`

#### Memory
- **memory_store**: Memory storage
  - `id`, `candidate_id`, `session_id`, `memory_type`, `content`, `embeddings`, `metadata_json`

#### Admin
- **admin_settings**: Admin configuration
  - `id`, `jd_id`, `setting_name`, `setting_value`, `version`
- **audit_logs**: Admin action logs
  - `id`, `admin_id`, `action_type`, `resource_type`, `changes`

### Relationships

- `Candidate` → `Resume` (one-to-many)
- `Candidate` → `Recording` (one-to-many)
- `Candidate` → `MatchResult` (one-to-many)
- `JobDescription` → `JDVersion` (one-to-many, with `current_version_id` reference)
- `JDVersion` → `JobDescription` (many-to-one via `jd_id`)
- `Recording` → `Transcript` (one-to-one)
- `MatchResult` → `EvidenceTracking` (one-to-many)

---

## 🔄 Workflows (LangGraph)

### Interview Pipeline

**File**: `workflows/interview_pipeline.py`

The main LangGraph workflow orchestrates the entire interview processing pipeline.

#### Workflow State

```python
class InterviewPipelineState(TypedDict):
    # Input
    recording_id: int
    candidate_id: int
    jd_id: int
    
    # Processing
    recording_path: Optional[str]
    transcript: Optional[Dict]
    extracted_resume: Optional[Dict]
    match_result: Optional[Dict]
    rag_context: Optional[Dict]
    
    # Output
    next_steps: List[str]
    errors: List[str]
```

#### Workflow Nodes

1. **Storage Node** (`nodes/storage.py`)
   - Loads recording from storage
   - Validates file existence

2. **Transcription Node** (`nodes/transcription.py`)
   - Transcribes audio using OpenAI Whisper
   - Extracts diarization data
   - Calculates confidence scores

3. **Extraction Node** (`nodes/extraction.py`)
   - Extracts structured data from resume
   - Uses LLM for parsing

4. **Matching Node** (`nodes/matching.py`)
   - Runs hard filters
   - Calculates weighted score
   - Tracks evidence
   - Generates explanation

5. **RAG Query Node** (`nodes/rag_query.py`)
   - Retrieves relevant JD content
   - Retrieves resume content
   - Provides context for evaluation

6. **Next Steps Node** (`nodes/next_steps.py`)
   - Determines next actions
   - Updates memory
   - Schedules evaluation

#### Workflow Graph

```
[START]
  ↓
[Storage Node] → Load recording
  ↓
[Transcription Node] → Transcribe audio
  ↓
[Extraction Node] → Extract resume data
  ↓
[Matching Node] → Match candidate with JD
  ↓
[RAG Query Node] → Retrieve context
  ↓
[Next Steps Node] → Determine actions
  ↓
[END]
```

#### Conditional Routing

The workflow includes conditional routing based on:
- Hard filter results (pass/fail)
- Match score thresholds
- Error conditions

---

## 🔧 Services

### 1. Evaluation Service

#### Agentic Evaluator (`services/evaluation/agentic_evaluator.py`)

**Multi-Agent LangGraph Workflow** for comprehensive interview assessment.

**State**:
```python
class EvaluationState(TypedDict):
    session_id: str
    questions: List[str]
    answers: List[str]
    jd_context: Dict
    resume_context: Dict
    technical_score: float
    communication_score: float
    problem_solving_score: float
    depth_score: float
    practical_score: float
    consensus_score: float
    final_report: Dict
```

**Agents**:
1. **Technical Evaluator**: Assesses technical accuracy
2. **Communication Evaluator**: Evaluates clarity and articulation
3. **Problem-Solving Evaluator**: Analyzes approach and methodology
4. **Depth Evaluator**: Measures knowledge depth
5. **Practical Evaluator**: Assesses real-world application

**Workflow**:
```
[Context Retrieval] → Retrieve JD + Resume
  ↓
[Parallel Evaluation] → All 5 agents evaluate simultaneously
  ↓
[Consensus Validation] → Aggregate scores, calculate variance
  ↓
[Report Generation] → Generate final comprehensive report
```

### 2. RAG Service

#### Hybrid Retrieval (`services/rag/hybrid_retrieval.py`)

Combines:
- **Vector Search**: Semantic similarity (ChromaDB)
- **Keyword Search**: BM25 or similar
- **Reranking**: Cross-encoder for final ranking

#### Citation Tracking (`services/rag/citation_tracker.py`)

Tracks sources for all retrieved information.

### 3. Matching Engine

#### Hard Filters (`services/matching/hard_filters.py`)

Must-have requirements:
- Years of experience
- Required skills
- Education level
- Certifications

#### Weighted Scoring (`services/matching/weighted_scoring.py`)

Nice-to-have requirements with weights:
- Preferred skills
- Bonus qualifications
- Cultural fit indicators

#### Evidence Tracking (`services/matching/evidence_tracker.py`)

Records evidence for each skill/requirement:
- Source location (resume, transcript, etc.)
- Confidence score
- Evidence type

### 4. Memory System

#### Working Memory (`services/memory/working_memory.py`)

Session-specific memory:
- Current interview context
- Q&A history
- Skill coverage tracking
- Temporary insights

#### Long-Term Memory (`services/memory/long_term_memory.py`)

Persistent memory:
- Candidate profile
- Historical interviews
- Skill evolution
- Evaluation patterns

#### Memory Retrieval (`services/memory/retrieval.py`)

Retrieves relevant memory:
- Semantic search
- Time-based filtering
- Context-aware retrieval

### 5. Storage Services

**Interfaces**: `services/interfaces/storage.py`

**Implementations**:
- `LocalStorageService`: Local file system
- `AzureBlobStorageService`: Azure Blob Storage (stub)
- `AWSS3StorageService`: AWS S3 (stub)
- `GCPStorageService`: GCP Cloud Storage (stub)

### 6. Transcription Services

**Interfaces**: `services/interfaces/transcriber.py`

**Implementations**:
- `OpenAIRealtimeTranscriber`: OpenAI Whisper API
- `AzureRealtimeTranscriber`: Azure Speech (stub)

### 7. Extraction Services

**LLM Extractor** (`services/extraction/llm_extractor.py`):
- Extracts structured data from resumes
- Extracts key information from transcripts
- Uses GPT-4 for parsing

---

## 📡 API Endpoints

### Authentication

#### `POST /api/v1/auth/signup`
Register a new user.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "message": "User created successfully"
}
```

#### `POST /api/v1/auth/login`
Authenticate user and get JWT token.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```

### Interview

#### `POST /api/v1/interview/evaluate`
Evaluate an interview session.

**Request**:
```json
{
  "session_id": "session_123",
  "conversation": [...],
  "questions": ["Q1", "Q2"],
  "answers": ["A1", "A2"]
}
```

**Response**:
```json
{
  "session_id": "session_123",
  "total_score": 85,
  "max_score": 100,
  "percentage": 85.0,
  "overall_analysis": "...",
  "detailed_feedback": [...],
  "strengths": [...],
  "areas_for_improvement": [...]
}
```

### Candidates

#### `GET /api/v1/candidates`
List all candidates (authenticated).

#### `POST /api/v1/candidates`
Create a new candidate.

### Recordings

#### `POST /api/v1/recordings/upload`
Upload interview recording.

**Request**: Multipart form data with file.

### Job Descriptions (Admin Only)

#### `GET /api/v1/jds`
List all JDs.

#### `POST /api/v1/jds`
Create a new JD.

#### `POST /api/v1/jds/{jd_id}/select`
Select JD for interview.

### Matching

#### `GET /api/v1/matching/{candidate_id}/{jd_id}`
Get match result between candidate and JD.

### RAG

#### `POST /api/v1/rag/query`
Query the RAG system.

**Request**:
```json
{
  "query": "What are the key requirements?",
  "jd_id": 1,
  "candidate_id": 1
}
```

### Face Detection

#### `WebSocket /face-detection/ws/{client_id}`
Real-time face detection WebSocket.

**Message Format**:
```json
{
  "type": "video_frame",
  "data": {
    "image": "base64_encoded_image"
  }
}
```

**Response**:
```json
{
  "type": "analysis_result",
  "data": {
    "analysis": {
      "face_detected": true,
      "attention_score": 0.85,
      "eye_tracking": {...},
      "head_pose": {...}
    }
  }
}
```

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 14+
- LiveKit account (or self-hosted)
- OpenAI API key

### Backend Setup

1. **Clone and navigate**:
```bash
cd voice-assistant/backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
Create `.env` file:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/interview_db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# LiveKit (for agent)
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-api-secret

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Storage
STORAGE_PROVIDER=local
STORAGE_BASE_PATH=./uploads

# Vector Store
VECTOR_STORE_PROVIDER=chroma
CHROMA_PERSIST_DIR=./db/vector_store
```

5. **Set up database**:
```bash
# Create database
createdb interview_db

# Run migrations
alembic upgrade head
```

6. **Run FastAPI server**:
```bash
uvicorn main:app --reload
```

### Frontend Setup

1. **Navigate to frontend**:
```bash
cd "../frontend"
```

2. **Install dependencies**:
```bash
npm install
# or
pnpm install
```

3. **Set up environment variables**:
Create `.env.local`:
```env
NEXT_PUBLIC_LIVEKIT_URL=wss://your-livekit-server.com
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. **Run development server**:
```bash
npm run dev
```

### LiveKit Agent Setup

1. **Navigate to backend**:
```bash
cd "../backend"
```

2. **Set environment variables** (already set in `.env`):
```env
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
OPENAI_API_KEY=your-openai-key
```

3. **Run agent**:
```bash
python app.py dev
```

### Generate Secret Key

```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## ⚙️ Configuration

### Backend Configuration

**File**: `app/core/config.py`

All configuration is managed via Pydantic Settings:

```python
class Settings(BaseSettings):
    # App
    app_name: str = "Interview Assistant API"
    version: str = "1.0.0"
    debug: bool = False
    
    # Database
    database_url: str
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OpenAI
    openai_api_key: str
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000"]
    
    # Storage
    storage_provider: str = "local"
    storage_base_path: str = "./uploads"
    
    # Vector Store
    vector_store_provider: str = "chroma"
    chroma_persist_dir: str = "./db/vector_store"
    
    # Evaluation
    evaluation_model: str = "gpt-4o"
    evaluation_temperature: float = 0.3
    evaluation_confidence_threshold: float = 0.7
```

### Frontend Configuration

**File**: `app-config.ts`

```typescript
export const appConfig = {
  livekit: {
    url: process.env.NEXT_PUBLIC_LIVEKIT_URL || "",
  },
  api: {
    url: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },
};
```

---

## 🔄 Workflow Details

### Interview Processing Flow

1. **Interview Completion**:
   - Recording saved
   - Q&A pairs stored
   - Session metadata saved

2. **Workflow Trigger**:
   - Recording uploaded via API
   - LangGraph workflow starts

3. **Processing Steps**:
   - **Storage**: Load recording file
   - **Transcription**: Convert audio to text
   - **Extraction**: Extract resume data
   - **Matching**: Match candidate with JD
   - **RAG**: Retrieve relevant context
   - **Evaluation**: Multi-agent evaluation
   - **Memory**: Update memory stores

4. **Result Storage**:
   - Evaluation results saved
   - Match results saved
   - Memory updated
   - Next steps determined

### Evaluation Workflow

1. **Context Retrieval**:
   - Load JD content from vector store
   - Load resume content
   - Prepare context for agents

2. **Parallel Evaluation**:
   - All 5 agents evaluate simultaneously
   - Each agent scores and provides notes

3. **Consensus Validation**:
   - Aggregate scores
   - Calculate variance
   - Determine confidence
   - Flag for human review if needed

4. **Report Generation**:
   - Synthesize all evaluations
   - Generate comprehensive report
   - Provide recommendations

---

## 🚢 Deployment

### Backend Deployment

#### Using Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Environment Variables

Set all required environment variables in your deployment platform.

### Frontend Deployment

#### Vercel (Recommended)

1. Connect GitHub repository
2. Set environment variables
3. Deploy

#### Other Platforms

Build and deploy:
```bash
npm run build
npm start
```

### LiveKit Agent Deployment

Deploy as a separate service that connects to LiveKit Cloud or self-hosted LiveKit server.

### Database

Use managed PostgreSQL (AWS RDS, Google Cloud SQL, Azure Database) or self-hosted.

### Vector Store

ChromaDB can be:
- Embedded (current setup)
- Server mode (for production)
- Cloud-hosted

---

## 📝 Additional Notes

### Security Considerations

- ✅ JWT authentication
- ✅ Password hashing (bcrypt)
- ✅ CORS configuration
- ✅ Input validation (Pydantic)
- ⚠️ Rate limiting (to be implemented)
- ⚠️ API key rotation (to be implemented)

### Performance Optimization

- Database connection pooling
- Vector store indexing
- Caching (to be implemented)
- Async processing for heavy operations

### Monitoring

- Logging with Python `logging`
- Metrics collection (LiveKit)
- Error tracking (to be implemented)

### Testing

- Unit tests (to be implemented)
- Integration tests (to be implemented)
- E2E tests (to be implemented)

---

## 🎓 Understanding the Codebase

### Key Concepts

1. **Agentic RAG**: Uses LangGraph for multi-step, context-aware retrieval
2. **Multi-Agent Evaluation**: Parallel specialized agents for comprehensive assessment
3. **JD-Focused**: Everything is centered around the job description
4. **Real-time Processing**: LiveKit + OpenAI Realtime for natural conversation
5. **Memory System**: Maintains context across sessions

### Code Patterns

- **Service Layer**: Business logic separated from API routes
- **Interface Pattern**: Abstract base classes for extensibility
- **Factory Pattern**: Service factories for different providers
- **Repository Pattern**: Database access through models
- **Workflow Pattern**: LangGraph for complex orchestration

### Best Practices

- Type hints throughout
- Pydantic for validation
- SQLAlchemy for database
- Async/await for I/O operations
- Error handling and logging
- Configuration via environment variables

---

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LiveKit Documentation](https://docs.livekit.io/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Next.js Documentation](https://nextjs.org/docs)
- [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime)

---

## 🤝 Contributing

This is a production-grade system. When contributing:

1. Follow existing code patterns
2. Add type hints
3. Write tests
4. Update documentation
5. Ensure security best practices

---

## 📄 License

[Your License Here]

---

**Last Updated**: December 2024

**Version**: 1.0.0

