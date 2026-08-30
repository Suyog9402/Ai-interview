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
    
    if provider == "openai_realtime":
        if not settings.openai_api_key:
            raise TranscriptionException("OpenAI API key not configured")
        return OpenAIRealtimeTranscriber(
            api_key=settings.openai_api_key,
            model=settings.openai_realtime_model
        )
    elif provider == "azure_realtime":
        if not settings.azure_speech_key or not settings.azure_speech_region:
            raise TranscriptionException("Azure Speech credentials not configured")
        # return AzureRealtimeTranscriber(
        #     api_key=settings.azure_speech_key,
        #     region=settings.azure_speech_region
        # )
        raise TranscriptionException("Azure Realtime transcription not yet implemented")
    else:
        raise TranscriptionException(f"Unknown transcriber provider: {provider}")

__all__ = ["get_transcriber", "BaseTranscriber", "OpenAIRealtimeTranscriber"]

