#!/bin/bash

echo "========================================"
echo "Traditional Medicine Mapping System"
echo "Starting Server..."
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the server
echo ""
echo "========================================"
echo "Server starting at http://localhost:8000"
echo "Open http://localhost:8000/ui/index.html"
echo ""
echo "Demo Login:"
echo "  Email: demo@example.com"
echo "  Password: demo123"
echo "========================================"
echo ""

uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
