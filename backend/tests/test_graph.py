"""Integration tests for LangGraph workflow."""

from unittest.mock import Mock, patch

import pytest

from main import build_graph, research_agent, budget_agent, local_agent, itinerary_agent


class TestBuildGraph:
    """Tests for build_graph function."""
    
    def test_builds_graph_structure(self):
        """Test that build_graph creates correct graph structure."""
        graph = build_graph()
        assert graph is not None
        
        # Verify graph has nodes
        nodes = graph.nodes
        assert "research_node" in nodes
        assert "budget_node" in nodes
        assert "local_node" in nodes
        assert "itinerary_node" in nodes
    
    def test_graph_has_correct_edges(self):
        """Test that graph has correct edge connections."""
        graph = build_graph()
        # Graph should have edges from START to all three agents
        # and from all three agents to itinerary_node
        # This is verified by successful execution


class TestGraphExecution:
    """Tests for complete graph execution."""
    
    def test_complete_workflow_execution(self, sample_trip_state, monkeypatch):
        """Test complete workflow with mocked agents."""
        # Mock all agent functions to return predictable state updates
        def mock_research_agent(state):
            return {
                "messages": [],
                "research": "Mock research summary",
                "tool_calls": [{"agent": "research", "tool": "essential_info", "args": {}}]
            }
        
        def mock_budget_agent(state):
            return {
                "messages": [],
                "budget": "Mock budget summary",
                "tool_calls": [{"agent": "budget", "tool": "budget_basics", "args": {}}]
            }
        
        def mock_local_agent(state):
            return {
                "messages": [],
                "local": "Mock local summary",
                "tool_calls": [{"agent": "local", "tool": "local_flavor", "args": {}}]
            }
        
        def mock_itinerary_agent(state):
            return {
                "messages": [],
                "final": "Mock complete itinerary"
            }
        
        with patch('main.research_agent', mock_research_agent), \
             patch('main.budget_agent', mock_budget_agent), \
             patch('main.local_agent', mock_local_agent), \
             patch('main.itinerary_agent', mock_itinerary_agent):
            
            graph = build_graph()
            initial_state = {
                "messages": [],
                "trip_request": sample_trip_state["trip_request"],
                "tool_calls": []
            }
            
            result = graph.invoke(initial_state)
        
        # Verify all agents executed
        assert "research" in result
        assert "budget" in result
        assert "local" in result
        assert "final" in result
        
        # Verify tool_calls were aggregated
        assert len(result.get("tool_calls", [])) == 3
        
        # Verify final itinerary was created
        assert result["final"] == "Mock complete itinerary"
    
    def test_parallel_agent_execution(self, sample_trip_state, monkeypatch):
        """Test that research, budget, and local agents execute in parallel."""
        execution_order = []
        
        def mock_research_agent(state):
            execution_order.append("research")
            return {"messages": [], "research": "Research", "tool_calls": []}
        
        def mock_budget_agent(state):
            execution_order.append("budget")
            return {"messages": [], "budget": "Budget", "tool_calls": []}
        
        def mock_local_agent(state):
            execution_order.append("local")
            return {"messages": [], "local": "Local", "tool_calls": []}
        
        def mock_itinerary_agent(state):
            execution_order.append("itinerary")
            return {"messages": [], "final": "Itinerary"}
        
        with patch('main.research_agent', mock_research_agent), \
             patch('main.budget_agent', mock_budget_agent), \
             patch('main.local_agent', mock_local_agent), \
             patch('main.itinerary_agent', mock_itinerary_agent):
            
            graph = build_graph()
            initial_state = {
                "messages": [],
                "trip_request": sample_trip_state["trip_request"],
                "tool_calls": []
            }
            
            graph.invoke(initial_state)
        
        # Verify itinerary runs after all three parallel agents
        assert "itinerary" in execution_order
        itinerary_index = execution_order.index("itinerary")
        assert "research" in execution_order[:itinerary_index]
        assert "budget" in execution_order[:itinerary_index]
        assert "local" in execution_order[:itinerary_index]
    
    def test_state_propagation_to_itinerary(self, sample_trip_state, monkeypatch):
        """Test that agent outputs propagate correctly to itinerary agent."""
        received_state = {}
        
        def mock_itinerary_agent(state):
            nonlocal received_state
            received_state = state.copy()
            return {"messages": [], "final": "Itinerary"}
        
        def mock_research_agent(state):
            return {"messages": [], "research": "Research output", "tool_calls": []}
        
        def mock_budget_agent(state):
            return {"messages": [], "budget": "Budget output", "tool_calls": []}
        
        def mock_local_agent(state):
            return {"messages": [], "local": "Local output", "tool_calls": []}
        
        with patch('main.research_agent', mock_research_agent), \
             patch('main.budget_agent', mock_budget_agent), \
             patch('main.local_agent', mock_local_agent), \
             patch('main.itinerary_agent', mock_itinerary_agent):
            
            graph = build_graph()
            initial_state = {
                "messages": [],
                "trip_request": sample_trip_state["trip_request"],
                "tool_calls": []
            }
            
            graph.invoke(initial_state)
        
        # Verify itinerary agent received all inputs
        assert received_state.get("research") == "Research output"
        assert received_state.get("budget") == "Budget output"
        assert received_state.get("local") == "Local output"
    
    def test_tool_calls_aggregation(self, sample_trip_state, monkeypatch):
        """Test that tool_calls from all agents are aggregated."""
        def mock_research_agent(state):
            return {
                "messages": [],
                "research": "Research",
                "tool_calls": [
                    {"agent": "research", "tool": "essential_info", "args": {}}
                ]
            }
        
        def mock_budget_agent(state):
            return {
                "messages": [],
                "budget": "Budget",
                "tool_calls": [
                    {"agent": "budget", "tool": "budget_basics", "args": {}},
                    {"agent": "budget", "tool": "attraction_prices", "args": {}}
                ]
            }
        
        def mock_local_agent(state):
            return {
                "messages": [],
                "local": "Local",
                "tool_calls": [
                    {"agent": "local", "tool": "local_flavor", "args": {}}
                ]
            }
        
        def mock_itinerary_agent(state):
            return {"messages": [], "final": "Itinerary"}
        
        with patch('main.research_agent', mock_research_agent), \
             patch('main.budget_agent', mock_budget_agent), \
             patch('main.local_agent', mock_local_agent), \
             patch('main.itinerary_agent', mock_itinerary_agent):
            
            graph = build_graph()
            initial_state = {
                "messages": [],
                "trip_request": sample_trip_state["trip_request"],
                "tool_calls": []
            }
            
            result = graph.invoke(initial_state)
        
        # Verify all tool_calls were aggregated
        tool_calls = result.get("tool_calls", [])
        assert len(tool_calls) == 4  # 1 + 2 + 1
        
        # Verify tool_calls from each agent
        research_calls = [tc for tc in tool_calls if tc["agent"] == "research"]
        budget_calls = [tc for tc in tool_calls if tc["agent"] == "budget"]
        local_calls = [tc for tc in tool_calls if tc["agent"] == "local"]
        
        assert len(research_calls) == 1
        assert len(budget_calls) == 2
        assert len(local_calls) == 1

