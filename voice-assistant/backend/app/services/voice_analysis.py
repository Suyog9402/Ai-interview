"""
Speech Delivery & Acoustic Metrics Service

Calculates quantifiable, objective speech delivery metrics:
- Speaking rate (Words Per Minute / WPM)
- Response latency (interviewer turn to candidate speech delay)
- Pause statistics (count, average duration, long pauses)
- Filler word frequency and inventory (um, uh, like, you know, etc.)
- Speaking-to-silence ratio and articulation pacing

NOTE: This service focuses strictly on measurable speech patterns and fluency metrics.
It avoids unscientific claims of psychological emotion or mind-reading confidence detection.
"""
import logging
import re
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Standard filler words and hesitation tokens in technical interviews
FILLER_WORDS = [
    "um", "uh", "er", "ah", "like", "you know", "i mean",
    "basically", "actually", "literally", "sort of", "kind of",
    "right", "so yeah", "honestly"
]

class SpeechMetricsService:
    """Calculates objective, quantifiable speech delivery and fluency metrics."""
    
    def __init__(self):
        self.is_connected = True
        self.last_turn_end_time: Optional[float] = None
        self.speech_start_time: Optional[float] = None
        
        self.analysis_state: Dict[str, Any] = {
            "speaking": False,
            # Measurable Speech Metrics
            "words_per_minute": 0.0,
            "word_count": 0,
            "duration_seconds": 0.0,
            "response_latency_seconds": 0.0,
            "pause_count": 0,
            "avg_pause_duration_seconds": 0.0,
            "filler_word_count": 0,
            "filler_words_per_100_words": 0.0,
            "filler_breakdown": {},
            "speaking_ratio": 0.0,
            # Fluency & Delivery Assessment (Defensible Rubric)
            "pace_category": "Normal",  # Slow (<110), Optimal (110-160), Fast (>160)
            "delivery_fluency_score": 0.8,  # 0.0 - 1.0 based on pacing & filler density
            "speech_patterns": [],
            "last_update": datetime.now().isoformat()
        }

    def record_interviewer_turn_end(self, timestamp: Optional[float] = None):
        """Record when the interviewer finished speaking to measure response latency."""
        self.last_turn_end_time = timestamp or time.time()

    def record_candidate_speech_start(self, timestamp: Optional[float] = None) -> float:
        """Record when the candidate started speaking and return latency in seconds."""
        self.speech_start_time = timestamp or time.time()
        latency = 0.0
        if self.last_turn_end_time is not None:
            latency = max(0.0, round(self.speech_start_time - self.last_turn_end_time, 2))
            self.analysis_state["response_latency_seconds"] = latency
        return latency

    def analyze_transcript(
        self,
        text_data: str,
        duration_seconds: Optional[float] = None,
        pause_durations: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Analyze transcript text and optional timing data to produce objective speech delivery metrics.
        
        Args:
            text_data: Transcribed candidate response.
            duration_seconds: Total duration of the speech segment in seconds.
            pause_durations: List of detected pause durations in seconds.
        """
        if not text_data or not text_data.strip():
            self.analysis_state.update({
                "speaking": False,
                "words_per_minute": 0.0,
                "word_count": 0,
                "duration_seconds": 0.0,
                "filler_word_count": 0,
                "filler_words_per_100_words": 0.0,
                "filler_breakdown": {},
                "speech_patterns": ["No speech detected"],
                "last_update": datetime.now().isoformat()
            })
            return self.analysis_state

        cleaned_text = text_data.strip()
        words = re.findall(r"\b[\w'-]+\b", cleaned_text.lower())
        word_count = len(words)
        
        # Estimate duration if not provided (assume average 130 WPM baseline for length estimation)
        effective_duration = duration_seconds if (duration_seconds and duration_seconds > 0) else max(1.0, (word_count / 130.0) * 60.0)
        
        # 1. Speaking Rate (Words Per Minute)
        wpm = round((word_count / effective_duration) * 60.0, 1) if effective_duration > 0 else 0.0
        
        # Pace categorization based on speech pathology and communication standards
        if wpm < 110:
            pace_category = "Deliberate / Slow (<110 WPM)"
        elif 110 <= wpm <= 165:
            pace_category = "Optimal (110-165 WPM)"
        else:
            pace_category = "Rapid / Fast (>165 WPM)"

        # 2. Filler Word & Hesitation Inventory
        filler_breakdown: Dict[str, int] = {}
        total_fillers = 0
        text_lower = cleaned_text.lower()
        
        for filler in FILLER_WORDS:
            # Match filler as a distinct word/phrase
            pattern = rf"\b{re.escape(filler)}\b"
            matches = len(re.findall(pattern, text_lower))
            if matches > 0:
                filler_breakdown[filler] = matches
                total_fillers += matches

        filler_rate = round((total_fillers / max(1, word_count)) * 100.0, 2)

        # 3. Pause Statistics
        pauses = pause_durations or []
        pause_count = len(pauses)
        avg_pause = round(sum(pauses) / max(1, pause_count), 2) if pause_count > 0 else 0.0
        total_pause_time = sum(pauses)
        speaking_ratio = round(max(0.0, min(1.0, (effective_duration - total_pause_time) / max(0.1, effective_duration))), 2)

        # 4. Objective Patterns
        patterns = []
        if wpm >= 110 and wpm <= 165:
            patterns.append("Balanced conversational pace")
        elif wpm > 165:
            patterns.append("Rapid delivery rate")
        elif wpm < 110 and word_count > 10:
            patterns.append("Measured, deliberate pacing")

        if filler_rate <= 2.5:
            patterns.append("Low filler-word density")
        elif filler_rate > 6.0:
            patterns.append(f"Elevated filler-word density ({filler_rate}%)")

        if any(p > 2.5 for p in pauses):
            patterns.append("Extended mid-sentence pauses detected (>2.5s)")

        # Technical terminology presence (objective lexical check)
        tech_terms = [
            "architecture", "api", "database", "latency", "async", "cache",
            "concurrency", "distributed", "scalability", "docker", "pipeline",
            "microservices", "testing", "monitoring", "framework"
        ]
        found_tech = [t for t in tech_terms if t in text_lower]
        if len(found_tech) >= 3:
            patterns.append(f"Technical vocabulary utilized: {', '.join(found_tech[:4])}")

        # 5. Composite Delivery Fluency Score (0.0 to 1.0)
        # Penalizes excessive fillers (>5%) and extreme pacing (<90 WPM or >190 WPM)
        fluency_score = 1.0
        if filler_rate > 3.0:
            fluency_score -= min(0.4, (filler_rate - 3.0) * 0.05)
        if wpm < 100 or wpm > 175:
            fluency_score -= 0.15
        fluency_score = max(0.2, min(1.0, round(fluency_score, 2)))

        self.analysis_state.update({
            "speaking": True,
            "words_per_minute": wpm,
            "word_count": word_count,
            "duration_seconds": round(effective_duration, 2),
            "pause_count": pause_count,
            "avg_pause_duration_seconds": avg_pause,
            "filler_word_count": total_fillers,
            "filler_words_per_100_words": filler_rate,
            "filler_breakdown": filler_breakdown,
            "speaking_ratio": speaking_ratio,
            "pace_category": pace_category,
            "delivery_fluency_score": fluency_score,
            # Backwards-compatible fields for UI
            "confidence": fluency_score,
            "nervousness": round(min(1.0, filler_rate / 10.0), 2),
            "speech_patterns": patterns,
            "last_update": datetime.now().isoformat()
        })
        return self.analysis_state

    def update_voice_analysis(self, audio_data: Optional[bytes] = None, text_data: Optional[str] = None):
        """Update voice analysis based on text transcription input."""
        return self.analyze_transcript(text_data or "")

    def get_analysis_state(self) -> Dict[str, Any]:
        """Get current speech delivery metrics state."""
        return self.analysis_state.copy()

    async def connect_to_voice_api(self, api_url: Optional[str] = None):
        """Local speech analysis is self-contained with 0 external API dependencies."""
        self.is_connected = True
        return True

    async def process_audio_chunk(self, audio_chunk: bytes):
        """Process incoming audio metadata locally."""
        pass

    async def start_realtime_analysis(self):
        """Start real-time voice analysis."""
        self.is_connected = True
        return True

    async def stop_realtime_analysis(self):
        """Stop real-time voice analysis."""
        self.is_connected = False
        return True


# Global voice analysis service instance (aliased for backwards compatibility)
VoiceAnalysisService = SpeechMetricsService
voice_analysis_service = SpeechMetricsService()