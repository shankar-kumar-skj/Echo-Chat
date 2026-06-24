# app.py
import streamlit as st
from agent import run_agent
from logging_config import setup_logging

setup_logging()

st.title("🛒 Online Store AI Assistant")
st.write("Ask me about orders, products, or alternatives.")

# Optional: Add a toggle for Gemini
use_gemini = st.checkbox("Use Gemini agent (requires API key)", value=False)

if use_gemini:
    try:
        from langchain_agent import run_agent_gemini
        agent_func = run_agent_gemini
    except ImportError:
        st.warning("Gemini agent not available. Falling back to rule‑based agent.")
        agent_func = run_agent
else:
    agent_func = run_agent

user_question = st.text_input("Your question:")

if user_question:
    with st.spinner("Thinking..."):
        response = agent_func(user_question)
    st.write(response)