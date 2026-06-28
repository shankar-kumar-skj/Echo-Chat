# agent.py
import re
from tools import get_order, search_products, get_product
import logging

logger = logging.getLogger(__name__)

def extract_order_id(text: str):
    patterns = [
        r'ORD-\d+',
        r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
        r'[0-9a-f]{32}'
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return None

def extract_product_id(text: str):
    patterns = [
        r'[0-9a-f]{32}',
        r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return None

def extract_category_name(text: str):
    patterns = [
        r'category\s+name\s+is\s+([a-zA-Z_]+)',
        r'category\s*:\s*([a-zA-Z_]+)',
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    match = re.search(r'category\s+([a-zA-Z_]+)', text, re.IGNORECASE)
    if match:
        candidate = match.group(1).strip()
        try:
            results = search_products(candidate, limit=1)
            if results:
                return candidate
        except Exception as e:
            logger.error(f"Error validating category '{candidate}': {e}")
    return None

def is_hex_id(text: str):
    return bool(re.fullmatch(r'[0-9a-f]{32}', text, re.IGNORECASE)) or bool(
        re.fullmatch(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', text, re.IGNORECASE)
    )

def is_ord_id(text: str):
    return bool(re.fullmatch(r'ORD-\d+', text, re.IGNORECASE))

def run_agent(question: str) -> str:
    logger.info(f"Processing question: {question}")
    question_lower = question.lower()

    try:
        stripped = question.strip()
        if is_ord_id(stripped):
            order = get_order(stripped)
            if order:
                status = order.get('order_status', 'unknown')
                return f"Order {stripped} has status **{status}** and contains {len(order.get('items', []))} item(s)."
            return f"Sorry, I couldn't find order {stripped}. Please verify."

        if is_hex_id(stripped):
            product = get_product(stripped)
            if product:
                name = product.get('category', 'Unknown product')
                return f"Product {stripped} is a '{name}'. It has {product.get('product_photos_qty', 0)} photo(s) and weighs {product.get('product_weight_g', 'unknown')}g."
            order = get_order(stripped)
            if order:
                status = order.get('order_status', 'unknown')
                return f"Order {stripped} has status **{status}** and contains {len(order.get('items', []))} item(s)."
            return f"I couldn't find any product or order with ID '{stripped}'. Please verify."

        # --- Compare branch (lazy import) ---
        if "compare" in question_lower and "order" in question_lower:
            order_id = extract_order_id(question)
            if order_id:
                from advanced_features import compare_order_products
                return compare_order_products(order_id)
            else:
                return "I couldn't find an order ID in your question. Please specify the order ID, e.g., 'compare products in ORD-1002'."

        order_id = extract_order_id(question)
        if order_id:
            if re.match(r'ORD-\d+', order_id, re.IGNORECASE):
                order = get_order(order_id)
                if order is None:
                    return f"Sorry, I couldn't find order {order_id}. Please verify the ID and try again."
                if "status" in question_lower or "where" in question_lower:
                    status = order.get('order_status', 'unknown')
                    return f"Your order {order_id} is currently **{status}**."
                elif "alternative" in question_lower or "cheaper" in question_lower:
                    items = order.get('items', [])
                    if not items:
                        return f"Order {order_id} has no items. I cannot find alternatives."
                    first_item = items[0]
                    product = first_item.get('product')
                    if not product:
                        return f"Sorry, I could not retrieve product details for the item in order {order_id}."
                    original_price = first_item.get('price')
                    if original_price is None:
                        return "I couldn't determine the price of the product to compare alternatives."
                    category = product.get('category')
                    if not category:
                        category = "product"
                    alternatives = search_products(category, limit=10)
                    cheaper_alternatives = [alt for alt in alternatives if alt.get('product_id') != product.get('product_id')]
                    if not cheaper_alternatives:
                        return f"I couldn't find any cheaper alternatives to the {category} you ordered."
                    alt_names = [f"{alt['category']} (ID: {alt['product_id']})" for alt in cheaper_alternatives[:3]]
                    alt_str = ", ".join(alt_names)
                    return f"I found some alternatives: {alt_str}. Would you like more details on any?"
                else:
                    status = order.get('order_status', 'unknown')
                    total_items = len(order.get('items', []))
                    return f"Order {order_id} has status **{status}** and contains {total_items} item(s)."
            else:
                if "order" in question_lower:
                    order = get_order(order_id)
                    if order:
                        if "status" in question_lower or "where" in question_lower:
                            status = order.get('order_status', 'unknown')
                            return f"Your order {order_id} is currently **{status}**."
                        elif "alternative" in question_lower or "cheaper" in question_lower:
                            items = order.get('items', [])
                            if not items:
                                return f"Order {order_id} has no items. I cannot find alternatives."
                            first_item = items[0]
                            product = first_item.get('product')
                            if not product:
                                return f"Sorry, I could not retrieve product details for the item in order {order_id}."
                            original_price = first_item.get('price')
                            if original_price is None:
                                return "I couldn't determine the price of the product to compare alternatives."
                            category = product.get('category')
                            if not category:
                                category = "product"
                            alternatives = search_products(category, limit=10)
                            cheaper_alternatives = [alt for alt in alternatives if alt.get('product_id') != product.get('product_id')]
                            if not cheaper_alternatives:
                                return f"I couldn't find any cheaper alternatives to the {category} you ordered."
                            alt_names = [f"{alt['category']} (ID: {alt['product_id']})" for alt in cheaper_alternatives[:3]]
                            alt_str = ", ".join(alt_names)
                            return f"I found some alternatives: {alt_str}. Would you like more details on any?"
                        else:
                            status = order.get('order_status', 'unknown')
                            total_items = len(order.get('items', []))
                            return f"Order {order_id} has status **{status}** and contains {total_items} item(s)."
                    else:
                        return f"Sorry, I couldn't find order {order_id}. Please verify the ID and try again."

        product_id = extract_product_id(question)
        if product_id:
            product = get_product(product_id)
            if product:
                name = product.get('category', 'Unknown product')
                return f"Product {product_id} is a '{name}'. It has {product.get('product_photos_qty', 0)} photo(s) and weighs {product.get('product_weight_g', 'unknown')}g."
            return f"Sorry, I couldn't find product {product_id}. Please verify the ID."

        if ("alternative" in question_lower or "cheaper" in question_lower) and "order" not in question_lower:
            return "I need your order ID to check the product and find alternatives. Please provide it like 'order 47770eb9...'."

        if "category" in question_lower:
            category_name = extract_category_name(question)
            if not category_name:
                return "I couldn't extract a category name. Please specify the category clearly, e.g., 'category name is instrumentos_musicais'."
            results = search_products(category_name)
            if not results:
                return f"I couldn't find any products in the category '{category_name}'."
            product_list = ", ".join([f"{r['category']} (ID: {r['product_id']})" for r in results[:5]])
            return f"I found these products in category '{category_name}': {product_list}. Would you like details on any?"

        search_triggers = [
            "search", "find", "suggest", "show", "tell me about",
            "details of", "for", "me", "products", "about"
        ]
        if any(word in question_lower for word in search_triggers):
            query = question_lower
            for word in search_triggers:
                query = query.replace(word, "")
            query = re.sub(r'[^\w\s]', '', query)
            query = ' '.join(query.split())
            if not query:
                return "What would you like me to search for?"
            results = search_products(query)
            if not results:
                return f"I couldn't find any products matching '{query}'. Please try a different keyword."
            result_str = ", ".join([f"{r['category']} (ID: {r['product_id']})" for r in results[:3]])
            return f"I found {len(results)} products: {result_str}. Would you like details on any?"

        return ("I'm not sure how to help. You can ask about order status, product details, "
                "or search for products. For example: 'What is the status of order 47770eb9...?' "
                "or 'Tell me about product 1e9e8ef0...' or 'Compare products in ORD-1002'.")

    except Exception as e:
        logger.error(f"Unhandled error in run_agent: {e}", exc_info=True)
        return "I'm sorry, something went wrong while processing your request. Please try again later."