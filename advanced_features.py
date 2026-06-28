# advanced_features.py
"""
Advanced features for the AI Agent:
- Multi‑question support
- Customer‑friendly responses (enhanced)
- Out‑of‑stock suggestions
- Price difference calculator
- Smart recommendations
- Error recovery
- Fuzzy search
- Product filters
- Follow‑up suggestions
- Analytics dashboard
"""

import re
import difflib
import logging
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict

from tools import get_order, search_products, get_product, products_df, order_items_df

logger = logging.getLogger(__name__)

# =============================================================================
# 1. Multi‑Question Support
# =============================================================================
def split_questions(text: str) -> List[str]:
    text = re.sub(r'\band\b', '|||', text, flags=re.IGNORECASE)
    text = re.sub(r'\bor\b', '|||', text, flags=re.IGNORECASE)
    parts = re.split(r'[?.!]', text)
    questions = []
    for p in parts:
        p = p.strip()
        if p:
            for sub in p.split('|||'):
                sub = sub.strip()
                if sub:
                    questions.append(sub)
    return questions

# =============================================================================
# 2. Fuzzy Search
# =============================================================================
def fuzzy_search(query: str, limit: int = 5, cutoff: float = 0.6) -> List[Dict]:
    if not products_df.empty:
        candidates = []
        for _, row in products_df.iterrows():
            cat_pt = row.get('product_category_name', '')
            cat_en = row.get('product_category_name_english', '')
            text = f"{cat_pt} {cat_en}".strip()
            if text:
                candidates.append((row['product_id'], text, row))
        matches = []
        for pid, text, row in candidates:
            score = difflib.SequenceMatcher(None, query.lower(), text.lower()).ratio()
            if score >= cutoff:
                matches.append((score, row))
        matches.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, row in matches[:limit]:
            results.append({
                'product_id': row['product_id'],
                'category': row.get('product_category_name_english', row.get('product_category_name', 'Unknown')),
                'score': round(score, 2)
            })
        return results
    return []

# =============================================================================
# 3. Product Filters
# =============================================================================
def filter_products(category: str = None, min_price: float = None, max_price: float = None) -> List[Dict]:
    if order_items_df.empty:
        return []
    avg_prices = order_items_df.groupby('product_id')['price'].mean().to_dict()
    filtered = []
    for _, row in products_df.iterrows():
        pid = row['product_id']
        if pid not in avg_prices:
            continue
        price = avg_prices[pid]
        if min_price and price < min_price:
            continue
        if max_price and price > max_price:
            continue
        cat_pt = row.get('product_category_name', '')
        cat_en = row.get('product_category_name_english', '')
        if category:
            if category.lower() not in cat_pt.lower() and category.lower() not in cat_en.lower():
                continue
        filtered.append({
            'product_id': pid,
            'category': cat_en or cat_pt,
            'avg_price': price
        })
    return filtered

# =============================================================================
# 4. Out‑of‑Stock Suggestions
# =============================================================================
def suggest_alternatives(product_id: str, limit: int = 3) -> List[Dict]:
    prod = get_product(product_id)
    if prod:
        return []
    return fuzzy_search(product_id, limit=limit)

# =============================================================================
# 5. Price Difference Calculator
# =============================================================================
def compare_prices(product_id1: str, product_id2: str) -> Optional[Dict]:
    if order_items_df.empty:
        return None
    avg_prices = order_items_df.groupby('product_id')['price'].mean().to_dict()
    if product_id1 not in avg_prices or product_id2 not in avg_prices:
        return None
    price1 = avg_prices[product_id1]
    price2 = avg_prices[product_id2]
    diff = price1 - price2
    prod1 = get_product(product_id1)
    prod2 = get_product(product_id2)
    return {
        'product1': prod1,
        'price1': price1,
        'product2': prod2,
        'price2': price2,
        'difference': diff,
        'cheaper': product_id1 if diff < 0 else product_id2,
        'savings': abs(diff)
    }

# =============================================================================
# Compare products within an order
# =============================================================================
def compare_order_products(order_id: str) -> str:
    order = get_order(order_id)
    if not order:
        return f"Order {order_id} not found."

    items = order.get('items', [])
    if len(items) < 2:
        return f"Order {order_id} contains only one item. Ask for alternatives if you want similar products."

    output = f"**Comparison of products in order {order_id}:**\n\n"
    output += "| Product | Category | Price | Freight |\n"
    output += "|---------|----------|-------|---------|\n"
    for item in items:
        prod = item.get('product', {})
        cat = prod.get('category', 'Unknown') if prod else 'Unknown'
        price = item.get('price', 'N/A')
        freight = item.get('freight_value', 'N/A')
        pid = item.get('product_id', '')
        output += f"| {pid[:8]}... | {cat} | {price} | {freight} |\n"

    if len(items) >= 2:
        prices = [item.get('price', 0) for item in items if item.get('price') is not None]
        if prices:
            max_price = max(prices)
            min_price = min(prices)
            diff = max_price - min_price
            output += f"\n**Price difference:** Most expensive is **{max_price}**, cheapest is **{min_price}** (difference: **{diff}**)."

    return output

# =============================================================================
# 6. Smart Recommendations Engine
# =============================================================================
class RecommendationEngine:
    def __init__(self):
        self.history = []
        self.product_interests = defaultdict(int)

    def add_interaction(self, query: str, response: str):
        self.history.append((query, response))
        cat_match = re.search(r"category '([^']+)'", response)
        if cat_match:
            cat = cat_match.group(1)
            self.product_interests[cat] += 1

    def get_recommendations(self, limit: int = 3) -> List[str]:
        if not self.product_interests:
            return ["Try searching for popular categories: electronics, furniture, shoes"]
        sorted_cats = sorted(self.product_interests.items(), key=lambda x: x[1], reverse=True)
        return [f"Search for {cat} products (you asked about it {count} times)" for cat, count in sorted_cats[:limit]]

# =============================================================================
# 7. Follow‑Up Suggestions
# =============================================================================
def generate_followups(question: str, response: str) -> List[str]:
    suggestions = []
    if "order" in response.lower():
        suggestions.append("Track another order")
    if "product" in response.lower() or "products" in response.lower():
        suggestions.append("Compare products")
        suggestions.append("Find cheaper alternatives")
    if "price" in response.lower() or "cost" in response.lower():
        suggestions.append("Compare prices")
    if not suggestions:
        suggestions = ["Search for products", "Check order status", "Find product details"]
    return suggestions[:4]

# =============================================================================
# 8. Analytics Dashboard
# =============================================================================
class Analytics:
    def __init__(self, db_name="analytics.db"):
        self.db_name = db_name
        self._init_db()
        self.total_queries = 0
        self.tool_usage = defaultdict(int)
        self.response_times = []
        self.failed_tool_calls = 0

    def _init_db(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        # General analytics table
        c.execute('''CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            query TEXT,
            tool_used TEXT,
            response_time REAL,
            success INTEGER
        )''')
        # Product searches with UNIQUE constraint for safe upsert
        c.execute('''CREATE TABLE IF NOT EXISTS product_searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT UNIQUE,
            count INTEGER DEFAULT 1
        )''')
        conn.commit()
        conn.close()

    def log_query(self, query: str, tool_used: str, response_time: float, success: bool):
        self.total_queries += 1
        self.tool_usage[tool_used] += 1
        self.response_times.append(response_time)
        if not success:
            self.failed_tool_calls += 1

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        # Insert into analytics
        c.execute(
            "INSERT INTO analytics (query, tool_used, response_time, success) VALUES (?, ?, ?, ?)",
            (query, tool_used, response_time, 1 if success else 0)
        )

        # Upsert product search count without ON CONFLICT
        if "search" in query.lower() or "find" in query.lower():
            try:
                c.execute(
                    "UPDATE product_searches SET count = count + 1 WHERE query = ?",
                    (query,)
                )
                if c.rowcount == 0:
                    c.execute(
                        "INSERT INTO product_searches (query, count) VALUES (?, 1)",
                        (query,)
                    )
            except sqlite3.OperationalError:
                # Fallback if UNIQUE constraint missing (old DB)
                try:
                    c.execute(
                        "INSERT INTO product_searches (query, count) VALUES (?, 1)",
                        (query,)
                    )
                except sqlite3.IntegrityError:
                    c.execute(
                        "UPDATE product_searches SET count = count + 1 WHERE query = ?",
                        (query,)
                    )
        conn.commit()
        conn.close()

    def get_metrics(self) -> Dict:
        avg_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        most_used_tool = max(self.tool_usage.items(), key=lambda x: x[1])[0] if self.tool_usage else "None"
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT query, count FROM product_searches ORDER BY count DESC LIMIT 5")
        top_searches = c.fetchall()
        conn.close()
        return {
            "total_queries": self.total_queries,
            "most_used_tool": most_used_tool,
            "avg_response_time": round(avg_time, 3),
            "failed_tool_calls": self.failed_tool_calls,
            "most_searched": top_searches
        }

# =============================================================================
# 9. Main Integration Function
# =============================================================================
_analytics = Analytics()
_recommendation_engine = RecommendationEngine()

def process_with_advanced_features(question: str, agent_func=None) -> str:
    # Lazy import to break circular dependency
    if agent_func is None:
        from agent import run_agent
        agent_func = run_agent

    qs = split_questions(question)
    if len(qs) > 1:
        responses = []
        for q in qs:
            resp = agent_func(q)
            responses.append(resp)
            _analytics.log_query(q, "multi_tool", 0.0, True)
            _recommendation_engine.add_interaction(q, resp)
        combined = "\n\n".join([f"Q: {q}\nA: {resp}" for q, resp in zip(qs, responses)])
        last_q = qs[-1]
        last_resp = responses[-1]
        fups = generate_followups(last_q, last_resp)
        if fups:
            combined += "\n\nYou may also ask:\n• " + "\n• ".join(fups)
        return combined
    else:
        resp = agent_func(question)
        _analytics.log_query(question, "single_tool", 0.0, True)
        _recommendation_engine.add_interaction(question, resp)
        fups = generate_followups(question, resp)
        if fups:
            resp += "\n\nYou may also ask:\n• " + "\n• ".join(fups)
        return resp

def get_analytics_dashboard() -> Dict:
    return _analytics.get_metrics()