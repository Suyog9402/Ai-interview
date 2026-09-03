from app.services.transcription.base import BaseTranscriber
from app.services.transcription.openai_realtime import OpenAIRealtimeTranscriber
from app.core.config import settings
from app.services.interfaces.transcriber import TranscriberInterface
from app.core.exceptions import TranscriptionException

# Azure implementation (stub for now)
# from app.services.transcription.azure_realtime import AzureRealtimeTranscriber


def get_transcriber() -> TranscriberInterface:
    """
    Factory function to get the appropriate transcriber based on config.
    """
    provider = settings.transcriber_provider.lower()
    
    if provider in ["groq", "openai_realtime", "openai"]:
        return OpenAIRealtimeTranscriber(
            api_key=settings.groq_api_key or settings.openai_api_key or settings.gemini_api_key,
            model=settings.groq_whisper_model or "whisper-large-v3"
        )
    elif provider == "azure_realtime":
        if not settings.azure_speech_key or not settings.azure_speech_region:
            raise TranscriptionException("Azure Speech credentials not configured")
        raise TranscriptionException("Azure Realtime transcription not yet implemented")
    else:
        return OpenAIRealtimeTranscriber()

__all__ = ["get_transcriber", "BaseTranscriber", "OpenAIRealtimeTranscriber"]

