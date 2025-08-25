"""
Simple AI Trip Planner Backend
A minimal example of using LLMs to build a travel planning API
Using OpenRouter for access to multiple AI models with a single API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Simple AI Trip Planner")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY not set in environment variables")
    print("Get your free API key at: https://openrouter.ai/keys")

# OpenRouter configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Model routing: https://openrouter.ai/docs/features/model-routing
# Primary model with automatic fallbacks using OpenRouter's routing
DEFAULT_MODEL = "openai/gpt-oss-20b:free"  # OpenAI's free 20B model

# Fallback chain using OpenRouter's pipe syntax for automatic failover
FALLBACK_MODEL = "openai/gpt-oss-20b:free|google/gemini-flash-1.5-8b|meta-llama/llama-3.2-3b-instruct:free"

# Alternative: Use "openrouter/auto" to automatically pick the best available model

# Request model
class TripRequest(BaseModel):
    destination: str
    duration: str
    budget: str = "moderate"
    interests: str = "general sightseeing"

# Response model
class TripResponse(BaseModel):
    success: bool
    itinerary: str = None
    error: str = None

@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML file"""
    if os.path.exists("frontend.html"):
        return FileResponse("frontend.html")
    return {"message": "Frontend not found. Please create frontend.html"}

@app.post("/api/plan-trip", response_model=TripResponse)
async def plan_trip(request: TripRequest):
    """
    Generate a trip itinerary using OpenRouter
    """
    # Build the prompt
    prompt = f"""
    Create a comprehensive {request.duration} trip itinerary for {request.destination}.
    
    Budget level: {request.budget}
    Interests: {request.interests}
    
    Please provide a detailed day-by-day plan that includes:
    - Morning, afternoon, and evening activities with specific locations
    - Restaurant recommendations with cuisine type and price ranges
    - Detailed costs for activities, meals, and transportation
    - Transportation tips and routes between locations
    - Unique local experiences and cultural insights for each day
    - Tips for saving money and avoiding tourist traps
    - Important cultural etiquette and customs to know
    
    Format the response using proper Markdown:
    - Use # for the main title
    - Use ## for each day header
    - Use ### for Morning/Afternoon/Evening sections
    - Use **bold** for important information
    - Use bullet points for activities and recommendations
    - Include tables for budget breakdowns if helpful
    
    Be comprehensive and detailed - provide as much helpful information as possible.
    """
    
    try:
        # Call OpenRouter API
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",  # Optional but recommended
            "X-Title": "Simple AI Trip Planner"  # Optional
        }
        
        # Use OpenRouter's model routing for automatic fallback
        # The pipe syntax (model1|model2|model3) tells OpenRouter to try each model in order
        data = {
            "model": FALLBACK_MODEL,  # Uses automatic fallback chain
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a helpful travel planner assistant. Provide practical, realistic itineraries, with a maximum of 100 words."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": 8000,
            "temperature": 0.7,
            # Optional: Add route preference for better routing
            "route": "fallback",  # Tells OpenRouter to use fallback routing
            "models": [  # Optional: Explicit model preferences
                "openai/gpt-oss-20b:free",
                "google/gemini-flash-1.5-8b",
                "meta-llama/llama-3.2-3b-instruct:free"
            ]
        }
        
        response = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            itinerary = result['choices'][0]['message']['content']
            # Check which model was actually used (OpenRouter returns this in headers)
            model_used = result.get('model', 'unknown')
            print(f"Successfully generated itinerary using model: {model_used}")
            return TripResponse(success=True, itinerary=itinerary)
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
            error_msg = error_data.get('error', {}).get('message', f"API Error: {response.status_code}")
            
            # Provide helpful error messages
            if "credit" in error_msg.lower() or "balance" in error_msg.lower():
                error_msg = "Free tier limit reached. Please wait a few minutes or add credits to your OpenRouter account."
            elif "api_key" in error_msg.lower():
                error_msg = "Invalid API key. Please check your OPENROUTER_API_KEY in .env file."
            
            return TripResponse(success=False, error=error_msg)
        
    except Exception as e:
        # Handle errors gracefully
        error_message = str(e)
        if "OPENROUTER_API_KEY" in error_message or not OPENROUTER_API_KEY:
            error_message = "API key not configured. Please set OPENROUTER_API_KEY in .env file"
        
        return TripResponse(success=False, error=error_message)

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "Simple AI Trip Planner"}

# Run the server if this file is executed directly
if __name__ == "__main__":
    import uvicorn
    print("Starting Simple AI Trip Planner...")
    print("Frontend will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    uvicorn.run(app, host="localhost", port=8000)