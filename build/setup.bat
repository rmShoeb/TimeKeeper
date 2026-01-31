@echo off
REM TimeKeeper Setup Script for Windows
REM This script sets up the backend and frontend dependencies

echo ============================================================
echo TimeKeeper Setup Script for Windows
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    exit /b 1
)

echo [1/6] Python found
python --version

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org
    exit /b 1
)

echo [2/6] Node.js found
node --version

REM Navigate to backend directory
cd /d "%~dp0..\backend"

echo.
echo [3/6] Creating Python virtual environment...
python -m venv venv

echo [4/6] Activating virtual environment and installing Python dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [5/6] Creating .env file from template...
if not exist .env (
    copy .env.example .env
    echo .env file created. Please update JWT_SECRET_KEY before running.
) else (
    echo .env file already exists. Skipping...
)

REM Navigate to frontend directory
cd /d "%~dp0..\frontend"

echo.
echo [6/6] Installing Node.js dependencies...
call npm install

echo.
echo ============================================================
echo Setup completed successfully!
echo ============================================================
echo.
echo Next steps:
echo 1. Update backend\.env file with a secure JWT_SECRET_KEY
echo 2. Run the application using: build\run.bat
echo.
echo ============================================================

pause
