# Echo-Cart – Agentic AI Assistant for Online Stores

An intelligent AI-powered customer support assistant for e-commerce platforms that answers customer queries by selecting and chaining the appropriate tools. The system combines a rule-based agent with optional Gemini, LangChain, and RAG capabilities to provide accurate, customer-friendly responses with graceful error handling.

---

## Overview

Echo-Cart helps customers interact with an online store through natural language queries. The assistant can:

* Track order status
* Retrieve product details
* Search products by keyword
* Recommend cheaper alternatives
* Perform semantic product discovery using RAG
* Handle invalid requests gracefully

The project includes a deterministic rule-based agent as the primary engine, with optional Gemini and LangChain integrations for advanced reasoning and semantic search.

---

## Features

### Intelligent Tool Selection

Automatically determines which tool(s) to invoke based on the customer's request.

### Tool Chaining

Supports multi-step workflows by calling tools in the correct sequence.

### Semantic Product Search (RAG)

Uses FAISS and Gemini embeddings to find products based on meaning rather than exact keywords.

### Customer-Friendly Responses

Returns natural language answers instead of raw database records.

### Error Handling

Gracefully handles:

* Invalid order IDs
* Invalid product IDs
* Empty search results
* API failures

### Logging

All tool invocations are recorded in `agent.log`.

### Web Interface

Interactive Streamlit application for testing and demonstration.

### Automated Testing

Comprehensive test suite built with `pytest`.

### Multi-Level Fallback System

1. LangChain + Gemini Agent
2. Direct Gemini Agent
3. Rule-Based Agent

Users always receive a response, even if external services fail.

---

## Tech Stack

| Category        | Technologies                       |
| --------------- | ---------------------------------- |
| Language        | Python 3.12+                       |
| Data Processing | pandas, regex                      |
| Dataset         | Olist Brazilian E-Commerce Dataset |
| LLM             | Google Gemini                      |
| Agent Framework | LangChain                          |
| RAG             | FAISS + Gemini Embeddings          |
| Web UI          | Streamlit                          |
| Testing         | pytest                             |
| Environment     | python-dotenv                      |
| Data Download   | kagglehub                          |

---

## Project Structure

```text
Echo-Cart/
│
├── data/
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── custom_orders.csv
│   ├── custom_order_items.csv
│   └── custom_products.csv
│
├── tests/
│   ├── test_agent.py
│   ├── test_gemini_agent.py
│   ├── test_langchain_agent.py
│   └── test_tools.py
│
├── tools.py
├── agent.py
├── gemini_agent.py
├── langchain_agent.py
├── app.py
├── main.py
├── logging_config.py
├── check_gemini.py
├── check_langchain.py
├── requirements.txt
├── .env
├── README.md
└── design_document.md
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

### Command-Line Interface

```bash
python main.py
```

### Streamlit Web Application

```bash
streamlit run app.py
```

---

## Running Tests

Execute the complete test suite:

```bash
pytest tests/ -v
```

---

## Verify Gemini Connectivity

```bash
python check_gemini.py
```

---

## Example Queries

### Order Status

**User**

```text
What is the status of order 47770eb9...?
```

**Response**

```text
Your order 47770eb9... is currently delivered.
```

---

### Product Details

**User**

```text
Tell me about product 1e9e8ef0...
```

**Response**

```text
Product 1e9e8ef0... belongs to the 'perfumery' category,
contains 1 image, and weighs 225g.
```

---

### Product Search

**User**

```text
Search for furniture
```

**Response**

```text
I found 5 matching products in the furniture category.
Would you like details on any of them?
```

---

### Cheaper Alternatives

**User**

```text
Find a cheaper alternative to the shoes in order ORD-1002.
```

**Response**

```text
I found several lower-priced alternatives.
Would you like more details on any of them?
```

---

### Semantic Search (RAG)

**User**

```text
Find something similar to a guitar.
```

**Response**

```text
I found several products related to musical instruments
that may match your interests.
```

---

## Architecture

### Rule-Based Agent

* Regex and keyword-based intent detection
* Deterministic behavior
* Fast execution
* No API dependency
* Works offline

### Gemini Integration

* Natural language understanding
* Dynamic reasoning
* Improved tool selection

### LangChain Agent

* Tool orchestration
* Agent memory
* Structured workflows
* Advanced reasoning chains

### RAG Pipeline

1. Product data is embedded using Gemini Embeddings.
2. Embeddings are stored in FAISS.
3. User queries are converted into embeddings.
4. Similar products are retrieved semantically.

---

## Error Handling

| Scenario           | Response                                     |
| ------------------ | -------------------------------------------- |
| Invalid Order ID   | "Sorry, I couldn't find that order."         |
| Invalid Product ID | "Sorry, I couldn't find that product."       |
| No Search Results  | "I couldn't find any matching products."     |
| Gemini Failure     | Fallback to Gemini Agent or Rule-Based Agent |
| LangChain Failure  | Automatic fallback                           |

The system never fabricates information and only returns results found in the dataset.

---

## Bonus Features

* Gemini LLM Integration
* LangChain Agent Framework
* RAG-based Semantic Search
* Streamlit Web Interface
* Tool Call Logging
* Automated Unit Tests
* Multi-Level Fallback System

---

## Dataset

This project uses the **Olist Brazilian E-Commerce Dataset**, which contains real-world e-commerce transactions, products, and order information.

Dataset:
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

---

## Future Improvements

* Multi-language customer support
* Order modification and cancellation workflows
* Personalized product recommendations
* Conversation memory
* Real-time inventory integration
* Deployment using Docker and cloud platforms

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

Built with ❤️ using Python, Gemini, LangChain, FAISS, and Streamlit.
