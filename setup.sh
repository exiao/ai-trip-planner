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

# Create virtual environment
echo "🔧 Creating virtual environment..."
uv venv

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
echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "  source .venv/bin/activate"
echo "  python backend.py"
echo ""
echo "Then open http://localhost:8000 in your browser"