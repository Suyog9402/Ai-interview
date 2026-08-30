from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import random
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

# Hard cap: real interviews are short. Only ask up to 10 questions total.
MAX_TOTAL_QUESTIONS = 10


class InterviewPhase(Enum):
    """Interview phases"""
    INTRODUCTION = "introduction"
    RESUME_DEEP_DIVE = "resume_deep_dive"  # Technical questions based on resume (skills, projects)
    TECHNICAL_QUESTIONS = "technical_questions"  # JD/role technical pool
    BEHAVIORAL = "behavioral"  # Only 1-2 if answer was interesting
    FOLLOW_UP = "follow_up"
    CLOSING = "closing"


class AnswerQuality(Enum):
    """Answer quality assessment"""
    EXCELLENT = "excellent"  # 80-100
    GOOD = "good"  # 60-79
    FAIR = "fair"  # 40-59
    POOR = "poor"  # 0-39


@dataclass
class QuestionContext:
    """Context for a question"""
    question: str
    question_type: str  # "file", "resume", "followup", "introduction"
    phase: InterviewPhase
    difficulty: str  # "easy", "medium", "hard"
    source: Optional[str] = None  # For resume questions, what part of resume
    asked_at: Optional[datetime] = None


@dataclass
class AnswerAssessment:
    """Assessment of an answer"""
    question: str
    answer: str
    quality: AnswerQuality
    score: float  # 0-100
    strengths: List[str]
    weaknesses: List[str]
    topics_covered: List[str]
    needs_followup: bool


class AdaptiveQuestionManager:
    """Manages adaptive question selection and generation"""
    
    def __init__(
        self,
        session_id: str,
        questions_pool: List[str],
        resume_data: Optional[Dict[str, Any]] = None,
        jd_requirements: Optional[Dict[str, Any]] = None,
        previous_topics: Optional[List[str]] = None
    ):
        self.session_id = session_id
        self.questions_pool = questions_pool
        self.resume_data = resume_data or {}
        self.jd_requirements = jd_requirements or {}
        self.previous_topics = set(previous_topics or [])
        
        # Calculate experience to determine if fresher
        self.experience_years = self._calculate_experience()
        self.is_fresher = 0 <= self.experience_years <= 2
        
        # Interview state
        self.current_phase = InterviewPhase.INTRODUCTION
        self.questions_asked: List[QuestionContext] = []
        self.answers_assessed: List[AnswerAssessment] = []
        self.used_questions = set()
        self.used_resume_questions = set()
        self.weak_areas: List[str] = []
        self.strong_areas: List[str] = []
        
        # Question counts
        self.intro_asked = False
        self.resume_questions_asked = 0
        self.technical_questions_asked = 0
        self.behavioral_questions_asked = 0
        self.followup_questions_asked = 0
        self.interesting_answers_count = 0  # Track answers that felt "interesting" for optional behavioral

        # Target distribution: strict 10-question interview. JD technical = core; minimal resume/behavioral/follow-up.
        # 1 intro + 1 resume + 6 JD technical + 0-1 behavioral + 0-1 follow-up = max 10
        self.target_resume_questions = 1
        self.target_technical_questions = 6  # Core technical from job description file
        self.max_behavioral_questions = 1  # Only if answer was clearly interesting
        self.target_followups = 1  # At most one follow-up from system
        
        # Difficulty tracking - start with "easy" for freshers (0-2 years)
        if self.is_fresher:
            self.current_difficulty = "easy"
            logger.info(f"[Adaptive] Candidate is fresher ({self.experience_years} years), starting with easy difficulty")
        else:
            self.current_difficulty = "medium"
        self.difficulty_history: List[Tuple[str, float]] = []  # (difficulty, score)
    
    def _calculate_experience(self) -> float:
        """Calculate experience years from resume data"""
        if not self.resume_data:
            return 0.0
        
        # First try explicit experience_years
        if self.resume_data.get("experience_years"):
            try:
                return float(self.resume_data["experience_years"])
            except (ValueError, TypeError):
                pass
        
        # Calculate from roles/experiences
        total_years = 0.0
        experiences = self.resume_data.get("experiences", [])
        roles = self.resume_data.get("roles", [])
        
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
                except (ValueError, TypeError, IndexError):
                    continue
        
        return round(total_years, 1)
    
    def get_next_question(self) -> Optional[QuestionContext]:
        """Get the next question based on current phase and state.
        Focus: resume-based technical + JD technical; only 0-1 behavioral if answers were interesting.
        Hard cap: MAX_TOTAL_QUESTIONS (10) total.
        """
        # Hard cap: never more than MAX_TOTAL_QUESTIONS (intro + resume + technical + behavioral + follow-up)
        if len(self.questions_asked) >= MAX_TOTAL_QUESTIONS:
            logger.info(f"[Adaptive] Reached max {MAX_TOTAL_QUESTIONS} questions, ending interview")
            return None

        # Phase 1: Introduction (always first, brief)
        if not self.intro_asked:
            self.intro_asked = True
            return QuestionContext(
                question="In one or two sentences, introduce yourself and the tech stack you work with.",
                question_type="introduction",
                phase=InterviewPhase.INTRODUCTION,
                difficulty="easy",
                asked_at=datetime.now()
            )

        # Phase 2: Resume deep dive — technical questions from resume (skills, projects, tech stack)
        if (self.resume_questions_asked < self.target_resume_questions and
            self.current_phase in [InterviewPhase.INTRODUCTION, InterviewPhase.RESUME_DEEP_DIVE]):
            self.current_phase = InterviewPhase.RESUME_DEEP_DIVE
            question = self._generate_resume_question()
            if question:
                self.resume_questions_asked += 1
                return question

        # Phase 3: JD/role technical questions (majority of interview)
        if (self.technical_questions_asked < self.target_technical_questions and
            (self.current_phase == InterviewPhase.RESUME_DEEP_DIVE or
             self.current_phase == InterviewPhase.TECHNICAL_QUESTIONS)):
            self.current_phase = InterviewPhase.TECHNICAL_QUESTIONS
            question = self._get_technical_question()
            if question:
                self.technical_questions_asked += 1
                return question

        # Phase 4: Behavioral — only 1-2 questions, and only if we had interesting answers
        if (self.interesting_answers_count > 0 and
            self.behavioral_questions_asked < self.max_behavioral_questions and
            (self.current_phase == InterviewPhase.TECHNICAL_QUESTIONS or
             self.current_phase == InterviewPhase.BEHAVIORAL)):
            self.current_phase = InterviewPhase.BEHAVIORAL
            question = self._generate_behavioral_question()
            if question:
                self.behavioral_questions_asked += 1
                return question

        # Phase 5: At most one follow-up (technical depth or weakness probe)
        if (self.followup_questions_asked < self.target_followups and self.technical_questions_asked >= 2):
            followup = self._generate_followup_question()
            if followup:
                self.followup_questions_asked += 1
                return followup

        total_asked = (self.resume_questions_asked + self.technical_questions_asked +
                      self.behavioral_questions_asked + self.followup_questions_asked)
        if total_asked >= MAX_TOTAL_QUESTIONS - 1:  # -1 because intro is not in total_asked
            self.current_phase = InterviewPhase.CLOSING
            return None

        # Fallback: more technical from pool
        question = self._get_technical_question()
        if question:
            self.technical_questions_asked += 1
            return question
        return None
    
    def _generate_resume_question(self) -> Optional[QuestionContext]:
        """Generate ONE short technical question tied to resume (skills/project). Kept brief so we move quickly to JD technical questions."""
        if not self.resume_data:
            return None

        skills = self.resume_data.get("skills", [])
        projects = self.resume_data.get("projects", [])
        resume_question_templates = []

        if skills:
            top_skills = skills[:3]
            skill_str = ", ".join(top_skills)
            resume_question_templates.append(
                f"You listed {skill_str}. In one project using these, what did you build and what was one technical decision you made?"
            )
        if projects:
            p = projects[0]
            name = p.get("name") or p.get("title") or "a project"
            resume_question_templates.append(
                f"For your project {name}, what was your role and one technical challenge you solved?"
            )
        if not resume_question_templates:
            resume_question_templates.append(
                "What's one technically substantial thing you built recently—what and with what stack?"
            )

        available = [q for q in resume_question_templates if q not in self.used_resume_questions]
        if not available:
            return None

        selected = random.choice(available)
        self.used_resume_questions.add(selected)
        return QuestionContext(
            question=selected,
            question_type="resume",
            phase=InterviewPhase.RESUME_DEEP_DIVE,
            difficulty="medium",
            source="resume_data",
            asked_at=datetime.now()
        )

    def _generate_behavioral_question(self) -> Optional[QuestionContext]:
        """Generate at most 1-2 behavioral questions; only used when answer_felt_interesting."""
        behavioral_pool = [
            "That was a strong example. Tell me about a time you had to convince your team or stakeholders to adopt a technical approach—what was the situation and outcome?",
            "You mentioned a concrete experience there. Can you describe a situation where a project or deadline was at risk and how you handled it?",
            "Following on that—describe a time you had to learn a new technology or concept quickly to ship something. How did you approach it?",
        ]
        available = [q for q in behavioral_pool if q not in self.used_resume_questions]
        if not available:
            available = behavioral_pool
        selected = random.choice(available)
        self.used_resume_questions.add(selected)
        return QuestionContext(
            question=selected,
            question_type="behavioral",
            phase=InterviewPhase.BEHAVIORAL,
            difficulty="medium",
            source="behavioral",
            asked_at=datetime.now()
        )

    def record_interesting_answer(self):
        """Call when assess_answer indicates the candidate's answer was particularly interesting (e.g. rich example)."""
        self.interesting_answers_count = min(self.interesting_answers_count + 1, 3)
    
    def _get_technical_question(self) -> Optional[QuestionContext]:
        """Get a technical question from the pool, avoiding previous topics"""
        available = [q for q in self.questions_pool 
                    if q not in self.used_questions]
        
        if not available:
            # If we've used all questions, allow reuse but prefer unused
            available = self.questions_pool
        
        # Filter out questions about topics we've already covered
        filtered = self._filter_by_previous_topics(available)
        if not filtered:
            filtered = available
        
        if not filtered:
            return None
        
        # Adjust difficulty based on performance
        selected = random.choice(filtered)
        self.used_questions.add(selected)
        
        return QuestionContext(
            question=selected,
            question_type="file",
            phase=InterviewPhase.TECHNICAL_QUESTIONS,
            difficulty=self.current_difficulty,
            source="question_file",
            asked_at=datetime.now()
        )
    
    def _filter_by_previous_topics(self, questions: List[str]) -> List[str]:
        """Filter questions to avoid topics covered in previous interviews"""
        if not self.previous_topics:
            return questions
        
        filtered = []
        for q in questions:
            # Simple keyword matching - can be enhanced with NLP
            q_lower = q.lower()
            has_previous_topic = any(topic.lower() in q_lower 
                                   for topic in self.previous_topics)
            if not has_previous_topic:
                filtered.append(q)
        
        return filtered if filtered else questions
    
    def _generate_followup_question(self) -> Optional[QuestionContext]:
        """Generate a follow-up question based on recent answers"""
        if not self.answers_assessed:
            return None
        
        # Find the most recent answer that needs follow-up
        for assessment in reversed(self.answers_assessed):
            if assessment.needs_followup and assessment.quality in [AnswerQuality.FAIR, AnswerQuality.POOR]:
                # Generate follow-up to probe weak area
                followup = self._create_followup_for_weakness(assessment)
                if followup:
                    return followup
        
        # If no weak areas, generate follow-up for good answers to go deeper
        for assessment in reversed(self.answers_assessed):
            if assessment.quality in [AnswerQuality.EXCELLENT, AnswerQuality.GOOD]:
                followup = self._create_followup_for_depth(assessment)
                if followup:
                    return followup
        
        return None
    
    def _create_followup_for_weakness(self, assessment: AnswerAssessment) -> Optional[QuestionContext]:
        """Create a follow-up question to probe a weak area. Use the question topic, not raw weakness text, so the follow-up is coherent."""
        weaknesses = assessment.weaknesses
        if not weaknesses:
            return None
        
        weakness = (weaknesses[0] or "").strip().lower()
        # Meta/phrase weaknesses that would make incoherent follow-ups (e.g. "could be more detailed", "answer too brief")
        generic_weak = any(
            phrase in weakness
            for phrase in ("could be more detailed", "more detail", "too brief", "too short", "elaborate", "expand")
        )
        if generic_weak or len(weakness.split()) > 6:
            # Use topic-agnostic follow-up so we don't say "elaborate on could be more detailed"
            followup_questions = [
                "Could you elaborate on that with a bit more detail or a concrete example?",
                "Can you give a specific example that illustrates what you mean?",
                "What would you do differently or add if you had more time to explain?",
            ]
        else:
            # Weakness is a concrete topic (e.g. "error handling"); use it in the follow-up
            followup_questions = [
                f"Can you elaborate on {weakness}?",
                f"Could you give an example related to {weakness}?",
            ]
        selected = random.choice(followup_questions)
        
        return QuestionContext(
            question=selected,
            question_type="followup",
            phase=InterviewPhase.FOLLOW_UP,
            difficulty=self.current_difficulty,
            source="weakness_probe",
            asked_at=datetime.now()
        )
    
    def _create_followup_for_depth(self, assessment: AnswerAssessment) -> Optional[QuestionContext]:
        """Create a follow-up question to go deeper into a good answer"""
        followup_templates = [
            "That's interesting. Can you walk me through a specific example where you applied this?",
            "Great! How would you handle an edge case in this scenario?",
            "Can you elaborate on the implementation details?",
            "What would you do differently if you had to approach this problem again?",
            "Can you give me a real-world scenario where this would be particularly important?",
        ]
        
        selected = random.choice(followup_templates)
        
        return QuestionContext(
            question=selected,
            question_type="followup",
            phase=InterviewPhase.FOLLOW_UP,
            difficulty=self.current_difficulty,
            source="depth_probe",
            asked_at=datetime.now()
        )
    
    def assess_answer(self, question: str, answer: str) -> AnswerAssessment:
        """Assess the quality of an answer (simplified - can use LLM for better assessment)"""
        # This is a simplified version - in production, use LLM to assess
        answer_lower = answer.lower()
        
        # Simple heuristics (replace with LLM-based assessment)
        quality_indicators = {
            "excellent": ["implemented", "designed", "architected", "optimized", "scaled", "built", "created"],
            "good": ["worked with", "familiar", "experience", "used", "applied"],
            "fair": ["heard of", "know about", "read about", "understand"],
            "poor": ["don't know", "not sure", "unfamiliar", "haven't", "no experience"]
        }
        
        score = 50  # Default
        quality = AnswerQuality.FAIR
        
        for q_level, indicators in quality_indicators.items():
            if any(ind in answer_lower for ind in indicators):
                if q_level == "excellent":
                    score = random.uniform(80, 100)
                    quality = AnswerQuality.EXCELLENT
                elif q_level == "good":
                    score = random.uniform(60, 79)
                    quality = AnswerQuality.GOOD
                elif q_level == "fair":
                    score = random.uniform(40, 59)
                    quality = AnswerQuality.FAIR
                else:
                    score = random.uniform(0, 39)
                    quality = AnswerQuality.POOR
                break
        
        # Determine if follow-up is needed
        needs_followup = quality in [AnswerQuality.FAIR, AnswerQuality.POOR] or score < 70
        
        assessment = AnswerAssessment(
            question=question,
            answer=answer,
            quality=quality,
            score=score,
            strengths=[],
            weaknesses=[],
            topics_covered=[],
            needs_followup=needs_followup
        )
        
        self.answers_assessed.append(assessment)
        self._update_difficulty(score)
        
        return assessment
    
    def _update_difficulty(self, score: float):
        """Adjust difficulty based on answer quality"""
        self.difficulty_history.append((self.current_difficulty, score))
        
        # Calculate average score for current difficulty
        recent_scores = [s for d, s in self.difficulty_history[-3:] 
                        if d == self.current_difficulty]
        
        if recent_scores:
            avg_score = sum(recent_scores) / len(recent_scores)
            
            if avg_score >= 80 and self.current_difficulty != "hard":
                self.current_difficulty = "hard"
                logger.info(f"[Adaptive] Increasing difficulty to hard (avg score: {avg_score})")
            elif avg_score < 60 and self.current_difficulty != "easy":
                self.current_difficulty = "easy"
                logger.info(f"[Adaptive] Decreasing difficulty to easy (avg score: {avg_score})")
    
    def record_question_asked(self, question_context: QuestionContext):
        """Record that a question was asked"""
        self.questions_asked.append(question_context)
    
    def get_interview_state(self) -> Dict[str, Any]:
        """Get current interview state"""
        return {
            "phase": self.current_phase.value,
            "questions_asked": len(self.questions_asked),
            "resume_questions": self.resume_questions_asked,
            "technical_questions": self.technical_questions_asked,
            "behavioral_questions": self.behavioral_questions_asked,
            "followup_questions": self.followup_questions_asked,
            "current_difficulty": self.current_difficulty,
            "weak_areas": self.weak_areas,
            "strong_areas": self.strong_areas,
        }

