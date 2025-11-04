#!/bin/bash
# Render startup script for Clarity backend

echo "🚀 Starting Clarity Backend..."

# Create ChromaDB directory
mkdir -p /opt/render/.clarity/chroma
echo "✅ Created ChromaDB directory"

# Run database migrations (if using Alembic)
# alembic upgrade head

# Start the FastAPI server
echo "🌟 Starting Uvicorn server..."
cd local_backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
