from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, BinaryIO
from pathlib import Path


class TranscriberInterface(ABC):
    """Interface for transcription providers (OpenAI Realtime, Azure Realtime)"""
    
    @abstractmethod
    async def transcribe_file(
        self,
        file_path: str,
        language: Optional[str] = None,
        enable_diarization: bool = True
    ) -> Dict[str, Any]:
        """
        Transcribe an audio/video file.
        
        Args:
            file_path: Path to audio/video file
            language: Optional language code (e.g., 'en-US')
            enable_diarization: Whether to enable speaker diarization
        
        Returns:
            Dictionary containing:
            - transcript_json: Full transcript with timestamps
            - diarization_data: Speaker labels and segmentation (if enabled)
            - confidence_scores: Per-segment confidence scores
            - segments: Time-segmented transcript
            - quality_score: Overall quality score (0-1)
        """
        pass
    
    @abstractmethod
    async def transcribe_stream(
        self,
        audio_stream: BinaryIO,
        language: Optional[str] = None,
        enable_diarization: bool = True
    ) -> Dict[str, Any]:
        """
        Transcribe an audio stream in real-time.
        
        Args:
            audio_stream: Audio stream to transcribe
            language: Optional language code
            enable_diarization: Whether to enable speaker diarization
        
        Returns:
            Same format as transcribe_file
        """
        pass
    
    @abstractmethod
    async def get_supported_formats(self) -> list[str]:
        """
        Get list of supported audio/video formats.
        
        Returns:
            List of supported format extensions (e.g., ['mp3', 'wav', 'mp4'])
        """
        pass

