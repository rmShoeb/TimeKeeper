#!/bin/bash
# TimeKeeper Setup Script for Linux/macOS
# This script sets up the backend and frontend dependencies

echo "============================================================"
echo "TimeKeeper Setup Script for Linux/macOS"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.10+ from your package manager or https://python.org"
    exit 1
fi

echo "[1/6] Python found"
python3 --version

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed or not in PATH"
    echo "Please install Node.js 18+ from your package manager or https://nodejs.org"
    exit 1
fi

echo "[2/6] Node.js found"
node --version

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Navigate to backend directory
cd "$PROJECT_ROOT/backend"

echo ""
echo "[3/6] Creating Python virtual environment..."
python3 -m venv venv

echo "[4/6] Activating virtual environment and installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "[5/6] Creating .env file from template..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env file created. Please update JWT_SECRET_KEY before running."
else
    echo ".env file already exists. Skipping..."
fi

# Navigate to frontend directory
cd "$PROJECT_ROOT/frontend"

echo ""
echo "[6/6] Installing Node.js dependencies..."
npm install

echo ""
echo "============================================================"
echo "Setup completed successfully!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Update backend/.env file with a secure JWT_SECRET_KEY"
echo "2. Run the application using: ./build/run.sh"
echo ""
echo "============================================================"
