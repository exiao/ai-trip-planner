# Simple AI Trip Planner

A minimal tutorial example showing how to build an AI-powered web application with just 200 lines of code.

## What You'll Learn

- How to call AI models via OpenRouter API
- Building a simple REST API with FastAPI  
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
Open http://localhost:8000 - Done! 🎉

### Local development
After initial setup, you only need:
```bash
source .venv/bin/activate
python backend/backend.py
```

Anytime you want to install new packages, add it to requirements.txt and then run:
```bash
uv pip install -r requirements.txt
```

## Project Structure
```
simple-ai-trip-planner/
├── .venv/           # Virtual environment (created by uv)
├── backend/         # Backend application folder
│   └── backend.py   # FastAPI server + OpenRouter integration
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

1. **`backend/backend.py`** (130 lines) - A FastAPI server that:
   - Receives trip planning requests
   - Calls OpenRouter API to generate itineraries (using free models!)
   - Returns the results as JSON

2. **`frontend/index.html`** (240 lines) - A clean, minimal web page that:
   - Simple form for trip preferences (destination, duration, budget, interests)
   - Clean, modern UI with system fonts and minimal styling
   - Full markdown rendering for beautiful itineraries

3. **`requirements.txt`** (4 lines) - Just the essentials:
   - FastAPI for the web server
   - Uvicorn to run the server
   - Requests for API calls
   - python-dotenv for environment variables

## Example Request

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
| `Port 8000 already in use` | Kill process: `lsof -ti:8000 \| xargs kill -9` |
| API key error | Get free key at https://openrouter.ai/keys |
| Rate limit reached | Wait 1 minute (free tier limit) or add credits |