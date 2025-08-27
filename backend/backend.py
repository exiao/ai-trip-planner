"""
Simple AI Trip Planner Backend
A minimal example of using LLMs to build a travel planning API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

# Configuration
CONFIG = {
    "api_url": "https://openrouter.ai/api/v1",
    "model": "openai/gpt-oss-20b",
    "fallback_models": ["openai/gpt-oss-20b", "google/gemini-flash-1.5-8b"],
    "max_tokens": 2000,
    "temperature": 0.7,
}

ERROR_MESSAGES = {
    "credit": "Free tier limit reached. Please wait a few minutes or add credits to your OpenRouter account.",
    "api_key": "Invalid API key. Please check your OPENROUTER_API_KEY in .env file.",
    "no_key": "API key not configured. Please set OPENROUTER_API_KEY in .env file",
}

# Initialize Phoenix observability (simplified)
try:
    import phoenix as px
    from phoenix.otel import register
    import socket
    
    # Check if Phoenix is already running on port 6006
    def is_phoenix_running():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', 6006))
            sock.close()
            return result == 0
        except:
            return False
    
    # Only launch Phoenix if it's not already running and no API key is set
    if not os.getenv("PHOENIX_API_KEY") and not is_phoenix_running():
        px.launch_app()
        print("🔭 Phoenix UI launched at http://localhost:6006")
    elif is_phoenix_running():
        print("🔭 Phoenix UI already running at http://localhost:6006")
    
    tracer_provider = register(project_name="ai-trip-planner", auto_instrument=True)
    tracer = tracer_provider.get_tracer(__name__)
    TRACING_ENABLED = True
except ImportError:
    TRACING_ENABLED = False
    print("ℹ️  Phoenix not installed, running without tracing")

# Initialize FastAPI app
app = FastAPI(title="Simple AI Trip Planner")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY not set")
    print("Get your free API key at: https://openrouter.ai/keys")

class TripRequest(BaseModel):
    destination: str
    duration: str
    budget: str = "moderate"
    interests: str = "general sightseeing"

class TripResponse(BaseModel):
    success: bool
    itinerary: str = None
    error: str = None

def set_trace_attributes(span, request, response_data=None, error=None):
    """Helper to set trace attributes"""
    if not span:
        return
    
    span.set_attribute("llm.request.model", CONFIG["model"])
    span.set_attribute("trip.destination", request.destination)
    span.set_attribute("trip.duration", request.duration)
    span.set_attribute("trip.budget", request.budget)
    span.set_attribute("trip.interests", request.interests)
    
    if response_data:
        span.set_attribute("llm.response.model", response_data.get('model', 'unknown'))
        span.set_attribute("llm.usage.total_tokens", response_data.get('usage', {}).get('total_tokens', 0))
    
    if error:
        span.set_attribute("error", True)
        span.set_attribute("error.message", str(error))

def get_error_message(error_text):
    """Get user-friendly error message"""
    error_lower = error_text.lower()
    if "credit" in error_lower or "balance" in error_lower:
        return ERROR_MESSAGES["credit"]
    elif "api_key" in error_lower:
        return ERROR_MESSAGES["api_key"]
    else:
        return error_text

def create_api_request(request: TripRequest):
    """Create OpenRouter API request"""
    prompt = f"""Create a {request.duration} trip itinerary for {request.destination}.
Budget: {request.budget}
Interests: {request.interests}

Provide a practical day-by-day plan with activities, restaurants, and estimated costs.
Format with markdown headers and bullet points."""

    return {
        "model": CONFIG["model"],
        "messages": [
            {"role": "system", "content": "You are a travel planner. Provide concise, practical itineraries."},
            {"role": "user", "content": prompt}
        ],
        "models": CONFIG["fallback_models"],
        "max_tokens": CONFIG["max_tokens"],
        "temperature": CONFIG["temperature"],
        "route": "fallback"
    }

@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML file"""
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"message": "Frontend not found. Please create frontend/index.html"}

@app.post("/api/plan-trip", response_model=TripResponse)
async def plan_trip(request: TripRequest):
    """Generate a trip itinerary using OpenRouter"""
    
    if not OPENROUTER_API_KEY:
        return TripResponse(success=False, error=ERROR_MESSAGES["no_key"])
    
    # Start tracing span
    span = None
    if TRACING_ENABLED:
        span = tracer.start_span("plan_trip")
        span.__enter__()
        set_trace_attributes(span, request)
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        
        data = create_api_request(request)
        
        response = requests.post(
            f"{CONFIG['api_url']}/chat/completions",
            headers=headers,
            json=data
        )
        
        if span:
            span.set_attribute("http.status_code", response.status_code)
        
        if response.status_code == 200:
            result = response.json()
            itinerary = result['choices'][0]['message']['content']
            
            if span:
                set_trace_attributes(span, request, response_data=result)
            
            return TripResponse(success=True, itinerary=itinerary)
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
            error_msg = error_data.get('error', {}).get('message', f"API Error: {response.status_code}")
            friendly_error = get_error_message(error_msg)
            
            if span:
                set_trace_attributes(span, request, error=friendly_error)
            
            return TripResponse(success=False, error=friendly_error)
    
    except Exception as e:
        error_msg = ERROR_MESSAGES["no_key"] if "OPENROUTER_API_KEY" in str(e) else str(e)
        
        if span:
            set_trace_attributes(span, request, error=error_msg)
        
        return TripResponse(success=False, error=error_msg)
    
    finally:
        if span:
            span.__exit__(None, None, None)

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "Simple AI Trip Planner"}

# Run the server if this file is executed directly
if __name__ == "__main__":
    import uvicorn
    print("Starting Simple AI Trip Planner...")
    print("Frontend: http://localhost:8000")
    print("API docs: http://localhost:8000/docs")
    uvicorn.run(app, host="localhost", port=8000)