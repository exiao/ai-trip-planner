# AI Trip Planner - Codebase Summary

## Codebase overview

A production-ready multi-agent AI system for generating personalized travel itineraries. Built with FastAPI, LangGraph, and LangChain, demonstrating three essential AI engineering patterns: multi-agent orchestration, RAG (Retrieval-Augmented Generation), and API integration with graceful degradation. The system uses 4 specialized agents running in parallel to research destinations, analyze budgets, suggest local experiences, and synthesize complete itineraries.

## Product features

- **Multi-Agent Orchestration**: 4 parallel agents (Research, Budget, Local, Itinerary) using LangGraph for coordinated execution
- **RAG System**: Optional vector search over 90+ curated local guides from `backend/data/local_guides.json` (enable with `ENABLE_RAG=1`)
- **Real-Time Web Search**: Integration with Tavily/SerpAPI for up-to-date travel data, with LLM fallback when APIs unavailable
- **Observability**: Full tracing via Arize for debugging agent execution, tool calls, and LLM usage
- **Graceful Degradation**: Works without API keys using LLM-generated responses as fallback
- **Performance**: Parallel execution achieves 22% faster response times (6.6s vs 8.5s)

## Folder structure

```
ai-trip-planner/
├── backend/                    # FastAPI application
│   ├── main.py                 # Core app: agents, tools, LangGraph workflow
│   ├── requirements.txt        # Python dependencies
│   ├── data/
│   │   └── local_guides.json  # 90+ curated experiences for RAG
│   └── .env                   # Environment variables (not in repo)
├── frontend/
│   └── index.html             # Minimal UI (served at /)
├── optional/
│   └── airtable/              # Optional Airtable integration
├── test scripts/              # Testing utilities
│   └── synthetic_data_gen.py  # Test data generator
├── start.sh                   # Startup script
├── render.yaml                # Render.com deployment config
├── README.md                  # Main documentation
├── IMPLEMENTATION_SPEC.md     # Architecture details
├── API_INTEGRATION_SPEC.md    # API integration roadmap
└── RAG.md                     # RAG feature docs
```

## Building the app

### Prerequisites
- Python 3.10+
- One LLM API key: `OPENAI_API_KEY` or `OPENROUTER_API_KEY`
- Optional: `ARIZE_SPACE_ID` + `ARIZE_API_KEY` for tracing
- Optional: `TAVILY_API_KEY` or `SERPAPI_API_KEY` for web search
- Optional: `ENABLE_RAG=1` for vector search

### Setup
```bash
# 1. Configure environment
cd backend
# Create .env file with your API keys

# 2. Install dependencies
uv pip install -r requirements.txt
# Or: pip install -r requirements.txt

# 3. Run the app
cd ..
./start.sh
# Or: cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Access
- Frontend UI: http://localhost:8000/
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Testing

### Running the Test Suite

The backend includes a comprehensive test suite covering all components. Run tests using the Makefile:

```bash
make test              # Run all tests with verbose output
make test-verbose      # Run tests with extra verbose output
make test-coverage     # Run tests with coverage report (HTML + terminal)
```

Or run pytest directly:
```bash
cd backend
pytest tests/ -v                    # Run all tests
pytest tests/test_api.py -v         # Run API tests only
pytest tests/ -k "test_retriever"   # Run specific test file/pattern
pytest tests/ --cov=main --cov-report=html  # With coverage
```

### Test Coverage

The test suite includes:
- **Unit Tests**: Tools, RAG retriever, agents (all functions tested with mocks)
- **Integration Tests**: LangGraph workflow, API endpoints
- **Coverage Goals**: 90%+ coverage across all components
- **Fast Execution**: All tests run in <5 seconds (no external API calls)

### Quick API Test
```bash
curl -X POST http://localhost:8000/plan-trip \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Tokyo, Japan",
    "duration": "7 days",
    "budget": "$2000",
    "interests": "food, culture"
  }'
```

### Test Scripts
```bash
python "test scripts/test_api.py"
python "test scripts/synthetic_data_gen.py" --base-url http://localhost:8000 --count 12
```

### Manual Testing
1. Open http://localhost:8000/
2. Fill form: destination, duration, budget, interests
3. Click "Plan My Trip"
4. View generated itinerary

### Observability
If Arize configured, view traces at https://app.arize.com/ to see:
- Parallel agent execution
- Tool calls and results
- LLM token usage
- RAG retrieval (if enabled)

## HOW TO CODE

Follow these principles for clean, maintainable code:

### Simplicity
- Write code that solves the problem directly, without unnecessary abstraction
- Prefer straightforward solutions over clever ones
- If you can't explain it simply, simplify it
- Remove code that doesn't add value

### Readability
- Use descriptive variable and function names that explain intent
- Write self-documenting code with clear structure
- Add comments only when code can't explain itself
- Format consistently and follow language conventions
- Break complex logic into smaller, named functions

### Incremental Building
- Start with a working minimal version, then iterate
- Build one feature at a time and test before moving on
- Make small, focused commits that build on each other
- Get feedback early rather than building everything first
- Refactor as you learn, not all at once

### Use Standard Libraries
- Prefer standard library and well-established packages over custom solutions
- Leverage existing, tested code rather than reinventing
- Use the right tool for the job from the ecosystem
- Only add dependencies when they provide clear value
- Document why you chose a library over alternatives

### No Premature Optimization
- Write correct, readable code first
- Measure performance before optimizing
- Optimize only when there's a proven bottleneck
- Prefer clarity over micro-optimizations
- Remember: "Premature optimization is the root of all evil" (Knuth)