import pandas as pd
import sqlite3
import os

# Define the path to your data folder
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# Load CSV files (adjust file names if necessary)
orders = pd.read_csv(os.path.join(DATA_DIR, 'olist_orders_dataset.csv'))
order_items = pd.read_csv(os.path.join(DATA_DIR, 'olist_order_items_dataset.csv'))
customers = pd.read_csv(os.path.join(DATA_DIR, 'olist_customers_dataset.csv'))
products = pd.read_csv(os.path.join(DATA_DIR, 'olist_products_dataset.csv'))

# Connect to (or create) a SQLite database in the project root
conn = sqlite3.connect('ecommerce.db')

# Write dataframes to SQL tables (tables will be replaced if they already exist)
orders.to_sql('orders', conn, if_exists='replace', index=False)
order_items.to_sql('order_items', conn, if_exists='replace', index=False)
customers.to_sql('customers', conn, if_exists='replace', index=False)
products.to_sql('products', conn, if_exists='replace', index=False)

print("Data loaded successfully into ecommerce.db!")
conn.close()

