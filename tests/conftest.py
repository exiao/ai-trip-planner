"""
pytest configuration and shared fixtures for AI Trip Planner tests
"""

import os
import sys
from pathlib import Path
import pytest
from unittest.mock import Mock

# Add backend directory to Python path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables"""
    os.environ['OPENROUTER_API_KEY'] = 'test-key-12345'
    os.environ['TESTING'] = 'true'
    yield
    # Cleanup after test
    if 'TESTING' in os.environ:
        del os.environ['TESTING']

@pytest.fixture
def mock_openrouter_response():
    """Mock successful OpenRouter API response"""
    response_data = {
        'choices': [{
            'message': {
                'content': """# 3-Day Tokyo Itinerary

## Day 1: Traditional Tokyo
**Morning**: Visit Senso-ji Temple in Asakusa
**Afternoon**: Explore Meiji Shrine and Harajuku
**Evening**: Dinner in Shibuya

## Day 2: Modern Tokyo  
**Morning**: Tokyo Skytree observation deck
**Afternoon**: Akihabara electronics district
**Evening**: Ginza shopping and dining

## Day 3: Culture & Food
**Morning**: Tsukiji Outer Market food tour
**Afternoon**: Imperial Palace gardens
**Evening**: Izakaya experience in Shinjuku

**Budget**: ~$300 per day including meals and activities
**Transportation**: Get a 3-day Tokyo Metro pass for $28"""
            }
        }],
        'model': 'openai/gpt-oss-20b',
        'usage': {'total_tokens': 245}
    }
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = response_data
    return mock_response

@pytest.fixture
def mock_openrouter_error():
    """Mock OpenRouter API error response"""
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.headers = {'content-type': 'application/json'}
    mock_response.json.return_value = {
        'error': {
            'message': 'Rate limit exceeded. Please wait before making another request.'
        }
    }
    return mock_response

@pytest.fixture
def sample_trip_request():
    """Sample trip request data"""
    return {
        "destination": "Tokyo",
        "duration": "3 days", 
        "budget": "moderate",
        "interests": "food, culture, technology"
    }

@pytest.fixture
def minimal_trip_request():
    """Minimal trip request with only required fields"""
    return {
        "destination": "Paris",
        "duration": "2 days"
    }

@pytest.fixture
def app_client():
    """FastAPI test client"""
    import backend
    from fastapi.testclient import TestClient
    return TestClient(backend.app)

@pytest.fixture
def phoenix_tracer():
    """Phoenix tracer for testing tracing functionality"""
    from phoenix.otel import register
    tracer_provider = register(project_name='test-project')
    return tracer_provider.get_tracer(__name__)