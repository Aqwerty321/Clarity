"""
Database models for notebooks and documents
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Notebook(Base):
    """Notebook model - represents a collection of documents"""
    __tablename__ = "notebooks"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    # Relationships
    documents = relationship("Document", back_populates="notebook", cascade="all, delete-orphan")
    mind_maps = relationship("MindMap", back_populates="notebook", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "documentCount": len(self.documents) if self.documents else 0,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }


class Document(Base):
    """Document model - represents a file uploaded to a notebook"""
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    notebook_id = Column(String, ForeignKey("notebooks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    file_path = Column(String, nullable=True)  # Local file system path
    file_type = Column(String, nullable=False)  # pdf, txt, md
    file_size = Column(Integer, nullable=True)  # Size in bytes
    chunk_count = Column(Integer, default=0)
    content_hash = Column(String, nullable=True)  # For deduplication
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    # Relationship to notebook
    notebook = relationship("Notebook", back_populates="documents")

    def to_dict(self):
        return {
            "id": self.id,
            "notebook_id": self.notebook_id,
            "name": self.name,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "chunkCount": self.chunk_count,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
