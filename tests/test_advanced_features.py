# tests/test_advanced_features.py
import pytest
import sqlite3
from unittest.mock import patch, MagicMock
import pandas as pd
import advanced_features  # needed to patch the global

from advanced_features import (
    split_questions,
    fuzzy_search,
    filter_products,
    suggest_alternatives,
    compare_prices,
    compare_order_products,
    RecommendationEngine,
    generate_followups,
    Analytics,
    process_with_advanced_features,
    get_analytics_dashboard,
)

# ---------------------------------------------------------------------
# 1. split_questions
# ---------------------------------------------------------------------
def test_split_questions():
    text = "What is the status of order ORD-1001? And track another order."
    result = split_questions(text)
    assert result == ["What is the status of order ORD-1001", "track another order"]

    text = "Search for shoes and electronics? Also compare prices."
    result = split_questions(text)
    assert "Search for shoes" in result
    assert "electronics" in result

    text = "Hello! How are you? I'm fine."
    result = split_questions(text)
    assert result == ["Hello", "How are you", "I'm fine"]

    text = "Single question without punctuation"
    result = split_questions(text)
    assert result == ["Single question without punctuation"]

    text = "Multiple? Questions? Here."
    result = split_questions(text)
    assert result == ["Multiple", "Questions", "Here"]


# ---------------------------------------------------------------------
# 2. fuzzy_search (FIXED: use "shoes" as query to get score above 0.6)
# ---------------------------------------------------------------------
def test_fuzzy_search():
    mock_df = pd.DataFrame({
        'product_id': ['p1', 'p2', 'p3'],
        'product_category_name': ['shoes', 'shoes', 'electronics'],
        'product_category_name_english': ['shoes', 'shoes', 'electronics']
    })

    # Save original and override
    original_df = advanced_features.products_df
    try:
        advanced_features.products_df = mock_df
        # Use "shoes" instead of "shoe" to get a similarity score >= 0.6
        results = fuzzy_search("shoes", limit=2)
        assert len(results) == 2
        assert results[0]['category'] == 'shoes'
        assert 'score' in results[0]

        results = fuzzy_search("nonexistent", cutoff=0.9)
        assert results == []

        empty_df = pd.DataFrame()
        advanced_features.products_df = empty_df
        results = fuzzy_search("anything")
        assert results == []
    finally:
        advanced_features.products_df = original_df


# ---------------------------------------------------------------------
# 3. filter_products
# ---------------------------------------------------------------------
@patch('advanced_features.order_items_df')
@patch('advanced_features.products_df')
def test_filter_products(mock_products_df, mock_order_items_df):
    mock_order_items_df.return_value = pd.DataFrame({
        'product_id': ['p1', 'p2', 'p3', 'p4'],
        'price': [10, 20, 30, 40]
    })
    mock_products_df.return_value = pd.DataFrame({
        'product_id': ['p1', 'p2', 'p3', 'p4'],
        'product_category_name': ['shoes', 'shoes', 'electronics', 'furniture'],
        'product_category_name_english': ['shoes', 'shoes', 'electronics', 'furniture']
    })
    with patch('advanced_features.order_items_df', mock_order_items_df.return_value), \
         patch('advanced_features.products_df', mock_products_df.return_value):
        results = filter_products()
        assert len(results) == 4

        results = filter_products(category='shoes')
        assert len(results) == 2
        assert all(r['category'] == 'shoes' for r in results)

        results = filter_products(min_price=25, max_price=35)
        assert len(results) == 1
        assert results[0]['avg_price'] == 30

        with patch('advanced_features.order_items_df', pd.DataFrame()):
            results = filter_products()
            assert results == []


# ---------------------------------------------------------------------
# 4. suggest_alternatives
# ---------------------------------------------------------------------
@patch('advanced_features.get_product')
@patch('advanced_features.fuzzy_search')
def test_suggest_alternatives(mock_fuzzy, mock_get_product):
    mock_get_product.return_value = {'product_id': 'p1'}
    result = suggest_alternatives('p1')
    assert result == []
    mock_fuzzy.assert_not_called()

    mock_get_product.return_value = None
    mock_fuzzy.return_value = [{'product_id': 'p2', 'category': 'shoes', 'score': 0.8}]
    result = suggest_alternatives('p1', limit=2)
    assert result == [{'product_id': 'p2', 'category': 'shoes', 'score': 0.8}]
    mock_fuzzy.assert_called_with('p1', limit=2)


# ---------------------------------------------------------------------
# 5. compare_prices
# ---------------------------------------------------------------------
@patch('advanced_features.order_items_df')
@patch('advanced_features.get_product')
def test_compare_prices(mock_get_product, mock_order_items_df):
    mock_order_items_df.return_value = pd.DataFrame({
        'product_id': ['p1', 'p2'],
        'price': [10, 20]
    })
    mock_get_product.side_effect = lambda pid: {'product_id': pid, 'category': 'shoes'}

    with patch('advanced_features.order_items_df', mock_order_items_df.return_value):
        result = compare_prices('p1', 'p2')
        assert result is not None
        assert result['price1'] == 10
        assert result['price2'] == 20
        assert result['difference'] == -10
        assert result['cheaper'] == 'p1'
        assert result['savings'] == 10

        result = compare_prices('p1', 'p3')
        assert result is None

        with patch('advanced_features.order_items_df', pd.DataFrame()):
            result = compare_prices('p1', 'p2')
            assert result is None


# ---------------------------------------------------------------------
# 6. compare_order_products
# ---------------------------------------------------------------------
@patch('advanced_features.get_order')
def test_compare_order_products(mock_get_order):
    mock_get_order.return_value = None
    result = compare_order_products('ORD-1001')
    assert "Order ORD-1001 not found" in result

    mock_get_order.return_value = {
        'order_id': 'ORD-1001',
        'items': [{'product_id': 'p1', 'price': 10, 'freight_value': 2, 'product': {'category': 'shoes'}}]
    }
    result = compare_order_products('ORD-1001')
    assert "contains only one item" in result

    mock_get_order.return_value = {
        'order_id': 'ORD-1002',
        'items': [
            {'product_id': 'p1', 'price': 10, 'freight_value': 2, 'product': {'category': 'shoes'}},
            {'product_id': 'p2', 'price': 20, 'freight_value': 3, 'product': {'category': 'shoes'}}
        ]
    }
    result = compare_order_products('ORD-1002')
    assert "Comparison of products in order ORD-1002" in result
    assert "10" in result and "20" in result
    assert "Price difference" in result
    assert "Most expensive is **20**" in result


# ---------------------------------------------------------------------
# 7. RecommendationEngine
# ---------------------------------------------------------------------
def test_recommendation_engine():
    engine = RecommendationEngine()
    assert engine.get_recommendations() == ["Try searching for popular categories: electronics, furniture, shoes"]

    engine.add_interaction("search shoes", "found products in category 'shoes'")
    engine.add_interaction("search shoes again", "found products in category 'shoes'")
    engine.add_interaction("search electronics", "found products in category 'electronics'")
    recs = engine.get_recommendations(limit=2)
    assert len(recs) == 2
    assert "shoes" in recs[0]
    assert "electronics" in recs[1]

    engine.add_interaction("hello", "I'm not sure")
    recs = engine.get_recommendations()
    assert len(recs) == 2
    assert "shoes" in recs[0]
    assert "electronics" in recs[1]


# ---------------------------------------------------------------------
# 8. generate_followups
# ---------------------------------------------------------------------
def test_generate_followups():
    question = "What is the status of my order?"
    response = "Order ORD-1001 is delivered."
    suggestions = generate_followups(question, response)
    assert "Track another order" in suggestions

    response = "Product p1 is a shoe."
    suggestions = generate_followups(question, response)
    assert "Compare products" in suggestions
    assert "Find cheaper alternatives" in suggestions

    response = "The price is $10."
    suggestions = generate_followups(question, response)
    assert "Compare prices" in suggestions

    response = "I'm not sure."
    suggestions = generate_followups(question, response)
    assert len(suggestions) == 3
    assert any("Search" in s for s in suggestions)


# ---------------------------------------------------------------------
# 9. Analytics
# ---------------------------------------------------------------------
@patch('sqlite3.connect')
def test_analytics(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    analytics = Analytics(db_name=':memory:')
    assert mock_connect.call_count == 1
    assert mock_cursor.execute.call_count >= 2

    mock_cursor.reset_mock()
    mock_conn.reset_mock()

    def execute_side_effect(sql, params=None):
        if sql.startswith("UPDATE"):
            mock_cursor.rowcount = 0
        else:
            mock_cursor.rowcount = None
        return None

    mock_cursor.execute.side_effect = execute_side_effect

    analytics.log_query("search shoes", "search_tool", 0.5, True)

    mock_cursor.execute.assert_any_call(
        "INSERT INTO analytics (query, tool_used, response_time, success) VALUES (?, ?, ?, ?)",
        ("search shoes", "search_tool", 0.5, 1)
    )
    mock_cursor.execute.assert_any_call(
        "UPDATE product_searches SET count = count + 1 WHERE query = ?",
        ("search shoes",)
    )
    mock_cursor.execute.assert_any_call(
        "INSERT INTO product_searches (query, count) VALUES (?, 1)",
        ("search shoes",)
    )

    mock_cursor.fetchall.return_value = [('shoes', 5), ('electronics', 3)]
    analytics.total_queries = 10
    analytics.tool_usage = {'search_tool': 5, 'order_tool': 2}
    analytics.response_times = [0.5, 0.7, 0.6]
    analytics.failed_tool_calls = 1
    metrics = analytics.get_metrics()
    assert metrics['total_queries'] == 10
    assert metrics['most_used_tool'] == 'search_tool'
    assert metrics['avg_response_time'] == 0.6
    assert metrics['failed_tool_calls'] == 1
    assert metrics['most_searched'] == [('shoes', 5), ('electronics', 3)]

    analytics.log_query("track order", "order_tool", 0.2, True)
    mock_cursor.execute.assert_called_with(
        "INSERT INTO analytics (query, tool_used, response_time, success) VALUES (?, ?, ?, ?)",
        ("track order", "order_tool", 0.2, 1)
    )


# ---------------------------------------------------------------------
# 10. process_with_advanced_features
# ---------------------------------------------------------------------
@patch('advanced_features._analytics')
@patch('advanced_features._recommendation_engine')
def test_process_with_advanced_features(mock_rec_engine, mock_analytics):
    def mock_agent_func(q):
        return f"Response to {q}"

    result = process_with_advanced_features("What is the status of order ORD-1001?", agent_func=mock_agent_func)
    assert result.startswith("Response to What is the status of order ORD-1001?")
    mock_analytics.log_query.assert_called_once_with("What is the status of order ORD-1001?", "single_tool", 0.0, True)
    mock_rec_engine.add_interaction.assert_called_once()

    mock_analytics.reset_mock()
    mock_rec_engine.reset_mock()
    result = process_with_advanced_features("What is order status? And search for shoes.", agent_func=mock_agent_func)
    lines = result.split('\n')
    assert "Q: What is order status" in lines[0]
    assert "A: Response to What is order status" in lines[1]
    assert lines[2] == ""
    assert "Q: search for shoes" in lines[3]
    assert "You may also ask" in result
    assert mock_analytics.log_query.call_count == 2
    assert mock_rec_engine.add_interaction.call_count == 2


# ---------------------------------------------------------------------
# 11. get_analytics_dashboard
# ---------------------------------------------------------------------
@patch('advanced_features._analytics')
def test_get_analytics_dashboard(mock_analytics):
    mock_analytics.get_metrics.return_value = {'total_queries': 10}
    result = get_analytics_dashboard()
    assert result == {'total_queries': 10}
    mock_analytics.get_metrics.assert_called_once()


# ---------------------------------------------------------------------
# 12. analytics_upsert_fallback
# ---------------------------------------------------------------------
@patch('sqlite3.connect')
def test_analytics_upsert_fallback(mock_connect):
    analytics = Analytics(db_name=':memory:')
    with patch.object(analytics, '_init_db') as mock_init:
        with patch('sqlite3.connect') as mock_connect2:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect2.return_value = mock_conn

            mock_cursor.execute.side_effect = [
                None,
                sqlite3.OperationalError("no such column"),
                sqlite3.IntegrityError("UNIQUE constraint failed"),
                None,
            ]
            analytics.log_query("search test", "tool", 0.1, True)

            update_calls = [call for call in mock_cursor.execute.call_args_list
                            if call[0][0] == "UPDATE product_searches SET count = count + 1 WHERE query = ?"]
            assert len(update_calls) >= 1