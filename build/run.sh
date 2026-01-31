#!/bin/bash
# TimeKeeper Run Script for Linux/macOS
# This script starts both backend and frontend servers

echo "============================================================"
echo "TimeKeeper Run Script for Linux/macOS"
echo "============================================================"
echo ""
echo "Starting backend and frontend servers..."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:4200"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "============================================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "Servers stopped."
    exit 0
}

# Set trap to catch Ctrl+C
trap cleanup INT TERM

# Start backend
cd "$PROJECT_ROOT/backend"
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# Wait a few seconds for backend to start
sleep 5

# Start frontend
cd "$PROJECT_ROOT/frontend"
npm start &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "Both servers are running..."
echo ""
echo "Backend: http://localhost:8000 (PID: $BACKEND_PID)"
echo "Frontend: http://localhost:4200 (PID: $FRONTEND_PID)"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
