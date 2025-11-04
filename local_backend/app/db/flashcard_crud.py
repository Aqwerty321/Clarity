"""
CRUD operations for flashcards
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from .flashcard_models import FlashcardDeck, FlashcardCard


# Deck CRUD
def create_deck(
    db: Session,
    user_id: str,
    title: str,
    description: Optional[str] = None,
    notebook_id: Optional[str] = None
) -> FlashcardDeck:
    """Create a new flashcard deck"""
    deck = FlashcardDeck(
        user_id=user_id,
        title=title,
        description=description,
        notebook_id=notebook_id
    )
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return deck


def get_deck(db: Session, deck_id: str, user_id: str) -> Optional[FlashcardDeck]:
    """Get a flashcard deck by ID"""
    return db.query(FlashcardDeck).filter(
        FlashcardDeck.id == deck_id,
        FlashcardDeck.user_id == user_id
    ).first()


def get_decks_by_user(db: Session, user_id: str) -> List[FlashcardDeck]:
    """Get all flashcard decks for a user"""
    return db.query(FlashcardDeck).filter(
        FlashcardDeck.user_id == user_id
    ).order_by(FlashcardDeck.updated_at.desc()).all()


def update_deck(
    db: Session,
    deck_id: str,
    user_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Optional[FlashcardDeck]:
    """Update a flashcard deck"""
    deck = get_deck(db, deck_id, user_id)
    if not deck:
        return None
    
    if title is not None:
        deck.title = title
    if description is not None:
        deck.description = description
    
    deck.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(deck)
    return deck


def delete_deck(db: Session, deck_id: str, user_id: str) -> bool:
    """Delete a flashcard deck"""
    deck = get_deck(db, deck_id, user_id)
    if not deck:
        return False
    
    db.delete(deck)
    db.commit()
    return True


# Card CRUD
def create_card(
    db: Session,
    deck_id: str,
    user_id: str,
    front: str,
    back: str
) -> FlashcardCard:
    """Create a new flashcard"""
    card = FlashcardCard(
        deck_id=deck_id,
        user_id=user_id,
        front=front,
        back=back
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


def get_card(db: Session, card_id: str, user_id: str) -> Optional[FlashcardCard]:
    """Get a flashcard by ID"""
    return db.query(FlashcardCard).filter(
        FlashcardCard.id == card_id,
        FlashcardCard.user_id == user_id
    ).first()


def get_cards_by_deck(db: Session, deck_id: str, user_id: str) -> List[FlashcardCard]:
    """Get all flashcards in a deck"""
    return db.query(FlashcardCard).filter(
        FlashcardCard.deck_id == deck_id,
        FlashcardCard.user_id == user_id
    ).order_by(FlashcardCard.created_at.desc()).all()


def get_due_cards(db: Session, deck_id: str, user_id: str, limit: int = 20, practice_mode: bool = False) -> List[FlashcardCard]:
    """Get cards due for review (or all cards if practice_mode=True)"""
    query = db.query(FlashcardCard).filter(
        FlashcardCard.deck_id == deck_id,
        FlashcardCard.user_id == user_id
    )
    
    # In practice mode, show all cards. Otherwise only show due cards
    if not practice_mode:
        query = query.filter(FlashcardCard.next_review <= datetime.utcnow())
    
    return query.order_by(FlashcardCard.next_review.asc()).limit(limit).all()


def update_card(
    db: Session,
    card_id: str,
    user_id: str,
    front: Optional[str] = None,
    back: Optional[str] = None
) -> Optional[FlashcardCard]:
    """Update a flashcard"""
    card = get_card(db, card_id, user_id)
    if not card:
        return None
    
    if front is not None:
        card.front = front
    if back is not None:
        card.back = back
    
    card.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(card)
    return card


def rate_card(db: Session, card_id: str, user_id: str, rating: str) -> Optional[FlashcardCard]:
    """Rate a flashcard (again, hard, good, easy)"""
    card = get_card(db, card_id, user_id)
    if not card:
        return None
    
    # Map rating to SM-2 quality (0-5)
    quality_map = {
        "again": 0,
        "hard": 3,
        "good": 4,
        "easy": 5
    }
    
    quality = quality_map.get(rating, 4)
    card.update_sm2(quality)
    
    db.commit()
    db.refresh(card)
    return card


def delete_card(db: Session, card_id: str, user_id: str) -> bool:
    """Delete a flashcard"""
    card = get_card(db, card_id, user_id)
    if not card:
        return False
    
    db.delete(card)
    db.commit()
    return True
