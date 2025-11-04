"""Models for storing notebook conversation history"""
from sqlalchemy import Column, String, Text, DateTime, Integer
from datetime import datetime
from .database import Base


class NotebookConversation(Base):
    """Store question-answer pairs for notebooks"""
    __tablename__ = "notebook_conversations"
    
    id = Column(String, primary_key=True)
    notebook_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(Text, nullable=True)  # JSON string of sources
    used_summary = Column(Integer, default=0)  # Boolean as int
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        import json
        return {
            "id": self.id,
            "notebookId": self.notebook_id,
            "userId": self.user_id,
            "question": self.question,
            "answer": self.answer,
            "sources": json.loads(self.sources) if self.sources else [],
            "usedSummary": bool(self.used_summary),
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
