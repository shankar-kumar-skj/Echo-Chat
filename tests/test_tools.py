# tests/test_tools.py
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from tools import get_order, search_products, get_product

# We'll mock the DataFrames globally before importing tools
# Better: use monkeypatch to replace global DataFrames

@pytest.fixture(autouse=True)
def mock_tools_data(monkeypatch, sample_orders_df, sample_order_items_df, sample_products_df):
    """Inject sample data into tools module."""
    import tools
    monkeypatch.setattr(tools, 'orders_df', sample_orders_df)
    monkeypatch.setattr(tools, 'order_items_df', sample_order_items_df)
    monkeypatch.setattr(tools, 'products_df', sample_products_df)

def test_get_order_valid(mock_tools_data):
    order = get_order("ORD-1001")
    assert order is not None
    assert order['order_id'] == "ORD-1001"
    assert order['order_status'] == "delivered"
    assert len(order['items']) == 1
    assert order['items'][0]['product_id'] == "p1"

def test_get_order_invalid():
    order = get_order("INVALID")
    assert order is None

def test_search_products():
    results = search_products("shoes")
    assert len(results) == 2
    assert results[0]['category'] == "shoes"

def test_search_products_empty():
    results = search_products("nonexistent")
    assert results == []

def test_get_product_valid():
    prod = get_product("p2")
    assert prod is not None
    assert prod['product_id'] == "p2"
    assert prod['category'] == "shoes"

def test_get_product_invalid():
    prod = get_product("unknown")
    assert prod is None