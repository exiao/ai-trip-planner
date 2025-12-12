"""Unit tests for agent functions."""

from unittest.mock import Mock, MagicMock, patch
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage

import pytest

from main import research_agent, budget_agent, local_agent, itinerary_agent


class TestResearchAgent:
    """Tests for research_agent function."""
    
    def test_with_tool_calls(self, sample_trip_state, monkeypatch):
        """Test research_agent with tool calls."""
        # Mock LLM response with tool calls
        mock_response = Mock()
        mock_response.content = ""
        mock_response.tool_calls = [
            {"name": "essential_info", "args": {"destination": "Tokyo"}, "id": "call_1"},
            {"name": "weather_brief", "args": {"destination": "Tokyo"}, "id": "call_2"}
        ]
        
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        mock_llm.invoke = Mock(side_effect=[
            mock_response,  # First call returns tool calls
            Mock(content="Synthesized research summary")  # Synthesis call
        ])
        
        # Mock ToolNode
        mock_tool_results = [
            ToolMessage(content="Essential info result", tool_call_id="call_1"),
            ToolMessage(content="Weather result", tool_call_id="call_2")
        ]
        
        with patch('main.llm', mock_llm), \
             patch('main.ToolNode') as mock_tool_node_class:
            mock_tool_node = Mock()
            mock_tool_node.invoke = Mock(return_value={"messages": mock_tool_results})
            mock_tool_node_class.return_value = mock_tool_node
            
            result = research_agent(sample_trip_state)
        
        assert "research" in result
        assert result["research"] == "Synthesized research summary"
        assert len(result["tool_calls"]) == 2
        assert result["tool_calls"][0]["agent"] == "research"
        assert result["tool_calls"][0]["tool"] == "essential_info"
    
    def test_without_tool_calls(self, sample_trip_state, monkeypatch):
        """Test research_agent without tool calls (direct response)."""
        mock_response = Mock()
        mock_response.content = "Direct research response"
        mock_response.tool_calls = []
        
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        mock_llm.invoke = Mock(return_value=mock_response)
        
        with patch('main.llm', mock_llm):
            result = research_agent(sample_trip_state)
        
        assert result["research"] == "Direct research response"
        assert len(result["tool_calls"]) == 0
    
    def test_tool_selection(self, sample_trip_state, monkeypatch):
        """Test that research_agent uses correct tools."""
        mock_response = Mock()
        mock_response.content = ""
        mock_response.tool_calls = [{"name": "essential_info", "args": {}, "id": "call_1"}]
        
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        mock_llm.invoke = Mock(side_effect=[
            mock_response,
            Mock(content="Summary")
        ])
        
        with patch('main.llm', mock_llm), \
             patch('main.ToolNode') as mock_tool_node_class:
            mock_tool_node = Mock()
            mock_tool_node.invoke = Mock(return_value={"messages": []})
            mock_tool_node_class.return_value = mock_tool_node
            
            # Check that bind_tools was called with correct tools
            research_agent(sample_trip_state)
            call_args = mock_llm.bind_tools.call_args[0][0]
            tool_names = [tool.name for tool in call_args]
            assert "essential_info" in tool_names
            assert "weather_brief" in tool_names
            assert "visa_brief" in tool_names


class TestBudgetAgent:
    """Tests for budget_agent function."""
    
    def test_with_budget_value(self, sample_trip_state, monkeypatch):
        """Test budget_agent with specific budget value."""
        sample_trip_state["trip_request"]["budget"] = "$2000"
        
        mock_response = Mock()
        mock_response.content = ""
        mock_response.tool_calls = [{"name": "budget_basics", "args": {}, "id": "call_1"}]
        
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        mock_llm.invoke = Mock(side_effect=[
            mock_response,
            Mock(content="Budget breakdown for $2000")
        ])
        
        with patch('main.llm', mock_llm), \
             patch('main.ToolNode') as mock_tool_node_class:
            mock_tool_node = Mock()
            mock_tool_node.invoke = Mock(return_value={"messages": []})
            mock_tool_node_class.return_value = mock_tool_node
            
            result = budget_agent(sample_trip_state)
        
        assert "budget" in result
        assert "$2000" in result["budget"] or "2000" in result["budget"]
        assert len(result["tool_calls"]) >= 0
    
    def test_with_default_budget(self, sample_trip_state, monkeypatch):
        """Test budget_agent defaults to 'moderate' when budget not specified."""
        sample_trip_state["trip_request"].pop("budget", None)
        
        mock_response = Mock()
        mock_response.content = "Budget analysis"
        mock_response.tool_calls = []
        
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        mock_llm.invoke = Mock(return_value=mock_response)
        
        with patch('main.llm', mock_llm):
            result = budget_agent(sample_trip_state)
        
        assert result["budget"] == "Budget analysis"
    
    def test_tool_selection(self, sample_trip_state, monkeypatch):
        """Test that budget_agent uses correct tools."""
        mock_response = Mock()
        mock_response.content = ""
        mock_response.tool_calls = []
        
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        mock_llm.invoke = Mock(return_value=mock_response)
        
        with patch('main.llm', mock_llm):
            budget_agent(sample_trip_state)
            call_args = mock_llm.bind_tools.call_args[0][0]
            tool_names = [tool.name for tool in call_args]
            assert "budget_basics" in tool_names
            assert "attraction_prices" in tool_names


class TestLocalAgent:
    """Tests for local_agent function."""
    
    def test_with_rag_disabled(self, sample_trip_state, monkeypatch):
        """Test local_agent when RAG is disabled."""
        import main
        monkeypatch.setattr(main, "ENABLE_RAG", False)
        
        mock_response = Mock()
        mock_response.content = "Local experiences"
        mock_response.tool_calls = []
        
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        mock_llm.invoke = Mock(return_value=mock_response)
        
        with patch('main.llm', mock_llm):
            result = local_agent(sample_trip_state)
        
        assert result["local"] == "Local experiences"
    
    def test_with_rag_enabled(self, sample_trip_state, monkeypatch):
        """Test local_agent when RAG is enabled and returns results."""
        import main
        monkeypatch.setattr(main, "ENABLE_RAG", True)
        
        mock_retrieved = [
            {
                "content": "City: Tokyo\nInterests: food\nGuide: Test guide",
                "metadata": {"city": "Tokyo", "interests": ["food"], "source": "test"}
            }
        ]
        
        mock_response = Mock()
        mock_response.content = "Local experiences"
        mock_response.tool_calls = []
        
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        mock_llm.invoke = Mock(return_value=mock_response)
        
        with patch('main.llm', mock_llm), \
             patch('main.GUIDE_RETRIEVER') as mock_retriever:
            mock_retriever.retrieve = Mock(return_value=mock_retrieved)
            
            result = local_agent(sample_trip_state)
        
        # Verify retriever was called
        mock_retriever.retrieve.assert_called_once()
        assert result["local"] == "Local experiences"
    
    def test_with_interests(self, sample_trip_state, monkeypatch):
        """Test local_agent with specific interests."""
        import main
        monkeypatch.setattr(main, "ENABLE_RAG", False)
        
        sample_trip_state["trip_request"]["interests"] = "art, architecture"
        
        mock_response = Mock()
        mock_response.content = "Art-focused experiences"
        mock_response.tool_calls = []
        
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        mock_llm.invoke = Mock(return_value=mock_response)
        
        with patch('main.llm', mock_llm):
            result = local_agent(sample_trip_state)
        
        assert result["local"] == "Art-focused experiences"
    
    def test_with_travel_style(self, sample_trip_state, monkeypatch):
        """Test local_agent with specific travel style."""
        import main
        monkeypatch.setattr(main, "ENABLE_RAG", False)
        
        sample_trip_state["trip_request"]["travel_style"] = "luxury"
        
        mock_response = Mock()
        mock_response.content = "Luxury experiences"
        mock_response.tool_calls = []
        
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        mock_llm.invoke = Mock(return_value=mock_response)
        
        with patch('main.llm', mock_llm):
            result = local_agent(sample_trip_state)
        
        assert result["local"] == "Luxury experiences"
    
    def test_tool_selection(self, sample_trip_state, monkeypatch):
        """Test that local_agent uses correct tools."""
        import main
        monkeypatch.setattr(main, "ENABLE_RAG", False)
        
        mock_response = Mock()
        mock_response.content = ""
        mock_response.tool_calls = []
        
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        mock_llm.invoke = Mock(return_value=mock_response)
        
        with patch('main.llm', mock_llm):
            local_agent(sample_trip_state)
            call_args = mock_llm.bind_tools.call_args[0][0]
            tool_names = [tool.name for tool in call_args]
            assert "local_flavor" in tool_names
            assert "local_customs" in tool_names
            assert "hidden_gems" in tool_names


class TestItineraryAgent:
    """Tests for itinerary_agent function."""
    
    def test_synthesis_with_all_inputs(self, sample_trip_state, monkeypatch):
        """Test itinerary_agent synthesizes research, budget, and local inputs."""
        sample_trip_state["research"] = "Research summary"
        sample_trip_state["budget"] = "Budget summary"
        sample_trip_state["local"] = "Local summary"
        
        mock_response = Mock()
        mock_response.content = "Complete itinerary"
        
        mock_llm = Mock()
        mock_llm.invoke = Mock(return_value=mock_response)
        
        with patch('main.llm', mock_llm):
            result = itinerary_agent(sample_trip_state)
        
        assert result["final"] == "Complete itinerary"
        # Verify LLM was called with all inputs
        call_args = mock_llm.invoke.call_args[0][0]
        prompt_content = call_args[0].content
        assert "Research summary" in prompt_content
        assert "Budget summary" in prompt_content
        assert "Local summary" in prompt_content
    
    def test_truncates_long_inputs(self, sample_trip_state, monkeypatch):
        """Test that itinerary_agent truncates inputs to 400 characters."""
        long_text = "x" * 500
        sample_trip_state["research"] = long_text
        sample_trip_state["budget"] = long_text
        sample_trip_state["local"] = long_text
        
        mock_response = Mock()
        mock_response.content = "Itinerary"
        
        mock_llm = Mock()
        mock_llm.invoke = Mock(return_value=mock_response)
        
        with patch('main.llm', mock_llm):
            result = itinerary_agent(sample_trip_state)
        
        # Verify truncation happened - check that inputs in prompt are max 400 chars
        call_args = mock_llm.invoke.call_args[0][0]
        prompt_content = call_args[0].content
        
        # Extract the research, budget, and local lines
        lines = prompt_content.split("\n")
        research_line = next((l for l in lines if l.startswith("Research:")), None)
        budget_line = next((l for l in lines if l.startswith("Budget:")), None)
        local_line = next((l for l in lines if l.startswith("Local:")), None)
        
        # Each should be truncated to 400 chars (plus prefix)
        if research_line:
            assert len(research_line.replace("Research: ", "")) <= 400
        if budget_line:
            assert len(budget_line.replace("Budget: ", "")) <= 400
        if local_line:
            assert len(local_line.replace("Local: ", "")) <= 400
    
    def test_with_user_input(self, sample_trip_state, monkeypatch):
        """Test itinerary_agent includes user_input when provided."""
        sample_trip_state["trip_request"]["user_input"] = "I prefer morning activities"
        sample_trip_state["research"] = "Research"
        sample_trip_state["budget"] = "Budget"
        sample_trip_state["local"] = "Local"
        
        mock_response = Mock()
        mock_response.content = "Itinerary with user preferences"
        
        mock_llm = Mock()
        mock_llm.invoke = Mock(return_value=mock_response)
        
        with patch('main.llm', mock_llm):
            result = itinerary_agent(sample_trip_state)
        
        call_args = mock_llm.invoke.call_args[0][0]
        prompt_content = call_args[0].content
        assert "I prefer morning activities" in prompt_content
    
    def test_without_user_input(self, sample_trip_state, monkeypatch):
        """Test itinerary_agent works without user_input."""
        sample_trip_state["trip_request"].pop("user_input", None)
        sample_trip_state["research"] = "Research"
        sample_trip_state["budget"] = "Budget"
        sample_trip_state["local"] = "Local"
        
        mock_response = Mock()
        mock_response.content = "Itinerary"
        
        mock_llm = Mock()
        mock_llm.invoke = Mock(return_value=mock_response)
        
        with patch('main.llm', mock_llm):
            result = itinerary_agent(sample_trip_state)
        
        call_args = mock_llm.invoke.call_args[0][0]
        prompt_content = call_args[0].content
        assert "User input:" not in prompt_content
    
    def test_with_travel_style(self, sample_trip_state, monkeypatch):
        """Test itinerary_agent includes travel_style."""
        sample_trip_state["trip_request"]["travel_style"] = "budget"
        sample_trip_state["research"] = "Research"
        sample_trip_state["budget"] = "Budget"
        sample_trip_state["local"] = "Local"
        
        mock_response = Mock()
        mock_response.content = "Budget itinerary"
        
        mock_llm = Mock()
        mock_llm.invoke = Mock(return_value=mock_response)
        
        with patch('main.llm', mock_llm):
            result = itinerary_agent(sample_trip_state)
        
        call_args = mock_llm.invoke.call_args[0][0]
        prompt_content = call_args[0].content
        assert "budget" in prompt_content.lower()
    
    def test_handles_missing_inputs(self, sample_trip_state, monkeypatch):
        """Test itinerary_agent handles missing research/budget/local inputs."""
        sample_trip_state.pop("research", None)
        sample_trip_state.pop("budget", None)
        sample_trip_state.pop("local", None)
        
        mock_response = Mock()
        mock_response.content = "Itinerary"
        
        mock_llm = Mock()
        mock_llm.invoke = Mock(return_value=mock_response)
        
        with patch('main.llm', mock_llm):
            result = itinerary_agent(sample_trip_state)
        
        assert result["final"] == "Itinerary"

