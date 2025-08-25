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
python backend.py
```
Open http://localhost:8000 - Done! 🎉

## Troubleshooting

If you are having trouble installing uv, a package manager for installing python libraries
#### 1. Install uv (One-time)
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with Homebrew
brew install uv
```

#### 2. Setup Project
```bash
git clone https://github.com/yourusername/simple-ai-trip-planner.git
cd simple-ai-trip-planner

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

#### 3. Configure API Key
```bash
cp .env.example .env
# Edit .env and add your OpenRouter API key
```

Get your FREE API key from: https://openrouter.ai/keys

#### 4. Run the Application
```bash
python backend.py
```

Open http://localhost:8000 in your browser!

### Daily Usage
After initial setup, you only need:
```bash
source .venv/bin/activate
python backend.py
```

## How It Works

This application consists of just 3 files:

1. **`backend.py`** (130 lines) - A FastAPI server that:
   - Receives trip planning requests
   - Calls OpenRouter API to generate itineraries (using free models!)
   - Returns the results as JSON

2. **`frontend.html`** (240 lines) - A clean, minimal web page that:
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

## Project Structure

```
simple-ai-trip-planner/
├── .venv/           # Virtual environment (created by uv)
├── backend.py       # FastAPI server + OpenRouter integration
├── frontend.html    # Web interface  
├── requirements.txt # Python dependencies (just 4!)
├── .env            # Your API keys (create from .env.example)
├── .env.example    # Template for environment variables
├── setup.sh        # Automated setup script
└── README.md       # This file
```

### File Descriptions
- **backend.py** - Complete backend server in ~130 lines
- **frontend.html** - Self-contained UI with inline CSS/JS (~150 lines)
- **requirements.txt** - Minimal dependencies: fastapi, uvicorn, requests, python-dotenv
- **setup.sh** - One-command setup that installs everything

## API Endpoints

- `GET /` - Serves the frontend
- `POST /api/plan-trip` - Generates a trip itinerary
- `GET /health` - Health check endpoint
- `GET /docs` - Auto-generated API documentation

## Technologies Used

- **Python 3.8+** - Backend language
- **FastAPI** - Modern, fast web framework
- **OpenRouter API** - Smart routing to multiple AI models with automatic fallback
- **HTML/CSS/JavaScript** - Simple frontend (no frameworks!)
- **uv** - Fast Python package manager (10-100x faster than pip!)

### OpenRouter Model Routing
The app uses OpenRouter's [model routing](https://openrouter.ai/docs/features/model-routing) feature:
- Automatically tries multiple models if one is unavailable
- Uses pipe syntax: `model1|model2|model3` for fallback chain
- Default: OpenAI GPT OSS 20B → Google Gemini → Meta Llama

## Local Deployment Details

### Why uv?
- **10-100x faster** than pip
- **Better dependency resolution**
- **No configuration needed**
- **Drop-in replacement** for pip

### Managing Dependencies
```bash
# Add a new package
uv pip install package-name
uv pip freeze > requirements.txt

# Update all packages
uv pip install -r requirements.txt --upgrade

# Show installed packages
uv pip list
```

### Advanced Options
```bash
# Run with auto-reload (for development)
uvicorn backend:app --reload

# Run on different port
uvicorn backend:app --port 3000

# Run with multiple workers (production)
uvicorn backend:app --workers 4
```

## Troubleshooting

**"uv: command not found"**
```bash
# Add uv to PATH
export PATH="$HOME/.cargo/bin:$PATH"
# Add to ~/.bashrc or ~/.zshrc to make permanent
```

**"No module named 'fastapi'"**
```bash
# Make sure virtual environment is activated
source .venv/bin/activate
# Reinstall dependencies
uv pip install -r requirements.txt
```

**"Port 8000 already in use"**
```bash
# Kill the process using port 8000
lsof -ti:8000 | xargs kill -9
# Or use a different port
python backend.py  # Then edit backend.py to change port
```

**"API key not configured"**
- Make sure you've created a `.env` file (not `.env.example`)
- Get your free key at https://openrouter.ai/keys
- Check that your API key is correct

**"No allowed providers are available" or "Free tier limit reached"**
- The app uses OpenRouter's automatic model routing to find available models
- Default: OpenAI GPT OSS 20B (free) with automatic fallback to other free models
- If all fail, wait a few minutes (free tier has rate limits)
- Or add credits to your OpenRouter account for unlimited access

**"Empty or poor quality responses"**
- The app uses OpenAI's free 20B model by default (good quality for free!)
- OpenRouter automatically falls back to other models if needed
- For premium quality: Add credits and change to GPT-4, Claude, etc.

## Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [Building Your First AI App](https://platform.openai.com/docs/quickstart)

## Total Lines of Code: ~250

- Backend: 100 lines
- Frontend: 150 lines
- No build process, no complexity!

## License

MIT - Use this for learning, teaching, or building your own projects!

---

Built as a tutorial for developers learning to create AI-powered applications. Perfect for workshops, bootcamps, or self-study.