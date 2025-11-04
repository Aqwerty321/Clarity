#!/bin/bash
# Quick start script for Clarity local development

echo "🚀 Starting Clarity Development Environment"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if PostgreSQL is running
echo -e "\n${YELLOW}Checking PostgreSQL...${NC}"
if pg_isready > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL is running${NC}"
else
    echo -e "${RED}❌ PostgreSQL is not running${NC}"
    echo "Start PostgreSQL and try again"
    exit 1
fi

# Check if Ollama is running
echo -e "\n${YELLOW}Checking Ollama...${NC}"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ollama is running${NC}"
else
    echo -e "${RED}❌ Ollama is not running${NC}"
    echo "Start Ollama: ollama serve"
    echo "Pull models: ollama pull llama3.1 && ollama pull nomic-embed-text"
    exit 1
fi

# Check if database exists
echo -e "\n${YELLOW}Checking database...${NC}"
if psql -U postgres -lqt | cut -d \| -f 1 | grep -qw clarity_db; then
    echo -e "${GREEN}✅ Database 'clarity_db' exists${NC}"
else
    echo -e "${YELLOW}Creating database 'clarity_db'...${NC}"
    createdb clarity_db
    echo -e "${GREEN}✅ Database created${NC}"
fi

# Check backend .env file
echo -e "\n${YELLOW}Checking backend configuration...${NC}"
if [ -f "local_backend/.env" ]; then
    echo -e "${GREEN}✅ Backend .env file exists${NC}"
else
    echo -e "${RED}❌ Backend .env file not found${NC}"
    echo "Copy local_backend/.env.example to local_backend/.env and configure it"
    exit 1
fi

# Check frontend .env file
echo -e "\n${YELLOW}Checking frontend configuration...${NC}"
if [ -f "frontend/.env" ]; then
    echo -e "${GREEN}✅ Frontend .env file exists${NC}"
else
    echo -e "${RED}❌ Frontend .env file not found${NC}"
    echo "Copy frontend/.env.example to frontend/.env and configure it"
    exit 1
fi

# Install backend dependencies if needed
echo -e "\n${YELLOW}Checking backend dependencies...${NC}"
if [ -d "local_backend/venv" ]; then
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
else
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    cd local_backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    echo -e "${GREEN}✅ Backend dependencies installed${NC}"
fi

# Install frontend dependencies if needed
echo -e "\n${YELLOW}Checking frontend dependencies...${NC}"
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✅ Frontend dependencies exist${NC}"
else
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
fi

echo -e "\n${GREEN}=========================================="
echo "🎉 All checks passed!"
echo "==========================================${NC}"

echo -e "\n${YELLOW}Starting services...${NC}\n"

# Start backend in background
echo "Starting backend on http://localhost:5000 ..."
cd local_backend
source venv/bin/activate
uvicorn app.main:app --reload --port 5000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready!${NC}"
        break
    fi
    sleep 1
    echo -n "."
done

# Start frontend
echo -e "\nStarting frontend on http://localhost:5173 ..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"

echo -e "\n${GREEN}=========================================="
echo "🚀 Clarity is running!"
echo "==========================================${NC}"
echo ""
echo "Frontend: http://localhost:5173"
echo "Backend:  http://localhost:5000"
echo "API Docs: http://localhost:5000/docs"
echo ""
echo "Backend logs: tail -f backend.log"
echo ""
echo "To stop all services:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Or press Ctrl+C and run:"
echo "  ./stop.sh"
echo ""

# Save PIDs to file for stop script
echo "$BACKEND_PID" > .clarity.pids
echo "$FRONTEND_PID" >> .clarity.pids

# Wait for user to press Ctrl+C
trap "echo -e '\n${YELLOW}Stopping services...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm .clarity.pids; echo -e '${GREEN}✅ Services stopped${NC}'; exit 0" INT

wait
