# main.py
import os
from agent import run_agent
from logging_config import setup_logging

run_agent_gemini = None
AGENT_TYPE = "RuleBased"

try:
    from langchain_agent import run_agent_gemini
    AGENT_TYPE = "LangChain"
except ImportError as e:
    print(f"LangChain agent import failed: {e}")
    try:
        from gemini_agent import run_agent_gemini
        AGENT_TYPE = "DirectGemini"
    except ImportError as e2:
        print(f"Direct Gemini agent import failed: {e2}")
        AGENT_TYPE = "RuleBased"

USE_GEMINI = True

if __name__ == "__main__":
    setup_logging()
    print("Agentic AI Assistant for Online Store")
    print("Type your question (or 'quit' to exit):")
    if USE_GEMINI and AGENT_TYPE != "RuleBased":
        print(f"Using {AGENT_TYPE} agent with Gemini and RAG.")
    else:
        print("Using rule‑based agent.")

    while True:
        user_input = input("> ")
        if user_input.lower() in ['quit', 'exit']:
            break
        try:
            if USE_GEMINI and AGENT_TYPE != "RuleBased" and run_agent_gemini:
                try:
                    response = run_agent_gemini(user_input)
                except Exception as gemini_error:
                    # If Gemini fails (permission, model not found, etc.), fallback to rule-based
                    print(f"⚠️ Gemini agent error: {gemini_error}. Falling back to rule‑based agent for this question.")
                    response = run_agent(user_input)
            else:
                response = run_agent(user_input)
            print(response)
        except Exception as e:
            print(f"Error: {e}")