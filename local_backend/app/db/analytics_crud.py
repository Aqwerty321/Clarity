import uuid
from sqlalchemy.orm import Session
from app.db.analytics_models import QuizAttempt, FlashcardAttempt, TopicMapping


# Quiz Attempts
def create_quiz_attempt(
    db: Session,
    user_id: str,
    quiz_id: str,
    notebook_id: str,
    topic: str,
    difficulty: str,
    answers: dict,
    score: float,
    correct_count: int,
    total_questions: int,
    normalized_topic: str = None
):
    """Create a new quiz attempt record"""
    attempt = QuizAttempt(
        id=str(uuid.uuid4()),
        user_id=user_id,
        quiz_id=quiz_id,
        notebook_id=notebook_id,
        topic=topic,
        normalized_topic=normalized_topic or topic,
        difficulty=difficulty,
        answers=answers,
        score=score,
        correct_count=correct_count,
        total_questions=total_questions
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def get_quiz_attempts_by_user(db: Session, user_id: str, notebook_id: str = None):
    """Get all quiz attempts for a user, optionally filtered by notebook"""
    query = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id)
    if notebook_id:
        query = query.filter(QuizAttempt.notebook_id == notebook_id)
    return query.order_by(QuizAttempt.attempted_at.desc()).all()


# Flashcard Attempts
def create_flashcard_attempt(
    db: Session,
    user_id: str,
    deck_id: str,
    card_id: str,
    notebook_id: str,
    topic: str,
    quality: int,
    was_correct: bool,
    normalized_topic: str = None
):
    """Create a new flashcard attempt record"""
    attempt = FlashcardAttempt(
        id=str(uuid.uuid4()),
        user_id=user_id,
        deck_id=deck_id,
        card_id=card_id,
        notebook_id=notebook_id,
        topic=topic,
        normalized_topic=normalized_topic or topic,
        quality=quality,
        was_correct=was_correct
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def get_flashcard_attempts_by_user(db: Session, user_id: str, notebook_id: str = None):
    """Get all flashcard attempts for a user, optionally filtered by notebook"""
    query = db.query(FlashcardAttempt).filter(FlashcardAttempt.user_id == user_id)
    if notebook_id:
        query = query.filter(FlashcardAttempt.notebook_id == notebook_id)
    return query.order_by(FlashcardAttempt.reviewed_at.desc()).all()


# Topic Mappings
def get_or_create_topic_mapping(db: Session, user_id: str, original_topic: str, normalized_topic: str):
    """Get existing mapping or create new one"""
    mapping = db.query(TopicMapping).filter(
        TopicMapping.user_id == user_id,
        TopicMapping.original_topic == original_topic
    ).first()
    
    if not mapping:
        mapping = TopicMapping(
            id=str(uuid.uuid4()),
            user_id=user_id,
            original_topic=original_topic,
            normalized_topic=normalized_topic
        )
        db.add(mapping)
        db.commit()
        db.refresh(mapping)
    
    return mapping


def get_topic_mappings(db: Session, user_id: str):
    """Get all topic mappings for a user"""
    return db.query(TopicMapping).filter(TopicMapping.user_id == user_id).all()


def update_normalized_topic(db: Session, user_id: str, original_topic: str, normalized_topic: str):
    """Update normalized topic for existing attempts"""
    # Update quiz attempts
    db.query(QuizAttempt).filter(
        QuizAttempt.user_id == user_id,
        QuizAttempt.topic == original_topic
    ).update({"normalized_topic": normalized_topic})
    
    # Update flashcard attempts
    db.query(FlashcardAttempt).filter(
        FlashcardAttempt.user_id == user_id,
        FlashcardAttempt.topic == original_topic
    ).update({"normalized_topic": normalized_topic})
    
    db.commit()
