from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import bcrypt
from app.db.database import Base


class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    job_descriptions = relationship("JobDescription", back_populates="admin")
    admin_settings = relationship("AdminSetting", back_populates="admin")
    audit_logs = relationship("AuditLog", back_populates="admin")
    
    def set_password(self, password: str):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hashed password"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))
        except Exception:
            return False


class AdminSetting(Base):
    __tablename__ = "admin_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    jd_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=True, index=True)  # null = global
    setting_name = Column(String, nullable=False, index=True)
    setting_value = Column(JSON, nullable=False)  # Setting value as JSONB
    admin_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    job_description = relationship("JobDescription", back_populates="admin_settings")
    admin = relationship("AdminUser", back_populates="admin_settings")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False, index=True)
    action_type = Column(String, nullable=False, index=True)  # create, update, delete, etc.
    resource_type = Column(String, nullable=False, index=True)  # jd, setting, etc.
    resource_id = Column(Integer, nullable=True)
    changes = Column(JSON, nullable=True)  # What changed
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    admin = relationship("AdminUser", back_populates="audit_logs")

