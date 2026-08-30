import logging
import os
import random
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError, ProgrammingError
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    RoomOutputOptions,
    RunContext,
    WorkerOptions,
    cli,
    metrics,
)
from livekit.agents.llm import function_tool
from livekit.agents.voice import MetricsCollectedEvent
from livekit.plugins import cartesia, deepgram, noise_cancellation, openai, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.plugins import openai
from openai.types.beta.realtime.session import TurnDetection

from app.services.adaptive_question_manager import (
    AdaptiveQuestionManager,
    InterviewPhase,
    AnswerQuality,
    QuestionContext
)
from app.services.answer_assessor import AnswerAssessor

logger = logging.getLogger("agent")

load_dotenv()

def _read_selected_jd_filename() -> str:
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"[Interview] backend_dir resolved to: {backend_dir}")
    selected_path = os.path.join(backend_dir, "selected_jd.txt")
    logger.info(f"[Interview] checking selected file at: {selected_path}")
    if os.path.exists(selected_path):
        try:
            with open(selected_path, "r", encoding="utf-8") as f:
                jd = f.read().strip()
                logger.info(f"[Interview] Selected JD from file: {jd}")
                return jd
        except Exception:
            return ""
    else:
        logger.info(f"[Interview] selected_jd.txt not found at: {selected_path}")
    # fallback to env var
    jd_env = os.getenv("INTERVIEW_JD_SOURCE", "").strip()
    if jd_env:
        logger.info(f"[Interview] Selected JD from env INTERVIEW_JD_SOURCE: {jd_env}")
    return jd_env

def _load_questions_from_file(jd_filename: str) -> List[str]:
    if not jd_filename:
        logger.info("[Interview] No JD filename provided to _load_questions_from_file")
        return []
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    questions_dir = os.path.join(backend_dir, "interview_questions")
    questions_path = os.path.join(questions_dir, jd_filename)
    logger.info(f"[Interview] attempting to load questions from: {questions_path}")
    if not os.path.exists(questions_path):
        logger.warning(f"[Interview] Questions file not found: {questions_path}")
        return []
    try:
        with open(questions_path, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f.readlines()]
        # extract numbered question lines like "1) ..."
        questions: List[str] = []
        for ln in lines:
            if ") " in ln and ln.split(") ", 1)[0].strip().rstrip("0123456789")=="":
                # simple heuristic; otherwise accept any non-empty line without headers
                pass
        # fallback: accept lines that look like numbered questions or start with a dash
        for ln in lines:
            if not ln:
                continue
            if ln[0].isdigit() and ") " in ln:
                q = ln.split(") ", 1)[1].strip()
                if q:
                    questions.append(q)
            elif ln.lower().startswith(("easy", "medium", "hard")):
                continue
            elif ln.startswith("- "):
                q = ln[2:].strip()
                if q:
                    questions.append(q)
        logger.info(f"[Interview] Loaded {len(questions)} questions from {jd_filename}")
        return questions
    except Exception:
        logger.exception(f"[Interview] Exception while loading questions from: {questions_path}")
        return []

def calculate_experience_years(resume_data: Optional[Dict[str, Any]]) -> float:
    """Calculate total years of experience from resume data"""
    if not resume_data:
        return 0.0
    
    # First try explicit experience_years
    if resume_data.get("experience_years"):
        try:
            return float(resume_data["experience_years"])
        except (ValueError, TypeError):
            pass
    
    # Calculate from roles/experiences
    total_years = 0.0
    experiences = resume_data.get("experiences", [])
    roles = resume_data.get("roles", [])
    
    # Combine experiences and roles
    all_roles = experiences + roles
    
    if not all_roles:
        return 0.0
    
    # Calculate from role dates
    from datetime import datetime
    
    for role in all_roles:
        start_date = role.get("start_date") or role.get("start")
        end_date = role.get("end_date") or role.get("end") or "present"
        
        if start_date:
            try:
                # Parse dates (simplified - handles YYYY-MM or YYYY-MM-DD)
                if end_date.lower() == "present" or end_date.lower() == "current":
                    end_date_obj = datetime.now()
                else:
                    # Try to parse date
                    date_parts = end_date.split("-")
                    if len(date_parts) >= 2:
                        end_date_obj = datetime(int(date_parts[0]), int(date_parts[1]), 1)
                    else:
                        end_date_obj = datetime(int(date_parts[0]), 1, 1)
                
                start_parts = start_date.split("-")
                if len(start_parts) >= 2:
                    start_date_obj = datetime(int(start_parts[0]), int(start_parts[1]), 1)
                else:
                    start_date_obj = datetime(int(start_parts[0]), 1, 1)
                
                # Calculate years difference
                years_diff = (end_date_obj - start_date_obj).days / 365.25
                total_years += max(0, years_diff)
            except (ValueError, TypeError, IndexError) as e:
                logger.debug(f"Could not parse date for role: {start_date} - {end_date}: {e}")
                continue
    
    return round(total_years, 1)


def adjust_jd_filename_for_experience(jd_filename: str, experience_years: float) -> str:
    """Adjust JD filename to use fresher version if experience is 0-2 years"""
    if not jd_filename:
        return jd_filename
    
    # If experience is 0-2 years, use fresher questions
    if 0 <= experience_years <= 2:
        # Check if filename already has a level suffix
        base_name = jd_filename.replace('.txt', '')
        
        # Remove existing level suffixes
        for suffix in ['_fresher', '_senior', '_junior', '_mid', '_mid_level']:
            if base_name.endswith(suffix):
                base_name = base_name[:-len(suffix)]
                break
        
        # Add fresher suffix if not already present
        if not base_name.endswith('_fresher'):
            adjusted_filename = f"{base_name}_fresher.txt"
            logger.info(f"[Interview] Experience is {experience_years} years (0-2), using fresher questions: {adjusted_filename}")
            return adjusted_filename
    
    return jd_filename


def get_random_interview_questions(resume_data: Optional[Dict[str, Any]] = None) -> List[str]:
    # Try dynamic source first
    logger.info("[Interview] ===== LOADING INTERVIEW QUESTIONS =====")
    jd_filename = _read_selected_jd_filename()
    
    # Calculate experience and adjust filename if needed
    if resume_data:
        experience_years = calculate_experience_years(resume_data)
        logger.info(f"[Interview] Candidate experience: {experience_years} years")
        
        # Adjust JD filename for fresher (0-2 years experience)
        jd_filename = adjust_jd_filename_for_experience(jd_filename, experience_years)
    else:
        logger.info("[Interview] No resume data available, using default JD filename")
    
    logger.info(f"[Interview] Selected JD filename: {jd_filename}")
    
    dynamic_questions = _load_questions_from_file(jd_filename)
    questions_pool: List[str]
    
    if dynamic_questions:
        logger.info(f"[Interview] ✅ Successfully loaded {len(dynamic_questions)} questions from {jd_filename}")
        questions_pool = dynamic_questions
    else:
        # fallback static pool
        logger.warning(f"[Interview] ⚠️ FALLING BACK TO STATIC GENAI QUESTIONS - Could not load from {jd_filename}")
        questions_pool = [
            "What is a prompt?",
            "How would you implement governance and approvals for prompts?",
            "What is a knowledge cutoff?",
            "What is a context window?",
            "Design evals for grounding and factuality.",
            "What does tokenization entail, and why is it critical for LLMs?",
            "Why is cross-entropy loss used in language modeling?",
            "How are gradients computed for embeddings in LLMs?",
            "How do LLMs differ from traditional statistical language models?",
            "What are sequence-to-sequence models, and where are they applied?",
        ]
        logger.info("[Interview] Using fallback static questions pool")
    
    # Return all questions for adaptive selection (not just 5)
    logger.info(f"[Interview] Loaded {len(questions_pool)} questions for adaptive selection")
    return questions_pool


def load_resume_data_for_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Load resume data for a session"""
    try:
        from app.db.database import SessionLocal
        from app.models.candidate import Resume
        from app.models.recording import Recording
        
        db = SessionLocal()
        try:
            # Try to find recording by session_id to get candidate_id (may fail if DB missing video_url column)
            recording = db.query(Recording).filter(
                Recording.session_id == session_id
            ).first()
            
            if recording and recording.candidate_id:
                # Get latest resume for candidate
                resume = db.query(Resume).filter(
                    Resume.candidate_id == recording.candidate_id
                ).order_by(Resume.created_at.desc()).first()
                
                if resume and resume.extracted_data:
                    logger.info(f"[Interview] Loaded resume data for session {session_id}")
                    return resume.extracted_data
        finally:
            db.close()
    except (ProgrammingError, OperationalError) as e:
        if "video_url" in str(e) or "does not exist" in str(e).lower():
            logger.debug("[Interview] Recording table missing video_url column, skipping resume load from recording")
        else:
            logger.warning(f"[Interview] DB error loading resume data: {e}")
    except Exception as e:
        logger.warning(f"[Interview] Could not load resume data: {e}")
    
    return None


def get_previous_interview_topics(user_id: Optional[int] = None) -> List[str]:
    """Get topics covered in previous interviews"""
    try:
        from app.db.database import SessionLocal
        from app.models.interview import InterviewResult
        
        if not user_id:
            return []
        
        db = SessionLocal()
        try:
            # Get previous interview results
            previous_interviews = db.query(InterviewResult).filter(
                InterviewResult.user_id == user_id
            ).order_by(InterviewResult.created_at.desc()).limit(5).all()
            
            topics = []
            for interview in previous_interviews:
                if interview.detailed_feedback:
                    # Extract topics from detailed feedback
                    for qa in interview.detailed_feedback:
                        if isinstance(qa, dict) and "question" in qa:
                            # Simple keyword extraction (can be enhanced)
                            question = qa["question"].lower()
                            # Extract key technical terms
                            tech_terms = ["javascript", "python", "react", "node", "database", 
                                        "api", "algorithm", "system", "design", "architecture"]
                            for term in tech_terms:
                                if term in question:
                                    topics.append(term)
            
            # Deduplicate
            unique_topics = list(set(topics))
            logger.info(f"[Interview] Found {len(unique_topics)} previous topics")
            return unique_topics
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"[Interview] Could not load previous topics: {e}")
    
    return []


class Assistant(Agent):
    def __init__(
        self, 
        session_questions: List[str], 
        role_description: str = "technical role",
        resume_data: Optional[Dict[str, Any]] = None,
        previous_topics: Optional[List[str]] = None,
        session_id: Optional[str] = None
    ) -> None:
        self.session_questions = session_questions
        self.session_id = session_id or "default"
        self.role_description = role_description
        
        # Initialize adaptive question manager
        self.question_manager = AdaptiveQuestionManager(
            session_id=self.session_id,
            questions_pool=session_questions,
            resume_data=resume_data,
            previous_topics=previous_topics
        )
        
        # Initialize answer assessor
        self.answer_assessor = AnswerAssessor()
        
        # Track conversation
        self.current_question_context: Optional[QuestionContext] = None
        self.conversation_turn = 0
        
        # Build instructions with adaptive system
        instructions = self._build_instructions()
        
        # Create function tools for adaptive questioning (async so LiveKit can await them)
        @function_tool()
        async def get_next_question() -> str:
            """Get the next question from the adaptive question system. Call this when you need to ask a new question."""
            next_q = self.question_manager.get_next_question()
            if next_q:
                self.current_question_context = next_q
                self.question_manager.record_question_asked(next_q)
                logger.info(f"[Adaptive] Next question: {next_q.question} (type: {next_q.question_type}, phase: {next_q.phase.value})")
                return next_q.question
            else:
                # Interview complete
                return "INTERVIEW_COMPLETE"
        
        @function_tool()
        async def assess_answer(answer: str) -> str:
            """Assess the candidate's answer quality. Call this after the candidate responds to understand their performance."""
            if not self.current_question_context:
                return "No current question to assess"
            # Truncate long answers to avoid JSON overflow when LLM sends huge payloads
            MAX_ANSWER_LEN = 2000
            if len(answer) > MAX_ANSWER_LEN:
                answer = answer[:MAX_ANSWER_LEN].rstrip() + "..."
            
            # Assess using LLM
            assessment_result = self.answer_assessor.assess_answer(
                question=self.current_question_context.question,
                answer=answer,
                context={"phase": self.question_manager.current_phase.value}
            )
            
            # Convert to AnswerAssessment (use .get() to avoid KeyError on malformed LLM output)
            from app.services.adaptive_question_manager import AnswerAssessment
            quality_str = (assessment_result.get("quality") or "fair").lower()
            try:
                quality = AnswerQuality(quality_str)
            except ValueError:
                quality = AnswerQuality.FAIR
            score = assessment_result.get("score", 50)
            if not isinstance(score, (int, float)):
                score = 50
            answer_assessment = AnswerAssessment(
                question=self.current_question_context.question,
                answer=answer,
                quality=quality,
                score=float(score),
                strengths=assessment_result.get("strengths") or [],
                weaknesses=assessment_result.get("weaknesses") or [],
                topics_covered=assessment_result.get("topics_covered") or [],
                needs_followup=assessment_result.get("needs_followup", False)
            )
            
            self.question_manager.answers_assessed.append(answer_assessment)
            self.question_manager._update_difficulty(score)
            if assessment_result.get("answer_felt_interesting"):
                self.question_manager.record_interesting_answer()
                logger.info("[Adaptive] Answer felt interesting — may ask 1-2 behavioral questions later")
            
            logger.info(f"[Adaptive] Answer assessed: {quality_str} (score: {score})")
            
            # Return summary for the LLM
            needs_followup = assessment_result.get("needs_followup", False)
            
            if quality == AnswerQuality.EXCELLENT:
                return f"Excellent answer (score: {score}). The candidate demonstrated strong understanding. Call get_next_question() for the next question."
            elif quality == AnswerQuality.GOOD:
                return f"Good answer (score: {score}). The candidate showed solid understanding. Call get_next_question() for the next question."
            elif quality == AnswerQuality.FAIR:
                return f"Fair answer (score: {score}). The candidate showed basic knowledge. Be brief, then call get_next_question() for the next question. Do not ask your own follow-up."
            else:
                return f"Poor answer (score: {score}). Be supportive briefly, then call get_next_question() for the next question."
        
        # Store tools as instance methods for access
        self._get_next_question = get_next_question
        self._assess_answer = assess_answer
        
        # Initialize Agent with instructions
        # Function tools should be automatically detected by LiveKit Agent framework
        super().__init__(
            instructions=instructions
        )
    
    def _build_instructions(self) -> str:
        """Build dynamic instructions based on interview state"""
        return f"""
You are a friendly, supportive AI technical interviewer conducting a first-round interview for a {self.role_description}. Your persona is warm, encouraging, and helpful — like a friendly human interviewer who wants to see candidates succeed.

🚨 CRITICAL RULE - READ THIS FIRST 🚨
YOU ARE AN INTERVIEWER. YOUR ONLY JOB IS TO ASK QUESTIONS AND LISTEN TO ANSWERS.
- YOU MUST NEVER ANSWER THE QUESTIONS YOU ASK
- YOU MUST NEVER PROVIDE SOLUTIONS OR EXPLANATIONS THAT REVEAL ANSWERS
- YOU MUST NEVER TEACH OR EXPLAIN CONCEPTS IN DETAIL
- YOU MUST NEVER GIVE HINTS OR SUGGESTIONS UNLESS THE USER EXPLICITLY ASKS FOR THEM
- IF THE CANDIDATE ASKS YOU A QUESTION, POLITELY REDIRECT BACK TO YOUR QUESTIONS
- YOU ONLY ASK QUESTIONS - YOU NEVER ANSWER THEM OR GIVE HINTS

IMPORTANT: You MUST ALWAYS respond in ENGLISH ONLY, regardless of the language the user speaks or writes in.

========================
ADAPTIVE INTERVIEW STRUCTURE
========================
This is a TECHNICAL interview tied to the JOB DESCRIPTION. Maximum 10 questions total. Every question MUST come from get_next_question()—do NOT invent or rephrase into generic/HR questions.

1. INTRODUCTION (First question only)
   - Use get_next_question() for the first question (brief intro + technical background).
   - Listen and acknowledge briefly, then move on.

2. RESUME DEEP DIVE (One technical question from their resume)
   - Use get_next_question() for this; ask exactly as returned.

3. TECHNICAL QUESTIONS (Core of the interview — from job description)
   - JD/role technical questions from get_next_question(). Ask the EXACT question returned.
   - Do NOT add your own follow-ups like "Could you elaborate?" or "Can you give an example?" as separate questions. If the candidate is brief, acknowledge and get the next question.

4. BEHAVIORAL (At most 1 question, only if the system returns one via get_next_question())
   - Use get_next_question(); if it returns a behavioral question, ask it. Otherwise continue with technical or end.

5. FOLLOW-UP (Only if get_next_question() returns a follow-up)
   - Do NOT invent follow-ups. Only ask what get_next_question() returns.

========================
HOW TO USE THE ADAPTIVE SYSTEM
========================
- MAX 10 QUESTIONS TOTAL. Every question MUST come from get_next_question(). Do NOT ask your own follow-ups (e.g. "Could you elaborate?", "Can you give an example?") as separate questions—those inflate the count and are not from the JD. If the candidate is brief, say a short acknowledgment and call get_next_question() for the next question.
- Ask the EXACT question returned by get_next_question(). Do NOT rephrase into generic HR questions. Questions are technical and tied to the job description—ask them as given.
1. To get a question: Call get_next_question()
   - Returns the next question to ask (ask verbatim). If it returns "INTERVIEW_COMPLETE", end the interview.
2. After the candidate answers: Call assess_answer(answer)
   - Then call get_next_question() to get the next question. Do NOT invent a follow-up; only ask what get_next_question() returns.
3. Flow:
   - get_next_question() → ask that question only → candidate responds → assess_answer(response) → get_next_question() → repeat. Stop when you get "INTERVIEW_COMPLETE".

========================
WAIT FOR COMPLETE ANSWER BEFORE NEXT QUESTION (CRITICAL)
========================
- Do NOT call assess_answer() or get_next_question() until the candidate has clearly FINISHED their answer, OR they explicitly ask to move on.
- A complete answer: the candidate has given a substantive response and stopped (natural pause / done speaking), or said they're done (e.g. "that's it", "that's all").
- If the candidate says only a few words or seems to pause mid-thought, wait or ask ONCE: "Would you like to add anything else?" or "Take your time." Do NOT move to the next question yet.
- Move to the next question ONLY when:
  (a) The candidate has given a full answer and clearly finished, OR
  (b) The candidate explicitly says they want to skip or move on, e.g.:
      - "I don't know", "idk", "not sure", "skip", "next question", "can you ask me something else", "ask me another thing", "move on", "pass", "I'll pass", "next one", "different question".
- When you hear one of these skip phrases, acknowledge briefly ("No problem, let's move on") then call assess_answer() with what they said, then get_next_question(). Do not insist they answer.
- Do NOT advance after every short user utterance (e.g. "um", "let me think")—wait for a complete answer or an explicit skip.

========================
CONVERSATION FLOW
========================
1. Start the interview immediately when the session begins
2. Greet warmly: "Hi! Thanks for joining us today. I'm [your name], and I'll be conducting your interview today. I'm excited to learn more about your background and experience."
3. Call get_next_question() to get the first question (introduction)
4. After each candidate response:
   - ONLY when the answer is complete or they said a skip phrase: Call assess_answer(candidate_response), then get_next_question() for the next question.
   - Give brief acknowledgments only ("That's great!", "I see", "Thanks"). Do NOT ask an extra follow-up question unless get_next_question() returns one.
   - If the answer was weak but complete, be supportive ("That's okay") and get the next question. Do not ask "Could you elaborate?" as a separate question—only use get_next_question().
   - If the answer was incomplete or they're still speaking, do NOT call assess_answer yet; wait or prompt once for more.
5. Use short transitions: "Great! Next question...", "Alright, here's another one..."
6. When get_next_question() returns "INTERVIEW_COMPLETE", conclude the interview (you will have asked at most 10 questions).

========================
CRITICAL RULES
========================
- NEVER provide answers or hints
- NEVER explain concepts in detail or give away solutions
- ALWAYS ask questions - never answer them
- Ask ONLY resume-based technical and JD/role technical questions from get_next_question(). Do NOT ask generic HR questions (e.g. "Where do you see yourself in 5 years?", "What's your greatest weakness?" unless it is the specific behavioral question returned by get_next_question()).
- Be warm and encouraging. Adjust tone if they struggle.
- ALWAYS use get_next_question() for every question—never invent questions or add "elaborate?" / "give an example?" as extra questions. Max 10 questions total.
- ALWAYS wait for a COMPLETE answer (or explicit skip phrase) before calling assess_answer(); then call get_next_question() for the next one. Never advance on partial or mid-sentence responses.

========================
INTERVIEW ENDING
========================
When get_next_question() returns "INTERVIEW_COMPLETE", conclude warmly:

"That concludes our interview. Thank you so much for taking the time to speak with me today. I really enjoyed our conversation. We'll review everything and get back to you with the next steps. Have a great day!"

After this message, end the conversation completely.
"""


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # each log entry will include these fields
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    session_id = ctx.room.name
    logger.info(f"[Interview] Starting session: {session_id}")

    # Load resume data first (needed for experience-based question selection)
    resume_data = load_resume_data_for_session(session_id)
    if resume_data:
        logger.info(f"[Interview] ✅ Loaded resume data for adaptive questioning")
        logger.info(f"[Interview] Resume data keys: {list(resume_data.keys()) if isinstance(resume_data, dict) else 'N/A'}")
    else:
        logger.info(f"[Interview] ⚠️ No resume data found, will skip resume questions")

    # Read JD file dynamically for each session (pass resume_data to adjust for experience)
    session_questions = get_random_interview_questions(resume_data=resume_data)
    logger.info(f"[Interview] Session {session_id}: Loaded {len(session_questions)} questions")

    # Get previous interview topics to avoid repetition
    previous_topics = []
    try:
        from app.db.database import SessionLocal
        from app.models.recording import Recording
        
        db = SessionLocal()
        try:
            recording = db.query(Recording).filter(
                Recording.session_id == session_id
            ).first()
            if recording:
                # Try to get user_id from candidate
                if hasattr(recording, 'candidate') and recording.candidate:
                    user_id = recording.candidate.user_id
                    previous_topics = get_previous_interview_topics(user_id)
                    if previous_topics:
                        logger.info(f"[Interview] ✅ Loaded {len(previous_topics)} previous topics to avoid")
                    else:
                        logger.info(f"[Interview] No previous interview topics found")
                else:
                    logger.info(f"[Interview] No candidate found for recording")
            else:
                logger.info(f"[Interview] No recording found for session {session_id}, will start fresh")
        finally:
            db.close()
    except (ProgrammingError, OperationalError) as e:
        if "video_url" in str(e) or "does not exist" in str(e).lower():
            logger.debug("[Interview] Recording table missing video_url column, skipping previous topics from recording")
        else:
            logger.warning(f"[Interview] DB error loading previous topics: {e}")
    except Exception as e:
        logger.warning(f"[Interview] Could not load previous topics: {e}", exc_info=True)

    # Determine role description from JD filename
    jd_filename = _read_selected_jd_filename()
    role_description = "technical role"  # default
    if jd_filename:
        # Extract role from filename (e.g., "backend_developer.txt" -> "Backend Developer")
        role_name = jd_filename.replace('.txt', '').replace('_', ' ').title()
        role_description = role_name
        logger.info(f"[Interview] Role description: {role_description}")

    # Set up a voice AI pipeline using OpenAI and the LiveKit turn detector
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            model="gpt-4o-realtime-preview",
            api_key=os.getenv("OPENAI_API_KEY"),
            turn_detection=TurnDetection(
                type="server_vad",
                threshold=0.8,
                prefix_padding_ms=300,
                silence_duration_ms=1000,
                create_response=True,
                interrupt_response=True,
            ),
        ),
        # Note: The original TTS provider (Cartesia) is not included here as
        # openai.realtime.RealtimeModel handles both LLM and TTS.
        # If you wish to use a separate TTS, you can add it here.
    )

    # log metrics as they are emitted, and total usage after session is over
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    # Capture user transcriptions for logging and debugging
    # Note: LiveKit agents framework handles transcriptions automatically
    # The transcriptions are sent to the frontend via LiveKit's transcription events
    # We just log for debugging purposes
    try:
        # Try to set up transcription event handlers if available
        # The exact event names may vary based on LiveKit agents version
        @session.on("user_speech_committed")
        def _on_user_speech(ev):
            """Log user speech transcriptions"""
            if hasattr(ev, 'text') and ev.text:
                logger.info(f"[Interview] User said: {ev.text}")
            elif hasattr(ev, 'transcript') and ev.transcript:
                logger.info(f"[Interview] User transcript: {ev.transcript}")
            else:
                logger.info(f"[Interview] User speech event received: {type(ev)}")
    except Exception as e:
        # Event might not exist in this version, that's okay
        logger.debug(f"[Interview] Could not set up user_speech_committed handler: {e}")

    # Log that transcription is enabled
    logger.info("[Interview] Transcription enabled - user speech will be transcribed and sent to frontend via LiveKit")

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    # shutdown callbacks are triggered when the session is over
    ctx.add_shutdown_callback(log_usage)

    # Create Assistant with adaptive question manager
    assistant = Assistant(
        session_questions, 
        role_description,
        resume_data=resume_data,
        previous_topics=previous_topics,
        session_id=session_id
    )
    
    logger.info(f"[Interview] ✅ Assistant initialized with adaptive question manager")
    logger.info(f"[Interview] Interview state: {assistant.question_manager.get_interview_state()}")

    await session.start(
        agent=assistant,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
        room_output_options=RoomOutputOptions(transcription_enabled=True),
    )

    # join the room when agent is ready
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm,
        initialize_process_timeout=60.0,
    ))
