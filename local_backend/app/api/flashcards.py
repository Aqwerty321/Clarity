"""
Flashcard API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging

from ..db.database import get_db
from ..db import flashcard_crud
from ..db.flashcard_models import FlashcardDeck, FlashcardCard
from ..services.llm_wrapper import llm_wrapper
from ..services.chroma_service import ChromaService
from ..services.embedder import Embedder

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
chroma_service = ChromaService()
embedder = Embedder()


# Pydantic models
class DeckCreate(BaseModel):
    user_id: str
    title: str
    description: Optional[str] = None
    notebook_id: Optional[str] = None
    generate_from_notebook: bool = False


class DeckUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class CardCreate(BaseModel):
    front: str
    back: str


class CardUpdate(BaseModel):
    front: Optional[str] = None
    back: Optional[str] = None


class CardRate(BaseModel):
    rating: str  # "again", "hard", "good", "easy"


# Deck endpoints
@router.get("/flashcard-decks")
async def get_decks(user_id: str, db: Session = Depends(get_db)):
    """Get all flashcard decks for a user"""
    try:
        decks = flashcard_crud.get_decks_by_user(db, user_id)
        return [deck.to_dict() for deck in decks]
    except Exception as e:
        logger.error(f"Failed to get decks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/flashcard-decks")
async def create_deck(deck: DeckCreate, db: Session = Depends(get_db)):
    """Create a new flashcard deck"""
    try:
        # Create the deck
        new_deck = flashcard_crud.create_deck(
            db=db,
            user_id=deck.user_id,
            title=deck.title,
            description=deck.description,
            notebook_id=deck.notebook_id
        )
        
        # Generate cards from notebook if requested
        if deck.generate_from_notebook and deck.notebook_id:
            await generate_cards_from_notebook(
                db=db,
                deck_id=new_deck.id,
                user_id=deck.user_id,
                notebook_id=deck.notebook_id
            )
            db.refresh(new_deck)
        
        logger.info(f"Created flashcard deck {new_deck.id} for user {deck.user_id}")
        return new_deck.to_dict()
    except Exception as e:
        logger.error(f"Failed to create deck: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flashcard-decks/{deck_id}")
async def get_deck(deck_id: str, user_id: str, db: Session = Depends(get_db)):
    """Get a specific flashcard deck"""
    deck = flashcard_crud.get_deck(db, deck_id, user_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return deck.to_dict()


@router.put("/flashcard-decks/{deck_id}")
async def update_deck(
    deck_id: str,
    user_id: str,
    deck_update: DeckUpdate,
    db: Session = Depends(get_db)
):
    """Update a flashcard deck"""
    deck = flashcard_crud.update_deck(
        db=db,
        deck_id=deck_id,
        user_id=user_id,
        title=deck_update.title,
        description=deck_update.description
    )
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    logger.info(f"Updated flashcard deck {deck_id}")
    return deck.to_dict()


@router.delete("/flashcard-decks/{deck_id}")
async def delete_deck(deck_id: str, user_id: str, db: Session = Depends(get_db)):
    """Delete a flashcard deck"""
    success = flashcard_crud.delete_deck(db, deck_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    logger.info(f"Deleted flashcard deck {deck_id}")
    return {"status": "success", "message": "Deck deleted"}


# Card endpoints
@router.get("/flashcard-decks/{deck_id}/cards")
async def get_cards(deck_id: str, user_id: str, db: Session = Depends(get_db)):
    """Get all cards in a deck"""
    try:
        # Verify deck exists
        deck = flashcard_crud.get_deck(db, deck_id, user_id)
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")
        
        cards = flashcard_crud.get_cards_by_deck(db, deck_id, user_id)
        return [card.to_dict() for card in cards]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get cards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flashcard-decks/{deck_id}/study")
async def get_study_cards(
    deck_id: str,
    user_id: str,
    limit: int = 20,
    practice_mode: bool = False,
    db: Session = Depends(get_db)
):
    """Get cards due for study (or all cards if practice_mode=True)"""
    try:
        # Verify deck exists
        deck = flashcard_crud.get_deck(db, deck_id, user_id)
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")
        
        cards = flashcard_crud.get_due_cards(db, deck_id, user_id, limit, practice_mode)
        return [card.to_dict() for card in cards]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get study cards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/flashcard-decks/{deck_id}/generate")
async def generate_cards_for_deck(
    deck_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Generate flashcards from the deck's linked notebook"""
    try:
        # Verify deck exists and has a notebook
        deck = flashcard_crud.get_deck(db, deck_id, user_id)
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")
        
        if not deck.notebook_id:
            raise HTTPException(status_code=400, detail="Deck is not linked to a notebook")
        
        # Generate cards
        await generate_cards_from_notebook(
            db=db,
            deck_id=deck_id,
            user_id=user_id,
            notebook_id=deck.notebook_id
        )
        
        # Get updated card count
        cards = flashcard_crud.get_cards_by_deck(db, deck_id, user_id)
        
        logger.info(f"Generated flashcards for deck {deck_id}, total cards: {len(cards)}")
        return {"status": "success", "count": len(cards), "message": "Flashcards generated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate cards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/flashcard-decks/{deck_id}/cards")
async def create_card(
    deck_id: str,
    user_id: str,
    card: CardCreate,
    db: Session = Depends(get_db)
):
    """Create a new flashcard"""
    try:
        # Verify deck exists
        deck = flashcard_crud.get_deck(db, deck_id, user_id)
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")
        
        new_card = flashcard_crud.create_card(
            db=db,
            deck_id=deck_id,
            user_id=user_id,
            front=card.front,
            back=card.back
        )
        
        logger.info(f"Created flashcard {new_card.id} in deck {deck_id}")
        return new_card.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create card: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/flashcard-cards/{card_id}")
async def update_card(
    card_id: str,
    user_id: str,
    card_update: CardUpdate,
    db: Session = Depends(get_db)
):
    """Update a flashcard"""
    card = flashcard_crud.update_card(
        db=db,
        card_id=card_id,
        user_id=user_id,
        front=card_update.front,
        back=card_update.back
    )
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    logger.info(f"Updated flashcard {card_id}")
    return card.to_dict()


@router.post("/flashcard-cards/{card_id}/rate")
async def rate_card(
    card_id: str,
    user_id: str,
    rating: CardRate,
    db: Session = Depends(get_db)
):
    """Rate a flashcard (spaced repetition)"""
    card = flashcard_crud.rate_card(db, card_id, user_id, rating.rating)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    logger.info(f"Rated flashcard {card_id} as {rating.rating}")
    return card.to_dict()


@router.delete("/flashcard-cards/{card_id}")
async def delete_card(card_id: str, user_id: str, db: Session = Depends(get_db)):
    """Delete a flashcard"""
    success = flashcard_crud.delete_card(db, card_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Card not found")
    
    logger.info(f"Deleted flashcard {card_id}")
    return {"status": "success", "message": "Card deleted"}


# Helper function to generate cards from notebook
async def generate_cards_from_notebook(
    db: Session,
    deck_id: str,
    user_id: str,
    notebook_id: str
):
    """Generate flashcards from notebook content using LLM"""
    try:
        # Get relevant context from ChromaDB
        collection_id = f"{user_id.replace('|', '_')}__{notebook_id}"
        
        # Query for all documents (using dummy embedding)
        results = chroma_service.query(
            user_id=collection_id,
            query_embedding=[0.0] * 768,  # Dummy query
            top_k=10
        )
        
        if not results.get("documents"):
            logger.warning(f"No documents found for notebook {notebook_id}")
            return
        
        # Combine context
        context = "\n\n".join(results["documents"][:5])
        
        # Generate flashcards using LLM
        prompt = f"""Generate 10 flashcards from the following content. Each flashcard should have a front (question) and back (answer).

Content:
{context}

Output ONLY valid JSON in this format:
{{
  "cards": [
    {{
      "front": "Question here?",
      "back": "Answer here"
    }}
  ]
}}

Rules:
- Generate exactly 10 flashcards
- Questions should test understanding, not just memorization
- Answers should be concise but complete
- Cover different topics from the content
- Output ONLY the JSON, no markdown, no code blocks, no extra text"""
        
        response = llm_wrapper.llm.generate(prompt, max_tokens=2000, temperature=0.7)
        
        # Parse JSON response
        import json
        import re
        
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            # Create flashcards
            for card_data in data.get("cards", []):
                flashcard_crud.create_card(
                    db=db,
                    deck_id=deck_id,
                    user_id=user_id,
                    front=card_data["front"],
                    back=card_data["back"]
                )
            
            logger.info(f"Generated {len(data.get('cards', []))} flashcards for deck {deck_id}")
        else:
            logger.error("Failed to parse LLM response for flashcard generation")
            
    except Exception as e:
        logger.error(f"Failed to generate flashcards from notebook: {e}")
        raise
