"""
Flashcard database models
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .database import Base


class FlashcardDeck(Base):
    """Flashcard deck model"""
    __tablename__ = "flashcard_decks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    notebook_id = Column(String, ForeignKey("notebooks.id", ondelete="SET NULL"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cards = relationship("FlashcardCard", back_populates="deck", cascade="all, delete-orphan")
    notebook = relationship("Notebook", foreign_keys=[notebook_id])
    
    def to_dict(self):
        """Convert to dictionary"""
        new_cards = sum(1 for card in self.cards if card.is_new())
        review_cards = sum(1 for card in self.cards if card.is_due())
        mastered_cards = sum(1 for card in self.cards if card.ease_factor >= 2.5 and card.interval >= 21)
        
        return {
            "id": self.id,
            "userId": self.user_id,
            "notebookId": self.notebook_id,
            "title": self.title,
            "description": self.description,
            "cardCount": len(self.cards),
            "newCards": new_cards,
            "reviewCards": review_cards,
            "masteredCards": mastered_cards,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }


class FlashcardCard(Base):
    """Flashcard card model with spaced repetition"""
    __tablename__ = "flashcard_cards"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    deck_id = Column(String, ForeignKey("flashcard_decks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, nullable=False, index=True)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    
    # Spaced repetition (SM-2 algorithm)
    ease_factor = Column(Float, default=2.5)  # Difficulty multiplier
    interval = Column(Integer, default=0)  # Days until next review
    repetitions = Column(Integer, default=0)  # Number of successful reviews
    next_review = Column(DateTime, default=datetime.utcnow)  # Next review date
    last_reviewed = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    deck = relationship("FlashcardDeck", back_populates="cards")
    
    def is_new(self):
        """Check if card is new (never reviewed)"""
        return self.repetitions == 0
    
    def is_due(self):
        """Check if card is due for review"""
        return self.next_review <= datetime.utcnow()
    
    def is_mastered(self):
        """Check if card is mastered (high ease, long interval, multiple reviews)"""
        return (self.repetitions >= 3 and 
                self.ease_factor >= 2.5 and 
                self.interval >= 7)
    
    def update_sm2(self, quality: int):
        """
        Update card using SM-2 algorithm
        quality: 0-5 (0=again, 3=hard, 4=good, 5=easy)
        """
        from datetime import timedelta
        
        # Map button names to quality
        # again=0, hard=3, good=4, easy=5
        
        if quality >= 3:
            # Correct response
            if self.repetitions == 0:
                self.interval = 1
            elif self.repetitions == 1:
                self.interval = 6
            else:
                self.interval = round(self.interval * self.ease_factor)
            
            self.repetitions += 1
        else:
            # Incorrect response
            self.repetitions = 0
            self.interval = 1
        
        # Update ease factor
        self.ease_factor = max(1.3, self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        
        # Set next review date
        self.next_review = datetime.utcnow() + timedelta(days=self.interval)
        self.last_reviewed = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "deckId": self.deck_id,
            "userId": self.user_id,
            "front": self.front,
            "back": self.back,
            "easeFactor": self.ease_factor,
            "interval": self.interval,
            "repetitions": self.repetitions,
            "nextReview": self.next_review.isoformat() if self.next_review else None,
            "lastReviewed": self.last_reviewed.isoformat() if self.last_reviewed else None,
            "isNew": self.is_new(),
            "isDue": self.is_due(),
            "isMastered": self.is_mastered(),
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
