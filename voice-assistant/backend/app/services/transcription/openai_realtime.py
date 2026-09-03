import os
import json
import logging
from typing import Dict, Any, Optional, BinaryIO
from pathlib import Path
from app.services.transcription.base import BaseTranscriber
from app.core.exceptions import TranscriptionException

from app.core.llm_provider import transcribe_audio_file

logger = logging.getLogger(__name__)


class OpenAIRealtimeTranscriber(BaseTranscriber):
    """Smart transcriber implementation using Groq Whisper / OpenAI Whisper"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "whisper-large-v3"):
        """
        Initialize transcriber.
        """
        super().__init__()
        self.api_key = api_key
        self.model = model
    
    async def transcribe_file(
        self,
        file_path: str,
        language: Optional[str] = None,
        enable_diarization: bool = True
    ) -> Dict[str, Any]:
        """
        Transcribe an audio/video file using Groq Whisper API / OpenAI Whisper API.
        """
        try:
            if not os.path.exists(file_path):
                raise TranscriptionException(f"File not found: {file_path}")
            
            # Use unified transcriber
            res = transcribe_audio_file(file_path)
            if not res:
                raise TranscriptionException("Audio transcription failed with available providers.")
            
            transcript_text = res.get("text", "")
            raw_segments = res.get("segments", [])
            lang = res.get("language", language or "en")
            
            transcript_data = {
                "text": transcript_text,
                "language": lang,
                "segments": []
            }
            
            for segment in raw_segments:
                if isinstance(segment, dict):
                    transcript_data["segments"].append({
                        "id": segment.get("id", 0),
                        "speaker": segment.get("speaker", "speaker_0"),
                        "start": segment.get("start", 0.0),
                        "end": segment.get("end", 0.0),
                        "text": segment.get("text", ""),
                        "confidence": segment.get("confidence", 1.0 - segment.get("no_speech_prob", 0.1))
                    })
                elif hasattr(segment, "text"):
                    transcript_data["segments"].append({
                        "id": getattr(segment, "id", 0),
                        "speaker": getattr(segment, "speaker", "speaker_0"),
                        "start": getattr(segment, "start", 0.0),
                        "end": getattr(segment, "end", 0.0),
                        "text": getattr(segment, "text", ""),
                        "confidence": 0.95
                    })
            
            # Diarization data from Deepgram or fallback
            diarization_data = res.get("diarization")
            if not diarization_data and enable_diarization:
                diarization_data = {
                    "speakers": ["speaker_0"],
                    "segments": [
                        {
                            "speaker": "speaker_0",
                            "start": 0.0,
                            "end": transcript_data["segments"][-1]["end"] if transcript_data["segments"] else 0.0
                        }
                    ]
                }
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(transcript_data)
            
            return {
                "transcript_json": transcript_data,
                "diarization_data": diarization_data,
                "confidence_scores": [seg.get("confidence", 0.9) for seg in transcript_data["segments"]],
                "segments": transcript_data["segments"],
                "quality_score": quality_score
            }
            
        except Exception as e:
            logger.error(f"Transcription error: {e}", exc_info=True)
            raise TranscriptionException(f"Failed to transcribe file: {str(e)}")
    
    async def transcribe_stream(
        self,
        audio_stream: BinaryIO,
        language: Optional[str] = None,
        enable_diarization: bool = True
    ) -> Dict[str, Any]:
        """
        Transcribe audio stream using OpenAI Realtime API.
        
        Args:
            audio_stream: Audio stream to transcribe
            language: Optional language code
            enable_diarization: Whether to enable speaker diarization
        
        Returns:
            Dictionary with transcript data
        """
        # For real-time streaming, we would use OpenAI Realtime API
        # This is a simplified implementation
        # In production, you'd use the Realtime API WebSocket connection
        raise TranscriptionException("Stream transcription not yet fully implemented. Use transcribe_file for now.")
    
    async def get_supported_formats(self) -> list[str]:
        """
        Get supported audio/video formats.
        
        Returns:
            List of supported format extensions
        """
        return ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]
    
    def _calculate_quality_score(self, transcript_data: Dict[str, Any]) -> float:
        """
        Calculate overall quality score for transcript.
        
        Args:
            transcript_data: Transcript data
        
        Returns:
            Quality score between 0 and 1
        """
        if not transcript_data.get("segments"):
            return 0.5
        
        # Average confidence across segments
        confidences = [seg.get("confidence", 0.5) for seg in transcript_data["segments"]]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
        
        # Normalize to 0-1 range
        return min(1.0, max(0.0, avg_confidence))

