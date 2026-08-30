import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.qa import QAPair
from app.models.interview import InterviewResult
from app.schemas.interview import InterviewResultResponse, ConversationMessage
from app.services.rag_service import rag_service
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import json

# Pydantic models for structured output
class QAPairExtraction(BaseModel):
    """A single question-answer pair extracted from the interview transcript."""
    question: str = Field(description="The actual question asked by the interviewer. Must be ONLY the question text, without any hints, responses, or transition phrases like 'That's okay', 'No worries', 'Let's think about it', etc.")
    answer: str = Field(description="The candidate's answer to this question. Use 'No answer provided' if the candidate didn't answer.")
    question_number: int = Field(description="The sequential number of this question (1, 2, 3, ...)")

class QAPairsExtraction(BaseModel):
    """Extracted question-answer pairs from an interview transcript."""
    qa_pairs: List[QAPairExtraction] = Field(description="List of ALL question-answer pairs from the transcript, in order (number sequentially from 1)")

class InterviewService:
    def __init__(self):
        # Initialize OpenAI for evaluation
        self.model = None
        if rag_service.openai_configured:
            try:
                self.model = ChatOpenAI(
                    model="gpt-4o",
                    api_key=os.getenv("OPENAI_API_KEY"),
                    temperature=0.3  # Lower temperature for more consistent, strict evaluation
                )
            except Exception as e:
                print(f"Error initializing interview service model: {e}")
        
        # Evaluation prompts
        self.evaluation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical interviewer. Evaluate each answer based on how correctly and completely it addresses the question.

IMPORTANT: This interview has N question-answer pairs. Evaluate EVERY Q&A pair in the order provided. The number of items in detailed_feedback MUST equal the number of Q&A pairs.

SCORING PRINCIPLE:
Score each answer based on:
- Is the answer CORRECT? (Technical accuracy)
- Does it COMPLETELY address the question? (Completeness)
- Is it well-explained? (Clarity)
- For resume/project questions: did they give concrete examples and technical detail?
- For behavioral questions (if any): did they give a specific situation and outcome?

SCORE RANGES:
- 90-100: Completely correct, comprehensive, well-explained
- 80-89: Correct with minor gaps or could be more detailed
- 70-79: Mostly correct but missing some important points
- 60-69: Partially correct, some understanding shown
- 50-59: Vague or partially incorrect
- 40-49: Mostly incorrect or very vague
- 30-39: Incorrect with minimal correct information
- 20-29: Very incorrect or doesn't address the question
- 10-19: Almost no correct information
- 0-9: No answer, "I don't know", or completely wrong

INTERVIEW DATA:
{qa_pairs}

Full Conversation Context:
{conversation}

For EACH question, evaluate:
1. Does the answer correctly address what was asked?
2. Is the technical content accurate (or for behavioral, is the example concrete)?
3. Is it complete and well-explained?

Provide evaluation in the following JSON format:
{{
    "overall_score": <total_score_out_of_100>,
    "overall_analysis": "<comprehensive analysis covering ALL questions: technical performance, resume/project answers, and any behavioral answers. Summarize strengths and gaps across the full interview.>",
    "detailed_feedback": [
        (ONE object per Q&A pair, in the same order as the pairs. Each object:)
        {{
            "question": "<exact question text>",
            "answer": "<exact answer text>",
            "score": <score_out_of_100>,
            "feedback": "<detailed feedback for this question>",
            "strengths": ["<strength1>", "<strength2>"],
            "weaknesses": ["<weakness1>", "<weakness2>"]
        }}
    ],
    "strengths": ["<overall_strength1>", "<overall_strength2>"],
    "areas_for_improvement": ["<area1>", "<area2>"],
    "recommendations": ["<recommendation1>", "<recommendation2>"]
}}

IMPORTANT:
- detailed_feedback must have exactly as many elements as there are Q&A pairs.
- Use the EXACT question and answer text from the Q&A pairs.
- Score each answer independently. Be strict: "I don't know" or vague answers score 0-9.
- overall_analysis must cover the entire interview (all questions).

Return only valid JSON."""),
            ("user", "Evaluate this technical interview session. Score every question-answer pair. Provide detailed_feedback for each pair and a comprehensive overall_analysis. Return only valid JSON.")
        ])
        
        # Q&A extraction prompt with structured output
        self.qa_extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at analyzing interview transcripts and extracting question-answer pairs.

CRITICAL RULES FOR QUESTION EXTRACTION:
1. Extract ONLY the actual question text - remove ALL transition phrases, hints, responses, and acknowledgments
2. DO NOT include phrases like:
   - "That's okay, no worries"
   - "That's a good start!"
   - "Let's think about it together"
   - "Of course, no worries"
   - "Let's move on"
   - "Great! Let's move on to the next question"
   - Any acknowledgments or hints before or after the question
3. Extract ONLY the question itself, for example:
   - If the transcript says: "That's okay, no worries. Can you talk about how you would choose a vector database?"
   - Extract ONLY: "Can you talk about how you would choose a vector database?"
4. If a message contains both a hint/response AND a question, extract ONLY the question part
5. Questions are typically sentences ending with "?" or sentences starting with question words (what, how, why, when, where, who, can you, tell me, explain, describe)

CRITICAL RULES FOR ANSWER EXTRACTION:
1. Extract the candidate's actual response to each question
2. If the candidate said "I don't know" or didn't answer, use "No answer provided"
3. If the candidate's answer is in a different message after the question, extract that answer
4. Do NOT include the interviewer's responses or hints in the answer

INTERVIEW STRUCTURE:
- The interview may have several to many questions (typically 8-12).
- Number each question-answer pair sequentially (1, 2, 3, ...).
- Extract ALL question-answer pairs in the order they appear.
- Match each question with the candidate's corresponding answer.
- Include intro, resume-based, technical, behavioral, and follow-up questions.

TRANSCRIPT:
{transcript}

Extract ALL question-answer pairs from the transcript. Ensure each question contains ONLY the question text (no hints, acknowledgments, or transition phrases)."""),
            ("user", "Extract all question-answer pairs from this interview transcript. Return the actual questions and the candidate's answers in order. Number them sequentially.")
        ])

    async def extract_qa_pairs_from_transcript(
        self,
        conversation: List[ConversationMessage]
    ) -> tuple[List[str], List[str]]:
        """
        Extract question-answer pairs from the conversation transcript using structured output.
        Returns (questions, answers) lists.
        """
        if not self.model:
            print("⚠️ Warning: Model not available for Q&A extraction, using fallback")
            return [], []
        
        try:
            # Format conversation transcript
            transcript_text = "\n".join([
                f"{msg.role.upper()}: {msg.content}" 
                for msg in conversation
            ])
            
            print("🔍 Extracting Q&A pairs from transcript using structured output...")
            
            # Use structured output to extract Q&A pairs
            chain = self.qa_extraction_prompt | self.model.with_structured_output(QAPairsExtraction)
            
            result = chain.invoke({
                "transcript": transcript_text
            })
            
            # Extract questions and answers in order
            extracted_pairs = sorted(result.qa_pairs, key=lambda x: x.question_number)
            questions = [pair.question for pair in extracted_pairs]
            answers = [pair.answer for pair in extracted_pairs]
            
            print(f"✅ Extracted {len(questions)} Q&A pairs from transcript:")
            for i, (q, a) in enumerate(zip(questions, answers), 1):
                print(f"  Q{i}: {q[:100]}{'...' if len(q) > 100 else ''}")
                print(f"  A{i}: {a[:100]}{'...' if len(a) > 100 else ''}")
            
            # Require at least one pair; no artificial cap
            if len(questions) == 0:
                print("⚠️ Warning: No Q&A pairs extracted.")
            else:
                print(f"✅ Will evaluate all {len(questions)} Q&A pairs.")
            return questions, answers
            
        except Exception as e:
            print(f"❌ Error extracting Q&A pairs from transcript: {e}")
            import traceback
            traceback.print_exc()
            return [], []

    async def evaluate_session(
        self,
        user_id: int,
        session_id: str,
        conversation: List[ConversationMessage],
        questions: List[str],
        answers: List[str],
        db: Session
    ) -> InterviewResultResponse:
        """
        Evaluate a complete interview session (variable number of questions).
        If questions/answers are not provided or are incorrect, extract them from the transcript.
        """
        # Extract Q&A pairs from transcript using structured output if needed
        # Always extract from transcript to ensure accuracy
        print("📝 Extracting Q&A pairs from transcript using structured output...")
        extracted_questions, extracted_answers = await self.extract_qa_pairs_from_transcript(conversation)
        
        # Use extracted Q&A pairs if we got any
        if extracted_questions and extracted_answers and len(extracted_questions) >= 1:
            questions = extracted_questions
            answers = extracted_answers
            print(f"✅ Using {len(questions)} Q&A pairs extracted from transcript")
        else:
            print("⚠️ Using provided Q&A pairs (extraction failed or incomplete)")
        # Validate and ensure we have matching questions and answers
        if len(questions) != len(answers):
            print(f"⚠️ Warning: Mismatch between questions ({len(questions)}) and answers ({len(answers)})")
            # Pad with empty strings to match the longer list
            max_length = max(len(questions), len(answers))
            while len(questions) < max_length:
                questions.append("No question provided")
            while len(answers) < max_length:
                answers.append("No answer provided")
        
        # Log each Q&A pair for verification
        print(f"📝 Evaluating {len(questions)} Q&A pairs:")
        for i, (q, a) in enumerate(zip(questions, answers), 1):
            print(f"  Q{i}: {q[:100]}{'...' if len(q) > 100 else ''}")
            print(f"  A{i}: {a[:100]}{'...' if len(a) > 100 else ''}")
            print()
        
        try:
            # Format conversation for evaluation
            conversation_text = "\n".join([
                f"{msg.role.upper()}: {msg.content}" 
                for msg in conversation
            ])
            
            # Prepare explicitly paired Q&A format for the LLM
            qa_pairs_text = "\n\n".join([
                f"=== QUESTION {i+1} ===\n{q}\n\n=== ANSWER {i+1} ===\n{a}"
                for i, (q, a) in enumerate(zip(questions, answers))
            ])
            
            # Get AI evaluation
            if self.model:
                chain = self.evaluation_prompt | self.model
                response = chain.invoke({
                    "qa_pairs": qa_pairs_text,  # Explicitly paired format
                    "conversation": conversation_text
                })
                
                # Parse JSON response
                try:
                    content = response.content.strip()
                    if content.startswith('```json'):
                        content = content[7:]
                    if content.startswith('```'):
                        content = content[3:]
                    if content.endswith('```'):
                        content = content[:-3]
                    content = content.strip()
                    
                    evaluation = json.loads(content)
                    
                    # Validate that we have feedback for all Q&A pairs
                    detailed_feedback = evaluation.get("detailed_feedback", [])
                    if len(detailed_feedback) != len(questions):
                        print(f"⚠️ Warning: LLM returned {len(detailed_feedback)} feedback items, expected {len(questions)}")
                    
                    # Helper function to clean question text (remove transition phrases)
                    def clean_question(question_text: str) -> str:
                        """Remove transition phrases and extract only the actual question"""
                        import re
                        if not question_text:
                            return question_text
                        
                        cleaned = question_text
                        # Remove common transition phrases
                        transition_patterns = [
                            r"^that'?s?\s+(absolutely\s+)?fine,?\s*no\s+problem\s+(at\s+all)?[.!]?\s*",
                            r"^that'?s?\s+okay,?\s*no\s+worries?[.!]?\s*",
                            r"^great!?\s*",
                            r"^alright,?\s*",
                            r"^perfect[.!]?\s*",
                            r"^thanks?\s+(for\s+that)?[.!]?\s*",
                            r"^okay,?\s*",
                            r"^sure,?\s*no\s+problem[.!]?\s*",
                            r"^let'?s?\s+move\s+on\s+(to\s+the\s+next\s+question)?[.!]?\s*",
                            r"^moving\s+(forward|on)[,.]?\s*",
                            r"^here'?s?\s+(another\s+one\s+for\s+you|the\s+next\s+question)[.!]?\s*",
                            r"^now,?\s*",
                            r"^so,?\s*",
                            r"^well,?\s*",
                            r"^i\s+see[.!]?\s*",
                            r"^got\s+it[.!]?\s*",
                            r"^makes\s+sense[.!]?\s*",
                            r"^interesting[.!]?\s*",
                            r"^good\s+point[.!]?\s*",
                            r"^that'?s?\s+great[.!]?\s*",
                            r"^i\s+see\s+what\s+you\s+mean[.!]?\s*",
                            r"^okay,?\s+that\s+makes\s+sense[.!]?\s*",
                            r"^interesting\s+approach[.!]?\s*",
                        ]
                        
                        for pattern in transition_patterns:
                            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
                        
                        # Remove redundant phrases
                        cleaned = re.sub(r"^(let\s+me\s+ask\s+you\s+about|i'?d?\s+like\s+to\s+know|can\s+you\s+tell\s+me)\s*", '', cleaned, flags=re.IGNORECASE)
                        
                        # Clean up multiple spaces
                        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                        
                        # If cleaned is too short, return original
                        if len(cleaned) < 10:
                            return question_text
                        
                        return cleaned
                    
                    # Create detailed feedback for each Q&A, ensuring correct pairing
                    validated_feedback = []
                    for i, (q, a) in enumerate(zip(questions, answers)):
                        # Clean the question to remove transition phrases
                        cleaned_q = clean_question(q)
                        
                        if i < len(detailed_feedback):
                            feedback_item = detailed_feedback[i]
                            # Use cleaned question and exact answer
                            feedback_item["question"] = cleaned_q
                            feedback_item["answer"] = a
                        else:
                            # Fallback if detailed feedback is missing
                            feedback_item = {
                                "question": q,
                                "answer": a,
                                "score": evaluation.get("overall_score", 0) // len(questions) if len(questions) > 0 else 0,
                                "feedback": "Evaluation completed",
                                "strengths": [],
                                "weaknesses": []
                            }
                        validated_feedback.append(feedback_item)
                    
                    # Log scores for verification
                    print("📊 Evaluation Scores:")
                    for i, fb in enumerate(validated_feedback, 1):
                        print(f"  Q{i}: {fb.get('score', 0)}/100 - {fb.get('feedback', '')[:80]}...")
                    
                    # Calculate scores
                    total_score = evaluation.get("overall_score", 0)
                    max_score = 100
                    percentage = (total_score / max_score) * 100
                    
                    # Create result
                    result = InterviewResultResponse(
                        session_id=session_id,
                        user_id=user_id,
                        total_score=total_score,
                        max_score=max_score,
                        percentage=percentage,
                        questions_evaluated=len(questions),
                        overall_analysis=evaluation.get("overall_analysis", "Evaluation completed"),
                        detailed_feedback=validated_feedback,
                        strengths=evaluation.get("strengths", []),
                        areas_for_improvement=evaluation.get("areas_for_improvement", []),
                        recommendations=evaluation.get("recommendations", []),
                        transcript=[{"role": msg.role, "content": msg.content, "timestamp": msg.timestamp} for msg in conversation],
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    
                    # Store in database
                    storage_success = await self._store_evaluation_result(result, db)
                    if not storage_success:
                        print("⚠️ Warning: Failed to store evaluation result in database")
                    
                    # Store individual Q&A pairs
                    qa_success = await self._store_qa_pairs(session_id, user_id, questions, answers, validated_feedback, db)
                    if not qa_success:
                        print("⚠️ Warning: Failed to store Q&A pairs in database")
                    
                    return result
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing error: {e}")
                    print(f"Raw response: {response.content[:500]}...")
                    fallback_result = self._create_fallback_result(session_id, user_id, questions, answers)
                    await self._store_evaluation_result(fallback_result, db)
                    await self._store_qa_pairs(session_id, user_id, questions, answers, fallback_result.detailed_feedback, db)
                    return fallback_result
            
            else:
                # Fallback when AI model is not available
                fallback_result = self._create_fallback_result(session_id, user_id, questions, answers)
                await self._store_evaluation_result(fallback_result, db)
                await self._store_qa_pairs(session_id, user_id, questions, answers, fallback_result.detailed_feedback, db)
                return fallback_result
                
        except Exception as e:
            print(f"❌ Error in interview evaluation: {e}")
            import traceback
            traceback.print_exc()
            fallback_result = self._create_fallback_result(session_id, user_id, questions, answers)
            await self._store_evaluation_result(fallback_result, db)
            await self._store_qa_pairs(session_id, user_id, questions, answers, fallback_result.detailed_feedback, db)
            return fallback_result

    def _create_fallback_result(
        self,
        session_id: str,
        user_id: int,
        questions: List[str],
        answers: List[str]
    ) -> InterviewResultResponse:
        """
        Create a fallback result when AI evaluation is not available
        """
        # Simple scoring based on answer length and content
        scores = []
        for answer in answers:
            # Basic scoring: longer, more detailed answers get higher scores
            base_score = min(len(answer.split()) * 2, 80)  # Max 80 for length
            if any(keyword in answer.lower() for keyword in ['because', 'example', 'specifically', 'however']):
                base_score += 10  # Bonus for detailed explanations
            scores.append(min(base_score, 100))
        
        total_score = sum(scores) // len(scores) if scores else 50
        max_score = 100
        percentage = (total_score / max_score) * 100
        
        detailed_feedback = []
        for i, (q, a) in enumerate(zip(questions, answers)):
            detailed_feedback.append({
                "question": q,
                "answer": a,
                "score": scores[i] if i < len(scores) else 50,
                "feedback": "Basic evaluation completed",
                "strengths": ["Answered the question"],
                "weaknesses": ["Detailed AI evaluation not available"]
            })
        
        return InterviewResultResponse(
            session_id=session_id,
            user_id=user_id,
            total_score=total_score,
            max_score=max_score,
            percentage=percentage,
            questions_evaluated=len(questions),
            overall_analysis="Basic evaluation completed. AI evaluation not available.",
            detailed_feedback=detailed_feedback,
            strengths=["Completed the interview"],
            areas_for_improvement=["Enable AI evaluation for detailed feedback"],
            recommendations=["Ensure OpenAI is configured for detailed evaluation"],
            transcript=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    async def _store_evaluation_result(
        self,
        result: InterviewResultResponse,
        db: Session
    ):
        """
        Store or update evaluation result in database based on session_id
        """
        try:
            # Check if a record with this session_id already exists
            existing_result = db.query(InterviewResult).filter(
                InterviewResult.session_id == result.session_id
            ).first()

            # Ensure transcript timestamps are serializable
            transcript = []
            if result.transcript:
                for msg in result.transcript:
                    msg_copy = msg.copy()
                    if 'timestamp' in msg_copy and isinstance(msg_copy['timestamp'], datetime):
                        msg_copy['timestamp'] = msg_copy['timestamp'].isoformat()
                    transcript.append(msg_copy)
            else:
                transcript = None

            # Ensure all JSON fields are serializable
            def make_serializable(obj):
                if isinstance(obj, dict):
                    return {k: make_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [make_serializable(item) for item in obj]
                elif isinstance(obj, datetime):
                    return obj.isoformat()
                return obj

            current_time = datetime.now()
            
            if existing_result:
                # Update existing record
                existing_result.total_score = result.total_score
                existing_result.max_score = result.max_score
                existing_result.percentage = result.percentage
                existing_result.questions_evaluated = result.questions_evaluated
                existing_result.overall_analysis = result.overall_analysis
                existing_result.detailed_feedback = make_serializable(result.detailed_feedback)
                existing_result.strengths = make_serializable(result.strengths)
                existing_result.areas_for_improvement = make_serializable(result.areas_for_improvement)
                existing_result.recommendations = make_serializable(result.recommendations)
                existing_result.transcript = transcript
                existing_result.updated_at = current_time
                
                db.add(existing_result)
                db.commit()
                db.refresh(existing_result)
                
                print(f"✅ Updated evaluation result for session {result.session_id}")
            else:
                # Create new record
                interview_result = InterviewResult(
                    session_id=result.session_id,
                    user_id=result.user_id,
                    total_score=result.total_score,
                    max_score=result.max_score,
                    percentage=result.percentage,
                    questions_evaluated=result.questions_evaluated,
                    overall_analysis=result.overall_analysis,
                    detailed_feedback=make_serializable(result.detailed_feedback),
                    strengths=make_serializable(result.strengths),
                    areas_for_improvement=make_serializable(result.areas_for_improvement),
                    recommendations=make_serializable(result.recommendations),
                    transcript=transcript,
                    created_at=result.created_at or current_time,
                    updated_at=current_time
                )
                
                db.add(interview_result)
                db.commit()
                db.refresh(interview_result)
                
                print(f"✅ Created new evaluation result for session {result.session_id}")
            
            return True
            
        except Exception as e:
            print(f"Error storing evaluation result: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
            return False

    async def _store_qa_pairs(
        self,
        session_id: str,
        user_id: int,
        questions: List[str],
        answers: List[str],
        detailed_feedback: List[Dict[str, Any]],
        db: Session
    ) -> bool:
        """
        Store individual Q&A pairs in the qa_pairs table
        """
        try:
            print(f"💾 Storing {len(questions)} Q&A pairs for session {session_id}")
            
            for i, (question, answer) in enumerate(zip(questions, answers)):
                # Get score from detailed feedback if available
                score = None
                if i < len(detailed_feedback):
                    score = detailed_feedback[i].get('score', None)
                
                # Create QA pair
                qa_pair = QAPair(
                    user_id=user_id,
                    session_id=session_id,
                    question=question,
                    answer=answer,
                    score=score
                )
                
                db.add(qa_pair)
            
            db.commit()
            print(f"✅ Successfully stored {len(questions)} Q&A pairs")
            return True
            
        except Exception as e:
            print(f"Error storing Q&A pairs: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
            return False

    async def get_user_history(
        self,
        user_id: int,
        db: Session
    ) -> List[InterviewResultResponse]:
        """
        Get user's interview history with proper datetime handling
        """
        try:
            # Get complete evaluation results from the new table
            interview_results = db.query(InterviewResult).filter(
                InterviewResult.user_id == user_id
            ).order_by(InterviewResult.created_at.desc()).all()
            
            results = []
            for result in interview_results:
                # Ensure we have valid timestamps
                created_at = result.created_at or datetime.now()
                updated_at = result.updated_at or created_at
                
                interview_result = InterviewResultResponse(
                    session_id=result.session_id,
                    user_id=result.user_id,
                    total_score=result.total_score,
                    max_score=result.max_score,
                    percentage=result.percentage,
                    questions_evaluated=result.questions_evaluated,
                    overall_analysis=result.overall_analysis or "No analysis available",
                    detailed_feedback=result.detailed_feedback or [],
                    strengths=result.strengths or [],
                    areas_for_improvement=result.areas_for_improvement or [],
                    recommendations=result.recommendations or [],
                    transcript=result.transcript or [],
                    created_at=created_at,
                    updated_at=updated_at
                )
                results.append(interview_result)
            
            return results
            
        except Exception as e:
            print(f"Error getting user history: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def get_session_result(
        self,
        session_id: str,
        user_id: Optional[int],
        db: Session
    ) -> Optional[InterviewResultResponse]:
        """
        Get specific session result with proper datetime handling.
        If user_id is None, admin can view any interview.
        """
        try:
            query = db.query(InterviewResult).filter(
                InterviewResult.session_id == session_id
            )
            
            # If user_id is provided, filter by it (normal user access)
            # If None, admin can view any interview
            if user_id is not None:
                query = query.filter(InterviewResult.user_id == user_id)
            
            result = query.first()
            
            if not result:
                return None
            
            # Ensure we have valid timestamps
            created_at = result.created_at or datetime.now()
            updated_at = result.updated_at or created_at
            
            return InterviewResultResponse(
                session_id=result.session_id,
                user_id=result.user_id,
                total_score=result.total_score,
                max_score=result.max_score,
                percentage=result.percentage,
                questions_evaluated=result.questions_evaluated,
                overall_analysis=result.overall_analysis,
                detailed_feedback=result.detailed_feedback or [],
                strengths=result.strengths or [],
                areas_for_improvement=result.areas_for_improvement or [],
                recommendations=result.recommendations or [],
                transcript=result.transcript or [],
                created_at=created_at,
                updated_at=updated_at
            )
            
        except Exception as e:
            print(f"Error getting session result: {e}")
            import traceback
            traceback.print_exc()
            return None 