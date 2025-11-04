"""
Mind map database models
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .database import Base


class MindMap(Base):
    __tablename__ = "mind_maps"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    notebook_id = Column(String, ForeignKey("notebooks.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    max_depth = Column(Integer, default=3)
    node_count = Column(Integer, default=0)
    depth = Column(Integer, default=0)
    nodes = Column(JSON, default=list)  # List of node objects
    edges = Column(JSON, default=list)  # List of edge objects
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    notebook = relationship("Notebook", back_populates="mind_maps")
