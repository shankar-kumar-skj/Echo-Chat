# tools.py
import pandas as pd
import os
import shutil
import logging
import kagglehub

logger = logging.getLogger(__name__)

DATA_PATH = "data/"
OLIST_FILES = [
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_products_dataset.csv",
    "product_category_name_translation.csv"
]
CUSTOM_FILES = [
    "custom_orders.csv",
    "custom_order_items.csv",
    "custom_products.csv"
]

def ensure_olist_files():
    os.makedirs(DATA_PATH, exist_ok=True)
    missing = [f for f in OLIST_FILES if not os.path.exists(os.path.join(DATA_PATH, f))]
    if not missing:
        logger.info("All Olist data files are present.")
        return
    logger.info(f"Missing Olist files: {missing}. Downloading from Kaggle...")
    dataset_path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")
    logger.info(f"Dataset downloaded to: {dataset_path}")
    for fname in OLIST_FILES:
        src = os.path.join(dataset_path, fname)
        dst = os.path.join(DATA_PATH, fname)
        if os.path.exists(src):
            shutil.copy(src, dst)
            logger.info(f"Copied {fname} to {DATA_PATH}")
        else:
            logger.error(f"File {fname} not found in downloaded dataset.")
    logger.info("All Olist files are now in data/.")

def load_custom_files():
    custom_orders = pd.DataFrame()
    custom_items = pd.DataFrame()
    custom_products = pd.DataFrame()
    for fname in CUSTOM_FILES:
        path = os.path.join(DATA_PATH, fname)
        if os.path.exists(path):
            df = pd.read_csv(path, encoding='latin1', engine='python')
            df.columns = df.columns.str.strip()
            if fname == "custom_orders.csv":
                custom_orders = df
            elif fname == "custom_order_items.csv":
                custom_items = df
            elif fname == "custom_products.csv":
                custom_products = df
            logger.info(f"Loaded custom {fname} with {len(df)} rows.")
        else:
            logger.info(f"Custom file {fname} not found – skipping.")
    return custom_orders, custom_items, custom_products

def load_data():
    ensure_olist_files()
    orders_file = os.path.join(DATA_PATH, "olist_orders_dataset.csv")
    items_file = os.path.join(DATA_PATH, "olist_order_items_dataset.csv")
    products_file = os.path.join(DATA_PATH, "olist_products_dataset.csv")
    category_file = os.path.join(DATA_PATH, "product_category_name_translation.csv")

    orders_df = pd.read_csv(orders_file, encoding='latin1', engine='python')
    order_items_df = pd.read_csv(items_file, encoding='latin1', engine='python')
    products_df = pd.read_csv(products_file, encoding='latin1', engine='python')
    category_names = pd.read_csv(category_file, encoding='latin1', engine='python')

    orders_df.columns = orders_df.columns.str.strip()
    order_items_df.columns = order_items_df.columns.str.strip()
    products_df.columns = products_df.columns.str.strip()
    category_names.columns = category_names.columns.str.strip()

    key_col = category_names.columns[0]
    products_df = products_df.merge(
        category_names,
        left_on='product_category_name',
        right_on=key_col,
        how='left',
        suffixes=('', '_cat')
    )
    if key_col != 'product_category_name':
        products_df.drop(columns=[key_col], inplace=True)

    custom_orders, custom_items, custom_products = load_custom_files()

    if not custom_orders.empty:
        for col in orders_df.columns:
            if col not in custom_orders.columns:
                custom_orders[col] = None
        orders_df = pd.concat([orders_df, custom_orders], ignore_index=True)
        logger.info(f"Merged custom orders. Total orders: {len(orders_df)}")

    if not custom_items.empty:
        for col in order_items_df.columns:
            if col not in custom_items.columns:
                custom_items[col] = None
        order_items_df = pd.concat([order_items_df, custom_items], ignore_index=True)
        logger.info(f"Merged custom order items. Total items: {len(order_items_df)}")

    if not custom_products.empty:
        for col in products_df.columns:
            if col not in custom_products.columns:
                custom_products[col] = None
        products_df = pd.concat([products_df, custom_products], ignore_index=True)
        logger.info(f"Merged custom products. Total products: {len(products_df)}")

    return orders_df, order_items_df, products_df

# Load once
orders_df, order_items_df, products_df = load_data()

# ----------------------------
# Tool implementations
# ----------------------------
def get_order(order_id: str):
    logger.info(f"get_order called with order_id={order_id}")
    order_row = orders_df[orders_df['order_id'] == order_id]
    if order_row.empty:
        logger.warning(f"Order {order_id} not found.")
        return None
    order = order_row.iloc[0].to_dict()
    items = order_items_df[order_items_df['order_id'] == order_id]
    item_list = []
    for _, item in items.iterrows():
        product_id = item['product_id']
        product = get_product(product_id)
        item_dict = {
            'product_id': product_id,
            'price': item['price'],
            'freight_value': item['freight_value'],
            'product': product
        }
        item_list.append(item_dict)
    order['items'] = item_list
    return order

def search_products(query: str, limit: int = 5):
    logger.info(f"search_products called with query='{query}', limit={limit}")
    if not query:
        return []
    cat_cols = []
    if 'product_category_name' in products_df.columns:
        cat_cols.append('product_category_name')
    if 'product_category_name_english' in products_df.columns:
        cat_cols.append('product_category_name_english')
    if not cat_cols:
        for col in products_df.columns:
            if 'category' in col.lower():
                cat_cols.append(col)
    if not cat_cols:
        logger.error("No category column found in products_df")
        return []
    mask = pd.Series([False] * len(products_df))
    for col in cat_cols:
        mask = mask | products_df[col].str.contains(query, case=False, na=False, regex=False)
    results = products_df[mask].head(limit)
    if results.empty:
        logger.info(f"No products found for query '{query}'.")
        return []
    products_list = []
    for _, row in results.iterrows():
        cat_name = row.get('product_category_name_english')
        if pd.isna(cat_name):
            cat_name = row.get('product_category_name', 'Unknown')
        prod = {
            'product_id': row['product_id'],
            'category': cat_name,
            'product_name_lenght': row.get('product_name_lenght', None),
            'product_description_length': row.get('product_description_length', None),
            'product_photos_qty': row.get('product_photos_qty', None),
            'product_weight_g': row.get('product_weight_g', None),
            'product_length_cm': row.get('product_length_cm', None),
            'product_height_cm': row.get('product_height_cm', None),
            'product_width_cm': row.get('product_width_cm', None),
        }
        products_list.append(prod)
    return products_list

def get_product(product_id: str):
    logger.info(f"get_product called with product_id={product_id}")
    product_row = products_df[products_df['product_id'] == product_id]
    if product_row.empty:
        logger.warning(f"Product {product_id} not found.")
        return None
    row = product_row.iloc[0]
    return {
        'product_id': row['product_id'],
        'category': row.get('product_category_name_english', row.get('product_category_name', None)),
        'product_name_lenght': row.get('product_name_lenght', None),
        'product_description_length': row.get('product_description_length', None),
        'product_photos_qty': row.get('product_photos_qty', None),
        'product_weight_g': row.get('product_weight_g', None),
        'product_length_cm': row.get('product_length_cm', None),
        'product_height_cm': row.get('product_height_cm', None),
        'product_width_cm': row.get('product_width_cm', None),
    }