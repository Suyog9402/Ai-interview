"""
Azure Realtime Speech-to-Text implementation (stub for future implementation)
"""
from app.services.transcription.base import BaseTranscriber
from app.core.exceptions import TranscriptionException


class AzureRealtimeTranscriber(BaseTranscriber):
    """Azure Realtime Speech-to-Text implementation - to be implemented"""
    
    def __init__(self, api_key: str, region: str):
        super().__init__()
        self.api_key = api_key
        self.region = region
        raise TranscriptionException("Azure Realtime transcription not yet implemented")
    
    async def transcribe_file(self, file_path: str, language=None, enable_diarization=True) -> Dict[str, Any]:
        raise NotImplementedError("Azure Realtime transcription not yet implemented")
    
    async def transcribe_stream(self, audio_stream, language=None, enable_diarization=True) -> Dict[str, Any]:
        raise NotImplementedError("Azure Realtime transcription not yet implemented")
    
    async def get_supported_formats(self) -> list[str]:
        raise NotImplementedError("Azure Realtime transcription not yet implemented")

