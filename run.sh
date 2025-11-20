#!/bin/bash

# Quick start script for Recognizant Forensics

echo "🔍 Recognizant Forensics - Starting local server..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+"
    exit 1
fi

# Check if ffmpeg is available
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  Warning: ffmpeg is not installed. Audio analysis will not work."
    echo "   Install with: brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)"
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Start the server
echo ""
echo "🚀 Starting Flask server..."
echo "   Access at: http://localhost:8080"
echo "   Press Ctrl+C to stop"
echo ""
python app.py

