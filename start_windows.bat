@echo off
echo ============================================================
echo    HR ASSISTANT - Quick Start
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import pandas" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting HR Assistant Backend...
echo.
echo IMPORTANT: Keep this window open!
echo Open 'frontend.html' in your browser to use the app
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Start the backend server
python backend.py

pause
