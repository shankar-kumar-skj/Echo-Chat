# gemini_agent.py
import os
import re
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

from dotenv import load_dotenv
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

from tools import get_order, search_products, get_product
from tools import products_df

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not set in .env")

genai.configure(api_key=API_KEY)

# ---- Lazy model ----
_model = None

def get_model():
    global _model
    if _model is not None:
        return _model
    try:
        models = genai.list_models()
        for m in models:
            if "generateContent" in m.supported_generation_methods:
                model_name = m.name
                print(f"✅ Found Gemini model: {model_name}")
                _model = genai.GenerativeModel(model_name)
                return _model
        raise RuntimeError("No model with generateContent found.")
    except Exception as e:
        for name in ["gemini-1.5-flash", "gemini-pro", "gemini-1.5-pro"]:
            try:
                print(f"⚠️ Trying fallback model: {name}")
                _model = genai.GenerativeModel(name)
                test = _model.generate_content("Hello")
                if test:
                    print(f"✅ Fallback model {name} works.")
                    return _model
            except:
                continue
        raise RuntimeError(f"Could not find a working Gemini model: {e}")

# ---- Alias for tests and backward compatibility ----
find_working_model = get_model

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
        for model_name in ["models/text-embedding-004", "models/embedding-001"]:
            try:
                embeddings = GoogleGenerativeAIEmbeddings(model=model_name, google_api_key=API_KEY)
                vectorstore = FAISS.from_documents(docs, embeddings)
                _retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
                print(f"✅ RAG retriever built with {model_name}")
                break
            except Exception:
                continue
        if _retriever is None:
            print("⚠️ All embedding models failed. RAG disabled.")
    except Exception as e:
        print(f"⚠️ RAG unavailable: {e}")
        _retriever = None
    return _retriever

def call_get_order(order_id):
    order = get_order(order_id)
    if order:
        return f"Order {order_id}: {order.get('order_status', 'unknown')}, {len(order.get('items', []))} items"
    return f"Order {order_id} not found."

def call_search_products(query):
    results = search_products(query, limit=5)
    return "\n".join([f"{r['category']} (ID: {r['product_id']})" for r in results]) if results else "No products found."

def call_get_product(product_id):
    prod = get_product(product_id)
    return f"Product {product_id}: {prod['category']}, weight {prod.get('product_weight_g', 'unknown')}g" if prod else f"Product {product_id} not found."

def call_rag_search(query):
    retriever = get_retriever()
    if retriever is None:
        return "RAG search is not available. Please use search_products instead."
    docs = retriever.invoke(query)
    if not docs:
        return "No similar products found."
    results = []
    for doc in docs:
        pid = doc.metadata["product_id"]
        prod = get_product(pid)
        if prod:
            results.append(f"{prod['category']} (ID: {pid})")
    return "\n".join(results) if results else "No products found."

TOOL_MAP = {
    "get_order": call_get_order,
    "search_products": call_search_products,
    "get_product": call_get_product,
    "rag_search": call_rag_search,
}

SYSTEM_PROMPT = """
You are a helpful assistant for an online store.
You can call these functions by outputting:
CALL: function_name('parameter')

Available functions:
- get_order('order_id') → status and items
- search_products('query') → matching products
- get_product('product_id') → details
- rag_search('query') → semantic search (if available)

After calling, you'll get the result. Then you can continue.
Finally, give a natural answer to the user.
"""

def execute_tool(call_line):
    match = re.match(r"CALL:\s*(\w+)\((.*)\)", call_line, re.IGNORECASE)
    if not match:
        return f"Error: invalid format {call_line}"
    func, args_str = match.groups()
    args = [a[0] or a[1] or float(a[2]) for a in re.findall(r"'([^']*)'|\"([^\"]*)\"|(\d+\.?\d*)", args_str)]
    if func in TOOL_MAP:
        try:
            return TOOL_MAP[func](*args)
        except Exception as e:
            return f"Error executing {func}: {e}"
    return f"Unknown function '{func}'."

def run_agent_gemini(question: str, max_steps=5) -> str:
    model = get_model()
    conversation = [{"role": "user", "parts": [SYSTEM_PROMPT + "\n\nUser: " + question]}]
    for _ in range(max_steps):
        try:
            response = model.generate_content(conversation)
        except Exception as e:
            return f"Gemini API error: {e}"
        reply = response.text.strip()
        conversation.append({"role": "model", "parts": [reply]})
        if "CALL:" in reply:
            for line in reply.splitlines():
                if line.strip().startswith("CALL:"):
                    result = execute_tool(line.strip())
                    conversation.append({"role": "user", "parts": [f"Result: {result}"]})
                    break
        else:
            return reply
    return "Could not resolve within steps."