"""
CRUD operations for notebooks and documents
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import Notebook, Document
import uuid


def create_notebook(db: Session, user_id: str, title: str, description: Optional[str] = None) -> Notebook:
    """Create a new notebook"""
    notebook = Notebook(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title=title,
        description=description
    )
    db.add(notebook)
    db.commit()
    db.refresh(notebook)
    return notebook


def get_notebook(db: Session, notebook_id: str, user_id: str) -> Optional[Notebook]:
    """Get a notebook by ID (ensuring user ownership)"""
    return db.query(Notebook).filter(
        Notebook.id == notebook_id,
        Notebook.user_id == user_id
    ).first()


def get_notebooks_by_user(db: Session, user_id: str) -> List[Notebook]:
    """Get all notebooks for a user"""
    return db.query(Notebook).filter(
        Notebook.user_id == user_id
    ).order_by(Notebook.updated_at.desc()).all()


def update_notebook(db: Session, notebook_id: str, user_id: str, **kwargs) -> Optional[Notebook]:
    """Update notebook fields"""
    notebook = get_notebook(db, notebook_id, user_id)
    if notebook:
        for key, value in kwargs.items():
            if hasattr(notebook, key) and key not in ['id', 'user_id', 'created_at']:
                setattr(notebook, key, value)
        db.commit()
        db.refresh(notebook)
    return notebook


def delete_notebook(db: Session, notebook_id: str, user_id: str) -> bool:
    """Delete a notebook (cascades to documents)"""
    notebook = get_notebook(db, notebook_id, user_id)
    if notebook:
        db.delete(notebook)
        db.commit()
        return True
    return False


def create_document(
    db: Session,
    notebook_id: str,
    user_id: str,
    name: str,
    file_type: str,
    file_path: Optional[str] = None,
    file_size: Optional[int] = None,
    chunk_count: int = 0,
    content_hash: Optional[str] = None
) -> Document:
    """Create a new document"""
    document = Document(
        id=str(uuid.uuid4()),
        notebook_id=notebook_id,
        user_id=user_id,
        name=name,
        file_type=file_type,
        file_path=file_path,
        file_size=file_size,
        chunk_count=chunk_count,
        content_hash=content_hash
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def get_document(db: Session, document_id: str, user_id: str) -> Optional[Document]:
    """Get a document by ID (ensuring user ownership)"""
    return db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user_id
    ).first()


def get_documents_by_notebook(db: Session, notebook_id: str, user_id: str) -> List[Document]:
    """Get all documents for a notebook"""
    return db.query(Document).filter(
        Document.notebook_id == notebook_id,
        Document.user_id == user_id
    ).order_by(Document.created_at.desc()).all()


def update_document(db: Session, document_id: str, user_id: str, **kwargs) -> Optional[Document]:
    """Update document fields"""
    document = get_document(db, document_id, user_id)
    if document:
        for key, value in kwargs.items():
            if hasattr(document, key) and key not in ['id', 'user_id', 'notebook_id', 'created_at']:
                setattr(document, key, value)
        db.commit()
        db.refresh(document)
    return document


def delete_document(db: Session, document_id: str, user_id: str) -> bool:
    """Delete a document"""
    document = get_document(db, document_id, user_id)
    if document:
        db.delete(document)
        db.commit()
        return True
    return False
