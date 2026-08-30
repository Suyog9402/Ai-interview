import json
import logging
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.services.extraction.base import BaseExtractor
from app.core.exceptions import ExtractionException

logger = logging.getLogger(__name__)


class LLMExtractor(BaseExtractor):
    """LLM-based structured data extraction"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o", temperature: float = 0.1):
        """
        Initialize LLM extractor.
        
        Args:
            api_key: OpenAI API key
            model: Model to use for extraction
            temperature: Temperature for extraction (low for consistency)
        """
        super().__init__()
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=temperature
        )
        
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
            
            # Parse JSON response
            content = response.content.strip()
            if content.startswith('```json'):
                content = content[7:]
            elif content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            extracted_data = json.loads(content)
            
            # Validate extraction
            is_valid, errors = await self.validate_extraction(extracted_data)
            if not is_valid:
                logger.warning(f"Extraction validation errors: {errors}")
            
            return extracted_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            raise ExtractionException(f"Failed to parse extraction result: {str(e)}")
        except Exception as e:
            logger.error(f"Extraction error: {e}", exc_info=True)
            raise ExtractionException(f"Failed to extract data from resume: {str(e)}")
    
    async def extract_from_transcript(
        self,
        transcript_data: Dict[str, Any],
        transcript_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from transcript.
        
        Args:
            transcript_data: Transcript data (from transcriber)
            transcript_metadata: Optional metadata about the transcript
        
        Returns:
            Dictionary with extracted structured data
        """
        try:
            # Convert transcript to text
            transcript_text = self._transcript_to_text(transcript_data)
            
            chain = self.transcript_prompt | self.llm
            response = chain.invoke({"transcript_text": transcript_text})
            
            # Parse JSON response
            content = response.content.strip()
            if content.startswith('```json'):
                content = content[7:]
            elif content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            extracted_data = json.loads(content)
            
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
            
            # Validate extraction
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

