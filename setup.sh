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

# Check for Phoenix observability (optional)
echo "🔍 Checking Phoenix observability setup..."
if python -c "import phoenix" 2>/dev/null; then
    echo "✅ Phoenix is available for observability"
    
    # Kill any existing Phoenix processes on both HTTP and gRPC ports
    echo "   Checking for existing Phoenix processes..."
    for port in 6006 4317 4318; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "   Killing process on port $port..."
            lsof -ti:$port | xargs kill -9 2>/dev/null || true
        fi
    done
    sleep 1
    
    echo "🚀 Starting Phoenix UI in background..."
    # Set environment variables to use alternative gRPC port
    export PHOENIX_GRPC_PORT=4318
    export PHOENIX_PORT=6006
    
    # Start Phoenix with error handling
    nohup python -m phoenix.server.main serve > phoenix.log 2>&1 &
    PHOENIX_PID=$!
    sleep 3
    
    # Check if Phoenix actually started successfully
    if lsof -Pi :6006 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "✅ Phoenix UI started successfully at http://localhost:6006"
    else
        echo "⚠️  Phoenix failed to start properly"
        
        # Kill the failed process if it's still running
        kill $PHOENIX_PID 2>/dev/null || true
        
        # Provide helpful error messages based on log content
        if [ -f phoenix.log ]; then
            if grep -q "Failed to bind\|RuntimeError.*Failed to bind" phoenix.log; then
                echo "   Error: Port binding failed - another service is using required ports"
                echo "   Try: sudo lsof -i :4317 -i :4318 to find conflicting processes"
            elif grep -q "DependencyConflict\|openai.*None" phoenix.log; then
                echo "   Error: Missing OpenAI dependency"
                echo "   Installing missing dependency..."
                uv pip install "openai>=1.69.0" || echo "   Failed to install openai - Phoenix observability disabled"
            else
                echo "   Phoenix will run without observability UI (check phoenix.log for details)"
            fi
        fi
        echo "   The main application will still work normally"
    fi
else
    echo "ℹ️  Phoenix not installed (observability disabled)"
    echo "   To enable: uv pip install arize-phoenix"
fi
echo ""

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