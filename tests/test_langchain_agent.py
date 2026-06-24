# tests/test_langchain_agent.py
import sys
import pytest
from unittest.mock import patch, MagicMock

def test_run_agent_gemini():
    if 'langchain_agent' in sys.modules:
        del sys.modules['langchain_agent']

    with patch('langchain_agent.find_working_model', return_value="dummy-model") as mock_find, \
         patch('langchain_agent.ChatGoogleGenerativeAI') as mock_llm_class, \
         patch('langchain_agent.create_agent') as mock_create_agent:
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [MagicMock(content="Order status: delivered")]
        }
        mock_create_agent.return_value = mock_agent

        from langchain_agent import run_agent_gemini
        response = run_agent_gemini("What is the status of order ORD-1001?")
        assert response == "Order status: delivered"
        mock_agent.invoke.assert_called_once_with({"messages": [("user", "What is the status of order ORD-1001?")]})

def test_find_working_model():
    from langchain_agent import find_working_model
    import google.generativeai as genai
    mock_model = MagicMock()
    mock_model.name = "models/gemini-1.5-flash"
    mock_model.supported_generation_methods = ["generateContent"]
    with patch('google.generativeai.list_models', return_value=[mock_model]) as mock_list, \
         patch('google.generativeai.configure') as mock_configure:
        result = find_working_model()
        assert result == "gemini-1.5-flash"
        mock_list.assert_called_once()

def test_fallback_on_error():
    # Ensure module is fresh
    if 'langchain_agent' in sys.modules:
        del sys.modules['langchain_agent']

    with patch('langchain_agent.find_working_model', return_value="dummy-model"), \
         patch('langchain_agent.ChatGoogleGenerativeAI') as mock_llm_class, \
         patch('langchain_agent.create_agent') as mock_create_agent:
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_agent = MagicMock()
        mock_agent.invoke.side_effect = Exception("API error")
        mock_create_agent.return_value = mock_agent

        from langchain_agent import run_agent_gemini
        # Should raise the exception to allow fallback in main.py
        with pytest.raises(Exception, match="API error"):
            run_agent_gemini("test")