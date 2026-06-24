# langchain_agent.py
import os
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from tools import get_order as real_get_order
from tools import search_products as real_search_products
from tools import get_product as real_get_product
from tools import products_df

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not set in .env")

# ---- Tools (unchanged) ----
@tool(description="Fetch order status and item count.")
def get_order(order_id: str) -> str:
    order = real_get_order(order_id)
    if order:
        return f"Order {order_id}: {order.get('order_status', 'unknown')}, {len(order.get('items', []))} items"
    return f"Order {order_id} not found."

@tool(description="Search products by keyword. Returns category and ID.")
def search_products(query: str) -> str:
    results = real_search_products(query, limit=5)
    return "\n".join([f"{r['category']} (ID: {r['product_id']})" for r in results]) if results else "No products found."

@tool(description="Get product details: category, weight.")
def get_product(product_id: str) -> str:
    prod = real_get_product(product_id)
    return f"Product {product_id}: {prod['category']}, weight {prod.get('product_weight_g', 'unknown')}g" if prod else f"Product {product_id} not found."

# ---- RAG (lazy) ----
_retriever = None
def get_retriever():
    global _retriever
    if _retriever is not None:
        return _retriever
    try:
        docs = []
        for _, row in products_df.iterrows():
            text = f"{row.get('product_category_name_english', '')} {row.get('product_description_length', '')}"
            docs.append(Document(page_content=text, metadata={"product_id": row['product_id']}))
        for model in ["models/text-embedding-004", "models/embedding-001"]:
            try:
                embeddings = GoogleGenerativeAIEmbeddings(model=model, google_api_key=API_KEY)
                vectorstore = FAISS.from_documents(docs, embeddings)
                _retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
                print(f"✅ RAG retriever built with {model}")
                break
            except Exception:
                continue
        if _retriever is None:
            print("⚠️ All embedding models failed. RAG disabled.")
    except Exception as e:
        print(f"⚠️ RAG unavailable: {e}")
        _retriever = None
    return _retriever

@tool(description="Semantic search for products using RAG.")
def rag_search(query: str) -> str:
    retriever = get_retriever()
    if retriever is None:
        return "RAG search is not available. Please use search_products."
    docs = retriever.invoke(query)
    if not docs:
        return "No similar products found."
    results = []
    for doc in docs:
        pid = doc.metadata["product_id"]
        prod = real_get_product(pid)
        if prod:
            results.append(f"{prod['category']} (ID: {pid})")
    return "\n".join(results) if results else "No products found."

# ---- Lazy LLM and Agent ----
_agent = None
_tools = [get_order, search_products, get_product, rag_search]

def find_working_model():
    import google.generativeai as genai
    genai.configure(api_key=API_KEY)
    try:
        models = genai.list_models()
        for m in models:
            if "generateContent" in m.supported_generation_methods:
                model_id = m.name.split("/")[-1]
                print(f"✅ Found working model: {model_id}")
                return model_id
        raise RuntimeError("No model with generateContent found.")
    except Exception as e:
        fallbacks = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        for name in fallbacks:
            try:
                print(f"⚠️ Trying fallback model: {name}")
                return name
            except:
                continue
        raise RuntimeError(f"Could not find a working Gemini model: {e}")

def _ensure_agent():
    global _agent
    if _agent is None:
        model_id = find_working_model()
        llm = ChatGoogleGenerativeAI(
            model=model_id,
            temperature=0,
            google_api_key=API_KEY,
            convert_system_message_to_human=True
        )
        system_prompt = """
You are a helpful assistant for an online store.
Use the provided tools to answer the user's questions. Be concise and friendly.

When a user asks for a cheaper alternative to a product they ordered (e.g., "cheaper alternative to the shoes I ordered"), follow these steps:
1. Use get_order to retrieve the order details.
2. If the order has multiple items, check if the user mentioned a specific category (like "shoes"). If they did, find the item(s) in that category.
3. For each relevant item, use get_product to get its category.
4. Use search_products with that category to find other products in the same category.
5. Suggest those alternatives to the user. Mention that while prices are not available, these are similar products.
If the user doesn't specify which item and the order has multiple items, ask them to clarify which item they want alternatives for.

For general product searches, use search_products or rag_search as appropriate.
For order status, use get_order.
For product details, use get_product.
"""
        _agent = create_agent(
            model=llm,
            tools=_tools,
            system_prompt=system_prompt,
        )
    return _agent

def run_agent_gemini(question: str) -> str:
    try:
        agent = _ensure_agent()
        result = agent.invoke({"messages": [("user", question)]})
        messages = result.get("messages", [])
        if messages:
            last_msg = messages[-1]
            if hasattr(last_msg, "content"):
                return last_msg.content
            elif isinstance(last_msg, dict) and "content" in last_msg:
                return last_msg["content"]
            else:
                return str(last_msg)
        return str(result)
    except Exception as e:
        # Re-raise so that main.py can catch and fallback
        raise