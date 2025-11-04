"""
CRUD operations for quizzes
"""
from sqlalchemy.orm import Session
from app.db.quiz_models import Quiz
from typing import List, Optional
import uuid


def create_quiz(
    db: Session,
    user_id: str,
    notebook_id: Optional[str],
    title: str,
    topic: Optional[str],
    difficulty: Optional[str],
    questions: list
) -> Quiz:
    """Create a new quiz"""
    quiz = Quiz(
        id=str(uuid.uuid4()),
        user_id=user_id,
        notebook_id=notebook_id,
        title=title,
        topic=topic,
        difficulty=difficulty,
        questions=questions
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz


def get_quiz(db: Session, quiz_id: str, user_id: str) -> Optional[Quiz]:
    """Get a quiz by ID"""
    return db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.user_id == user_id
    ).first()


def get_quizzes_by_user(db: Session, user_id: str) -> List[Quiz]:
    """Get all quizzes for a user"""
    return db.query(Quiz).filter(
        Quiz.user_id == user_id
    ).order_by(Quiz.created_at.desc()).all()


def get_quizzes_by_notebook(db: Session, notebook_id: str, user_id: str) -> List[Quiz]:
    """Get all quizzes for a specific notebook"""
    return db.query(Quiz).filter(
        Quiz.notebook_id == notebook_id,
        Quiz.user_id == user_id
    ).order_by(Quiz.created_at.desc()).all()


def delete_quiz(db: Session, quiz_id: str, user_id: str) -> bool:
    """Delete a quiz"""
    quiz = get_quiz(db, quiz_id, user_id)
    if quiz:
        db.delete(quiz)
        db.commit()
        return True
    return False


def update_quiz(
    db: Session,
    quiz_id: str,
    user_id: str,
    title: Optional[str] = None,
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    questions: Optional[list] = None
) -> Optional[Quiz]:
    """Update a quiz"""
    quiz = get_quiz(db, quiz_id, user_id)
    if quiz:
        if title is not None:
            quiz.title = title
        if topic is not None:
            quiz.topic = topic
        if difficulty is not None:
            quiz.difficulty = difficulty
        if questions is not None:
            quiz.questions = questions
        db.commit()
        db.refresh(quiz)
    return quiz
