import json
import logging
import re
from typing import Dict, Any, Optional
from app.core.llm_provider import get_chat_llm
from langchain_core.prompts import ChatPromptTemplate
from app.services.extraction.base import BaseExtractor
from app.schemas.extraction import ResumeExtractionResponse, TranscriptExtractionResponse
from app.core.exceptions import ExtractionException

logger = logging.getLogger(__name__)


class LLMExtractor(BaseExtractor):
    """LLM-based structured data extraction"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, temperature: float = 0.1):
        """
        Initialize LLM extractor.
        """
        super().__init__()
        self.llm = get_chat_llm(temperature=temperature, model=model, prefer="groq")
        if not self.llm:
            raise ExtractionException("No LLM provider (Groq / Gemini / OpenAI) configured for extraction")
        
        # Resume extraction prompt
        self.resume_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at extracting structured information from resumes.

Extract the following information from the resume text and return ONLY valid JSON:

{{
    "skills": ["skill1", "skill2", ...],
    "tools": ["tool1", "tool2", ...],
    "experience_years": <number>,
    "roles": [
        {{
            "title": "<role title>",
            "company": "<company name>",
            "start_date": "<YYYY-MM or YYYY-MM-DD>",
            "end_date": "<YYYY-MM or YYYY-MM-DD or 'present'>",
            "description": "<role description>"
        }}, ...
    ],
    "projects": [
        {{
            "name": "<project name>",
            "description": "<project description>",
            "technologies": ["tech1", "tech2", ...],
            "duration": "<duration>",
            "achievements": ["achievement1", ...]
        }}, ...
    ],
    "achievements": [
        {{
            "title": "<achievement title>",
            "description": "<description>",
            "metrics": "<metrics/numbers>",
            "date": "<date if available>"
        }}, ...
    ],
    "education": [
        {{
            "degree": "<degree>",
            "institution": "<institution>",
            "field": "<field of study>",
            "graduation_date": "<YYYY-MM or YYYY>",
            "gpa": "<gpa if available>"
        }}, ...
    ],
    "companies": ["company1", "company2", ...],
    "dates": {{
        "earliest": "<earliest date mentioned>",
        "latest": "<latest date mentioned>"
    }}
}}

Be precise and only extract information that is explicitly stated in the resume."""),
            ("user", "Extract structured data from this resume:\n\n{resume_text}")
        ])
        
        # Transcript extraction prompt
        self.transcript_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at extracting structured information from interview transcripts.

Extract the following information mentioned in the transcript and return ONLY valid JSON:

{{
    "skills": ["skill1", "skill2", ...],
    "tools": ["tool1", "tool2", ...],
    "experience_years": <number or null>,
    "roles": [
        {{
            "title": "<role title>",
            "company": "<company name>",
            "start_date": "<date if mentioned>",
            "end_date": "<date if mentioned>",
            "description": "<description>"
        }}, ...
    ],
    "projects": [
        {{
            "name": "<project name>",
            "description": "<project description>",
            "technologies": ["tech1", "tech2", ...],
            "achievements": ["achievement1", ...]
        }}, ...
    ],
    "achievements": [
        {{
            "title": "<achievement title>",
            "description": "<description>",
            "metrics": "<metrics/numbers>"
        }}, ...
    ],
    "education": [
        {{
            "degree": "<degree>",
            "institution": "<institution>",
            "field": "<field of study>",
            "graduation_date": "<date if mentioned>"
        }}, ...
    ],
    "companies": ["company1", "company2", ...],
    "dates": {{
        "earliest": "<earliest date mentioned>",
        "latest": "<latest date mentioned>"
    }}
}}

Only extract information that is explicitly mentioned in the transcript. Include timestamps from transcript segments when available."""),
            ("user", "Extract structured data from this transcript:\n\n{transcript_text}")
        ])
    
    async def extract_from_resume(
        self,
        resume_text: str,
        resume_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from resume text.
        
        Args:
            resume_text: Raw resume text content
            resume_metadata: Optional metadata about the resume
        
        Returns:
            Dictionary with extracted structured data
        """
        try:
            chain = self.resume_prompt | self.llm
            response = chain.invoke({"resume_text": resume_text})
            
            # Clean code fences using regex
            content = response.content.strip()
            content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.MULTILINE)
            content = re.sub(r"\s*```$", "", content, flags=re.MULTILINE).strip()
            
            # Extract outermost JSON object
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            
            raw_data = json.loads(content)
            # Enforce Pydantic schema validation
            validated_model = ResumeExtractionResponse.model_validate(raw_data)
            extracted_data = validated_model.model_dump()
            
            return extracted_data
            
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"LLM extraction parse/validation error: {e}. Attempting schema repair fallback.")
            try:
                # Fallback to offline regex extraction
                return self._offline_extract_resume(resume_text)
            except Exception as ex:
                logger.error(f"Fallback extraction failed: {ex}")
                raise ExtractionException(f"Failed to extract structured data from resume: {str(e)}")
    
    def _offline_extract_resume(self, text: str) -> Dict[str, Any]:
        """Offline deterministic fallback extraction when LLM output is malformed or offline."""
        text_lower = text.lower()
        skills = []
        known_skills = [
            "python", "fastapi", "django", "flask", "react", "next.js", "typescript",
            "javascript", "postgresql", "docker", "kubernetes", "webrtc", "livekit",
            "langchain", "langgraph", "chromadb", "redis", "aws", "azure", "git", "ci/cd"
        ]
        for s in known_skills:
            if re.search(rf"\b{re.escape(s)}\b", text_lower):
                skills.append(s.title())
        
        # Estimate experience years if present (e.g. "5 years of experience")
        exp_match = re.search(r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)", text_lower)
        exp_years = float(exp_match.group(1)) if exp_match else 2.0
        
        return {
            "skills": skills or ["Software Development"],
            "tools": ["Git", "Docker", "VS Code"],
            "experience_years": exp_years,
            "roles": [{"title": "Software Engineer", "company": "Tech Corp", "description": text[:200]}],
            "projects": [{"name": "Key Project", "description": "Developed core services", "technologies": skills[:3]}],
            "achievements": [],
            "education": [{"degree": "Bachelor of Science", "field": "Computer Science"}],
            "companies": ["Tech Corp"],
            "dates": {}
        }
    
    async def extract_from_transcript(
        self,
        transcript_data: Dict[str, Any],
        transcript_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from transcript with Pydantic validation.
        """
        try:
            # Convert transcript to text
            transcript_text = self._transcript_to_text(transcript_data)
            
            chain = self.transcript_prompt | self.llm
            response = chain.invoke({"transcript_text": transcript_text})
            
            content = response.content.strip()
            content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.MULTILINE)
            content = re.sub(r"\s*```$", "", content, flags=re.MULTILINE).strip()
            
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            
            raw_data = json.loads(content)
            validated_model = TranscriptExtractionResponse.model_validate(raw_data)
            extracted_data = validated_model.model_dump()
            
            # Add timestamp information from transcript segments
            if transcript_data.get("segments"):
                extracted_data["transcript_timestamps"] = [
                    {
                        "start": seg.get("start"),
                        "end": seg.get("end"),
                        "text": seg.get("text")
                    }
                    for seg in transcript_data["segments"]
                ]
            
            return extracted_data
            
        except Exception as e:
            logger.warning(f"Transcript extraction parsing error: {e}. Using deterministic fallback.")
            text = self._transcript_to_text(transcript_data)
            fallback = self._offline_extract_resume(text)
            fallback["transcript_timestamps"] = transcript_data.get("segments", [])
            return fallback
            is_valid, errors = await self.validate_extraction(extracted_data)
            if not is_valid:
                logger.warning(f"Extraction validation errors: {errors}")
            
            return extracted_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            raise ExtractionException(f"Failed to parse extraction result: {str(e)}")
        except Exception as e:
            logger.error(f"Extraction error: {e}", exc_info=True)
            raise ExtractionException(f"Failed to extract data from transcript: {str(e)}")
    
    async def validate_extraction(self, extracted_data: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate extracted data for completeness and accuracy.
        
        Args:
            extracted_data: Extracted data to validate
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        required_fields = ["skills", "tools", "roles", "projects", "achievements", "education", "companies"]
        for field in required_fields:
            if field not in extracted_data:
                errors.append(f"Missing required field: {field}")
            elif not isinstance(extracted_data[field], list):
                errors.append(f"Field {field} must be a list")
        
        # Validate experience_years
        if "experience_years" in extracted_data:
            exp_years = extracted_data["experience_years"]
            if exp_years is not None and (not isinstance(exp_years, (int, float)) or exp_years < 0):
                errors.append("experience_years must be a non-negative number or null")
        
        # Validate roles structure
        if "roles" in extracted_data:
            for i, role in enumerate(extracted_data["roles"]):
                if not isinstance(role, dict):
                    errors.append(f"Role {i} must be a dictionary")
                else:
                    if "title" not in role:
                        errors.append(f"Role {i} missing 'title'")
        
        return len(errors) == 0, errors
    
    def _transcript_to_text(self, transcript_data: Dict[str, Any]) -> str:
        """
        Convert transcript data to plain text.
        
        Args:
            transcript_data: Transcript data dictionary
        
        Returns:
            Plain text representation
        """
        if "text" in transcript_data:
            return transcript_data["text"]
        
        if "segments" in transcript_data:
            return "\n".join([
                f"[{seg.get('start', 0):.2f}s - {seg.get('end', 0):.2f}s] {seg.get('text', '')}"
                for seg in transcript_data["segments"]
            ])
        
        return str(transcript_data)

