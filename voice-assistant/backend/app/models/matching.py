from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class MatchResult(Base):
    __tablename__ = "match_results"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    jd_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False, index=True)
    session_id = Column(String, ForeignKey("recordings.session_id"), nullable=True, index=True)
    hard_filter_passed = Column(Boolean, nullable=False)
    hard_filter_reasons = Column(JSON, nullable=True)  # List of failure reasons
    weighted_score = Column(Float, nullable=False)
    score_breakdown = Column(JSON, nullable=True)  # Detailed score breakdown
    evidence_map = Column(JSON, nullable=True)  # skill -> evidence locations
    explanation = Column(Text, nullable=True)
    threshold_passed = Column(Boolean, nullable=False, index=True)
    settings_version_id = Column(Integer, ForeignKey("admin_settings.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate = relationship("Candidate", back_populates="match_results")
    job_description = relationship("JobDescription", back_populates="match_results")
    settings_version = relationship("AdminSetting", foreign_keys=[settings_version_id])
    evidence_tracking = relationship("EvidenceTracking", back_populates="match_result", cascade="all, delete-orphan")


class EvidenceTracking(Base):
    __tablename__ = "evidence_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    match_result_id = Column(Integer, ForeignKey("match_results.id"), nullable=False, index=True)
    skill_name = Column(String, nullable=False, index=True)
    evidence_type = Column(String, nullable=False)  # "resume" or "transcript"
    source_location = Column(JSON, nullable=False)  # chunk_id, timestamp, etc.
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    match_result = relationship("MatchResult", back_populates="evidence_tracking")

