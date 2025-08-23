# Simple AI Trip Planner - Codebase Overview

## Purpose
This is a minimal tutorial repository demonstrating how to build an AI-powered web application with just 250 lines of code. Perfect for workshops, bootcamps, or developers learning to integrate AI into web applications.

## Architecture (Simplified)

### Files (Just 5!)
```
simple-ai-trip-planner/
├── backend.py       # FastAPI server (100 lines)
├── frontend.html    # Web interface (150 lines)  
├── requirements.txt # Dependencies (4 lines)
├── .env.example    # API key template
├── README.md       # User documentation
└── CLAUDE.md       # This file
```

### How It Works
1. User enters trip preferences in `frontend.html`
2. JavaScript sends POST request to backend
3. `backend.py` calls OpenAI API with structured prompt
4. OpenAI returns generated itinerary
5. Frontend displays formatted results

### Tech Stack
- **Backend**: FastAPI + OpenAI Python SDK
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **AI**: OpenAI GPT-3.5/GPT-4
- **No frameworks, no build tools, no complexity!**

## API Endpoints

- `GET /` - Serves frontend.html
- `POST /api/plan-trip` - Generates itinerary
  - Input: `{destination, duration, budget, interests}`
  - Output: `{success, itinerary, error}`
- `GET /health` - Health check
- `GET /docs` - Swagger documentation

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add your OpenAI API key to .env

# Run
python backend.py

# Use
Open http://localhost:8000
```

## Key Learning Points

This tutorial demonstrates:
1. **Minimal API Design** - Just one endpoint needed
2. **Prompt Engineering** - Structured prompts for consistent output
3. **Error Handling** - Graceful failures with user-friendly messages
4. **CORS Setup** - Allowing frontend-backend communication
5. **Environment Variables** - Secure API key management
6. **Async Python** - Using FastAPI's async capabilities
7. **No Build Process** - Direct HTML file serving

## Customization Guide

### To Use Different AI Providers

**For Anthropic Claude:**
```python
# Replace openai with anthropic
import anthropic
client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))
```

**For Groq (Faster):**
```python
# Use Groq's OpenAI-compatible endpoint
from groq import Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
```

### To Add Features

1. **Database**: Add SQLite to store trips
2. **Authentication**: Add simple session-based auth
3. **Export**: Add PDF generation with reportlab
4. **Caching**: Cache responses to reduce API calls
5. **Rate Limiting**: Prevent API abuse

## Teaching Notes

### Workshop Structure (2 hours)
1. **Introduction** (15 min) - What we're building
2. **Setup** (15 min) - Environment and API keys
3. **Backend** (30 min) - Build FastAPI server together
4. **Frontend** (30 min) - Create HTML interface
5. **Integration** (20 min) - Connect frontend to backend
6. **Customization** (10 min) - Modify prompts, add features

### Common Student Questions

**Q: Why not use React/Vue?**
A: This tutorial focuses on AI integration, not frontend frameworks. Vanilla JS keeps it simple.

**Q: Can this scale to production?**
A: Yes, with additions: database, caching, authentication, rate limiting, monitoring.

**Q: How much do API calls cost?**
A: GPT-3.5: ~$0.002 per trip. GPT-4: ~$0.02 per trip.

## Debugging Tips

1. **Check API Key**: Most errors are from missing/invalid keys
2. **CORS Issues**: Ensure backend allows frontend origin
3. **Port Conflicts**: Change port if 8000 is in use
4. **Python Version**: Requires Python 3.8+

## From Tutorial to Production

To make this production-ready, add:
- **Database**: PostgreSQL for persistence
- **Authentication**: OAuth or JWT
- **Monitoring**: Sentry for errors, analytics
- **Caching**: Redis for response caching
- **Queue**: Celery for background tasks
- **Deployment**: Docker + cloud provider
- **CDN**: For static assets
- **Rate Limiting**: Protect against abuse

## License

MIT - Free for educational use