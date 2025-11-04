#!/bin/bash

# Clarity Local Demo Startup Script
# This script starts the local backend, seeds demo data, and launches the frontend

set -e

echo "🔍 Starting Clarity Local Demo..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if Node is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env with your Auth0 credentials before continuing."
    exit 1
fi

# Start local backend
echo -e "${BLUE}📦 Starting Local Backend...${NC}"
cd local_backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

# Start backend in background
echo "Starting FastAPI server on port 5000..."
uvicorn app.main:app --host 0.0.0.0 --port 5000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Seed demo data (optional)
# echo -e "${BLUE}📚 Seeding demo data...${NC}"
# python scripts/seed_demo_data.py

cd "$PROJECT_ROOT"

# Start frontend
echo -e "${BLUE}🎨 Starting Frontend...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

echo "Starting Vite dev server on port 5173..."
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 3

echo -e "${GREEN}✅ Clarity is running!${NC}"
echo ""
echo "Frontend: http://localhost:5173"
echo "Backend:  http://localhost:5000"
echo "API Docs: http://localhost:5000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Trap Ctrl+C to kill both processes
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# Wait for processes
wait
