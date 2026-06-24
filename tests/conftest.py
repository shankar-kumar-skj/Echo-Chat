# tests/conftest.py
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch

@pytest.fixture(scope="session")
def sample_orders_df():
    """Return a small sample orders DataFrame."""
    return pd.DataFrame({
        "order_id": ["ORD-1001", "ORD-1002", "ORD-1003"],
        "customer_id": ["c1", "c2", "c3"],
        "order_status": ["delivered", "shipped", "delivered"],
        "order_purchase_timestamp": ["2023-01-01", "2023-01-02", "2023-01-03"]
    })

@pytest.fixture(scope="session")
def sample_order_items_df():
    return pd.DataFrame({
        "order_id": ["ORD-1001", "ORD-1002", "ORD-1002"],
        "product_id": ["p1", "p2", "p3"],
        "price": [10.0, 20.0, 15.0],
        "freight_value": [2.0, 3.0, 2.5]
    })

@pytest.fixture(scope="session")
def sample_products_df():
    return pd.DataFrame({
        "product_id": ["p1", "p2", "p3", "p4"],
        "product_category_name": ["shoes", "shoes", "electronics", "furniture"],
        "product_category_name_english": ["shoes", "shoes", "electronics", "furniture"],
        "product_name_lenght": [10, 12, 8, 15],
        "product_description_length": [50, 60, 40, 70],
        "product_photos_qty": [2, 3, 1, 4],
        "product_weight_g": [500, 600, 200, 1000],
        "product_length_cm": [30, 32, 20, 80],
        "product_height_cm": [10, 12, 8, 40],
        "product_width_cm": [20, 22, 15, 50]
    })