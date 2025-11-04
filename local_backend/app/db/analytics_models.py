from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Boolean, Float
from sqlalchemy.sql import func
from app.db.models import Base

class QuizAttempt(Base):
    """Track individual quiz attempts for analytics"""
    __tablename__ = "quiz_attempts"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    quiz_id = Column(String, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    notebook_id = Column(String, ForeignKey("notebooks.id", ondelete="CASCADE"), nullable=True)
    
    # Quiz metadata
    topic = Column(String, nullable=True)
    normalized_topic = Column(String, nullable=True, index=True)  # AI-normalized topic
    difficulty = Column(String, nullable=True)
    
    # Attempt data
    answers = Column(JSON, nullable=False)  # User's answers
    score = Column(Float, nullable=False)  # Percentage score
    correct_count = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    
    # Timestamps
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'quiz_id': self.quiz_id,
            'notebook_id': self.notebook_id,
            'topic': self.topic,
            'normalized_topic': self.normalized_topic,
            'difficulty': self.difficulty,
            'answers': self.answers,
            'score': self.score,
            'correct_count': self.correct_count,
            'total_questions': self.total_questions,
            'attempted_at': self.attempted_at.isoformat() if self.attempted_at else None,
        }


class FlashcardAttempt(Base):
    """Track individual flashcard reviews for analytics"""
    __tablename__ = "flashcard_attempts"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    deck_id = Column(String, ForeignKey("flashcard_decks.id", ondelete="CASCADE"), nullable=False)
    card_id = Column(String, nullable=False)  # ID of the specific card
    notebook_id = Column(String, ForeignKey("notebooks.id", ondelete="CASCADE"), nullable=True)
    
    # Card metadata
    topic = Column(String, nullable=True)  # Extracted from deck or card
    normalized_topic = Column(String, nullable=True, index=True)  # AI-normalized
    
    # Review data
    quality = Column(Integer, nullable=False)  # 0-5 rating (SM-2 algorithm compatible)
    was_correct = Column(Boolean, nullable=False)  # Simple correct/incorrect
    
    # Timestamps
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'deck_id': self.deck_id,
            'card_id': self.card_id,
            'notebook_id': self.notebook_id,
            'topic': self.topic,
            'normalized_topic': self.normalized_topic,
            'quality': self.quality,
            'was_correct': self.was_correct,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
        }


class TopicMapping(Base):
    """Cache for AI-normalized topic mappings"""
    __tablename__ = "topic_mappings"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    original_topic = Column(String, nullable=False, index=True)
    normalized_topic = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_topic': self.original_topic,
            'normalized_topic': self.normalized_topic,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
