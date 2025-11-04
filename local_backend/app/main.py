"""
Main FastAPI application for local RAG backend
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (parent of local_backend)
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Clarity Local Backend",
    description="Local-first RAG pipeline with ChromaDB and LLM inference",
    version="1.0.0"
)

# CORS middleware
# Get CORS origins from environment variable for production
cors_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

# Filter out empty strings and strip whitespace
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

logger.info(f"CORS origins configured: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from .api.endpoints import router as api_router
from .api.notebooks import router as notebooks_router
from .api.flashcards import router as flashcards_router
from .api.mindmaps import router as mindmaps_router
from .api.gamification import router as gamification_router
from .db import init_db

app.include_router(api_router, prefix="/api", tags=["api"])
app.include_router(notebooks_router, prefix="/api", tags=["notebooks"])
app.include_router(flashcards_router, prefix="/api", tags=["flashcards"])
app.include_router(mindmaps_router, prefix="/api", tags=["mindmaps"])
app.include_router(gamification_router, prefix="/api", tags=["gamification"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting Clarity Local Backend")
    
    # Initialize database
    try:
        init_db()
        logger.info("✅ PostgreSQL database initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        logger.warning("⚠️  Make sure PostgreSQL is running!")
    
    logger.info("📂 ChromaDB initialized")
    logger.info("🤖 LLM wrapper ready")
    logger.info("✅ Server is ready!")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Clarity Local Backend",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )
