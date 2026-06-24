Echo-Cart – Agentic AI Assistant for Online Store
=================================================

A smart AI agent that answers customer questions about an online store by intelligently selecting and chaining tools, with graceful error handling and customer-friendly responses.

OVERVIEW
--------

This project implements an AI agent for an online store that can:

- Answer questions about order status (e.g., "Where is my order?")
- Provide product details (e.g., "Tell me about this product")
- Search for products (e.g., "Search for shoes")
- Find cheaper alternatives (e.g., "Is there a cheaper alternative to the shoes I ordered?")
- Handle semantic searches using RAG (e.g., "Find something similar to a guitar")

The agent uses a rule‑based decision engine as the core, with optional Gemini + LangChain integration for enhanced reasoning and RAG (Retrieval-Augmented Generation) for semantic product search.

FEATURES
--------

- Tool Selection – decides which tools to call based on the user's question.
- Tool Chaining – calls multiple tools in the correct order for complex queries.
- Error Handling – gracefully handles invalid orders/products and empty search results.
- Customer-Friendly Responses – returns natural language answers, never raw data.
- Logging – logs all tool calls to agent.log.
- Web Interface – Streamlit UI for easy interaction.
- Unit Tests – comprehensive test suite using pytest.
- Gemini Integration – optional LLM-powered agent with reasoning.
- RAG – semantic product search using FAISS + Gemini embeddings.
- LangChain – advanced agent framework with tools, memory, and chains.
- Fallback – automatically falls back to rule‑based agent if Gemini fails.

TECH STACK
----------

Core: Python 3.12+, pandas, regex
Data: Kagglehub (auto‑downloads Olist dataset)
LLM: Google Gemini (google-generativeai)
Agent Framework: LangChain (create_agent)
RAG: FAISS + Gemini Embeddings
Web UI: Streamlit
Testing: pytest
Environment: python-dotenv

PROJECT STRUCTURE
-----------------

Echo-Cart/
├── data/                                  # CSV files (auto‑downloaded)
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── custom_orders.csv                  # Optional custom data
│   ├── custom_order_items.csv
│   └── custom_products.csv
├── tests/                                 # Unit tests
│   ├── test_agent.py
│   ├── test_gemini_agent.py
│   ├── test_langchain_agent.py
│   └── test_tools.py
├── tools.py                               # Data loading & core tools
├── agent.py                               # Rule‑based agent
├── gemini_agent.py                        # Direct Gemini agent (fallback)
├── langchain_agent.py                     # LangChain + Gemini + RAG agent
├── main.py                                # CLI entry point
├── app.py                                 # Streamlit web interface
├── logging_config.py                      # Logging setup
├── check_gemini.py                        # Gemini API connectivity test
├── check_langchain.py                     # LangChain environment check
├── requirements.txt                       # Dependencies
├── .env                                   # API keys (not committed)
├── README.md                              # This file
└── design_document.md                     # Design decisions (1‑2 pages)

QUICK START
-----------

1. Clone the repository:
   git clone https://github.com/yourusername/Echo-Cart.git
   cd Echo-Cart

2. Create a virtual environment:
   python -m venv venv
   source venv/bin/activate          # macOS/Linux
   # or
   venv\Scripts\activate              # Windows

3. Install dependencies:
   pip install -r requirements.txt

4. Set up environment variables:
   Create a .env file with:
   GOOGLE_API_KEY=your-gemini-api-key
   Get a key from: https://makersuite.google.com/app/apikey

5. Run the agent:
   CLI: python main.py
   Web UI: streamlit run app.py

6. Run tests:
   pytest tests/ -v

7. Check Gemini connectivity:
   python check_gemini.py

SAMPLE INPUTS & OUTPUTS
-----------------------

User Question: What is the status of order 47770eb9...?
Agent Response: Your order 47770eb9... is currently delivered.

User Question: Tell me about product 1e9e8ef0...
Agent Response: Product 1e9e8ef0... is a 'perfumery'. It has 1.0 photo(s) and weighs 225.0g.

User Question: Search for furniture
Agent Response: I found 5 products: furniture_decor (ID: ...), ... Would you like details on any?

User Question: Find me a cheaper alternative to the shoes in order ORD-1002.
Agent Response: I found some alternatives: fashion_shoes (ID: ...), ... Would you like more details on any?

User Question: category musical_instruments
Agent Response: I found these products in category 'musical_instruments': ...

User Question: Hello
Agent Response: I'm not sure how to help. You can ask about order status, product details, or search for products.

User Question: Invalid order
Agent Response: Sorry, I couldn't find order ORD-9999. Please verify the ID and try again.

User Question: Empty search
Agent Response: I couldn't find any products matching 'nonexistentproduct'. Please try a different keyword.

DESIGN DECISIONS
----------------

Rule‑Based Agent:
- Uses regex and keyword matching for intent detection.
- Fast, deterministic, and works offline – no API calls.
- Fully meets all mandatory assignment requirements.

LangChain + Gemini + RAG (Bonus):
- Uses LangChain's create_agent (new API for LangChain 1.x).
- Gemini provides natural language reasoning and tool selection.
- RAG uses FAISS + Gemini embeddings for semantic product search.
- Lazy initialisation – the model is loaded only when needed.

Fallback System:
- If LangChain agent fails (403, 404, etc.), it falls back to the direct Gemini agent.
- If the direct Gemini agent fails, it falls back to the rule‑based agent.
- The user always receives an answer.

Error Handling:
- Invalid order/product IDs → "Sorry, I couldn't find..."
- Empty search results → "I couldn't find any products matching..."
- No fabricated data – only real dataset results.

BONUS FEATURES
--------------
- LLM Integration: Gemini + LangChain (both direct and agent framework)
- RAG: FAISS + Gemini embeddings
- Logging: All tool calls logged to agent.log
- Web Interface: Streamlit (app.py)
- Unit Tests: pytest tests/ – 23 passing tests

RESOURCES
---------
- Dataset: Olist Brazilian E‑Commerce Dataset – https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- Google Gemini API: https://makersuite.google.com/app/apikey
- Gemini API Documentation: https://ai.google.dev/gemini-api/docs
- Google Generative AI Python SDK: https://github.com/google-gemini/generative-ai-python
- LangChain Documentation: https://python.langchain.com/docs/
- LangChain Google GenAI Integration: https://python.langchain.com/docs/integrations/chat/google_generativeai
- LangChain GitHub: https://github.com/langchain-ai/langchain
- FAISS GitHub: https://github.com/facebookresearch/faiss
- FAISS Documentation: https://faiss.ai/
- Streamlit Documentation: https://docs.streamlit.io/
- pytest Documentation: https://docs.pytest.org/
- pandas: https://pandas.pydata.org/
- python-dotenv: https://github.com/theskumar/python-dotenv
- kagglehub: https://github.com/Kaggle/kagglehub

CONTRIBUTING
------------
This is a student assignment – contributions are not required. Feel free to fork and experiment.

LICENSE
-------
MIT License – see LICENSE for details.

CONTACT
-------
For any questions, reach out via GitHub Issues.

Built with ❤️ for the Agentic AI Assignment. 🚀