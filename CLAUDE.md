# Simple AI Trip Planner

A minimal tutorial example showing how to build an AI-powered web application with just 200 lines of code, now with **real-time streaming responses**!

## What You'll Learn

- How to call AI models via OpenRouter API
- Building a simple REST API with FastAPI  
- **Streaming responses** with Server-Sent Events (SSE)
- Creating a web interface without frameworks
- Connecting frontend and backend

## Quick Start (1 minute)

```bash
git clone https://github.com/yourusername/simple-ai-trip-planner.git
cd simple-ai-trip-planner
./setup.sh
source .venv/bin/activate
python backend/backend.py
```
Open http://localhost:7000 - Done! 🎉

### Local development
After initial setup, you only need:
```bash
source .venv/bin/activate
python backend/backend.py
```

**Using a custom port** (if 7000 is busy):
```bash
python backend/backend.py 7001
```

Anytime you want to install new packages, add it to requirements.txt and then run:
```bash
uv pip install -r requirements.txt
```

### Running Tests
```bash
# Run tests
pytest backend/tests/ -v

# Quick tests only (skip streaming)
pytest backend/tests/ -k "not stream"
```

## Project Structure
```
simple-ai-trip-planner/
├── .venv/           # Virtual environment (created by uv)
├── backend/         # Backend application folder
│   ├── backend.py   # FastAPI server + OpenRouter integration
│   └── tests/       # Test suite
│       └── test_api.py  # API endpoint tests
├── frontend/        # Frontend application folder
│   └── index.html   # Web interface
├── specs/           # Specifications and documentation
├── requirements.txt # Python dependencies (just 4!)
├── .env            # Your API keys (create from .env.example)
├── .env.example    # Template for environment variables
├── setup.sh        # Automated setup script
├── DESIGN.md       # Design guidelines to build higher quality UIs 
├── CLAUDE.md       # An introduction to the codebase for Claude
└── README.md       # An introduction to the codebase for readers
```

## How It Works

This application consists of just 3 main components:

1. **`backend/backend.py`** (~300 lines) - A FastAPI server that:
   - Receives trip planning requests
   - Calls OpenRouter API to generate itineraries (using free models!)
   - Returns results as JSON or **streams them in real-time**
   - Supports custom port configuration

2. **`frontend/index.html`** (~600 lines) - A clean, minimal web page that:
   - Simple form for trip preferences (destination, duration, budget, interests)
   - **Streaming mode toggle** - watch your itinerary being written in real-time!
   - Clean, modern UI with system fonts and minimal styling
   - Full markdown rendering for beautiful itineraries

3. **`requirements.txt`** (6 lines) - Just the essentials:
   - FastAPI for the web server
   - Uvicorn to run the server
   - Requests for API calls
   - python-dotenv for environment variables
   - pytest for testing
   - httpx for test client

## Features

### 🚀 Real-Time Streaming
- **Toggle streaming mode** with a simple checkbox
- Watch your itinerary being generated word-by-word
- Immediate feedback as content arrives
- Progressive markdown rendering

### 📝 Example Request

When you enter:
- **Destination**: Tokyo
- **Duration**: 5 days
- **Budget**: Moderate
- **Interests**: Food, culture, technology

The AI will generate a complete day-by-day itinerary with:
- Morning, afternoon, and evening activities
- Restaurant recommendations
- Estimated costs
- Transportation tips
- Local experiences

## Customization Ideas

Want to extend this project? Try:

1. **Different AI Models**: OpenRouter gives you access to GPT-4, Claude, Gemini, Llama, and more!
2. **Save Trips**: Add a database to store generated itineraries
3. **User Accounts**: Let users save and share their trips
4. **Weather Integration**: Add real-time weather data
5. **Maps**: Integrate Google Maps to show locations
6. **Export**: Add PDF or email export functionality

## Troubleshooting

If setup.sh doesn't work, run these commands manually:

```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Setup environment
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# 3. Configure API key
cp .env.example .env
# Edit .env and add your OpenRouter API key from https://openrouter.ai/keys

# 4. Run
python backend/backend.py
```

### Common Issues

| Issue | Solution |
|-------|----------|
| `uv: command not found` | Add to PATH: `export PATH="$HOME/.cargo/bin:$PATH"` |
| `No module named 'fastapi'` | Activate venv: `source .venv/bin/activate` |
| `Port 7000 already in use` | Kill process: `lsof -ti:7000 \| xargs kill -9` or use different port: `python backend/backend.py 7001` |
| API key error | Get free key at https://openrouter.ai/keys |
| Rate limit reached | Wait 1 minute (free tier limit) or add credits |