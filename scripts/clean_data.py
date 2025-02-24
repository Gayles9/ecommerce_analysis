import pandas as pd
import sqlite3

# Connect to the database
conn = sqlite3.connect('ecommerce.db')

# Read the orders table to inspect data types
orders = pd.read_sql_query("SELECT * FROM orders LIMIT 5", conn)
print("Sample orders data:")
print(orders.head())

# Convert order timestamp to datetime (if needed)
# Adjust column name if it differs—commonly it’s named 'order_purchase_timestamp'
try:
    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
except Exception as e:
    print("Conversion error (check column name):", e)

# Check for missing values in each table (sample for orders)
print("Missing values in orders:")
print(orders.isnull().sum())

# You can add further cleaning steps here (e.g., drop duplicates, impute missing values)
# For example, to drop rows with missing timestamps:
orders_clean = orders.dropna(subset=['order_purchase_timestamp'])

# Save cleaned orders back to the database (if needed)
orders_clean.to_sql('orders', conn, if_exists='replace', index=False)
print("Orders table cleaned and updated.")

conn.close()
