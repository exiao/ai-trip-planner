"""
Simple AI Trip Planner Backend
A minimal example of using LLMs to build a travel planning API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import openai

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

# Configure OpenAI (you can also use Groq or other providers)
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    print("Warning: OPENAI_API_KEY not set in environment variables")

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
    Generate a trip itinerary using OpenAI
    """
    # Build the prompt
    prompt = f"""
    Create a detailed {request.duration} trip itinerary for {request.destination}.
    
    Budget level: {request.budget}
    Interests: {request.interests}
    
    Please provide a day-by-day plan that includes:
    - Morning, afternoon, and evening activities
    - Specific restaurant recommendations with cuisine type
    - Approximate costs for activities and meals
    - Transportation tips between locations
    - One unique local experience per day
    
    Format the response clearly with day headers and bullet points.
    Keep the total response concise but informative (max 500 words).
    """
    
    try:
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Use gpt-4 for better quality
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful travel planner assistant. Provide practical, realistic itineraries."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=1000,
            temperature=0.7  # Balanced creativity
        )
        
        # Extract the generated itinerary
        itinerary = response.choices[0].message.content
        
        return TripResponse(success=True, itinerary=itinerary)
        
    except Exception as e:
        # Handle errors gracefully
        error_message = str(e)
        if "api_key" in error_message.lower():
            error_message = "API key not configured. Please set OPENAI_API_KEY in .env file"
        
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
    uvicorn.run(app, host="0.0.0.0", port=8000)