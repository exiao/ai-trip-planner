# Simple AI Trip Planner

A minimal tutorial example showing how to build an AI-powered web application with just 200 lines of code.

## What You'll Learn

- How to call OpenAI's API from Python
- Building a simple REST API with FastAPI  
- Creating a web interface without frameworks
- Connecting frontend and backend

## Quick Start (2 minutes)

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/simple-ai-trip-planner.git
cd simple-ai-trip-planner
pip install -r requirements.txt
```

### 2. Set Up Your API Key

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

Get your API key from: https://platform.openai.com/api-keys

### 3. Run the Application

```bash
python backend.py
```

### 4. Open in Browser

Go to http://localhost:8000

That's it! Start planning trips with AI.

## How It Works

This application consists of just 3 files:

1. **`backend.py`** (100 lines) - A FastAPI server that:
   - Receives trip planning requests
   - Calls OpenAI to generate itineraries
   - Returns the results as JSON

2. **`frontend.html`** (150 lines) - A simple web page that:
   - Collects trip preferences (destination, duration, budget, interests)
   - Sends requests to the backend
   - Displays the generated itinerary

3. **`requirements.txt`** (4 lines) - Just the essentials:
   - FastAPI for the web server
   - Uvicorn to run the server
   - OpenAI for AI capabilities
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

1. **Different AI Models**: Switch to GPT-4 for better quality or Claude for different style
2. **Save Trips**: Add a database to store generated itineraries
3. **User Accounts**: Let users save and share their trips
4. **Weather Integration**: Add real-time weather data
5. **Maps**: Integrate Google Maps to show locations
6. **Export**: Add PDF or email export functionality

## Code Structure

```
simple-ai-trip-planner/
├── backend.py       # FastAPI server + OpenAI integration
├── frontend.html    # Web interface
├── requirements.txt # Python dependencies
├── .env.example    # Environment variable template
└── README.md       # This file
```

## API Endpoints

- `GET /` - Serves the frontend
- `POST /api/plan-trip` - Generates a trip itinerary
- `GET /health` - Health check endpoint
- `GET /docs` - Auto-generated API documentation

## Technologies Used

- **Python 3.8+** - Backend language
- **FastAPI** - Modern, fast web framework
- **OpenAI API** - For generating intelligent itineraries
- **HTML/CSS/JavaScript** - Simple frontend (no frameworks!)

## Troubleshooting

**"API key not configured"**
- Make sure you've created a `.env` file (not `.env.example`)
- Check that your API key is correct

**"Failed to connect to server"**
- Ensure the backend is running (`python backend.py`)
- Check that port 8000 is not in use

**Empty or poor quality responses**
- Try using GPT-4 instead of GPT-3.5 for better quality
- Make your prompts more specific

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