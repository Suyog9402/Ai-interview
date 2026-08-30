from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class JobDescription(Base):
    __tablename__ = "job_descriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    current_version_id = Column(Integer, ForeignKey("jd_versions.id"), nullable=True)
    admin_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    admin = relationship("AdminUser", back_populates="job_descriptions")
    versions = relationship("JDVersion", back_populates="job_description", foreign_keys="JDVersion.jd_id", cascade="all, delete-orphan")
    current_version = relationship("JDVersion", foreign_keys=[current_version_id], uselist=False)
    match_results = relationship("MatchResult", back_populates="job_description", cascade="all, delete-orphan")
    admin_settings = relationship("AdminSetting", back_populates="job_description", cascade="all, delete-orphan")


class JDVersion(Base):
    __tablename__ = "jd_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    jd_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    requirements = Column(JSON, nullable=True)  # Parsed requirements as JSONB
    admin_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    is_active = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    job_description = relationship("JobDescription", back_populates="versions", foreign_keys=[jd_id])
    admin = relationship("AdminUser", foreign_keys=[admin_id])

