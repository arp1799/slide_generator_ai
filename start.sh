#!/bin/bash

# Production startup script for Slide Generator API

echo "🚀 Starting Slide Generator API..."

# Set default port if not provided
export PORT=${PORT:-8000}

# Create necessary directories
mkdir -p samples
mkdir -p logs

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set. Using mock content generation."
else
    echo "✅ OpenAI API key configured."
fi

# Run database migrations (if any)
echo "📊 Checking database setup..."

# Start the application
echo "🌐 Starting server on port $PORT..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 1 \
    --log-level ${LOG_LEVEL:-info} 