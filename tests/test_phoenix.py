"""
Test Phoenix observability integration
"""

import pytest
import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

class TestPhoenixIntegration:
    """Test Phoenix observability integration"""
    
    def test_phoenix_modules_import(self):
        """Test that Phoenix modules import correctly"""
        try:
            import phoenix as px
            from phoenix.otel import register
            from openinference.instrumentation.openai import OpenAIInstrumentor
            assert True, "Phoenix modules imported successfully"
        except ImportError as e:
            pytest.skip(f"Phoenix not available: {e}")
    
    def test_backend_with_phoenix(self):
        """Test that backend works with or without Phoenix"""
        import backend
        
        # Backend should work regardless of Phoenix availability
        assert hasattr(backend, 'app'), "FastAPI app not created"
        assert hasattr(backend, 'TRACING_ENABLED'), "TRACING_ENABLED not defined"
        
        # If Phoenix is available, tracer should be created
        if backend.TRACING_ENABLED:
            assert hasattr(backend, 'tracer'), "Tracer not created when Phoenix enabled"
    
    def test_tracing_attributes_helper(self):
        """Test the set_trace_attributes helper function"""
        import backend
        from unittest.mock import Mock
        
        # Create mock span and request
        mock_span = Mock()
        mock_request = backend.TripRequest(
            destination="Tokyo",
            duration="3 days",
            budget="moderate",
            interests="food, culture"
        )
        
        # Test with just request
        backend.set_trace_attributes(mock_span, mock_request)
        
        # Verify attributes were set
        expected_calls = [
            ('llm.request.model', backend.CONFIG["model"]),
            ('trip.destination', 'Tokyo'),
            ('trip.duration', '3 days'),
            ('trip.budget', 'moderate'),
            ('trip.interests', 'food, culture'),
        ]
        
        for attr, value in expected_calls:
            mock_span.set_attribute.assert_any_call(attr, value)
    
    def test_tracing_with_response_data(self):
        """Test tracing with response data"""
        import backend
        from unittest.mock import Mock
        
        mock_span = Mock()
        mock_request = backend.TripRequest(destination="Paris", duration="2 days")
        response_data = {
            'model': 'openai/gpt-oss-20b',
            'usage': {'total_tokens': 150}
        }
        
        backend.set_trace_attributes(mock_span, mock_request, response_data=response_data)
        
        # Check response-specific attributes
        mock_span.set_attribute.assert_any_call('llm.response.model', 'openai/gpt-oss-20b')
        mock_span.set_attribute.assert_any_call('llm.usage.total_tokens', 150)
    
    def test_tracing_with_error(self):
        """Test tracing with error"""
        import backend
        from unittest.mock import Mock
        
        mock_span = Mock()
        mock_request = backend.TripRequest(destination="London", duration="1 day")
        
        backend.set_trace_attributes(mock_span, mock_request, error="Test error")
        
        # Check error attributes
        mock_span.set_attribute.assert_any_call('error', True)
        mock_span.set_attribute.assert_any_call('error.message', 'Test error')
    
    def test_tracing_with_none_span(self):
        """Test that helper handles None span gracefully"""
        import backend
        
        mock_request = backend.TripRequest(destination="Berlin", duration="4 days")
        
        # Should not raise exception
        backend.set_trace_attributes(None, mock_request)
        backend.set_trace_attributes(None, mock_request, response_data={})
        backend.set_trace_attributes(None, mock_request, error="test")

def test_phoenix_integration():
    """Standalone test function for simple test runner compatibility"""
    test_instance = TestPhoenixIntegration()
    
    print("🧪 Testing Phoenix Integration...")
    
    try:
        test_instance.test_phoenix_modules_import()
        print("✓ Phoenix modules import test passed")
    except Exception as e:
        print(f"⚠️  Phoenix modules not available: {e}")
    
    try:
        test_instance.test_backend_with_phoenix()
        print("✓ Backend with Phoenix test passed")
        
        test_instance.test_tracing_attributes_helper()
        print("✓ Tracing attributes helper test passed")
        
        test_instance.test_tracing_with_response_data()
        print("✓ Tracing with response data test passed")
        
        test_instance.test_tracing_with_error()
        print("✓ Tracing with error test passed")
        
        test_instance.test_tracing_with_none_span()
        print("✓ Tracing with None span test passed")
        
        print("🎉 All Phoenix integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Phoenix integration test failed: {e}")
        return False

if __name__ == "__main__":
    import sys
    sys.exit(0 if test_phoenix_integration() else 1)