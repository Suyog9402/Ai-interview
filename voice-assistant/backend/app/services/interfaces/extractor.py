from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class ExtractorInterface(ABC):
    """Interface for structured data extraction from resumes and transcripts"""
    
    @abstractmethod
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
            Dictionary containing:
            - skills: List of skills
            - tools: List of tools/technologies
            - experience_years: Total years of experience
            - roles: List of roles/positions
            - projects: List of projects with details
            - achievements: List of achievements with metrics
            - education: Education details
            - companies: List of companies worked at
            - dates: Employment dates
        """
        pass
    
    @abstractmethod
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
            Dictionary containing:
            - skills: Skills mentioned in transcript
            - tools: Tools/technologies mentioned
            - experience_years: Experience mentioned
            - roles: Roles discussed
            - projects: Projects discussed
            - achievements: Achievements mentioned
            - education: Education discussed
            - companies: Companies mentioned
            - dates: Dates mentioned
        """
        pass
    
    @abstractmethod
    async def validate_extraction(self, extracted_data: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate extracted data for completeness and accuracy.
        
        Args:
            extracted_data: Extracted data to validate
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        pass

