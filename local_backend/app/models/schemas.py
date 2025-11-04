from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class DocumentIngestRequest(BaseModel):
    """Request model for document ingestion"""
    title: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    user_id: str = Field(..., description="Auth0 user ID")


class DocumentIngestResponse(BaseModel):
    """Response model for document ingestion"""
    document_id: str
    title: str
    num_chunks: int
    status: str = "success"
    message: Optional[str] = None


class EmbedRequest(BaseModel):
    """Request model for embedding generation"""
    texts: List[str] = Field(..., description="List of texts to embed")


class EmbedResponse(BaseModel):
    """Response model for embedding generation"""
    embeddings: List[List[float]]
    model: str
    dimension: int


class SourceChunk(BaseModel):
    """A retrieved source chunk with relevance score"""
    id: str
    text: str
    score: float
    metadata: Optional[Dict[str, Any]] = None


class AskRequest(BaseModel):
    """Request model for RAG question answering"""
    user_id: str = Field(..., description="Auth0 user ID")
    notebook_id: Optional[str] = Field(None, description="Notebook ID to query (if None, queries all notebooks)")
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=4, ge=1, le=20)
    use_summary: bool = Field(default=True)


class AskResponse(BaseModel):
    """Response model for RAG question answering"""
    answer: str
    source_chunks: List[SourceChunk]
    used_prompt: Optional[str] = None
    model: Optional[str] = None


class QuizQuestion(BaseModel):
    """A single quiz question"""
    question: str
    options: List[str]
    correct_answer: Optional[int] = None
    explanation: Optional[str] = None
    hint: Optional[str] = None
    incorrect_explanations: Optional[List[str]] = None


class GenerateQuizRequest(BaseModel):
    """Request model for quiz generation"""
    user_id: str
    notebook_id: Optional[str] = Field(None, description="Notebook ID to generate quiz from (if None, uses all notebooks)")
    topic: str
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    num_questions: int = Field(default=5, ge=1, le=20)


class GenerateQuizResponse(BaseModel):
    """Response model for quiz generation"""
    title: str
    questions: List[QuizQuestion]
    topic: str
    difficulty: str


class SyncPushRequest(BaseModel):
    """Request model for pushing local state to cloud"""
    user_id: str
    notebooks: List[Dict[str, Any]]
    last_sync: Optional[datetime] = None


class SyncPushResponse(BaseModel):
    """Response model for sync push"""
    status: str
    synced_count: int
    conflicts: List[Dict[str, Any]] = []


class SyncPullResponse(BaseModel):
    """Response model for sync pull"""
    notebooks: List[Dict[str, Any]]
    last_sync: datetime


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    embedder_model: str
    llm_model: str
    chroma_collections: int


class NotebookCreate(BaseModel):
    """Request model for creating a notebook"""
    user_id: str
    title: str
    description: Optional[str] = None


class NotebookUpdate(BaseModel):
    """Request model for updating a notebook"""
    user_id: str
    title: Optional[str] = None
    description: Optional[str] = None


class NotebookResponse(BaseModel):
    """Response model for notebook"""
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    documentCount: int
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class DocumentResponse(BaseModel):
    """Response model for document"""
    id: str
    notebook_id: str
    name: str
    file_type: str
    file_size: Optional[int] = None
    chunkCount: int
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
