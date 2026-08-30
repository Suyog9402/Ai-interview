from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.sql import func
from app.db.database import Base

class InterviewResult(Base):
    __tablename__ = "interview_results"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, index=True)
    total_score = Column(Integer)
    max_score = Column(Integer)
    percentage = Column(Float)
    questions_evaluated = Column(Integer)
    overall_analysis = Column(Text)
    detailed_feedback = Column(JSON)  # Store as JSON
    strengths = Column(JSON)  # Store as JSON array
    areas_for_improvement = Column(JSON)  # Store as JSON array
    recommendations = Column(JSON)  # Store as JSON array
    transcript = Column(JSON)  # Store conversation transcript as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 