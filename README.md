# Echo-Cart – Agentic AI Assistant for Online Stores

An intelligent AI-powered customer support assistant for e‑commerce platforms that answers customer queries by selecting and chaining the appropriate tools. The system combines a **rule‑based agent** with optional **Gemini**, **LangChain**, and **RAG** capabilities, and now includes a full suite of advanced features such as **multi‑question handling**, **product comparison**, **fuzzy search**, **follow‑up suggestions**, and an **analytics dashboard** – all wrapped in a modern chat UI.

---

## Overview

Echo‑Cart helps customers interact with an online store through natural language queries. The assistant can:

- Track order status (single or multiple)
- Retrieve product details
- Search products by keyword or category
- Recommend cheaper alternatives
- Compare products **within an order**
- Perform semantic product discovery using RAG
- Handle **multiple questions** in one message
- Suggest **follow‑up actions** automatically
- Log all interactions and provide an **analytics dashboard**

The project includes a deterministic rule‑based agent as the primary engine, with optional Gemini and LangChain integrations for advanced reasoning and semantic search.

---

## Features

### 🔧 Intelligent Tool Selection  
Automatically determines which tool(s) to invoke based on the customer’s request.

### ⛓️ Tool Chaining  
Supports multi‑step workflows by calling tools in the correct sequence.

### 🔍 Semantic Product Search (RAG)  
Uses FAISS and Gemini embeddings to find products based on meaning rather than exact keywords.

### 💬 Customer‑Friendly Responses  
Returns natural language answers instead of raw database records.

### ❌ Error Handling  
Gracefully handles invalid IDs, empty results, API failures, and more – without ever fabricating information.

### 📝 Logging  
All tool invocations are recorded in `agent.log`.

### 🖥️ Modern Web Interface  
Interactive Streamlit application with:

- **Left‑right chat bubbles** (user messages on the right, assistant on the left)
- **Hover‑visible timestamps**
- **Sidebar with full conversation history** grouped by user‑assistant pairs
- **"Clear All Chats"** button
- Input field with a `>` send button (instead of “Ask”)

### 🧪 Automated Testing  
Comprehensive test suite built with `pytest` covering all core modules, including `advanced_features.py`.

### 🧠 Advanced Capabilities (new)

- **Multi‑question support** – split a single input into multiple questions (e.g., *“Order status? And search for shoes?”*)
- **Compare products within an order** – generate a table with prices, freight, and price differences (e.g., *“Compare products in ORD‑1002”*)
- **Fuzzy search** – find products even with typos or partial matches
- **Product filters** – filter by category and price range
- **Smart recommendations** – track user interests and suggest relevant categories
- **Follow‑up suggestions** – automatically propose next actions (e.g., “Track another order”, “Compare prices”)
- **Analytics dashboard** – log queries, tool usage, response times, and most‑searched products

### 🛡️ Multi‑Level Fallback System

1. LangChain + Gemini Agent  
2. Direct Gemini Agent  
3. Rule‑Based Agent  

Users always receive a response, even if external services fail.

---

## Tech Stack

| Category          | Technologies                                 |
| ----------------- | -------------------------------------------- |
| Language          | Python 3.12+                                 |
| Data Processing   | pandas, regex                                |
| Dataset           | Olist Brazilian E‑Commerce Dataset           |
| LLM               | Google Gemini                                |
| Agent Framework   | LangChain (optional)                         |
| RAG               | FAISS + Gemini Embeddings                    |
| Web UI            | Streamlit                                    |
| Testing           | pytest                                       |
| Environment       | python‑dotenv                                |
| Data Download     | kagglehub                                    |

---

## Project Structure

```
Echo-Cart/
│
├── data/                               # Dataset files (auto‑downloaded)
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── custom_orders.csv
│   ├── custom_order_items.csv
│   └── custom_products.csv
│
├── tests/                              # Unit tests
│   ├── __init__.py
│   ├── check_imports.py                # Import checker script
│   ├── check_langchain.py              # LangChain compatibility script
│   ├── conftest.py                     # Pytest fixtures
│   ├── test_agent.py                   # Rule‑based agent tests
│   ├── test_gemini_agent.py            # Gemini agent tests
│   ├── test_langchain_agent.py         # LangChain agent tests
│   ├── test_tools.py                   # Tools tests
│   └── test_advanced_features.py       # Advanced features tests
│
├── tools.py                            # Core data loading and tool functions
├── agent.py                            # Rule‑based agent (primary)
├── gemini_agent.py                     # Direct Gemini integration
├── langchain_agent.py                  # LangChain agent (optional)
├── advanced_features.py                # Advanced features (comparison, fuzzy search, analytics, etc.)
├── app.py                              # Streamlit web application
├── main.py                             # Command‑line interface
├── logging_config.py                   # Logging configuration
├── requirements.txt                    # Python dependencies
├── .env                                # Environment variables (GOOGLE_API_KEY)
├── chat_history.db                     # SQLite database for chat history
├── analytics.db                        # SQLite database for analytics
└── README.md                           # This file
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Echo-Cart.git
cd Echo-Cart
```

### 2. Create a Virtual Environment

#### macOS / Linux

```bash
python -m venv venv
source venv/bin/activate
```

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key
```

Get your API key from:  
https://makersuite.google.com/app/apikey

---

## Running the Project

### Command‑Line Interface (CLI)

```bash
python main.py
```

### Streamlit Web Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## Running Tests

Execute the complete test suite:

```bash
pytest tests/ -v
```

Run a specific test file:

```bash
pytest tests/test_advanced_features.py -v
```

---

## Verify Gemini Connectivity

```bash
python check_gemini.py
```

---

## Example Queries

### Order Status

**User:**  
`What is the status of order 47770eb9...?`

**Response:**  
`Your order 47770eb9... is currently **delivered** and contains 2 item(s).`

---

### Product Details

**User:**  
`Tell me about product 1e9e8ef0...`

**Response:**  
`Product 1e9e8ef0... belongs to the 'perfumery' category, contains 1 image, and weighs 225g.`

---

### Product Search

**User:**  
`Search for furniture`

**Response:**  
`I found 5 products in category 'furniture': sofa (ID: ...), chair (ID: ...), table (ID: ...). Would you like details on any?`

---

### Cheaper Alternatives

**User:**  
`Find a cheaper alternative to the shoes in order ORD‑1002`

**Response:**  
`I found some alternatives: sneakers (ID: p2...), boots (ID: p3...). Would you like more details?`

---

### Compare Products in an Order (new)

**User:**  
`Compare products in ORD‑1002`

**Response:**  

| Product   | Category | Price | Freight |
|-----------|----------|-------|---------|
| p2...     | shoes    | 20.0  | 3.0     |
| p3...     | shoes    | 15.0  | 2.5     |

**Price difference:** Most expensive is **20.0**, cheapest is **15.0** (difference: **5.0**).

---

### Semantic Search (RAG)

**User:**  
`Find something similar to a guitar`

**Response:**  
`I found several products related to musical instruments that may match your interests.`

---

### Multi‑Question (new)

**User:**  
`What is the status of order ORD‑1002? And search for shoes`

**Response:**  
`Q: What is the status of order ORD‑1002? A: Order ORD‑1002 has status **delivered** and contains 2 item(s).`  
`Q: And search for shoes A: I found 3 products in category 'shoes': ...`  
`You may also ask: · Compare products · Find cheaper alternatives`

---

## Architecture

### Rule‑Based Agent (`agent.py`)

- Regex‑based intent detection (order, product, compare, search, category)
- Deterministic and fast
- No external API dependency
- Includes **compare** branch (lazy‑imports `compare_order_products` from `advanced_features`)

### Advanced Features Module (`advanced_features.py`)

- **Multi‑question** splitting and processing
- **Fuzzy search** using `difflib`
- **Product filters** (category and price range)
- **Out‑of‑stock suggestions** (returns alternatives if product not found)
- **Price difference calculator** between two products
- **Compare products within an order** – renders a Markdown table
- **Recommendation engine** – tracks user interests
- **Follow‑up suggestions** – generated from the latest response
- **Analytics** – logs every query, tracks tool usage, and stores top searches in `analytics.db` (with safe upsert logic)

### Gemini Integration (`gemini_agent.py`)

- Direct API calls to Gemini
- Tool‑calling via `CALL:` protocol
- RAG retriever built on demand

### LangChain Agent (`langchain_agent.py`)

- Uses `create_agent` (LangChain 1.x / LangGraph)
- Tools: `get_order`, `search_products`, `get_product`, `rag_search`
- System prompt guides alternative and comparison reasoning

### RAG Pipeline

1. Product data is embedded using Gemini Embeddings.
2. Embeddings are stored in FAISS.
3. User queries are converted into embeddings.
4. Similar products are retrieved semantically.

### Web Application (`app.py`)

- **Custom CSS** for chat bubbles (user right, assistant left)
- **Full conversation display** in the main area with hover‑visible timestamps
- **Sidebar** with grouped conversation history (user‑assistant pairs, latest first)
- **Clear All Chats** button
- Input form with `>` send button
- Chat history stored in `chat_history.db` (SQLite)

---

## Error Handling

| Scenario               | Response                                                       |
| ---------------------- | -------------------------------------------------------------- |
| Invalid Order ID       | `"Sorry, I couldn't find order ..."`                           |
| Invalid Product ID     | `"Sorry, I couldn't find product ..."`                         |
| No Search Results      | `"I couldn't find any products matching ..."`                  |
| Compare without Order  | `"I couldn't find an order ID in your question..."`            |
| Gemini API Failure     | Falls back to rule‑based agent                                 |
| LangChain Failure      | Automatic fallback to rule‑based agent                         |
| SQLite `ON CONFLICT`   | Safe upsert logic in analytics (update‑or‑insert with fallback) |

The system never fabricates information and only returns results found in the dataset.

---

## Bonus Features

- ✅ Gemini LLM Integration  
- ✅ LangChain Agent Framework  
- ✅ RAG‑based Semantic Search  
- ✅ Streamlit Web Interface  
- ✅ Tool Call Logging  
- ✅ Automated Unit Tests  
- ✅ Multi‑Level Fallback System  
- ✅ **Multi‑Question Support**  
- ✅ **Product Comparison**  
- ✅ **Fuzzy Search**  
- ✅ **Follow‑Up Suggestions**  
- ✅ **Analytics Dashboard**  
- ✅ **Modern Chat UI** (left‑right bubbles, hover timestamps)  

---

## Dataset

This project uses the **Olist Brazilian E‑Commerce Dataset**, which contains real‑world e‑commerce transactions, products, and order information.

Dataset:  
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

---

## Future Improvements

- Multi‑language customer support
- Order modification and cancellation workflows
- Personalized product recommendations with user history
- Conversation memory across sessions
- Real‑time inventory integration
- Deployment using Docker and cloud platforms
- More advanced analytics (visualizations in Streamlit)

---

## Contributing

This project was developed as part of an Agentic AI assignment. Contributions are not required, but feel free to fork the repository and experiment with new features.

---

## License

This project is licensed under the MIT License.  
See the `LICENSE` file for details.

---

## Contact

For questions, suggestions, or bug reports, please open an issue on GitHub.

---

Built with ❤️ using Python, Gemini, LangChain, FAISS, Streamlit, and SQLite.