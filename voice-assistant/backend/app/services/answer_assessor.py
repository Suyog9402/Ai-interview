from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
import logging
import json

logger = logging.getLogger(__name__)


class AnswerAssessor:
    """Assesses answer quality using LLM"""
    
    def __init__(self):
        self.model = None
        if os.getenv("OPENAI_API_KEY"):
            try:
                self.model = ChatOpenAI(
                    model="gpt-4o-mini",
                    api_key=os.getenv("OPENAI_API_KEY"),
                    temperature=0.3
                )
            except Exception as e:
                logger.error(f"Error initializing answer assessor: {e}")
    
    def assess_answer(
        self, 
        question: str, 
        answer: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Assess answer quality and extract insights"""
        if not self.model:
            # Fallback to simple assessment
            return self._simple_assess(answer)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical interviewer assessing candidate answers.

Analyze the answer and provide:
1. Quality score (0-100)
2. Quality level (excellent/good/fair/poor)
3. Strengths (list)
4. Weaknesses (list)
5. Topics covered (list)
6. Whether follow-up is needed (boolean)
7. answer_felt_interesting (boolean): true ONLY when the answer is excellent or good AND includes a concrete example, real project, or specific story (not generic). Used to decide whether to ask 1-2 optional behavioral questions later. Set false for vague or purely theoretical answers.

Be strict but fair. Excellent answers (80-100) show deep understanding and experience.
Good answers (60-79) show solid understanding.
Fair answers (40-59) show basic knowledge.
Poor answers (0-39) show lack of knowledge or understanding.

Return JSON format:
{
    "score": <0-100>,
    "quality": "<excellent|good|fair|poor>",
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "topics_covered": ["topic1", "topic2"],
    "needs_followup": <true|false>,
    "answer_felt_interesting": <true|false>
}"""),
            ("user", f"""Question: {question}

Answer: {answer}

Context: {context or 'None'}

Assess this answer and return JSON.""")
        ])
        
        content = ""
        try:
            response = self.model.invoke(prompt.format_messages())
            content = (getattr(response, "content", None) or str(response)).strip()
            
            # Extract JSON: strip markdown code fences and take only the JSON object
            if "```" in content:
                start = content.find("```")
                if start >= 0:
                    rest = content[start:]
                    # Skip opening fence line
                    nl = rest.find("\n")
                    if nl >= 0:
                        rest = rest[nl + 1:]
                    end = rest.find("```")
                    if end >= 0:
                        content = rest[:end].strip()
            start_brace = content.find("{")
            end_brace = content.rfind("}")
            if start_brace >= 0 and end_brace > start_brace:
                content = content[start_brace : end_brace + 1]
            
            result = json.loads(content)
            if not isinstance(result, dict):
                return self._simple_assess(answer)
            
            # Use .get() for all keys to avoid KeyError on malformed or truncated output
            score = result.get("score", 50)
            if not isinstance(score, (int, float)):
                score = 50
            quality = (result.get("quality") or "fair").lower()
            if quality not in ("excellent", "good", "fair", "poor"):
                quality = "fair"
            return {
                "score": float(score),
                "quality": quality,
                "strengths": result.get("strengths") if isinstance(result.get("strengths"), list) else [],
                "weaknesses": result.get("weaknesses") if isinstance(result.get("weaknesses"), list) else [],
                "topics_covered": result.get("topics_covered") if isinstance(result.get("topics_covered"), list) else [],
                "needs_followup": bool(result.get("needs_followup", score < 70)),
                "answer_felt_interesting": bool(
                    result.get("answer_felt_interesting",
                        quality in ("excellent", "good") and score >= 70
                    )
                ),
            }
        except json.JSONDecodeError as e:
            snippet = content[:300] if content else "n/a"
            logger.warning(f"Answer assessor JSON parse error: {e}, content snippet: {snippet}")
            return self._simple_assess(answer)
        except Exception as e:
            logger.warning(f"Error assessing answer: {e}", exc_info=True)
            return self._simple_assess(answer)
    
    def _simple_assess(self, answer: str) -> Dict[str, Any]:
        """Simple fallback assessment"""
        answer_lower = answer.lower()
        length = len(answer.split())
        
        if length < 10:
            return {
                "score": 20,
                "quality": "poor",
                "strengths": [],
                "weaknesses": ["Answer too brief"],
                "topics_covered": [],
                "needs_followup": True,
                "answer_felt_interesting": False,
            }
        elif length < 30:
            return {
                "score": 50,
                "quality": "fair",
                "strengths": [],
                "weaknesses": ["Could be more detailed"],
                "topics_covered": [],
                "needs_followup": True,
                "answer_felt_interesting": False,
            }
        else:
            return {
                "score": 70,
                "quality": "good",
                "strengths": ["Detailed answer"],
                "weaknesses": [],
                "topics_covered": [],
                "needs_followup": False,
                "answer_felt_interesting": True,
            }

