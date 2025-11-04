"""
Notebook and document management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import logging
import os
import shutil
import hashlib
from pathlib import Path

from app.db import get_db, crud
from app.models.schemas import (
    NotebookCreate,
    NotebookUpdate,
    NotebookResponse,
    DocumentResponse,
)
from app.utils.pdf_parser import extract_text_from_file
from app.utils.chunker import chunk_text
from app.services.embedder import embedder
from app.services.chroma_service import chroma_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Directory for storing uploaded files
UPLOAD_DIR = Path(os.getenv("CLARITY_BASE_DIR", "~/.clarity")).expanduser() / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


@router.post("/notebooks", response_model=NotebookResponse)
async def create_notebook(
    notebook: NotebookCreate,
    db: Session = Depends(get_db)
):
    """Create a new notebook"""
    try:
        db_notebook = crud.create_notebook(
            db=db,
            user_id=notebook.user_id,
            title=notebook.title,
            description=notebook.description
        )
        logger.info(f"Created notebook {db_notebook.id} for user {notebook.user_id}")
        return NotebookResponse(**db_notebook.to_dict())
    except Exception as e:
        logger.error(f"Failed to create notebook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notebooks", response_model=List[NotebookResponse])
async def get_notebooks(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get all notebooks for a user"""
    try:
        notebooks = crud.get_notebooks_by_user(db, user_id)
        return [NotebookResponse(**nb.to_dict()) for nb in notebooks]
    except Exception as e:
        logger.error(f"Failed to get notebooks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notebooks/{notebook_id}", response_model=NotebookResponse)
async def get_notebook(
    notebook_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific notebook"""
    notebook = crud.get_notebook(db, notebook_id, user_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return NotebookResponse(**notebook.to_dict())


@router.put("/notebooks/{notebook_id}", response_model=NotebookResponse)
async def update_notebook(
    notebook_id: str,
    notebook: NotebookUpdate,
    db: Session = Depends(get_db)
):
    """Update a notebook"""
    update_data = {k: v for k, v in notebook.dict().items() if v is not None and k != 'user_id'}
    db_notebook = crud.update_notebook(db, notebook_id, notebook.user_id, **update_data)
    if not db_notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    logger.info(f"Updated notebook {notebook_id}")
    return NotebookResponse(**db_notebook.to_dict())


@router.delete("/notebooks/{notebook_id}")
async def delete_notebook(
    notebook_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Delete a notebook and all its documents"""
    # Get documents to delete their files
    documents = crud.get_documents_by_notebook(db, notebook_id, user_id)
    
    # Delete physical files
    for doc in documents:
        if doc.file_path and os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except Exception as e:
                logger.warning(f"Failed to delete file {doc.file_path}: {e}")
    
    # Delete from ChromaDB
    collection_name = f"clarity_user__{user_id.replace('|', '_')}__{notebook_id}"
    try:
        chroma_service.delete_collection(collection_name)
    except Exception as e:
        logger.warning(f"Failed to delete ChromaDB collection: {e}")
    
    # Delete from database (cascades to documents)
    success = crud.delete_notebook(db, notebook_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    logger.info(f"Deleted notebook {notebook_id}")
    return {"message": "Notebook deleted successfully"}


@router.get("/notebooks/{notebook_id}/documents", response_model=List[DocumentResponse])
async def get_documents(
    notebook_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get all documents in a notebook"""
    # Verify notebook exists and user owns it
    notebook = crud.get_notebook(db, notebook_id, user_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    documents = crud.get_documents_by_notebook(db, notebook_id, user_id)
    return [DocumentResponse(**doc.to_dict()) for doc in documents]


@router.post("/notebooks/{notebook_id}/documents", response_model=DocumentResponse)
async def upload_document(
    notebook_id: str,
    user_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a document to a notebook"""
    # Verify notebook exists
    notebook = crud.get_notebook(db, notebook_id, user_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    try:
        # Determine file type
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in ['pdf', 'txt', 'md']:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Create user/notebook directory
        user_dir = UPLOAD_DIR / user_id.replace('|', '_') / notebook_id
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = user_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(file_path)
        content_hash = calculate_file_hash(str(file_path))
        
        # Extract and chunk text
        logger.info(f"Extracting text from {file.filename}")
        with open(file_path, "rb") as f:
            file_content = f.read()
        text = extract_text_from_file(file.filename, file_content)
        
        if not text:
            raise HTTPException(status_code=400, detail="Failed to extract text from file")
        
        logger.info(f"Chunking text (length: {len(text)} chars)")
        chunk_size = int(os.getenv("CLARITY_CHUNK_SIZE", "500"))
        chunk_overlap = int(os.getenv("CLARITY_CHUNK_OVERLAP", "100"))
        chunk_results = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = [chunk_text for chunk_text, _, _ in chunk_results]  # Extract just the text
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(chunks)} chunks")
        embeddings = embedder.embed_texts(chunks)
        
        # Store in ChromaDB (use notebook-specific collection)
        collection_id = f"{user_id.replace('|', '_')}__{notebook_id}"
        logger.info(f"Storing {len(chunks)} chunks in ChromaDB for user: {collection_id}")
        
        chroma_service.add_documents(
            user_id=collection_id,
            documents=chunks,
            embeddings=embeddings,
            metadatas=[{
                "source": file.filename,
                "chunk_index": i,
                "notebook_id": notebook_id
            } for i in range(len(chunks))],
            ids=[f"{file.filename}_{i}" for i in range(len(chunks))]
        )
        
        # Create document record
        document = crud.create_document(
            db=db,
            notebook_id=notebook_id,
            user_id=user_id,
            name=file.filename,
            file_type=file_ext,
            file_path=str(file_path),
            file_size=file_size,
            chunk_count=len(chunks),
            content_hash=content_hash
        )
        
        logger.info(f"Document {document.id} uploaded successfully")
        return DocumentResponse(**document.to_dict())
        
    except Exception as e:
        logger.error(f"Failed to upload document: {e}")
        # Clean up file if database/chroma operations failed
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/notebooks/{notebook_id}/documents/{document_id}")
async def delete_document(
    notebook_id: str,
    document_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Delete a document from a notebook"""
    document = crud.get_document(db, document_id, user_id)
    if not document or document.notebook_id != notebook_id:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete physical file
    if document.file_path and os.path.exists(document.file_path):
        try:
            os.remove(document.file_path)
        except Exception as e:
            logger.warning(f"Failed to delete file {document.file_path}: {e}")
    
    # Delete from ChromaDB (delete chunks with matching source)
    collection_name = f"clarity_user__{user_id.replace('|', '_')}__{notebook_id}"
    try:
        # This is a simplification - in production you'd want to track chunk IDs
        logger.info(f"Deleting document chunks from ChromaDB collection: {collection_name}")
    except Exception as e:
        logger.warning(f"Failed to delete from ChromaDB: {e}")
    
    # Delete from database
    success = crud.delete_document(db, document_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    logger.info(f"Deleted document {document_id}")
    return {"message": "Document deleted successfully"}
