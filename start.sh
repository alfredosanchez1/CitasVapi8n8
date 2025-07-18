#!/bin/bash
set -e  # Exit on any error

echo "🚀 Starting FastAPI application..."

# Check if we're in the right directory
echo "📁 Current directory: $(pwd)"
echo "📁 Contents: $(ls -la)"

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt found"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Check if main.py exists
if [ -f "main.py" ]; then
    echo "✅ main.py found"
else
    echo "❌ main.py not found"
    exit 1
fi

# Install dependencies with break-system-packages
echo "📦 Installing dependencies..."
pip install --break-system-packages -r requirements.txt

# Check if uvicorn is installed
echo "🔍 Checking uvicorn installation..."
which uvicorn || echo "❌ uvicorn not found in PATH"
uvicorn --version || echo "❌ uvicorn version check failed"

# Check environment variables
echo "🔧 Environment variables:"
echo "PORT: $PORT"
echo "PYTHONPATH: $PYTHONPATH"

# Start the application
echo "🌐 Starting uvicorn server on port $PORT..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT 