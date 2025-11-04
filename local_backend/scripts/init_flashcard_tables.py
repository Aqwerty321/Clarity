"""
Initialize flashcard tables
"""
from app.db import Base, engine
from app.db.flashcard_models import FlashcardDeck, FlashcardCard
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_flashcard_tables():
    """Create flashcard tables"""
    try:
        logger.info("Creating flashcard tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Flashcard tables created successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        return False

if __name__ == "__main__":
    init_flashcard_tables()
