"""
Database models for Render sync backend
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    auth0_sub = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    notebooks = relationship("Notebook", back_populates="user", cascade="all, delete-orphan")
    sync_logs = relationship("SyncLog", back_populates="user", cascade="all, delete-orphan")


class Notebook(Base):
    """Notebook model"""
    __tablename__ = "notebooks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(500))
    metadata = Column(JSON, default=dict)
    content_snapshot = Column(JSON, default=dict)
    last_sync = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notebooks")


class SyncLog(Base):
    """Sync log model for tracking sync history"""
    __tablename__ = "sync_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50))  # 'push', 'pull', 'conflict'
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, default=dict)
    
    # Relationships
    user = relationship("User", back_populates="sync_logs")
