# Tests for AI Trip Planner

This directory contains simplified, comprehensive tests for the AI Trip Planner application.

## Simplified Test Structure

```
tests/
├── __init__.py          # Package initialization
├── conftest.py         # pytest configuration and shared fixtures
├── test_api.py         # All API, backend, and helper tests (13 tests)
├── test_phoenix.py     # Phoenix observability tests (7 tests)  
└── README.md          # This file
```

**Total: 20 tests covering all functionality**

## Running Tests

### Using pytest (recommended)
```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::TestHealthEndpoint::test_health_check
```

### Using uv
```bash
uv run pytest tests/ -v
```

## Test Coverage

### `test_api.py` - Complete Application Testing (13 tests)
- **Backend Initialization** (2 tests): Configuration, imports, app setup
- **Helper Functions** (2 tests): Error handling, request building
- **Health Endpoint** (1 test): Service status check
- **Frontend Endpoint** (1 test): Static file serving  
- **Trip Planning API** (7 tests): Full API functionality including success cases, error handling, validation, and edge cases

*Note: Model validation is covered implicitly by the API tests*

### `test_phoenix.py` - Observability Testing (7 tests)
- Phoenix module imports and availability
- Backend integration with/without Phoenix
- Tracing attribute helpers
- Error tracing functionality

## Configuration

### Auto-Setup
Tests automatically configure:
- `OPENROUTER_API_KEY=test-key-12345`
- `TESTING=true`

### Available Fixtures
- `app_client`: FastAPI test client
- `sample_trip_request`: Complete test request
- `minimal_trip_request`: Minimal valid request
- `mock_openrouter_response`: Successful API response mock
- `mock_openrouter_error`: Error API response mock
- `phoenix_tracer`: Phoenix tracer for observability tests

## Simplified Features

✅ **All external API calls are mocked** - no real API requests  
✅ **Tests run fast** - under 4 seconds for full suite  
✅ **No complex setup** - pytest handles everything  
✅ **Comprehensive coverage** - tests all endpoints and error cases  
✅ **Phoenix optional** - tests pass even without Phoenix installed  

## Adding Tests

Simple pattern for new tests:
```python
class TestYourFeature:
    """Test your new feature"""
    
    def test_something(self, app_client):
        response = app_client.get("/your-endpoint")
        assert response.status_code == 200
```

## CI/CD Ready

Example GitHub Actions:
```yaml
- name: Run Tests
  run: |
    pip install -r requirements.txt
    pytest tests/ -v
```

The simplified test suite provides complete coverage with minimal complexity!