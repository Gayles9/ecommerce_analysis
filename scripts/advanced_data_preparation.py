import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime


# Load Data


# Define file paths (adjust if necessary)
orders_path = 'data/olist_orders_dataset.csv'
order_items_path = 'data/olist_order_items_dataset.csv'
customers_path = 'data/olist_customers_dataset.csv'
products_path = 'data/olist_products_dataset.csv'

# Load datasets into DataFrames
orders = pd.read_csv(orders_path)
order_items = pd.read_csv(order_items_path)
customers = pd.read_csv(customers_path)
products = pd.read_csv(products_path)

print("Loaded datasets:")
print("Orders shape:", orders.shape)
print("Order Items shape:", order_items.shape)
print("Customers shape:", customers.shape)
print("Products shape:", products.shape)


# Data Cleaning & Date Conversion


# Convert date columns in orders to datetime objects
if 'order_purchase_timestamp' in orders.columns:
    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'], errors='coerce')
else:
    print("Warning: 'order_purchase_timestamp' not found in orders dataset.")

# (Optional) Check and handle missing values as needed
print("Missing values in orders:\n", orders.isnull().sum())


# Merge Datasets


# Merge orders with order_items on 'order_id'
orders_order_items = pd.merge(order_items, orders, on='order_id', how='left')

# Merge with customers on 'customer_id'
orders_order_items_customers = pd.merge(orders_order_items, customers, on='customer_id', how='left')

# Merge with products on 'product_id'
full_data = pd.merge(orders_order_items_customers, products, on='product_id', how='left')

print("Merged dataset shape:", full_data.shape)


# Advanced Metrics Computation


# Revenue Metrics: Calculate Monthly Revenue and Growth Rate
# Create a new column for month (as a period, e.g., '2017-08')
full_data['order_month'] = full_data['order_purchase_timestamp'].dt.to_period('M')

# Aggregate monthly revenue by summing the 'price' from order_items
monthly_revenue = full_data.groupby('order_month')['price'].sum().reset_index()
monthly_revenue.columns = ['order_month', 'total_revenue']
# Convert period to string for easier plotting later
monthly_revenue['order_month'] = monthly_revenue['order_month'].astype(str)

# Calculate month-over-month revenue growth rate (in percentage)
monthly_revenue['revenue_growth_rate'] = monthly_revenue['total_revenue'].pct_change() * 100

print("\nMonthly Revenue Metrics:")
print(monthly_revenue.head())

# Average Order Value (AOV)
# Calculate the total order value per order by summing prices from order_items
order_values = full_data.groupby('order_id')['price'].sum().reset_index().rename(columns={'price': 'order_value'})

# Compute overall Average Order Value (AOV)
average_order_value = order_values['order_value'].mean()
print("\nAverage Order Value (AOV): ${:.2f}".format(average_order_value))

# Customer Segmentation Features
# Compute total spending per customer
customer_spending = full_data.groupby('customer_id')['price'].sum().reset_index().rename(columns={'price': 'total_spent'})

# Compute order frequency (number of unique orders per customer)
customer_orders = full_data.groupby('customer_id')['order_id'].nunique().reset_index().rename(columns={'order_id': 'order_frequency'})

# Compute recency: days since the customer's last order.
# Use the maximum order_purchase_timestamp in the data as the reference date.
reference_date = full_data['order_purchase_timestamp'].max()
customer_last_order = full_data.groupby('customer_id')['order_purchase_timestamp'].max().reset_index().rename(
    columns={'order_purchase_timestamp': 'last_order_date'}
)
customer_last_order['recency_days'] = (reference_date - customer_last_order['last_order_date']).dt.days

# Merge the customer features into one DataFrame
customer_features = pd.merge(customer_spending, customer_orders, on='customer_id')
customer_features = pd.merge(customer_features, customer_last_order[['customer_id', 'recency_days']], on='customer_id')

print("\nCustomer Segmentation Features (first 5 rows):")
print(customer_features.head())

# Product Performance Metrics: Sales by Product Category
# Sum total sales (price) by product category
product_performance = full_data.groupby('product_category_name')['price'].sum().reset_index().rename(
    columns={'price': 'total_sales'}
)

# Count number of unique orders per product category
orders_per_category = full_data.groupby('product_category_name')['order_id'].nunique().reset_index().rename(
    columns={'order_id': 'order_count'}
)

# Merge the product performance metrics
product_performance = pd.merge(product_performance, orders_per_category, on='product_category_name')

print("\nProduct Performance Metrics (first 5 rows):")
print(product_performance.head())


# Step 5: Save Enhanced DataFrames to SQLite Database


# Create/connect to a new SQLite database
conn = sqlite3.connect('ecommerce_advanced.db')

# Write DataFrames to the database
monthly_revenue.to_sql('monthly_revenue', conn, if_exists='replace', index=False)
order_values.to_sql('order_values', conn, if_exists='replace', index=False)
customer_features.to_sql('customer_features', conn, if_exists='replace', index=False)
product_performance.to_sql('product_performance', conn, if_exists='replace', index=False)

conn.close()
print("\nEnhanced data saved to 'ecommerce_advanced.db'.")
