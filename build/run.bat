@echo off
REM TimeKeeper Run Script for Windows
REM This script starts both backend and frontend servers

echo ============================================================
echo TimeKeeper Run Script for Windows
echo ============================================================
echo.
echo Starting backend and frontend servers...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:4200
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop both servers
echo ============================================================
echo.

REM Start backend in a new window
start "TimeKeeper Backend" cmd /k "cd /d "%~dp0..\backend" && call venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait a few seconds for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend in a new window
start "TimeKeeper Frontend" cmd /k "cd /d "%~dp0..\frontend" && npm start"

echo.
echo Both servers are starting in separate windows...
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:4200
echo API Docs: http://localhost:8000/docs
echo.
echo To stop the servers, close their respective windows or press Ctrl+C in each.
echo.

pause
