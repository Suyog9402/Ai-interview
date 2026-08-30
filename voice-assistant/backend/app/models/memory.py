from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class MemoryStore(Base):
    __tablename__ = "memory_store"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    session_id = Column(String, nullable=True, index=True)
    memory_type = Column(String, nullable=False, index=True)  # "working" or "long_term"
    content = Column(JSON, nullable=False)  # Memory content as JSONB
    embeddings = Column(JSON, nullable=True)  # Vector embeddings (stored as JSON for now, can be pgvector later)
    metadata_json = Column(JSON, nullable=True)  # Additional metadata (renamed from 'metadata' to avoid SQLAlchemy conflict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    candidate = relationship("Candidate", back_populates="memory_store")

