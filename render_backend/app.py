"""
Main FastAPI application for Render sync backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
import os

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
    title="Clarity Sync Backend",
    description="Cloud sync service for Clarity notebooks",
    version="1.0.0"
)

# CORS middleware - allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://clarity-frontend.vercel.app",  # Update with actual frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes
from .routes.sync import router as sync_router

app.include_router(sync_router, prefix="/api", tags=["sync"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting Clarity Sync Backend")
    
    # TODO: Initialize database connection
    # from .db.models import Base
    # from sqlalchemy import create_engine
    # DATABASE_URL = os.getenv("DATABASE_URL")
    # engine = create_engine(DATABASE_URL)
    # Base.metadata.create_all(bind=engine)
    
    logger.info("✅ Server is ready!")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Clarity Sync Backend",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
