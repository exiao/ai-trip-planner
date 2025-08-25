"""
Tests for the AI Trip Planner API
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os
from unittest.mock import patch, MagicMock

# Set testing environment variable
os.environ["TESTING"] = "1"

# Add parent directory to path to import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "Simple AI Trip Planner"}


def test_serve_frontend():
    """Test that the frontend endpoint returns the HTML file"""
    response = client.get("/")
    assert response.status_code == 200
    # Check if it's returning HTML content
    assert "text/html" in response.headers["content-type"]


def test_plan_trip_stream_missing_fields():
    """Test the streaming endpoint with missing required fields"""
    response = client.post(
        "/api/plan-trip-stream",
        json={
            "budget": "moderate",
            "interests": "food"
            # Missing destination and duration
        }
    )
    assert response.status_code == 422  # Unprocessable Entity


def test_plan_trip_stream_endpoint_exists():
    """Test that streaming endpoint exists and requires proper fields"""
    # Test with valid request structure (not testing actual streaming)
    response = client.post(
        "/api/plan-trip-stream",
        json={
            "destination": "Paris",
            "duration": "5 days"
        }
    )
    # Should return 200 with streaming response (even if API key is missing)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")


def test_invalid_json_request():
    """Test the endpoint with invalid JSON"""
    response = client.post(
        "/api/plan-trip-stream",
        content='{"invalid json}',
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422 or response.status_code == 400


def test_empty_request_body():
    """Test the endpoint with empty request body"""
    response = client.post(
        "/api/plan-trip-stream",
        json={}
    )
    assert response.status_code == 422  # Missing required fields


if __name__ == "__main__":
    pytest.main([__file__, "-v"])