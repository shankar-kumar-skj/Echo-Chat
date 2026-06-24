# tests/test_agent.py
import pytest
from unittest.mock import patch, MagicMock
from agent import run_agent, extract_order_id, extract_product_id, extract_category_name

def test_extract_order_id():
    assert extract_order_id("ORD-1001") == "ORD-1001"
    assert extract_order_id("abc-123") is None
    assert extract_order_id("9e7b6a4f-5c8d-4a1b-9f2e-5b8c6a7d8e9f") == "9e7b6a4f-5c8d-4a1b-9f2e-5b8c6a7d8e9f"
    assert extract_order_id("1234567890abcdef1234567890abcdef") == "1234567890abcdef1234567890abcdef"

def test_extract_product_id():
    assert extract_product_id("1e9e8ef04dbcff4541ed26657ea517e5") == "1e9e8ef04dbcff4541ed26657ea517e5"
    assert extract_product_id("abcd-1234") is None

def test_extract_category_name():
    assert extract_category_name("category name is shoes") == "shoes"
    assert extract_category_name("category: electronics") == "electronics"
    assert extract_category_name("category furniture") == "furniture"
    assert extract_category_name("no category here") is None

@patch('agent.get_order')
def test_run_agent_order_status(mock_get_order):
    mock_get_order.return_value = {
        'order_id': 'ORD-1001',
        'order_status': 'delivered',
        'items': [{'product_id': 'p1', 'price': 10.0}]
    }
    response = run_agent("What is the status of order ORD-1001?")
    assert "delivered" in response
    mock_get_order.assert_called_with("ORD-1001")

@patch('agent.get_order')
def test_run_agent_order_not_found(mock_get_order):
    mock_get_order.return_value = None
    response = run_agent("Where is order ORD-9999?")
    assert "couldn't find order" in response

@patch('agent.get_product')
@patch('agent.extract_product_id')
def test_run_agent_product_details(mock_extract, mock_get_product):
    # Force the agent to treat "p1" as a product ID
    mock_extract.return_value = "p1"
    mock_get_product.return_value = {
        'product_id': 'p1',
        'category': 'shoes',
        'product_photos_qty': 2,
        'product_weight_g': 500
    }
    response = run_agent("Tell me about product p1")
    assert "shoes" in response
    assert "2 photo(s)" in response

@patch('agent.search_products')
def test_run_agent_search(mock_search):
    mock_search.return_value = [{'product_id': 'p1', 'category': 'shoes'}]
    response = run_agent("Search for shoes")
    assert "found" in response
    mock_search.assert_called_with("shoes")

@patch('agent.search_products')
def test_run_agent_search_empty(mock_search):
    mock_search.return_value = []
    response = run_agent("Search for nonexistent")
    assert "couldn't find any products" in response

def test_run_agent_fallback():
    response = run_agent("Hello")
    assert "not sure how to help" in response