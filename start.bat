@echo off
echo ========================================
echo    AutoEval - Starting Application
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo Please create a .env file with your OpenAI API key.
    echo.
    echo 1. Copy .env.example to .env
    echo 2. Add your OpenAI API key
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "..\venv\Scripts\activate.bat" (
    echo [WARNING] Virtual environment not found at ..\venv
    echo Using global Python installation...
    echo.
)

REM Activate virtual environment if it exists
if exist "..\venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call ..\venv\Scripts\activate.bat
)

REM Install dependencies
echo [INFO] Checking dependencies...
pip install -q -r requirements.txt

REM Start the application
echo.
echo ========================================
echo [SUCCESS] Starting AutoEval Server...
echo ========================================
echo.
echo Open your browser and go to:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause

