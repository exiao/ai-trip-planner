"""Shared pytest fixtures and test configuration."""

import os
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from unittest.mock import Mock, MagicMock

import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

# Set TEST_MODE before importing main to enable fake LLM
os.environ["TEST_MODE"] = "1"
os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("OPENROUTER_API_KEY", None)
os.environ.pop("ENABLE_RAG", None)

from main import app, TripRequest, LocalGuideRetriever
from tests.fixtures.sample_data import SAMPLE_LOCAL_GUIDES, SAMPLE_TRIP_REQUEST


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables for the entire test session."""
    # Ensure TEST_MODE is set
    os.environ["TEST_MODE"] = "1"
    # Disable RAG by default unless explicitly enabled in test
    os.environ.pop("ENABLE_RAG", None)
    yield
    # Cleanup
    os.environ.pop("TEST_MODE", None)


@pytest.fixture
def test_client():
    """FastAPI TestClient instance."""
    return TestClient(app)


@pytest.fixture
def sample_trip_request():
    """Sample TripRequest data."""
    return SAMPLE_TRIP_REQUEST.copy()


@pytest.fixture
def sample_trip_request_minimal():
    """Minimal TripRequest with only required fields."""
    return {
        "destination": "Tokyo, Japan",
        "duration": "7 days"
    }


@pytest.fixture
def mock_llm_response():
    """Mock LLM response object."""
    class MockResponse:
        def __init__(self, content: str = "Test response", tool_calls: Optional[list] = None):
            self.content = content
            self.tool_calls = tool_calls or []
    
    return MockResponse


@pytest.fixture
def mock_llm_with_tool_calls():
    """Mock LLM that returns tool calls."""
    def create_mock_llm(tool_calls: list):
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = ""
        mock_response.tool_calls = tool_calls
        mock_llm.invoke = Mock(return_value=mock_response)
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        return mock_llm
    return create_mock_llm


@pytest.fixture
def mock_search_api_success(monkeypatch):
    """Mock _search_api to return successful results."""
    def mock_search(query: str) -> Optional[str]:
        return f"Mock search result for: {query[:50]}"
    
    import main
    monkeypatch.setattr(main, "_search_api", mock_search)
    return mock_search


@pytest.fixture
def mock_search_api_failure(monkeypatch):
    """Mock _search_api to return None (triggers LLM fallback)."""
    def mock_search(query: str) -> Optional[str]:
        return None
    
    import main
    monkeypatch.setattr(main, "_search_api", mock_search)
    return mock_search


@pytest.fixture
def mock_llm_fallback(monkeypatch):
    """Mock _llm_fallback to return predictable responses."""
    def mock_fallback(instruction: str, context: Optional[str] = None) -> str:
        return f"LLM fallback response for: {instruction[:50]}"
    
    import main
    monkeypatch.setattr(main, "_llm_fallback", mock_fallback)
    return mock_fallback


@pytest.fixture
def temp_local_guides_file(tmp_path):
    """Create a temporary local_guides.json file for testing."""
    guides_file = tmp_path / "local_guides.json"
    guides_file.write_text(json.dumps(SAMPLE_LOCAL_GUIDES, indent=2))
    return guides_file


@pytest.fixture
def temp_empty_guides_file(tmp_path):
    """Create an empty local_guides.json file."""
    guides_file = tmp_path / "local_guides.json"
    guides_file.write_text(json.dumps([], indent=2))
    return guides_file


@pytest.fixture
def temp_malformed_guides_file(tmp_path):
    """Create a malformed JSON file."""
    guides_file = tmp_path / "local_guides.json"
    guides_file.write_text("{ invalid json }")
    return guides_file


@pytest.fixture
def temp_nonexistent_file(tmp_path):
    """Return path to a non-existent file."""
    return tmp_path / "nonexistent.json"


@pytest.fixture
def mock_retriever_with_data():
    """Create a LocalGuideRetriever with sample data."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(SAMPLE_LOCAL_GUIDES, f)
        temp_path = Path(f.name)
    
    retriever = LocalGuideRetriever(temp_path)
    yield retriever
    
    # Cleanup
    temp_path.unlink()


@pytest.fixture
def mock_retriever_empty():
    """Create an empty LocalGuideRetriever."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump([], f)
        temp_path = Path(f.name)
    
    retriever = LocalGuideRetriever(temp_path)
    yield retriever
    
    # Cleanup
    temp_path.unlink()


@pytest.fixture
def mock_tool_node(monkeypatch):
    """Mock ToolNode.invoke to return predictable tool results."""
    from langchain_core.messages import AIMessage, ToolMessage
    
    def mock_invoke(state: Dict[str, Any]) -> Dict[str, Any]:
        messages = state.get("messages", [])
        tool_results = []
        for msg in messages:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tool_result = ToolMessage(
                        content=f"Mock result for {tool_call['name']}",
                        tool_call_id=tool_call.get("id", "test-id")
                    )
                    tool_results.append(tool_result)
        return {"messages": tool_results}
    
    from langgraph.prebuilt import ToolNode
    original_invoke = ToolNode.invoke
    ToolNode.invoke = mock_invoke
    yield mock_invoke
    ToolNode.invoke = original_invoke


@pytest.fixture
def sample_trip_state():
    """Sample TripState for testing agents."""
    return {
        "messages": [],
        "trip_request": SAMPLE_TRIP_REQUEST.copy(),
        "research": None,
        "budget": None,
        "local": None,
        "final": None,
        "tool_calls": []
    }

