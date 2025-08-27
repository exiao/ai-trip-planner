#!/bin/bash

echo "🚀 Simple AI Trip Planner - Setup Script"
echo "========================================"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv (fast Python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv installed successfully!"
    echo ""
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🔧 Creating virtual environment..."
    uv venv
else
    echo "✅ Virtual environment already exists, skipping creation"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies with uv..."
uv pip install -r requirements.txt

# Create .env from example if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Add your OpenRouter API key to .env"
    echo "   Get a free key at: https://openrouter.ai/keys"
    echo ""
fi

echo ""
echo "🎉 Setup complete!"
echo ""

# Check if API key is configured
if [ -f .env ] && grep -q "^OPENROUTER_API_KEY=" .env && ! grep -q "^OPENROUTER_API_KEY=$" .env; then
    echo "✅ API key found in .env file"
    echo "🚀 Starting the server..."
    echo ""
    echo "Frontend: http://localhost:8000"
    echo "API docs: http://localhost:8000/docs"  
    echo "Phoenix UI: http://localhost:6006 (if enabled)"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    # Start server (virtual environment is already activated)
    python backend/backend.py
else
    echo "⚠️  Please add your OpenRouter API key to .env file first:"
    echo "   OPENROUTER_API_KEY=your_key_here"
    echo ""
    echo "Get a free key at: https://openrouter.ai/keys"
    echo ""
    echo "Then run:"
    echo "   source .venv/bin/activate"
    echo "   python backend/backend.py" 
    echo ""
    echo "Or run ./setup.sh again after adding the API key"
fi