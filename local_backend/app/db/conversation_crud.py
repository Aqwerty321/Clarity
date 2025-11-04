"""CRUD operations for notebook conversations"""
from sqlalchemy.orm import Session
from typing import List
import uuid
import json
from .conversation_models import NotebookConversation


def create_conversation(
    db: Session,
    notebook_id: str,
    user_id: str,
    question: str,
    answer: str,
    sources: list = None,
    used_summary: bool = False
) -> NotebookConversation:
    """Create a new conversation entry"""
    conversation = NotebookConversation(
        id=str(uuid.uuid4()),
        notebook_id=notebook_id,
        user_id=user_id,
        question=question,
        answer=answer,
        sources=json.dumps(sources) if sources else None,
        used_summary=1 if used_summary else 0
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_conversations_by_notebook(
    db: Session,
    notebook_id: str,
    user_id: str,
    limit: int = 50
) -> List[NotebookConversation]:
    """Get all conversations for a notebook"""
    return db.query(NotebookConversation).filter(
        NotebookConversation.notebook_id == notebook_id,
        NotebookConversation.user_id == user_id
    ).order_by(NotebookConversation.created_at.desc()).limit(limit).all()


def delete_conversation(db: Session, conversation_id: str, user_id: str) -> bool:
    """Delete a conversation"""
    conversation = db.query(NotebookConversation).filter(
        NotebookConversation.id == conversation_id,
        NotebookConversation.user_id == user_id
    ).first()
    
    if conversation:
        db.delete(conversation)
        db.commit()
        return True
    return False


def clear_notebook_conversations(db: Session, notebook_id: str, user_id: str) -> int:
    """Clear all conversations for a notebook"""
    count = db.query(NotebookConversation).filter(
        NotebookConversation.notebook_id == notebook_id,
        NotebookConversation.user_id == user_id
    ).delete()
    db.commit()
    return count
