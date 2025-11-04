"""
Minimal Sync Service for Clarity
Handles ONLY metadata sync and backup - NO AI processing
"""
import os
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging
import jwt
from jwt.algorithms import RSAAlgorithm
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "").replace("postgres://", "postgresql://")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Auth0 configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE")
security = HTTPBearer()

# Database Models
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)  # Auth0 user ID
    email = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_sync = Column(DateTime, default=datetime.utcnow)

class NotebookSync(Base):
    __tablename__ = "notebook_sync"
    id = Column(String, primary_key=True)
    user_id = Column(String, index=True)
    title = Column(String)
    content = Column(Text)  # Markdown text only, NO vectors
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    device_id = Column(String)  # Track which device last updated

class ConversationSync(Base):
    __tablename__ = "conversation_sync"
    id = Column(String, primary_key=True)
    user_id = Column(String, index=True)
    notebook_id = Column(String)
    question = Column(Text)
    answer = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserSettings(Base):
    __tablename__ = "user_settings"
    user_id = Column(String, primary_key=True)
    settings_json = Column(Text)  # JSON string of user preferences
    updated_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title="Clarity Sync Service",
    description="Minimal sync service for metadata and backups - NO AI processing",
    version="1.0.0"
)

# CORS
cors_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:4173",
]
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth0 token verification
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Auth0 JWT token"""
    token = credentials.credentials
    
    try:
        # Get Auth0 public key
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        jwks = requests.get(jwks_url).json()
        
        # Decode token header to get kid
        unverified_header = jwt.get_unverified_header(token)
        
        # Find the right key
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        
        if not rsa_key:
            raise HTTPException(status_code=401, detail="Unable to find appropriate key")
        
        # Verify token
        public_key = RSAAlgorithm.from_jwk(rsa_key)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=AUTH0_API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        
        return payload
    
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Pydantic models
class NotebookSyncRequest(BaseModel):
    id: str
    title: str
    content: str
    device_id: str

class ConversationSyncRequest(BaseModel):
    id: str
    notebook_id: str
    question: str
    answer: str

class SettingsSyncRequest(BaseModel):
    settings_json: str

# Health check
@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "sync",
        "message": "Clarity Sync Service - Metadata & Backup Only (No AI Processing)",
        "timestamp": datetime.utcnow().isoformat()
    }

# Sync status
@app.get("/api/sync/status")
def get_sync_status(
    user_info: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get user's last sync status"""
    user_id = user_info["sub"]
    
    # Get or create user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, email=user_info.get("email", ""))
        db.add(user)
        db.commit()
    
    # Count synced items
    notebook_count = db.query(NotebookSync).filter(NotebookSync.user_id == user_id).count()
    conversation_count = db.query(ConversationSync).filter(ConversationSync.user_id == user_id).count()
    
    return {
        "user_id": user_id,
        "last_sync": user.last_sync.isoformat() if user.last_sync else None,
        "notebooks_synced": notebook_count,
        "conversations_synced": conversation_count,
        "status": "connected"
    }

# Sync notebooks
@app.post("/api/sync/notebooks")
def sync_notebook(
    notebook: NotebookSyncRequest,
    user_info: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Sync notebook metadata and content (text only, no vectors)"""
    user_id = user_info["sub"]
    
    # Check if notebook exists
    existing = db.query(NotebookSync).filter(
        NotebookSync.id == notebook.id,
        NotebookSync.user_id == user_id
    ).first()
    
    if existing:
        # Update existing
        existing.title = notebook.title
        existing.content = notebook.content
        existing.device_id = notebook.device_id
        existing.updated_at = datetime.utcnow()
    else:
        # Create new
        new_notebook = NotebookSync(
            id=notebook.id,
            user_id=user_id,
            title=notebook.title,
            content=notebook.content,
            device_id=notebook.device_id
        )
        db.add(new_notebook)
    
    # Update user's last sync
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.last_sync = datetime.utcnow()
    
    db.commit()
    
    return {
        "status": "synced",
        "notebook_id": notebook.id,
        "updated_at": datetime.utcnow().isoformat()
    }

# Get notebooks
@app.get("/api/sync/notebooks")
def get_notebooks(
    user_info: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get all synced notebooks for user"""
    user_id = user_info["sub"]
    
    notebooks = db.query(NotebookSync).filter(
        NotebookSync.user_id == user_id
    ).order_by(NotebookSync.updated_at.desc()).all()
    
    return {
        "notebooks": [
            {
                "id": nb.id,
                "title": nb.title,
                "content": nb.content,
                "device_id": nb.device_id,
                "created_at": nb.created_at.isoformat(),
                "updated_at": nb.updated_at.isoformat()
            }
            for nb in notebooks
        ]
    }

# Get single notebook
@app.get("/api/sync/notebooks/{notebook_id}")
def get_notebook(
    notebook_id: str,
    user_info: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get a specific notebook"""
    user_id = user_info["sub"]
    
    notebook = db.query(NotebookSync).filter(
        NotebookSync.id == notebook_id,
        NotebookSync.user_id == user_id
    ).first()
    
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    return {
        "id": notebook.id,
        "title": notebook.title,
        "content": notebook.content,
        "device_id": notebook.device_id,
        "created_at": notebook.created_at.isoformat(),
        "updated_at": notebook.updated_at.isoformat()
    }

# Delete notebook
@app.delete("/api/sync/notebooks/{notebook_id}")
def delete_notebook(
    notebook_id: str,
    user_info: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Delete a synced notebook"""
    user_id = user_info["sub"]
    
    notebook = db.query(NotebookSync).filter(
        NotebookSync.id == notebook_id,
        NotebookSync.user_id == user_id
    ).first()
    
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    db.delete(notebook)
    db.commit()
    
    return {"status": "deleted", "notebook_id": notebook_id}

# Sync conversation
@app.post("/api/sync/conversations")
def sync_conversation(
    conversation: ConversationSyncRequest,
    user_info: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Sync conversation history (text only)"""
    user_id = user_info["sub"]
    
    # Check if conversation exists
    existing = db.query(ConversationSync).filter(
        ConversationSync.id == conversation.id,
        ConversationSync.user_id == user_id
    ).first()
    
    if not existing:
        new_conversation = ConversationSync(
            id=conversation.id,
            user_id=user_id,
            notebook_id=conversation.notebook_id,
            question=conversation.question,
            answer=conversation.answer
        )
        db.add(new_conversation)
        db.commit()
    
    return {
        "status": "synced",
        "conversation_id": conversation.id
    }

# Get conversations
@app.get("/api/sync/conversations")
def get_conversations(
    notebook_id: Optional[str] = None,
    user_info: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get conversation history"""
    user_id = user_info["sub"]
    
    query = db.query(ConversationSync).filter(ConversationSync.user_id == user_id)
    
    if notebook_id:
        query = query.filter(ConversationSync.notebook_id == notebook_id)
    
    conversations = query.order_by(ConversationSync.created_at.desc()).all()
    
    return {
        "conversations": [
            {
                "id": conv.id,
                "notebook_id": conv.notebook_id,
                "question": conv.question,
                "answer": conv.answer,
                "created_at": conv.created_at.isoformat()
            }
            for conv in conversations
        ]
    }

# Sync settings
@app.put("/api/sync/settings")
def sync_settings(
    settings: SettingsSyncRequest,
    user_info: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Sync user settings across devices"""
    user_id = user_info["sub"]
    
    existing = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    
    if existing:
        existing.settings_json = settings.settings_json
        existing.updated_at = datetime.utcnow()
    else:
        new_settings = UserSettings(
            user_id=user_id,
            settings_json=settings.settings_json
        )
        db.add(new_settings)
    
    db.commit()
    
    return {
        "status": "synced",
        "updated_at": datetime.utcnow().isoformat()
    }

# Get settings
@app.get("/api/sync/settings")
def get_settings(
    user_info: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get user settings"""
    user_id = user_info["sub"]
    
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    
    if not settings:
        return {"settings_json": "{}", "updated_at": None}
    
    return {
        "settings_json": settings.settings_json,
        "updated_at": settings.updated_at.isoformat()
    }

# Root endpoint
@app.get("/")
def root():
    return {
        "service": "Clarity Sync Service",
        "description": "Minimal sync service for metadata and backups",
        "note": "NO AI processing - all AI happens locally",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "status": "/api/sync/status",
            "notebooks": "/api/sync/notebooks",
            "conversations": "/api/sync/conversations",
            "settings": "/api/sync/settings"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
