"""Integration tests for FastAPI endpoints."""

from unittest.mock import Mock, patch

import pytest

from main import TripRequest, TripResponse


class TestHealthEndpoint:
    """Tests for GET /health endpoint."""
    
    def test_health_endpoint(self, test_client):
        """Test health endpoint returns correct response."""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ai-trip-planner"


class TestFrontendEndpoint:
    """Tests for GET / endpoint."""
    
    def test_frontend_endpoint_exists(self, test_client):
        """Test frontend endpoint returns file or message."""
        response = test_client.get("/")
        assert response.status_code == 200
        # Either returns file or JSON message
        if response.headers.get("content-type", "").startswith("text/html"):
            assert len(response.content) > 0
        else:
            data = response.json()
            assert "message" in data


class TestPlanTripEndpoint:
    """Tests for POST /plan-trip endpoint."""
    
    def test_with_minimal_fields(self, test_client, sample_trip_request_minimal):
        """Test plan_trip with only required fields."""
        def mock_graph_invoke(state):
            return {
                "final": "Test itinerary",
                "tool_calls": []
            }
        
        with patch('main.build_graph') as mock_build:
            mock_graph = Mock()
            mock_graph.invoke = Mock(side_effect=mock_graph_invoke)
            mock_build.return_value = mock_graph
            
            response = test_client.post("/plan-trip", json=sample_trip_request_minimal)
        
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "tool_calls" in data
        assert data["result"] == "Test itinerary"
    
    def test_with_all_fields(self, test_client, sample_trip_request):
        """Test plan_trip with all optional fields."""
        sample_trip_request["session_id"] = "test-session-123"
        sample_trip_request["user_id"] = "user-456"
        sample_trip_request["turn_index"] = 1
        
        def mock_graph_invoke(state):
            return {
                "final": "Complete itinerary",
                "tool_calls": [
                    {"agent": "research", "tool": "essential_info", "args": {}}
                ]
            }
        
        with patch('main.build_graph') as mock_build:
            mock_graph = Mock()
            mock_graph.invoke = Mock(side_effect=mock_graph_invoke)
            mock_build.return_value = mock_graph
            
            response = test_client.post("/plan-trip", json=sample_trip_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "Complete itinerary"
        assert len(data["tool_calls"]) == 1
    
    def test_missing_destination(self, test_client):
        """Test plan_trip validation error for missing destination."""
        invalid_request = {
            "duration": "7 days"
        }
        
        response = test_client.post("/plan-trip", json=invalid_request)
        assert response.status_code == 422  # Validation error
    
    def test_missing_duration(self, test_client):
        """Test plan_trip validation error for missing duration."""
        invalid_request = {
            "destination": "Tokyo"
        }
        
        response = test_client.post("/plan-trip", json=invalid_request)
        assert response.status_code == 422  # Validation error
    
    def test_invalid_request_type(self, test_client):
        """Test plan_trip with invalid data types."""
        invalid_request = {
            "destination": 123,  # Should be string
            "duration": "7 days"
        }
        
        response = test_client.post("/plan-trip", json=invalid_request)
        assert response.status_code == 422  # Validation error
    
    def test_response_structure(self, test_client, sample_trip_request_minimal):
        """Test that response matches TripResponse model."""
        def mock_graph_invoke(state):
            return {
                "final": "Itinerary",
                "tool_calls": [
                    {"agent": "research", "tool": "weather_brief", "args": {"destination": "Tokyo"}},
                    {"agent": "budget", "tool": "budget_basics", "args": {"destination": "Tokyo", "duration": "7 days"}}
                ]
            }
        
        with patch('main.build_graph') as mock_build:
            mock_graph = Mock()
            mock_graph.invoke = Mock(side_effect=mock_graph_invoke)
            mock_build.return_value = mock_graph
            
            response = test_client.post("/plan-trip", json=sample_trip_request_minimal)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "result" in data
        assert "tool_calls" in data
        assert isinstance(data["result"], str)
        assert isinstance(data["tool_calls"], list)
        assert len(data["tool_calls"]) == 2
    
    def test_empty_tool_calls(self, test_client, sample_trip_request_minimal):
        """Test response when no tool calls are made."""
        def mock_graph_invoke(state):
            return {
                "final": "Itinerary without tools",
                "tool_calls": []
            }
        
        with patch('main.build_graph') as mock_build:
            mock_graph = Mock()
            mock_graph.invoke = Mock(side_effect=mock_graph_invoke)
            mock_build.return_value = mock_graph
            
            response = test_client.post("/plan-trip", json=sample_trip_request_minimal)
        
        assert response.status_code == 200
        data = response.json()
        assert data["tool_calls"] == []
    
    def test_missing_final_in_state(self, test_client, sample_trip_request_minimal):
        """Test handling when final is missing from graph state."""
        def mock_graph_invoke(state):
            return {
                "tool_calls": []
            }
        
        with patch('main.build_graph') as mock_build:
            mock_graph = Mock()
            mock_graph.invoke = Mock(side_effect=mock_graph_invoke)
            mock_build.return_value = mock_graph
            
            response = test_client.post("/plan-trip", json=sample_trip_request_minimal)
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == ""  # Empty string when missing
    
    def test_with_optional_fields_none(self, test_client):
        """Test plan_trip with None values for optional fields."""
        request = {
            "destination": "Tokyo",
            "duration": "7 days",
            "budget": None,
            "interests": None,
            "travel_style": None
        }
        
        def mock_graph_invoke(state):
            return {
                "final": "Itinerary",
                "tool_calls": []
            }
        
        with patch('main.build_graph') as mock_build:
            mock_graph = Mock()
            mock_graph.invoke = Mock(side_effect=mock_graph_invoke)
            mock_build.return_value = mock_graph
            
            response = test_client.post("/plan-trip", json=request)
        
        assert response.status_code == 200
    
    def test_state_construction(self, test_client, sample_trip_request):
        """Test that state is constructed correctly from request."""
        captured_state = {}
        
        def mock_graph_invoke(state):
            nonlocal captured_state
            captured_state = state.copy()
            return {
                "final": "Itinerary",
                "tool_calls": []
            }
        
        with patch('main.build_graph') as mock_build:
            mock_graph = Mock()
            mock_graph.invoke = Mock(side_effect=mock_graph_invoke)
            mock_build.return_value = mock_graph
            
            test_client.post("/plan-trip", json=sample_trip_request)
        
        # Verify state structure
        assert "messages" in captured_state
        assert "trip_request" in captured_state
        assert "tool_calls" in captured_state
        
        # Verify trip_request contains all fields
        trip_req = captured_state["trip_request"]
        assert trip_req["destination"] == sample_trip_request["destination"]
        assert trip_req["duration"] == sample_trip_request["duration"]
    
    def test_graph_invocation(self, test_client, sample_trip_request_minimal):
        """Test that graph is invoked correctly."""
        graph_invoked = False
        
        def mock_graph_invoke(state):
            nonlocal graph_invoked
            graph_invoked = True
            return {
                "final": "Itinerary",
                "tool_calls": []
            }
        
        with patch('main.build_graph') as mock_build:
            mock_graph = Mock()
            mock_graph.invoke = Mock(side_effect=mock_graph_invoke)
            mock_build.return_value = mock_graph
            
            test_client.post("/plan-trip", json=sample_trip_request_minimal)
        
        assert graph_invoked
        assert mock_build.called

