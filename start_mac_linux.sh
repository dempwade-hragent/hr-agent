#!/bin/bash

echo "============================================================"
echo "   HR ASSISTANT - Quick Start"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python from https://www.python.org/downloads/"
    exit 1
fi

# Check if dependencies are installed
python3 -c "import pandas" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

echo ""
echo "Starting HR Assistant Backend..."
echo ""
echo "IMPORTANT: Keep this terminal window open!"
echo "Open 'frontend.html' in your browser to use the app"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

# Start the backend server
python3 backend.py
