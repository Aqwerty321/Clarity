"""
Database models for quizzes
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Quiz(Base):
    """Quiz model - represents a saved quiz"""
    __tablename__ = "quizzes"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    notebook_id = Column(String, ForeignKey("notebooks.id", ondelete="CASCADE"), nullable=True)
    title = Column(String, nullable=False)
    topic = Column(String, nullable=True)
    difficulty = Column(String, nullable=True)  # easy, medium, hard
    questions = Column(JSON, nullable=False)  # Store as JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    # Relationship to notebook
    notebook = relationship("Notebook", backref="quizzes")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "notebook_id": self.notebook_id,
            "title": self.title,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "questions": self.questions,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
