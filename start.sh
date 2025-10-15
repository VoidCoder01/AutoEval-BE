#!/bin/bash

echo "========================================"
echo "   AutoEval - Starting Application"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "[ERROR] .env file not found!"
    echo "Please create a .env file with your OpenAI API key."
    echo ""
    echo "1. Copy .env.example to .env"
    echo "2. Add your OpenAI API key"
    echo ""
    exit 1
fi

# Check if virtual environment exists
if [ -d "../venv" ]; then
    echo "[INFO] Activating virtual environment..."
    source ../venv/bin/activate
else
    echo "[WARNING] Virtual environment not found"
    echo "Using global Python installation..."
    echo ""
fi

# Install dependencies
echo "[INFO] Checking dependencies..."
pip install -q -r requirements.txt

# Start the application
echo ""
echo "========================================"
echo "[SUCCESS] Starting AutoEval Server..."
echo "========================================"
echo ""
echo "Open your browser and go to:"
echo "http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py

