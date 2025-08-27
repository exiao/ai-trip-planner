"""
Test API endpoints, backend functionality, and request/response handling
"""

import pytest
from unittest.mock import patch, Mock
import json
import sys
from pathlib import Path

# Add backend directory to path  
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

class TestBackendInitialization:
    """Test backend initialization and configuration"""
    
    def test_backend_imports_successfully(self):
        """Test that backend imports without errors"""
        import backend
        
        assert hasattr(backend, 'app'), "FastAPI app not created"
        assert backend.app.title == "Simple AI Trip Planner"
        assert hasattr(backend, 'CONFIG'), "CONFIG not defined"
        assert hasattr(backend, 'ERROR_MESSAGES'), "ERROR_MESSAGES not defined"
    
    def test_configuration_values(self):
        """Test configuration is set correctly"""
        import backend
        
        assert backend.CONFIG["model"] == "openai/gpt-oss-20b"
        assert backend.CONFIG["api_url"] == "https://openrouter.ai/api/v1"
        assert isinstance(backend.CONFIG["fallback_models"], list)
        assert len(backend.CONFIG["fallback_models"]) > 0


class TestHelperFunctions:
    """Test helper functions"""
    
    def test_get_error_message(self):
        """Test error message formatting"""
        import backend
        
        # Test credit error
        credit_error = backend.get_error_message("Credit limit exceeded")
        assert "Free tier limit reached" in credit_error
        
        # Test API key error
        api_error = backend.get_error_message("Invalid API key provided")
        assert "Invalid API key" in api_error
        
        # Test generic error
        generic_error = backend.get_error_message("Random error")
        assert generic_error == "Random error"
    
    def test_create_api_request(self, sample_trip_request):
        """Test API request creation"""
        import backend
        
        request = backend.TripRequest(**sample_trip_request)
        api_data = backend.create_api_request(request)
        
        assert api_data["model"] == backend.CONFIG["model"]
        assert len(api_data["messages"]) == 2
        assert api_data["messages"][0]["role"] == "system"
        assert api_data["messages"][1]["role"] == "user"
        assert sample_trip_request["destination"] in api_data["messages"][1]["content"]

class TestHealthEndpoint:
    """Test the health check endpoint"""
    
    def test_health_check(self, app_client):
        """Test health endpoint returns correct status"""
        response = app_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Simple AI Trip Planner"

class TestFrontendEndpoint:
    """Test the frontend serving endpoint"""
    
    def test_frontend_endpoint(self, app_client):
        """Test frontend endpoint responds appropriately"""
        response = app_client.get("/")
        
        # Should either serve frontend file or return not found message
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            # If serving file, should be HTML content
            assert response.headers.get("content-type") is not None
        else:
            # If not found, should return JSON message
            data = response.json()
            assert "Frontend not found" in data["message"]

class TestTripPlanningEndpoint:
    """Test the main trip planning API endpoint"""
    
    @patch('requests.post')
    def test_successful_trip_planning(self, mock_post, app_client, sample_trip_request, mock_openrouter_response):
        """Test successful trip planning request"""
        mock_post.return_value = mock_openrouter_response
        
        response = app_client.post("/api/plan-trip", json=sample_trip_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert data["success"] is True
        assert data["itinerary"] is not None
        assert data["error"] is None
        
        # Check itinerary content
        itinerary = data["itinerary"]
        assert "Tokyo" in itinerary
        assert "Day 1" in itinerary
        
        # Verify API was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        # Check URL
        assert "chat/completions" in call_args[0][0]
        
        # Check headers
        headers = call_args[1]['headers']
        assert "Authorization" in headers
        assert "Bearer" in headers["Authorization"]
        
        # Check request data
        api_data = call_args[1]['json']
        assert api_data['model'] == 'openai/gpt-oss-20b'
        assert len(api_data['messages']) == 2
        assert api_data['messages'][0]['role'] == 'system'
        assert sample_trip_request['destination'] in api_data['messages'][1]['content']
    
    @patch('requests.post')
    def test_rate_limit_error(self, mock_post, app_client, sample_trip_request, mock_openrouter_error):
        """Test rate limit error handling"""
        mock_post.return_value = mock_openrouter_error
        
        response = app_client.post("/api/plan-trip", json=sample_trip_request)
        
        assert response.status_code == 200  # FastAPI returns 200 with error in body
        data = response.json()
        
        assert data["success"] is False
        assert data["itinerary"] is None
        assert data["error"] is not None
        assert "limit" in data["error"].lower()
    
    @patch('requests.post')
    def test_api_key_error(self, mock_post, app_client, sample_trip_request):
        """Test API key error handling"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {
            'error': {'message': 'Invalid API key provided'}
        }
        mock_post.return_value = mock_response
        
        response = app_client.post("/api/plan-trip", json=sample_trip_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert "API key" in data["error"]
    
    def test_missing_api_key(self, app_client, sample_trip_request):
        """Test handling when API key is not configured"""
        import backend
        
        # Temporarily remove API key
        original_key = backend.OPENROUTER_API_KEY
        backend.OPENROUTER_API_KEY = None
        
        try:
            response = app_client.post("/api/plan-trip", json=sample_trip_request)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is False
            assert "API key not configured" in data["error"]
        finally:
            # Restore original key
            backend.OPENROUTER_API_KEY = original_key
    
    def test_invalid_request_data(self, app_client):
        """Test handling of invalid request data"""
        invalid_requests = [
            {},  # Empty request
            {"destination": "Tokyo"},  # Missing duration
            {"duration": "3 days"},  # Missing destination
        ]
        
        for invalid_request in invalid_requests:
            response = app_client.post("/api/plan-trip", json=invalid_request)
            assert response.status_code == 422  # Validation error
    
    def test_minimal_valid_request(self, app_client, minimal_trip_request):
        """Test minimal valid request with defaults"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [{'message': {'content': 'Simple Paris itinerary'}}],
                'model': 'openai/gpt-oss-20b',
                'usage': {'total_tokens': 100}
            }
            mock_post.return_value = mock_response
            
            response = app_client.post("/api/plan-trip", json=minimal_trip_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            # Check that defaults were used in API call
            call_args = mock_post.call_args
            api_data = call_args[1]['json']
            user_message = api_data['messages'][1]['content']
            assert "moderate" in user_message  # Default budget
            assert "general sightseeing" in user_message  # Default interests
    
    @patch('requests.post')
    def test_network_error_handling(self, mock_post, app_client, sample_trip_request):
        """Test network error handling"""
        mock_post.side_effect = Exception("Network connection failed")
        
        response = app_client.post("/api/plan-trip", json=sample_trip_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert data["error"] is not None