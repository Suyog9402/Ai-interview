from app.services.interfaces.extractor import ExtractorInterface
from typing import Dict, Any, Optional


class BaseExtractor(ExtractorInterface):
    """Base class for extractor implementations"""
    
    def __init__(self):
        """Initialize base extractor"""
        pass
    
    async def extract_from_resume(
        self,
        resume_text: str,
        resume_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Base implementation - should be overridden"""
        raise NotImplementedError
    
    async def extract_from_transcript(
        self,
        transcript_data: Dict[str, Any],
        transcript_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Base implementation - should be overridden"""
        raise NotImplementedError
    
    async def validate_extraction(self, extracted_data: Dict[str, Any]) -> tuple[bool, list[str]]:
        """Base implementation - should be overridden"""
        raise NotImplementedError

