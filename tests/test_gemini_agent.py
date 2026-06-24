# tests/test_gemini_agent.py
import pytest
from unittest.mock import patch, MagicMock
from gemini_agent import run_agent_gemini, find_working_model, execute_tool, TOOL_MAP

@pytest.fixture
def mock_gemini_model():
    # Patch the lazy model getter instead of the model itself
    with patch('gemini_agent.get_model') as mock_get_model, \
         patch('gemini_agent.get_retriever') as mock_retriever:
        # Create a mock model that returns a fixed response
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = [
            MagicMock(text="CALL: get_order('ORD-1001')"),
            MagicMock(text="Your order is delivered.")
        ]
        mock_get_model.return_value = mock_model
        mock_retriever.return_value = None
        yield mock_get_model, mock_retriever

def test_run_agent_gemini_tool_call(mock_gemini_model):
    mock_get_model, _ = mock_gemini_model
    # Patch execute_tool to return a result
    with patch('gemini_agent.execute_tool') as mock_execute:
        mock_execute.return_value = "Order status: delivered"
        response = run_agent_gemini("What is the status of order ORD-1001?")
        assert "delivered" in response
        mock_get_model.assert_called_once()

def test_run_agent_gemini_final_answer(mock_gemini_model):
    mock_get_model, _ = mock_gemini_model
    # Override the mock to return final answer directly (no CALL)
    mock_model = MagicMock()
    mock_model.generate_content.return_value = MagicMock(text="Your order is delivered.")
    mock_get_model.return_value = mock_model
    response = run_agent_gemini("What is the status of order ORD-1001?")
    assert "delivered" in response

def test_execute_tool_get_order():
    with patch('gemini_agent.get_order') as mock_get:
        mock_get.return_value = {'order_status': 'delivered', 'items': []}
        result = execute_tool("CALL: get_order('ORD-1001')")
        assert "delivered" in result
        assert "0 items" in result

def test_execute_tool_invalid():
    result = execute_tool("CALL: unknown_func('arg')")
    assert "Unknown function" in result

def test_find_working_model():
    # This now calls get_model (the alias), which is lazy, but we can mock list_models
    import google.generativeai as genai
    mock_model = MagicMock()
    mock_model.name = "models/gemini-1.5-flash"
    mock_model.supported_generation_methods = ["generateContent"]
    with patch('google.generativeai.list_models', return_value=[mock_model]) as mock_list, \
         patch('google.generativeai.configure') as mock_configure:
        # We need to reset the cached model to force a fresh call
        import gemini_agent
        gemini_agent._model = None
        model = find_working_model()
        assert model is not None
        mock_list.assert_called_once()