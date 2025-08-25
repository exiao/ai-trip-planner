"""
Simple AI Trip Planner Backend
A minimal example of using LLMs to build a travel planning API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import requests
import json
import asyncio
from typing import AsyncGenerator

load_dotenv()

def fix_encoding(text):
    """Fix double-encoded UTF-8 text from OpenRouter"""
    if not text:
        return text
    
    try:
        # Common double-encoding patterns that indicate UTF-8 encoded as Latin-1
        encoding_patterns = [
            'Ã©', 'Ã¨', 'Ã ', 'Ã¡', 'Ã¢', 'Ã¤', 'Ã§', 'Ã´', 'Ã¶', 'Ã¹', 'Ã»', 'Ã¼',
            'Ã‰', 'Ã€', 'Ã', 'Ã‚', 'Ã„', 'Ã‡', 'Ã"', 'Ã–', 'Ã™', 'Ã›', 'Ãœ',
            'â€™', 'â€œ', 'â€', 'â€"', 'â€"', 'â€¢', 'âˆ'
        ]
        
        # Check if text contains any double-encoding patterns
        has_double_encoding = any(pattern in text for pattern in encoding_patterns)
        
        if has_double_encoding:
            # Try to fix by re-encoding as latin-1 then decoding as UTF-8
            fixed = text.encode('latin-1').decode('utf-8')
            return fixed
            
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    
    return text

app = FastAPI(title="Simple AI Trip Planner")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "openai/gpt-oss-20b:free|google/gemini-flash-1.5-8b|meta-llama/llama-3.2-3b-instruct:free"

if not OPENROUTER_API_KEY:
    print("Warning: Set OPENROUTER_API_KEY in .env file")
    print("Get your free API key at: https://openrouter.ai/keys")

class TripRequest(BaseModel):
    destination: str
    duration: str
    budget: str = "moderate"
    interests: str = "general sightseeing"

@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML file"""
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    return FileResponse(frontend_path) if os.path.exists(frontend_path) else {"message": "Frontend not found"}

@app.post("/api/plan-trip-stream")
async def plan_trip_stream(request: TripRequest):
    """Generate a trip itinerary with streaming"""
    
    async def generate() -> AsyncGenerator[str, None]:
        prompt = f"""Create a {request.duration} trip itinerary for {request.destination}.

Budget: {request.budget}
Interests: {request.interests}

Include:
- Daily activities (morning/afternoon/evening) with WHY each was chosen
- Restaurant recommendations with budget explanations
- Costs, transportation, and cultural insights
- Tips for saving money and local etiquette

Format in Markdown:
- # Main title
- ## Why This Itinerary? (explain the overall approach)
- ## Day headers
- ### Time of day sections
- **Bold** for explanations and important info
- > Blockquotes for special tips

Explain WHY each recommendation fits their {request.interests} interests and {request.budget} budget."""

        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            }
            
            data = {
                "model": MODEL,
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are an expert travel planner. Always explain WHY you recommend activities based on the traveler's interests and budget."
                    },
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 8000,
                "temperature": 0.7,
                "stream": True,
            }
            
            response = requests.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=data,
                stream=True
            )
            
            if response.status_code == 200:
                for line in response.iter_lines(decode_unicode=True):
                    if line and line.startswith('data: '):
                        data_str = line[6:]
                        if data_str == '[DONE]':
                            yield 'data: [DONE]\n\n'
                            break
                        try:
                            data_json = json.loads(data_str)
                            content = data_json.get('choices', [{}])[0].get('delta', {}).get('content', '')
                            if content:
                                # Fix encoding issues from OpenRouter
                                fixed_content = fix_encoding(content)
                                yield f'data: {json.dumps({"content": fixed_content}, ensure_ascii=False)}\n\n'
                                if os.getenv("TESTING") != "1":
                                    await asyncio.sleep(0.01)
                        except json.JSONDecodeError:
                            continue
            else:
                error_msg = "API Error. Check your API key or try again later."
                yield f'data: {json.dumps({"error": error_msg}, ensure_ascii=False)}\n\n'
                
        except Exception as e:
            error_msg = "API key not configured" if not OPENROUTER_API_KEY else str(e)
            yield f'data: {json.dumps({"error": error_msg}, ensure_ascii=False)}\n\n'
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Simple AI Trip Planner"}

if __name__ == "__main__":
    import uvicorn
    import sys
    
    port = 7000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}, using 7000")
    
    print(f"Starting Simple AI Trip Planner on http://localhost:{port}")
    
    try:
        uvicorn.run(app, host="localhost", port=port)
    except OSError as e:
        if "address already in use" in str(e).lower():
            print(f"Port {port} in use. Try: python backend/backend.py 7001")
            sys.exit(1)
        raise