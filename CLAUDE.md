# AI Trip Planner - Codebase Overview

## 1. Product Overview
The AI Trip Planner is a full-stack web application that generates intelligent, personalized travel itineraries using LangGraph and Groq LLM. It provides:
- Fast trip planning with parallel AI processing (10-15 seconds response time)
- Comprehensive itineraries with budget analysis and local experiences
- Real-time observability through Arize tracing
- Data labeling capabilities via Airtable integration

Look at DESIGN.md for design guidelines when implementing new product features.

## 2. Product Features

### Core Features:
- **Intelligent Trip Planning**: AI-powered itinerary generation based on destination, duration, budget, interests, and travel style
- **Parallel Processing**: Simultaneous research, budget analysis, and local experience discovery
- **Fast Inference**: Groq integration provides 10x faster responses than traditional OpenAI
- **Comprehensive Results**: Day-by-day plans with activities, restaurants, accommodations, and cultural tips

### Observability Features:
- **Arize Tracing**: Complete LangGraph workflow visualization
- **Performance Monitoring**: Latency tracking, token usage, and success rates
- **Prompt Template Versioning**: Track and optimize prompts over time
- **Error Debugging**: Full trace context for debugging issues

### Data Management:
- **Airtable Integration**: Export traces for manual labeling
- **Quality Assessment**: Label trip plans as excellent/good/poor
- **Evaluation Pipeline**: Analyze labeled data for model improvements

## 3. URL Routes & API Endpoints

### Backend API (FastAPI - Port 8000):
- `GET /` - Welcome page
- `POST /plan-trip` - Main endpoint for trip planning
  - Request: `{destination, duration, budget, interests, travel_style}`
  - Response: Markdown-formatted itinerary
- `GET /health` - Health check endpoint
- `GET /docs` - Swagger API documentation
- `GET /traces/unlabeled` - Fetch unlabeled traces (Airtable)
- `POST /traces/{record_id}/label` - Update trace labels
- `GET /evaluation/export` - Export labeled data

### Frontend Routes (React - Port 3000):
- `/` - Main application page with trip planner form and results display

## 4. Architecture

### Frontend Stack:
- **Framework**: React 19 with TypeScript
- **UI Library**: Material-UI (MUI) v7
- **State Management**: React hooks (useState)
- **HTTP Client**: Fetch API
- **Markdown Rendering**: react-markdown
- **Build Tool**: Create React App

### Backend Stack:
- **Framework**: FastAPI with async support
- **LLM Orchestration**: LangGraph for workflow management
- **LLM Provider**: Groq (primary) with OpenAI fallback via LiteLLM
- **Observability**: Arize with OpenTelemetry instrumentation
- **Data Storage**: Airtable for trace storage
- **Tools**: LangChain tools, Tavily search

### LangGraph Workflow:
```
START → [Parallel Execution] → Itinerary → END
         ├── Research Node (destination analysis)
         ├── Budget Node (cost breakdown)
         └── Local Experiences Node (authentic recommendations)
```

### Key Components:
- **Research Node**: Analyzes destination, weather, attractions
- **Budget Node**: Provides cost breakdowns and money-saving tips
- **Local Experiences Node**: Curates hidden gems and cultural tips
- **Itinerary Node**: Combines all data into day-by-day plan

## 5. Deployment Instructions

### Docker Deployment (Recommended):
```bash
# 1. Clone repository
git clone <repository>
cd ai-trip-planner

# 2. Setup environment variables
cp backend/env_example.txt backend/.env
# Edit .env with your API keys

# 3. Build and run with Docker Compose
docker-compose up --build

# Access at:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
```

### Local Development:
```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Frontend setup (new terminal)
cd frontend
npm install
npm start
```

### Quick Start Script:
```bash
./start.sh  # Runs both frontend and backend
```

### Environment Variables Required:
```bash
# Required
GROQ_API_KEY=your_groq_key
ARIZE_SPACE_ID=your_space_id
ARIZE_API_KEY=your_arize_key

# Optional
TAVILY_API_KEY=for_web_search
OPENAI_API_KEY=fallback_llm
AIRTABLE_API_KEY=data_labeling
AIRTABLE_BASE_ID=your_base_id
```

## 6. Testing Instructions

### Frontend Testing:
```bash
cd frontend
npm test                    # Run test suite
npm test -- --coverage     # With coverage report
npm test -- --watchAll     # Watch mode for development
```

### Backend Testing:
```bash
cd backend
# Manual API testing
curl http://localhost:8000/health

# Test trip planning endpoint
curl -X POST http://localhost:8000/plan-trip \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Tokyo, Japan",
    "duration": "7 days",
    "budget": "$2000",
    "interests": "food, culture",
    "travel_style": "cultural"
  }'
```

### Synthetic Data Testing:
```bash
cd backend
python generate_itineraries.py  # Generates 15 test cases
```

### Performance Testing:
- Monitor in Arize dashboard at https://app.arize.com
- Check latency metrics (target: <15 seconds)
- Verify parallel node execution
- Review token usage and costs

### Integration Testing:
1. Start both services
2. Submit trip request from frontend
3. Verify response renders correctly
4. Check Arize traces appear
5. Test error handling with invalid inputs

## 7. Project Structure
```
ai-trip-planner/
├── backend/
│   ├── main.py                 # FastAPI app & LangGraph workflow
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables
│   ├── Dockerfile             # Backend container
│   └── generate_itineraries.py # Test data generator
├── frontend/
│   ├── src/
│   │   ├── App.tsx            # Main React component
│   │   ├── components/
│   │   │   ├── TripPlannerForm.tsx  # Input form
│   │   │   └── TripResults.tsx      # Results display
│   │   └── types/
│   │       └── trip.ts        # TypeScript interfaces
│   ├── package.json           # Node dependencies
│   └── Dockerfile            # Frontend container
├── docker-compose.yml         # Container orchestration
├── start.sh                  # Quick start script
├── CLAUDE.md                 # This file - codebase overview
└── README.md                 # User documentation
```

## 8. Key Configuration Files
- **Backend**: `requirements.txt`, `.env`, `Dockerfile`
- **Frontend**: `package.json`, `tsconfig.json`, `Dockerfile`
- **Deployment**: `docker-compose.yml`, `start.sh`

## 9. Development Workflow

### Making Changes:
1. Backend changes: Edit `backend/main.py`, restart server
2. Frontend changes: Edit React components, auto-reloads
3. Test changes locally before committing
4. Monitor Arize for performance impact

### Common Tasks:
- **Add new LangGraph node**: Update `StateGraph` in main.py
- **Modify prompts**: Edit prompt templates in tool functions
- **Update UI**: Modify components in `frontend/src/components/`
- **Add API endpoint**: Add route decorator in main.py
- **Change LLM model**: Update `model` parameter in LiteLLM config

### Debugging:
- Check backend logs: `docker-compose logs backend`
- Check frontend console: Browser developer tools
- View Arize traces: https://app.arize.com
- Test API directly: http://localhost:8000/docs

## 10. Performance Optimization Notes

### Current Optimizations:
- Parallel node execution reduces latency by 3x
- Groq provides 10x faster inference than OpenAI
- Token limits keep responses concise (2000 max)
- 30-second timeout prevents hanging requests

### Monitoring Metrics:
- **Target Latency**: <15 seconds end-to-end
- **Success Rate**: >95%
- **Token Usage**: ~1000-1500 per request
- **Parallel Efficiency**: 3 nodes running simultaneously

This application is production-ready with comprehensive monitoring, fast performance, and clean architecture suitable for scaling to handle multiple concurrent users.