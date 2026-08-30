from app.services.extraction.base import BaseExtractor
from app.services.extraction.llm_extractor import LLMExtractor
from app.core.config import settings
from app.services.interfaces.extractor import ExtractorInterface
from app.core.exceptions import ExtractionException


def get_extractor() -> ExtractorInterface:
    """
    Factory function to get the appropriate extractor based on config.
    """
    # For now, we only have LLM extractor
    # Future: could add hybrid extractor
    if not settings.openai_api_key:
        raise ExtractionException("OpenAI API key not configured for extraction")
    
    return LLMExtractor(
        api_key=settings.openai_api_key,
        model=settings.extraction_model,
        temperature=settings.extraction_temperature
    )

__all__ = ["get_extractor", "BaseExtractor", "LLMExtractor"]

