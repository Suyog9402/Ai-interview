from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Recording(Base):
    __tablename__ = "recordings"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    session_id = Column(String, unique=True, nullable=False, index=True)
    file_path = Column(String, nullable=False)  # Relative path in local storage
    video_url = Column(String, nullable=True)  # HTTP URL to access file
    file_version = Column(Integer, default=1)
    format = Column(String, nullable=False)  # "audio" or "video"
    duration_seconds = Column(Float, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    storage_provider = Column(String, nullable=False, default="local")  # local, azure, aws, gcp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    candidate = relationship("Candidate", back_populates="recordings")
    transcript = relationship("Transcript", back_populates="recording", uselist=False, cascade="all, delete-orphan")


class Transcript(Base):
    __tablename__ = "transcripts"
    
    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(Integer, ForeignKey("recordings.id"), unique=True, nullable=False, index=True)
    transcript_json = Column(JSON, nullable=False)  # Full transcript with timestamps
    diarization_data = Column(JSON, nullable=True)  # Speaker labels and segmentation
    confidence_scores = Column(JSON, nullable=True)  # Per-segment confidence scores
    segments = Column(JSON, nullable=True)  # Time-segmented transcript
    quality_score = Column(Float, nullable=True)  # Overall quality score 0-1
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    recording = relationship("Recording", back_populates="transcript")

