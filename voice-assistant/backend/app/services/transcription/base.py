from app.services.interfaces.transcriber import TranscriberInterface
from typing import Dict, Any, Optional, BinaryIO


class BaseTranscriber(TranscriberInterface):
    """Base class for transcriber implementations"""
    
    def __init__(self):
        """Initialize base transcriber"""
        pass
    
    async def transcribe_file(
        self,
        file_path: str,
        language: Optional[str] = None,
        enable_diarization: bool = True
    ) -> Dict[str, Any]:
        """Base implementation - should be overridden"""
        raise NotImplementedError
    
    async def transcribe_stream(
        self,
        audio_stream: BinaryIO,
        language: Optional[str] = None,
        enable_diarization: bool = True
    ) -> Dict[str, Any]:
        """Base implementation - should be overridden"""
        raise NotImplementedError
    
    async def get_supported_formats(self) -> list[str]:
        """Base implementation - should be overridden"""
        raise NotImplementedError

